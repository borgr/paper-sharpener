#!/usr/bin/env python3
"""Integrity checks: does the document agree with itself.

Every rule here compares the document against itself or against files it names on
disk, so nothing needs outside knowledge. Rules that would need the published record,
a rendered PDF, the funder's call text or the author's intent are not implemented,
because a rule that cannot be decided from the source produces false positives, and a
false positive costs more than a miss.

Second pass adds twenty rules, in three groups. A rewrite that left both versions live
(a repeated sentence, a duplicated paragraph, a macro defined twice, a table row twice, a
heading twice) -- check.py catches only the two-\input and spliced-sentence shapes. The
document against its own numbers (one value written two ways, a rounded figure the exact
one contradicts, a total against the column above it, a hand-numbered run with a gap).
And apparatus completeness, over the .bib the file names (truncated author lists, missing
publication data, preprints with no identifier, working notes that will print, a claim
resting on one unpublished work) plus quotation fidelity and an error inside a quotation,
which is reported and never repaired.

What stays out, and what each one would need. The rendered PDF: page cuts against the page
limit, font and margin minimums, figure text against a renamed term, whether a figure's
values are machine-readable. The published record: author lists and venues in the track
record, whether an in-preparation entry now exists as a preprint, whether the nearest
groups are cited. The funder's call: which reference style is required, whether references
count inside the page limit, portal character caps, NSF's and NIH's own URL and citation
rules, the portal abstract to diff against. And a judgement no pattern makes: which
sentences carry a citable claim, whether an edit moved a proposition's strength, what
level of edit was authorised, whether a style sheet exists, and whether a citation
supports the claim it is attached to -- that last one needs the cited source read.

Interface: checks(src, spans, ctx) -> list[dict]   (see CHECKS_API.md)
"""
import os
import re
import sys
import pathlib
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex

FAMILY = 'integrity'

# Environments that carry a number and therefore need a caption and a label.
FLOAT_ENVS = ('figure', 'figure*', 'table', 'table*', 'algorithm', 'algorithm*',
              'wrapfigure', 'wraptable', 'listing', 'sidewaystable', 'sidewaysfigure')
MATH_ENVS = ('equation', 'align', 'gather', 'multline', 'eqnarray', 'displaymath', 'flalign')
SECTION_CMDS = ('chapter', 'section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph')

# Words an author writes before \ref, and the element type each one promises.
REF_WORDS = {
    'table': 'table', 'tables': 'table', 'tab': 'table', 'tabs': 'table',
    'figure': 'figure', 'figures': 'figure', 'fig': 'figure', 'figs': 'figure',
    'section': 'section', 'sections': 'section', 'sec': 'section', 'secs': 'section',
    'subsection': 'section', 'chapter': 'section', 'appendix': 'section',
    'app': 'section', 'appendices': 'section',
    'equation': 'equation', 'equations': 'equation', 'eq': 'equation', 'eqs': 'equation',
    'eqn': 'equation',
    'algorithm': 'algorithm', 'alg': 'algorithm', 'algorithms': 'algorithm',
    'listing': 'listing', 'lst': 'listing',
}
ENV_TYPE = {'figure': 'figure', 'figure*': 'figure', 'wrapfigure': 'figure',
            'sidewaysfigure': 'figure',
            'table': 'table', 'table*': 'table', 'wraptable': 'table',
            'sidewaystable': 'table',
            'algorithm': 'algorithm', 'algorithm*': 'algorithm',
            'listing': 'listing', 'lstlisting': 'listing', 'verbatim': 'listing'}
for _e in MATH_ENVS:
    ENV_TYPE[_e] = 'equation'
    ENV_TYPE[_e + '*'] = 'equation'

# Hosts whose contents the authors can change after review without a trace.
MUTABLE_HOSTS = ('drive.google.com', 'docs.google.com', 'sites.google.com',
                 'dropbox.com', 'onedrive.live.com', '1drv.ms', 'wetransfer.com',
                 'we.tl', 'mega.nz', 'mediafire.com', 'pastebin.com')

# Strings that exist only in the sample files shipped with conference templates.
# Each string is unique to a template sample file. "Anonymous Author(s)" is deliberately
# absent: under double-blind review it is the correct text, not a leftover.
TEMPLATE_DUMMY = ('Antiquus S.', 'S.~Hippocampus', 'S. Hippocampus', 'Cranberry-Lemon',
                  'Amygdale', 'Yevgeny LeNet', 'Ji Q. Ren', 'hippo,brain,jen',
                  'Natalia Cerebro', 'Lorem ipsum', 'lorem ipsum', 'Institution1')

US_UK = [('behavior', 'behaviour'), ('color', 'colour'), ('favor', 'favour'),
         ('labor', 'labour'), ('honor', 'honour'), ('center', 'centre'),
         ('fiber', 'fibre'), ('defense', 'defence'), ('offense', 'offence'),
         ('modeling', 'modelling'), ('modeled', 'modelled'), ('labeling', 'labelling'),
         ('labeled', 'labelled'), ('canceled', 'cancelled'), ('traveled', 'travelled'),
         ('fulfill', 'fulfil'), ('skillful', 'skilful'), ('artifact', 'artefact'),
         ('program', 'programme')]
# -ise/-ize stems whose two spellings are different words, or are not variants at all.
IZE_DENY = ('analy', 'paraly', 'advi', 'devi', 'revi', 'supervi', 'televi', 'exerci',
            'practi', 'promi', 'compromi', 'franchi', 'incis', 'preci', 'conci',
            'licen', 'expert', 'otherwi', 'likewi', 'surpri', 'enterpri', 'merchandi',
            'improvi', 'disgui', 'chasti', 'demi', 'ari', 'wi', 'ri')


# --------------------------------------------------------------------------- utils
def _blank_comments(src, spans):
    """src with every byte the compiler never sees replaced by a space.

    That means % comments, \\begin{comment} blocks and \\iffalse blocks. Structural
    macros are matched against this and never against raw src, or a commented-out
    \\includegraphics, or a whole retired section parked inside a comment environment,
    would be reported as live.
    """
    out = list(src)

    def blank(a, b):
        for i in range(a, b):
            if out[i] != '\n':
                out[i] = ' '

    for sp in spans:
        if sp.kind == 'comment':
            blank(sp.start, sp.end)
    for m in re.finditer(r'\\begin\s*\{comment\}.*?\\end\s*\{comment\}', src, re.S):
        blank(m.start(), m.end())
    for m in re.finditer(r'\\iffalse\b.*?\\fi\b', src, re.S):
        blank(m.start(), m.end())
    return ''.join(out)


def _arg(s, i):
    """Brace-matched argument starting at the '{' at index i -> (body, end_index)."""
    if i >= len(s) or s[i] != '{':
        return None, i
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return None, i


def _cmd_args(code, name):
    """Yield (start, body) for every \\name{...} with a brace-matched body."""
    for m in re.finditer(r'\\' + name + r'\s*(?:\[[^\]]*\])?\s*(?=\{)', code):
        body, _ = _arg(code, m.end())
        if body is not None:
            yield m.start(), body


def _envs(code):
    """Every environment as (name, begin_start, body_start, body_end, end_end).

    Stack-based, so a figure holding a subfigure or a table holding a tabular each
    report their own extent instead of the regex's first \\end.
    """
    out, stack = [], []
    for m in re.finditer(r'\\(begin|end)\s*\{([^}]{1,40})\}', code):
        kind, name = m.group(1), m.group(2).strip()
        if kind == 'begin':
            stack.append((name, m.start(), m.end()))
        else:
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0] == name:
                    nm, bs, be = stack[k]
                    out.append((nm, bs, be, m.start(), m.end()))
                    del stack[k:]
                    break
    return out


def _unquoted(t):
    """The rendered string with ``...'' quotations blanked.

    A quotation keeps its source's spelling and hyphenation, so normalising it would be
    a misquotation rather than a fix.
    """
    return re.sub(r"``.*?''|``[^\n]*", lambda m: ' ' * len(m.group(0)), t, flags=re.S)


def _norm(t):
    """Collapse a caption or heading to a comparable core."""
    t = re.sub(r'\\label\s*\{[^}]*\}', '', t)
    t = re.sub(r'\\[a-zA-Z@]+\*?', ' ', t)
    t = re.sub(r'[^a-z0-9]+', ' ', t.lower())
    return t.strip()


def _locate(sp, needle):
    """Offset into src for a rendered fragment, by searching the span's own source."""
    if needle:
        probe = needle.strip()[:24]
        i = sp.text.find(probe)
        if i < 0 and len(probe) > 8:
            i = sp.text.find(probe[:8])
        if i >= 0:
            return sp.start + i
    return sp.start


def _F(rule, offset, tier, cost, blocks, text, fix=''):
    return {'rule': rule, 'family': FAMILY, 'offset': int(offset), 'tier': tier,
            'cost': cost, 'blocks': bool(blocks), 'text': text, 'fix': fix}


def _roots(ctx):
    """Directories a relative \\input or \\includegraphics path could be built from."""
    p = ctx.get('path') or ''
    out = []
    if p:
        d = pathlib.Path(p).resolve().parent
        out += [d, d.parent]
    out.append(pathlib.Path.cwd())
    seen, keep = set(), []
    for d in out:
        if str(d) not in seen:
            seen.add(str(d))
            keep.append(d)
    return keep


PACKAGE_IMAGES = ('example-image', 'example-grid', 'blank', 'mwe/')


def _resolve(name, ctx, exts, extra_dirs=()):
    """True when some root + name (+ ext) exists on disk."""
    name = name.strip().strip('"')
    if not name or '\\' in name or '#' in name:
        return True                      # macro-built path: undecidable, stay silent
    if any(name.startswith(x) for x in PACKAGE_IMAGES):
        return True                      # drawn by the mwe package, not a file
    cands = list(extra_dirs) + [pathlib.Path('.')]
    for root in _roots(ctx):
        for sub in cands:
            base = (root / sub / name)
            for e in exts:
                try:
                    if (base if not e else base.with_name(base.name + e)).exists():
                        return True
                except (OSError, ValueError):
                    continue
    return False


# ------------------------------------------------------------------ label plumbing
def _labels(code):
    """label name -> list of offsets, in source order."""
    d = collections.OrderedDict()
    for off, body in _cmd_args(code, 'label'):
        d.setdefault(body.strip(), []).append(off)
    return d


def _label_type(code, envs, off):
    """The element type of the label at offset off: from the innermost float or math
    environment holding it, else 'section' when a sectioning command precedes it."""
    best, best_span = None, None
    for name, bs, bodys, bodye, ee in envs:
        if bs <= off < ee:
            t = ENV_TYPE.get(name)
            if t is None:
                continue
            if best_span is None or (ee - bs) < best_span:
                best, best_span = (name, t), ee - bs
    if best:
        name, t = best
        # A figure built round a tabular, or a table built round an image, is honestly
        # describable either way. Refuse to judge those.
        for nm, bs, bodys, bodye, ee in envs:
            if nm == name and bs <= off < ee:
                body = code[bodys:bodye]
                if t == 'figure' and re.search(r'\\begin\s*\{tabular', body):
                    return 'ambiguous'
                if t == 'table' and re.search(r'\\includegraphics', body):
                    return 'ambiguous'
        return t
    if re.search(r'\\(' + '|'.join(SECTION_CMDS) + r')\*?\s*(\[[^\]]*\])?\s*\{',
                 code[:off][-4000:]):
        return 'section'
    return None


# ------------------------------------------------------------------------- checks


def checks(src, spans, ctx):
    ctx = dict(ctx or {})
    code = _blank_comments(src, spans)
    envs = _envs(code)
    labels = _labels(code)
    prose = [sp for sp in spans if sp.kind == 'text' and sp.rendered.strip()]
    body = ' '.join(sp.rendered for sp in prose)
    submission = ctx.get('stage') == 'submission'
    # Second-pass state, computed once and passed through ctx so the twenty-five
    # first-pass signatures stay untouched.
    ctx['_clean'] = _clean_prose(src, spans, prose)
    ctx['_cites'] = _cite_calls(code)
    ctx['_bib'] = _bib_index(code, ctx)
    out = []
    for fn in (_c_duplicate_label, _c_label_before_caption, _c_ref_type,
               _c_unnumbered_equation, _c_hardcoded_ref, _c_repeated_cite_key,
               _c_undefined_cite_key, _c_missing_graphic, _c_missing_input,
               _c_missing_bib, _c_float_no_caption, _c_float_no_label,
               _c_duplicate_caption, _c_availability, _c_mutable_location,
               _c_no_limitations, _c_quote_balance, _c_hyphen_variant,
               _c_spelling_variety, _c_percentage_math, _c_placeholder_prose,
               _c_template_dummy, _c_prior_submission, _c_commented_label,
               _c_list_count,
               # --- second pass ---
               _c_repeated_sentence, _c_duplicate_paragraph, _c_duplicate_macro,
               _c_repeated_table_row, _c_duplicate_heading,
               _c_number_format_variant, _c_approximate_figure, _c_table_total,
               _c_manual_enumeration_gap,
               _c_quotation_no_source, _c_error_in_quotation,
               _c_attributed_claim_no_cite, _c_named_section_missing,
               _c_bib_abbreviated_authors, _c_bib_missing_pubdata,
               _c_bib_preprint_no_id, _c_bib_note_scaffolding,
               _c_sole_unpublished_support, _c_output_entry_no_date,
               _c_uncited_bibitem):
        try:
            out += fn(src, code, spans, prose, body, envs, labels, ctx, submission) or []
        except Exception:
            continue                     # a broken check must return nothing, not raise
    out.sort(key=lambda f: (f['offset'], f['rule']))
    return out


def _c_duplicate_label(src, code, spans, prose, body, envs, labels, ctx, sub):
    """Two \\label{k} for one key: every \\ref to it resolves to the last one."""
    out = []
    for k, offs in labels.items():
        if len(offs) > 1 and k:
            out.append(_F('duplicate-label', offs[1], 'query', 'free', True,
                          f'\\label{{{k}}} is defined {len(offs)} times, so every '
                          f'\\ref to it points at the last one',
                          'Rename all but one and repoint the references that meant the others'))
    return out


def _c_label_before_caption(src, code, spans, prose, body, envs, labels, ctx, sub):
    """\\label ahead of \\caption inside a float takes the section number."""
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if name not in FLOAT_ENVS:
            continue
        blk = code[bodys:bodye]
        caps = [m.start() for m in re.finditer(r'\\caption\s*(\[[^\]]*\])?\s*\{', blk)]
        labs = [m.start() for m in re.finditer(r'\\label\s*\{', blk)]
        if len(caps) == 1 and len(labs) == 1 and labs[0] < caps[0]:
            out.append(_F('label-before-caption', bodys + labs[0], 'query', 'free', True,
                          f'in this {name}, \\label comes before \\caption, so the '
                          f'reference will print the enclosing section number',
                          'Move the \\label inside or after the \\caption'))
    return out


def _c_ref_type(src, code, spans, prose, body, envs, labels, ctx, sub):
    """"Table \\ref{...}" pointing at a figure, and the other way round."""
    out = []
    for m in re.finditer(r'([A-Za-z]{2,12})\.?[~ ]{0,2}\\(?:eq)?ref\*?\s*\{([^}]*)\}', code):
        word, key = m.group(1).lower(), m.group(2).strip()
        want = REF_WORDS.get(word)
        if not want or key not in labels:
            continue
        got = _label_type(code, envs, labels[key][0])
        if got in (None, 'ambiguous') or got == want:
            continue
        if {want, got} == {'section', 'listing'}:
            continue
        out.append(_F('reference-type-mismatch', m.start(), 'query', 'free', True,
                      f'the text says "{m.group(1)}" but \\label{{{key}}} sits in a '
                      f'{got}',
                      'Point at the element the sentence describes, or correct the word'))
    return out


def _c_unnumbered_equation(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A \\label inside a starred math environment has no number to print."""
    out = []
    refd = set()
    for m in re.finditer(r'\\(?:auto|c|C|eq)?ref\*?\s*\{([^}]*)\}', code):
        refd.add(m.group(1).strip())
    starred = [(n, bs, ee) for n, bs, bodys, bodye, ee in envs
               if n.endswith('*') and n[:-1] in MATH_ENVS]
    for k, offs in labels.items():
        if k not in refd:
            continue
        for off in offs:
            for n, bs, ee in starred:
                if bs <= off < ee and not re.search(r'\\nonumber|\\notag', code[bs:ee]):
                    out.append(_F('reference-to-unnumbered-equation', off, 'query',
                                  'free', True,
                                  f'\\label{{{k}}} is inside {n}, which prints no '
                                  f'number, so the reference to it renders as ??',
                                  f'Drop the star from {n}, or reference the '
                                  f'surrounding text instead'))
                    break
    return out


def _c_commented_label(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A \\ref pointing at a \\label that is now commented out prints as ??.

    check.py's dangling-reference cannot see this one, because the label is still in the
    source and only a comment-stripped view shows that it is gone.
    """
    dead = {}
    for m in re.finditer(r'\\label\s*\{([^}]*)\}', src):
        k = m.group(1).strip()
        if k and k not in labels:
            dead.setdefault(k, m.start())
    if not dead:
        return []
    out = []
    for m in re.finditer(r'\\(?:auto|c|C|eq)?ref\*?\s*\{([^}]*)\}', code):
        k = m.group(1).strip()
        if k in dead:
            out.append(_F('reference-to-commented-out-label', m.start(), 'query', 'free',
                          True,
                          f'\\ref{{{k}}} points at a \\label that survives only inside a '
                          f'comment, so it prints as ??',
                          'Restore the commented element, or repoint the reference at '
                          'what replaced it'))
    return out


_COUNT_WORD = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
               'eight': 8, 'nine': 9, 'ten': 10}
_LIST_ENVS = ('enumerate', 'itemize', 'description')


def _c_list_count(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A stated count that the list right under it does not match."""
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if name not in _LIST_ENVS:
            continue
        lead = code[max(0, bs - 120):bs]
        m = None
        for m in re.finditer(r'\b(two|three|four|five|six|seven|eight|nine|ten)\s+'
                             r'([a-z]{4,}s)\b', lead, re.I):
            pass
        # The count must introduce this list directly. Anything longer than a short
        # colon clause between them and the number is probably counting something else.
        if not m or not re.match(r'^[^.;:]{0,25}:?\s*$', lead[m.end():]):
            continue
        want = _COUNT_WORD[m.group(1).lower()]
        depth, got = 0, 0
        for t in re.finditer(r'\\(begin|end)\s*\{[^}]*\}|\\item\b', code[bodys:bodye]):
            if t.group(0).startswith('\\begin'):
                depth += 1
            elif t.group(0).startswith('\\end'):
                depth -= 1
            elif depth == 0:
                got += 1
        if got and got != want:
            out.append(_F('stated-count-vs-list', bs, 'query', 'free', True,
                          f'the text says {m.group(1).lower()} {m.group(2).lower()} and '
                          f'the {name} under it has {got} items',
                          'Query which is right; the count and the list disagree'))
    return out


_HARD_REF = re.compile(
    r'\b(Table|Tables|Tab|Figure|Figures|Fig|Section|Sections|Sec|Equation|Equations|'
    r'Eq|Appendix|Appendices|App|Algorithm|Algorithms|Alg|Listing)s?\.?\s*'
    r'(\d{1,2}(?:\.\d{1,2})?|[A-H](?:\.\d{1,2})?)(?![\w.])')


def _c_hardcoded_ref(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A number typed into the prose where a \\ref belongs: it will not follow a move."""
    out = []
    for sp in prose:
        for m in _HARD_REF.finditer(sp.rendered):
            after = sp.rendered[m.end():m.end() + 24]
            before = sp.rendered[max(0, m.start() - 90):m.start()]
            # "Table 2 of Smith et al." points into someone else's paper.
            if re.match(r'\s*(of|in|from)\b', after) or '\u2020' in after[:6]:
                continue
            if '\u2020' in before[-80:] or re.search(r'et al|\[[\w.:-]{6,}\]', before[-80:]):
                continue
            # "Part A, Section 3 - Budget" names the funder's form, which does not move.
            if re.search(r'Part\s+[AB]\b|submission form|\bthe form\b|\bthe call\b|'
                         r'guidelines|\bthe guide\b|\btemplate\b', before[-70:] + after,
                         re.I):
                continue
            out.append(_F('hardcoded-cross-reference', _locate(sp, m.group(0)), 'query',
                          'free', False,
                          f'"{m.group(0)}" is typed as text, so it will not move with '
                          f'the element it names',
                          f'Replace the number with \\ref to that element\'s label'))
    return out


def _c_repeated_cite_key(src, code, spans, prose, body, envs, labels, ctx, sub):
    """One key twice in one \\cite prints the same reference twice."""
    out = []
    for m in re.finditer(r'\\(?:no)?cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}', code):
        keys = [k.strip() for k in m.group(1).split(',') if k.strip()]
        dup = [k for k, n in collections.Counter(keys).items() if n > 1]
        if dup:
            out.append(_F('repeated-citation-key', m.start(), 'query', 'free', True,
                          f'{", ".join(dup)} appears twice inside one citation',
                          'Delete the repeat'))
    return out


def _bib_keys(code, ctx):
    """Keys the document could resolve: every \\bibitem, plus every named .bib file.

    Returns None when a named bib file cannot be found, because then absence of a key
    proves nothing.
    """
    keys, saw = set(), False
    for off, b in _cmd_args(code, 'bibitem'):
        keys.add(b.strip())
        saw = True
    names = []
    for m in re.finditer(r'\\(?:bibliography|addbibresource)\s*\{([^}]*)\}', code):
        names += [n.strip() for n in m.group(1).split(',') if n.strip()]
    for n in names:
        if '\\' in n:
            return None
        found = None
        for root in _roots(ctx):
            for cand in (root / n, root / (n + '.bib')):
                if cand.is_file():
                    found = cand
                    break
            if found:
                break
        if not found:
            return None
        try:
            txt = found.read_text(encoding='utf-8', errors='replace')
        except OSError:
            return None
        for m in re.finditer(r'@[A-Za-z]+\s*[{(]\s*([^,\s}]+)\s*,', txt):
            keys.add(m.group(1).strip())
        saw = True
    return keys if saw else None


def _c_undefined_cite_key(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A cite key that is in no bibliography the document names prints as [?]."""
    known = _bib_keys(code, ctx)
    if not known:
        return []
    out, seen = [], set()
    for m in re.finditer(r'\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}', code):
        for k in (x.strip() for x in m.group(1).split(',')):
            if not k or k == '*' or k in known or k in seen:
                continue
            seen.add(k)
            out.append(_F('undefined-citation-key', m.start(), 'query', 'lookup', True,
                          f'cite key {k} is in no bibliography this file names, so it '
                          f'prints as a question mark',
                          'Add the entry to the .bib file, or correct the key'))
    return out


def _c_missing_graphic(src, code, spans, prose, body, envs, labels, ctx, sub):
    """\\includegraphics naming a file that is not on disk: the build breaks."""
    extra = ['.']
    for m in re.finditer(r'\\graphicspath\s*\{(.+?)\}\s*(?:\n|%|\\)', code, re.S):
        extra += re.findall(r'\{([^{}]*)\}', m.group(1))
    exts = ['', '.pdf', '.png', '.jpg', '.jpeg', '.eps', '.PDF', '.PNG', '.JPG', '.svg']
    calls = list(_cmd_args(code, 'includegraphics'))
    missing = [(off, name) for off, name in calls
               if not _resolve(name, ctx, exts, extra)]
    # When most graphics are unresolvable the figure tree is simply not present — an
    # unfetched asset directory, a build-time generated path, a partial checkout. Reporting
    # each file then produces hundreds of findings about one fact. A corpus sweep over 2140
    # real files hit 285 in a single file this way.
    if calls and len(missing) > max(3, 0.4 * len(calls)):
        off = missing[0][0]
        return [_F('graphics-tree-absent', off, 'query', 'lookup', False,
                   f'{len(missing)} of {len(calls)} graphics do not resolve, so the figure '
                   f'directory looks absent rather than each file being missing',
                   'Fetch or generate the figure directory, then re-run to see real gaps')]
    out = []
    for off, name in missing:
        out.append(_F('missing-graphic-file', off, 'query', 'rework', True,
                      f'\\includegraphics names {name}, which is not next to the '
                      f'source', 'Restore or regenerate the figure file, or fix the path'))
    return out


def _c_missing_input(src, code, spans, prose, body, envs, labels, ctx, sub):
    """\\input or \\include naming a file that is not on disk."""
    out = []
    for cmd in ('input', 'include'):
        for off, name in _cmd_args(code, cmd):
            if re.match(r'^\s*$', name) or ' ' in name.strip() and '.' not in name:
                continue
            if not _resolve(name, ctx, ['', '.tex', '.sty', '.tikz']):
                out.append(_F('missing-input-file', off, 'query', 'rework', True,
                              f'\\{cmd}{{{name}}} names a file that is not next to the '
                              f'source', 'Restore the file, or fix the path'))
    return out


def _c_missing_bib(src, code, spans, prose, body, envs, labels, ctx, sub):
    """\\bibliography naming a .bib that is not on disk: every citation prints as [?]."""
    out = []
    for m in re.finditer(r'\\(?:bibliography|addbibresource)\s*\{([^}]*)\}', code):
        for n in (x.strip() for x in m.group(1).split(',')):
            if not n or '\\' in n:
                continue
            if not _resolve(n, ctx, ['', '.bib']):
                out.append(_F('missing-bib-file', m.start(), 'query', 'rework', True,
                              f'bibliography file {n} is not next to the source, so no '
                              f'citation can resolve', 'Restore the .bib, or fix the name'))
    return out


def _c_float_no_caption(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A numbered float with content and no caption: the reader gets no legend."""
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if name not in FLOAT_ENVS:
            continue
        blk = code[bodys:bodye]
        if re.search(r'\\caption(of)?\s*(\[|\{)|\\subcaption', blk):
            continue
        if not re.search(r'\\includegraphics|\\begin\s*\{(tabular|tikzpicture|'
                         r'lstlisting|verbatim)|\\input|\\pgfplots', blk):
            continue
        if name.startswith('wrap') and not re.search(r'\\label\s*\{', blk):
            continue                     # decorative inset: no number, nothing to caption
        out.append(_F('float-missing-caption', bs, 'query', 'lookup', True,
                      f'this {name} has content but no \\caption',
                      'Add a caption that says what the reader is looking at'))
    return out


def _c_float_no_label(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A captioned float with no \\label can never be referenced from the text."""
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if name not in FLOAT_ENVS:
            continue
        blk = code[bodys:bodye]
        if not re.search(r'\\caption(of)?\s*(\[|\{)', blk):
            continue
        if re.search(r'\\label\s*\{', blk):
            continue
        cap = ''
        for off, b in _cmd_args(blk, 'caption'):
            cap = _norm(b)[:50]
            break
        out.append(_F('float-missing-label', bs, 'query', 'free', False,
                      f'this {name} carries no \\label, so no sentence can point at '
                      f'it: "{cap}"',
                      'Add a \\label after the caption and reference it where the '
                      'text discusses it'))
    return out


def _c_duplicate_caption(src, code, spans, prose, body, envs, labels, ctx, sub):
    """Two identical captions: almost always two conditions of one experiment."""
    seen = {}
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if name not in FLOAT_ENVS:
            continue
        blk = code[bodys:bodye]
        for off, b in _cmd_args(blk, 'caption'):
            n = _norm(b)
            if len(n) < 25:
                continue
            key = (ENV_TYPE.get(name, name), n)
            if key in seen:
                out.append(_F('duplicate-caption', bodys + off, 'query', 'lookup', True,
                              f'this caption is word for word the caption at offset '
                              f'{seen[key]}: "{n[:60]}"',
                              'Name the condition that distinguishes the two'))
            else:
                seen[key] = bodys + off
    return out


# A present-tense claim only. "We will release the code" in a proposal is a plan, not a
# statement pointing at a location, and flagging it would be wrong.
_AVAIL = re.compile(
    r'\b(?:code|codebase|data|dataset|datasets|corpus|checkpoints?|weights|models?|'
    r'scripts?|annotations?)\b(?:\s+and\s+\w+)?\s+(?:is|are)\s+'
    r'(?:now\s+|all\s+|freely\s+|publicly\s+|openly\s+)*'
    r'(?:available|released|online|open[- ]sourced?)\b'
    r'|\bwe\s+(?:hereby\s+)?(?:release|have\s+released|publicly\s+release)\b'
    r'|\b(?:available|released)\s+(?:at|from|via|on|in)\s+'
    r'(?:https?|www|the\s+(?:repository|supplement|following))', re.I)


def _c_availability(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A promise to release something, with no location anywhere in the file."""
    if re.search(r'https?://|\\url\b|\bdoi\.org|\bgithub\b|huggingface|zenodo\.|'
                 r'\bosf\.io|figshare|\bdryad\b|\\href', code, re.I):
        return []
    for sp in prose:
        m = _AVAIL.search(sp.rendered)
        if not m:
            continue
        frag = re.sub(r'\s+', ' ', m.group(0))[:70]
        return [_F('availability-claim-no-location', _locate(sp, m.group(0)), 'query',
                   'lookup', True,
                   f'"{frag}" promises an artifact, and this file names no URL, DOI or '
                   f'repository', 'State where it lives, in a form a reader can open')]
    return []


def _c_mutable_location(src, code, spans, prose, body, envs, labels, ctx, sub):
    """An artifact link the authors can change after review without a trace."""
    out = []
    for m in re.finditer(r'https?://([A-Za-z0-9._~-]+)', code):
        host = m.group(1).lower()
        for bad in MUTABLE_HOSTS:
            if host.endswith(bad):
                out.append(_F('mutable-artifact-location', m.start(), 'query', 'rework',
                              False,
                              f'{host} can be edited or withdrawn after review, so the '
                              f'link is not evidence',
                              'Deposit the artifact somewhere versioned and immutable, '
                              'and cite that identifier'))
                break
    return out


def _c_no_limitations(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A paper with no limitations section. Only runs on a whole paper-shaped file."""
    if '\\documentclass' not in code or '\\begin{abstract}' not in code.replace(' ', ''):
        return []
    heads = [b for m in re.finditer(r'\\(?:sub)?section\*?\s*(?:\[[^\]]*\])?\s*(?=\{)', code)
             for b in [_arg(code, m.end())[0]] if b]
    if not any(re.search(r'related work|experiment|results|evaluation|ablation', h, re.I)
               for h in heads):
        return []                        # not a research paper: no such expectation
    if re.search(r'work package|\bWP\d|ercformatting|granttypeyear', code, re.I):
        return []
    if any(re.search(r'limitation|threats? to validity|broader impact', h, re.I)
           for h in heads):
        return []
    m = re.search(r'\\begin\{document\}', code)
    return [_F('missing-limitations-section', m.start() if m else 0, 'query', 'rework',
               False,
               'the paper has no limitations section, so nothing states the assumptions '
               'whose failure would change the conclusions',
               'Add one naming the assumptions, the scope of the evaluation and the '
               'sensitivity of the results')]


def _c_quote_balance(src, code, spans, prose, body, envs, labels, ctx, sub):
    """Unequal `` and '' : one quotation does not close where the author meant."""
    op = cl = 0
    first = None
    for sp in prose:
        op += sp.text.count('``')
        cl += len(re.findall(r"(?<![a-zA-Z])''|(?<=[a-zA-Z])''(?![a-zA-Z])", sp.text))
        if first is None and '``' in sp.text:
            first = sp.start + sp.text.find('``')
    straight = sum(sp.text.count('"') for sp in prose)
    if op and cl != op:
        extra = (f'; {straight} straight " in the prose, which closes a quotation with '
                 f'the wrong glyph' if straight else '')
        return [_F('unbalanced-quotation-marks', first or 0, 'query', 'free', True,
                   f"{op} opening `` against {cl} closing '' in the prose, so at least "
                   f"one quotation does not close where the quoted words end{extra}",
                   "Close each quotation with '' at the end of the quoted words")]
    return []


_WORD = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)+|[A-Za-z]{3,}")


def _c_hyphen_variant(src, code, spans, prose, body, envs, labels, ctx, sub):
    """One compound spelled both hyphenated and closed in the author's own prose."""
    toks = collections.Counter()
    where = {}
    for sp in prose:
        for m in _WORD.finditer(_unquoted(sp.rendered)):
            w = m.group(0).lower()
            toks[w] += 1
            where.setdefault(w, _locate(sp, m.group(0)))
    out = []
    for w, n in sorted(toks.items()):
        if '-' not in w:
            continue
        parts = w.split('-')
        if len(parts) != 2 or min(len(p) for p in parts) < 3:
            continue
        closed = w.replace('-', '')
        if len(closed) < 7 or closed not in toks:
            continue
        out.append(_F('hyphenation-variant', where[w], 'query', 'free', False,
                      f'"{w}" appears {n} times and "{closed}" {toks[closed]} times',
                      ''))
    return out


def _c_spelling_variety(src, code, spans, prose, body, envs, labels, ctx, sub):
    """Both spelling varieties of one word in one document."""
    toks = collections.Counter()
    where = {}
    for sp in prose:
        for m in re.finditer(r"[A-Za-z]{4,}", _unquoted(sp.rendered)):
            w = m.group(0).lower()
            toks[w] += 1
            where.setdefault(w, _locate(sp, m.group(0)))
    out = []
    done = set()
    for a, b in US_UK:
        for x, y in ((a, b), (a + 's', b + 's')):
            if toks.get(x) and toks.get(y) and (x, y) not in done:
                done.add((x, y))
                out.append(_F('spelling-variety-mixed', where[x], 'query', 'free', False,
                              f'"{x}" appears {toks[x]} times and "{y}" {toks[y]} times',
                              ''))
    for w in list(toks):
        m = re.match(r'^(.+?)(ize|ized|izes|izing|ization|izations)$', w)
        if not m or len(w) < 8:
            continue
        stem, tail = m.group(1), m.group(2)
        if any(stem.startswith(d) or stem == d for d in IZE_DENY):
            continue
        other = stem + tail.replace('iz', 'is')
        if toks.get(other) and (w, other) not in done:
            done.add((w, other))
            out.append(_F('spelling-variety-mixed', where[w], 'query', 'free', False,
                          f'"{w}" appears {toks[w]} times and "{other}" '
                          f'{toks[other]} times', ''))
    return out


_PCT = re.compile(
    r'(\d[\d,]*)\s*(?:/|\bof\b|\bout of\b)\s*(\d[\d,]*)\s*'
    r'[(\[]\s*(\d+(?:\.\d+)?)\s*\\?%')
_PCT2 = re.compile(
    r'(\d[\d,]*)\s*[(\[]\s*(\d+(?:\.\d+)?)\s*\\?%\s*[)\]]\s*(?:of|out of)\s*(\d[\d,]*)')


def _c_percentage_math(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A stated percentage that its own numerator and denominator do not give."""
    out = []
    for sp in prose:
        for rx, order in ((_PCT, (0, 1, 2)), (_PCT2, (0, 2, 1))):
            for m in rx.finditer(sp.rendered):
                g = m.groups()
                try:
                    n = float(g[order[0]].replace(',', ''))
                    d = float(g[order[1]].replace(',', ''))
                    p = g[order[2]]
                except (ValueError, IndexError):
                    continue
                if d <= 0 or n > d:
                    continue
                dec = len(p.split('.')[1]) if '.' in p else 0
                tol = 0.5 * (10 ** -dec) + 0.06
                got = 100.0 * n / d
                if abs(got - float(p)) > tol:
                    out.append(_F('percentage-arithmetic-mismatch',
                                  _locate(sp, m.group(0)), 'query', 'lookup', True,
                                  f'"{re.sub(chr(92)+"s+", " ", m.group(0))[:50]}" '
                                  f'-- {n:g}/{d:g} is {got:.{max(dec,1)}f}%, not {p}%',
                                  'Query which of the three numbers is the right one; '
                                  'change none of them until the author answers'))
    return out


# Case-sensitive on purpose: lowercase "fill in a value" is ordinary prose, and only
# the shouted forms are scaffolding.
_PLACE = re.compile(r'\bTBDs?\b|\bTODO\b|\bFIXME\b|\bTBA\b|XXX+|\?\?\?|'
                    r'\[MISSING\]|\bFILL IN\b|\bREF\?|[Ll]orem ipsum')


def _c_placeholder_prose(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A placeholder in reader-visible prose, not in a comment. Submission only."""
    if not sub:
        return []
    out = []
    for sp in prose:
        for m in _PLACE.finditer(sp.rendered):
            ctxt = re.sub(r'\s+', ' ', sp.rendered[max(0, m.start() - 30):m.end() + 30])
            out.append(_F('placeholder-in-prose', _locate(sp, m.group(0)), 'batch',
                          'lookup', True,
                          f'placeholder "{m.group(0)}" is in the printed text: '
                          f'...{ctxt.strip()}...',
                          'Supply the real value, or delete the sentence'))
    return out


def _c_template_dummy(src, code, spans, prose, body, envs, labels, ctx, sub):
    """Sample text from the venue template still in the submission."""
    if not sub:
        return []
    hits = [(code.find(s), s) for s in TEMPLATE_DUMMY if code.find(s) >= 0]
    if not hits:
        return []
    hits.sort()
    names = ', '.join(f'"{s}"' for _, s in hits[:4])
    return [_F('template-dummy-text', hits[0][0], 'batch', 'free', True,
               f'sample text from the venue template is still in the source: {names}'
               + (f' and {len(hits) - 4} more' if len(hits) > 4 else ''),
               'Replace the template sample block with the real values, or delete it')]


_PRIOR = (r"our previous submission", r"previous submission", r"this resubmission",
          r"our earlier proposal", r"our previous (application|proposal)",
          r"the previous reviewers", r"previous reviewers'? (comments|report)",
          r"in the earlier version of this (paper|proposal)",
          r"as noted in our previous")


def _c_prior_submission(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A back-reference to an earlier submission, in a document read as new."""
    out = []
    seen = set()
    for sp in prose:
        for pat in _PRIOR:
            for m in re.finditer(pat, sp.rendered, re.I):
                key = m.group(0).lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append(_F('previous-submission-back-reference',
                              _locate(sp, m.group(0)), 'query', 'rework', True,
                              f'"{m.group(0)}" points at an earlier submission this '
                              f'reader has not seen',
                              'State the content the sentence pointed at, and keep any '
                              'resubmission narrative to the section the funder provides'))
    return out


# ============================================================ second pass
# Rules skipped in the first pass for effort rather than impossibility. Everything here
# compares the document against itself or against the .bib it names, so no rule needs the
# rendered PDF, the published record or the funder's call.

# Two-argument review macros the extractor does not mask. \lc, \wzm and \todo are masked
# upstream as their own span kinds, but ercreview.sty's \ercscore{section}{note} is a
# two-argument form, and the extractor's single-argument unwrapper turns its note body
# into prose. Without this, every prose rule below reads a co-author's review note as if
# the author had written it -- four notes on one real proposal, one of them 90 words.
REVIEW_2ARG = ('ercblock', 'ercscore', 'ercpolish', 'ercnote', 'reviewnote', 'authornote')

# Single-argument wrappers holding a retired version of a passage beside its replacement.
# \ReviewOld comes from the erc-review kit's review_diff.py, which renders it struck
# through in grey, so it is a labelled old version and not a rewrite left live by
# accident. Reading it as prose reported nine repeated sentences on one generated diff
# file, every one of them the passage the macro exists to strike out.
REVIEW_1ARG = ('ReviewOld', 'reviewold', 'oldversion', 'strickenout')


def _blank_offprose(src):
    """src with review notes, retired versions and heading titles blanked, length
    preserved, so every offset taken from the result still indexes into the source.

    Heading titles go too. A rendered span glues a heading onto the sentence that follows
    it, with no stop between them, so the same sentence under two different headings
    compares unequal and the repetition rules miss it. Headings have their own rules.
    """
    out = list(src)

    def blank(a, b):
        for i in range(a, b):
            if out[i] != '\n':
                out[i] = ' '

    for name in REVIEW_2ARG:
        for m in re.finditer(r'\\' + name + r'\s*\{[^{}]{0,60}\}\s*(?=\{)', src):
            _, end = _arg(src, m.end())
            if end > m.end():
                blank(m.start(), end)
    for name in REVIEW_1ARG:
        for m in re.finditer(r'\\' + name + r'\s*(?=\{)', src):
            _, end = _arg(src, m.end())
            if end > m.end():
                blank(m.start(), end)
    for m in re.finditer(r'\\(?:(?:sub)*section|chapter|part|paragraph|title|caption)\*?'
                         r'\s*(?:\[[^\]]*\])?\s*(?=\{)', src):
        _, end = _arg(src, m.end())
        if end > m.end():
            blank(m.start(), end)
    return ''.join(out)


def _clean_prose(src, spans, prose):
    """Prose spans with review notes and heading titles removed."""
    src2 = _blank_offprose(src)
    if src2 == src:
        return prose
    try:
        return [sp for sp in ex.extract(src2)
                if sp.kind == 'text' and sp.rendered.strip()]
    except Exception:
        return prose


def _key_text(t):
    """A sentence or paragraph reduced to what two copies of it would share."""
    t = re.sub(r'[\u2020\u2021]', ' ', t)
    t = re.sub(r'[^a-z0-9]+', ' ', t.lower())
    return t.strip()


def _wordy(k, floor):
    """True when a normalised passage holds `floor` tokens of three characters or more.

    A macro file renders as runs of single letters -- \newcommand{\va}{\vec{a}} and its
    twenty-five siblings become "a b c d e ..." -- and those runs repeat identically in
    every block. That was nine bogus duplicated paragraphs on one real definition file.
    """
    return sum(1 for w in k.split() if len(w) >= 3) >= floor


def _sentences(prose):
    """(sentence, span) for every complete sentence in reader-visible prose."""
    for sp in prose:
        for s in re.split(r'(?<=[.!?])\s+', sp.rendered):
            s = s.strip()
            if s:
                yield s, sp


def _cite_calls(code):
    """(offset, [keys]) for every citation command."""
    out = []
    for m in re.finditer(r'\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}', code):
        out.append((m.start(), [k.strip() for k in m.group(1).split(',') if k.strip()]))
    return out


# ------------------------------------------------------- a rewrite left both versions
def _c_repeated_sentence(src, code, spans, prose, body, envs, labels, ctx, sub):
    """One sentence printed twice: what an in-place rewrite leaves when the original is
    not deleted. Eight words and a sentence-final stop are required, because a shorter
    fragment repeats honestly (a caption stub, a table lead-in) and because a span cut by
    a masked equation yields half-sentences that would collide. A sentence inside a
    paragraph that repeats wholesale is left to the paragraph rule, so one duplicated
    paragraph is one finding and not one per sentence."""
    seen, seen_para, out = {}, set(), []
    for sp in ctx.get('_clean') or prose:
        for para in re.split(r'\n\s*\n', sp.rendered):
            pk = _key_text(para)
            if pk in seen_para:
                continue        # the whole paragraph repeats; its own rule reports that
            seen_para.add(pk)
            if not _wordy(pk, 5):
                continue
            for s in re.split(r'(?<=[.!?])\s+', para):
                s = s.strip()
                if not re.search(r'[.!?]$', s):
                    continue
                k = _key_text(s)
                if len(k) < 45 or len(k.split()) < 8 or not _wordy(k, 5):
                    continue
                if k in seen:
                    out.append(_F('repeated-sentence', _locate(sp, s), 'query', 'free',
                                  False,
                                  f'this sentence already appears at offset {seen[k]}, '
                                  f'word for word: "{s[:70]}"',
                                  'Query which of the two the author meant to keep'))
                else:
                    seen[k] = _locate(sp, s)
    return out


def _c_duplicate_paragraph(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A whole paragraph printed twice, which is a rewrite pasted beside its original."""
    seen, out = {}, []
    for sp in ctx.get('_clean') or prose:
        for para in re.split(r'\n\s*\n', sp.rendered):
            k = _key_text(para)
            if len(k.split()) < 25 or not _wordy(k, 12):
                continue
            if k in seen:
                out.append(_F('duplicated-paragraph', _locate(sp, para.strip()), 'query',
                              'free', True,
                              f'this paragraph repeats the one at offset {seen[k]} word '
                              f'for word: "{k[:70]}"',
                              'Delete the copy the author did not mean to keep'))
            else:
                seen[k] = _locate(sp, para.strip())
    return out


_DEF_CMD = re.compile(r'\\(newcommand|def|DeclareMathOperator|DeclareRobustCommand)\*?\s*'
                      r'\{?\s*\\([A-Za-z@]+)\s*\}?\s*(?=[\[{#])')


def _c_duplicate_macro(src, code, spans, prose, body, envs, labels, ctx, sub):
    """One macro defined twice. \\newcommand twice for one name does not compile, and
    \\def twice compiles with the second body silently winning, which is how a renamed
    or retuned macro survives beside the version it replaced. \\renewcommand and
    \\providecommand are deliberate overrides and are not counted, and a definition
    guarded by \\ifdefined is a fallback rather than a duplicate."""
    where = collections.OrderedDict()
    for m in _DEF_CMD.finditer(code):
        name = m.group(2)
        lead = code[max(0, m.start() - 200):m.start()]
        if re.search(r'\\(ifdefined|ifundefined|@ifundefined|ifdef|ifx|else|providecommand)'
                     r'|\\newif', lead):
            continue
        where.setdefault(name, []).append(m.start())
    out = []
    for name, offs in where.items():
        if len(offs) > 1:
            out.append(_F('duplicate-macro-definition', offs[1], 'query', 'free', True,
                          f'\\{name} is defined {len(offs)} times, so the last definition '
                          f'silently wins wherever it is used',
                          'Keep the definition the document is written against and delete '
                          'the other'))
    return out


def _drop_colspec(blk):
    """A tabular body with its column specification blanked, length preserved.

    _envs starts a body straight after \\begin{tabular}, so the {lrr} argument -- and the
    width argument tabularx takes before it -- lands in the first row and makes that row
    compare unequal to an identical row further down.
    """
    out, i = blk, 0
    for _ in range(2):
        m = re.match(r'\s*(?:\[[^\]]*\])?\s*(?=\{)', out[i:])
        if not m:
            break
        _, end = _arg(out, i + m.end())
        if end <= i + m.end():
            break
        out = out[:i] + ' ' * (end - i) + out[end:]
        i = end
    return out


def _c_repeated_table_row(src, code, spans, prose, body, envs, labels, ctx, sub):
    """The same data row twice in one table. A row needs a word and a digit to count, so
    an all-zero row and a rule line do not collide, and a longtable with a repeating
    header (\\endhead) is skipped because its header genuinely repeats."""
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if not re.match(r'(tabular|tabularx|longtable)\b', name):
            continue
        blk = _drop_colspec(code[bodys:bodye])
        if re.search(r'\\endhead|\\endfirsthead', blk):
            continue
        seen = {}
        pos = bodys
        for row in re.split(r'\\\\', blk):
            here, pos = pos, pos + len(row) + 2
            k = re.sub(r'\\[a-zA-Z@]+\*?|[{}\s]', '', row)
            if len(k) < 20 or '&' not in k or not re.search(r'\d', k):
                continue
            if not re.search(r'[A-Za-z]{3}', k):
                continue
            if k in seen:
                out.append(_F('repeated-table-row', here, 'query', 'lookup', True,
                              f'this {name} row is identical to the one at offset '
                              f'{seen[k]}: "{re.sub(chr(92) + "s+", " ", row.strip())[:60]}"',
                              'Query which row the author meant; one of the two is a '
                              'leftover from an edit'))
            else:
                seen[k] = here
    return out


def _c_duplicate_heading(src, code, spans, prose, body, envs, labels, ctx, sub):
    """Two headings at one level with the same title: two live versions of one section.

    \\paragraph and \\subparagraph are excluded. They are run-in labels, and a document
    with parallel subsections legitimately repeats them -- two \\paragraph{SmolLM2-360M.}
    labels, one under Architecture and one under Configurations, were the only two hits on
    a real paper.
    """
    seen, out = {}, []
    for m in re.finditer(r'\\((?:sub)*section|chapter)(\*?)\s*(?:\[[^\]]*\])?\s*(?=\{)',
                         code):
        b, _ = _arg(code, m.end())
        if b is None:
            continue
        k = (m.group(1), _norm(b))
        if len(k[1]) < 8:
            continue
        if k in seen:
            out.append(_F('duplicate-section-heading', m.start(), 'query', 'free', True,
                          f'a second \\{m.group(1)} carries the title already used at '
                          f'offset {seen[k]}: "{k[1][:50]}"',
                          'Query which section survives; a reader cannot tell the two '
                          'apart in the contents list'))
        else:
            seen[k] = m.start()
    return out


# ------------------------------------------------- the document against its own numbers
def _c_number_format_variant(src, code, spans, prose, body, envs, labels, ctx, sub):
    """One value written two ways, 2,048 in one place and 2048 in another. Reported, not
    repaired: which form is house style is the author's call, and both forms name the same
    exact count, so nothing here can reach the value itself.

    Only values that appear in both forms are compared. A document-wide separator audit
    was measured and dropped: ORCIDs, DOIs and grant identifiers render as bare four-digit
    runs and produced five bogus values on one proposal."""
    forms, where = collections.defaultdict(set), {}
    for sp in ctx.get('_clean') or prose:
        for m in re.finditer(r'(?<![\w.,$-])(\d{1,3}(?:,\d{3})+|\d{4,7})(?![\d.,\-])',
                             sp.rendered):
            t = m.group(1)
            forms[t.replace(',', '')].add(t)
            where.setdefault(t, _locate(sp, t))
    out = []
    for v, fs in forms.items():
        if len(fs) < 2:
            continue
        a = sorted(fs, key=lambda x: where.get(x, 0))
        out.append(_F('number-format-variant', where[a[0]], 'query', 'free', False,
                      f'the same value is written {" and ".join(a)} in this document',
                      'Pick one form for numbers of this size and use it throughout'))
    return out


_MAG = {'k': 1e3, 'm': 1e6, 'b': 1e9, 'bn': 1e9, 'thousand': 1e3, 'million': 1e6,
        'billion': 1e9, 'trillion': 1e12}
_APPROX_NEAR = ('about', 'approximately', 'approx', 'roughly', 'around', 'some', 'circa',
                '~')
_APPROX_BELOW = ('almost', 'nearly', 'close to', 'just under')
_APPROX_LOWER = ('over', 'more than', 'at least', 'above', 'upwards of')
_APPROX_UPPER = ('under', 'fewer than', 'less than', 'below', 'at most', 'up to')
_QUANT = re.compile(
    r'(?<![\w.$-])(?:(about|approximately|approx|almost|nearly|roughly|around|some|circa|'
    r'close to|just under|over|more than|at least|above|upwards of|under|fewer than|'
    r'less than|below|at most|up to|~)\s*)?'
    r'(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*'
    r'(K|M|B|bn|thousand|million|billion|trillion)?\s+([a-z][a-z-]{3,20})\b', re.I)


def _c_approximate_figure(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A rounded figure that the exact figure elsewhere contradicts, judged by what the
    author's own approximator claims: "almost N" wants a value just below N, "over N" a
    value above it, "about N" a value that rounds to N.

    Two guards keep this off legitimately different quantities that share a noun. The
    noun must carry exactly two distinct values in the whole document, so a paper
    reporting one noun per condition is skipped, and the two values must be within a
    factor of 1.7, so 20 exposures against 1000 exposures is never compared."""
    groups = collections.defaultdict(list)
    for sp in ctx.get('_clean') or prose:
        for m in _QUANT.finditer(sp.rendered):
            appr, num, mag, noun = m.groups()
            try:
                v = float(num.replace(',', '')) * (_MAG[mag.lower()] if mag else 1)
            except (ValueError, KeyError):
                continue
            groups[noun.lower().rstrip('s')].append(
                (appr and appr.lower(), v, num, m.group(0), sp))
    out = []
    for noun, items in groups.items():
        if len({v for _, v, _, _, _ in items}) != 2:
            continue
        for appr, v, num, txt, sp in items:
            if not appr:
                continue
            digits = re.sub(r'[^0-9]', '', num.split('.')[0])
            unit = 10 ** (len(digits) - len(digits.rstrip('0')))
            if '.' in num:
                unit = 10 ** -len(num.split('.')[1])
            unit *= v / float(num.replace(',', '')) if float(num.replace(',', '')) else 1
            tol = min(unit / 2.0, 0.10 * v)
            for appr2, v2, _, txt2, _sp2 in items:
                if appr2 is not None or v2 == v or v <= 0:
                    continue
                if not 0.6 < v2 / v < 1.7:
                    continue
                bad = ((appr in _APPROX_NEAR and abs(v2 - v) > tol)
                       or (appr in _APPROX_BELOW and not 0.9 * v <= v2 < v)
                       or (appr in _APPROX_LOWER and v2 < v)
                       or (appr in _APPROX_UPPER and v2 > v))
                if bad and max(v, v2) >= 100:
                    out.append(_F('approximate-figure-inconsistent', _locate(sp, txt),
                                  'query', 'lookup', True,
                                  f'"{txt}" and "{txt2}" cannot both describe the same '
                                  f'{noun}',
                                  'Query which value is right; fix one figure and one '
                                  'rounding for this quantity and use them everywhere'))
                    break
    return out


_TOTAL_ROW = re.compile(r'^(total|totals|sum|overall|all told|combined)\b', re.I)


def _cell_text(c):
    c = re.sub(r'\\(text(bf|it|rm|sf|tt)|emph|mathrm|num|si)\s*\{([^{}]*)\}', r'\3', c)
    c = re.sub(r'\\[a-zA-Z@]+\*?', ' ', c)
    return c.replace('{', '').replace('}', '').replace('$', '').strip()


def _cell_num(c):
    m = re.fullmatch(r'-?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*%?', c.strip())
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', '')) * (-1 if c.strip().startswith('-') else 1)
    except ValueError:
        return None


def _c_table_total(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A row that says Total against the column it sits under. Only fires when the whole
    column is plain numbers -- three or more of them, no approximation marker, no
    \\multicolumn or \\multirow anywhere in the table -- because a total taken over cells
    the parser cannot align is a guess, and 0.5% slack absorbs displayed rounding."""
    out = []
    for name, bs, bodys, bodye, ee in envs:
        if not re.match(r'(tabular|tabularx|longtable)\b', name):
            continue
        blk = _drop_colspec(code[bodys:bodye])
        if re.search(r'\\multicolumn|\\multirow', blk):
            continue
        rows, pos, spots = [], bodys, []
        for row in re.split(r'\\\\', blk):
            rows.append(row)
            spots.append(pos)
            pos += len(row) + 2
        for ri, row in enumerate(rows):
            cells = [_cell_text(c) for c in re.split(r'(?<!\\)&', row)]
            if len(cells) < 2 or not _TOTAL_ROW.match(cells[0]):
                continue
            start = 0
            for rj in range(ri - 1, -1, -1):
                if re.match(r'\s*\\(midrule|hline|toprule|cmidrule)', rows[rj]):
                    start = rj
                    break
            parts = []
            for rj in range(start, ri):
                pc = [_cell_text(c) for c in re.split(r'(?<!\\)&', rows[rj])]
                if len(pc) == len(cells) and pc[0]:
                    parts.append((rows[rj], pc))
            if len(parts) < 3:
                continue
            if any(re.search(r'~|\\approx|\\pm|\u2248|\u00b1|\\ldots|--|<|>', r)
                   for r, _ in parts) or re.search(r'~|\\approx|\\pm|\u2248|\u00b1', row):
                continue
            for j in range(1, len(cells)):
                tot = _cell_num(cells[j])
                vals = [_cell_num(pc[j]) for _, pc in parts]
                if tot is None or any(v is None for v in vals):
                    continue
                s = sum(vals)
                if abs(s - tot) > max(0.51, 0.005 * abs(tot)):
                    out.append(_F('table-total-mismatch', spots[ri], 'query', 'lookup',
                                  True,
                                  f'the total row says {cells[j]} in column {j + 1} and '
                                  f'the {len(vals)} rows above it add to {s:g}',
                                  'Query which number is wrong; recompute the column and '
                                  'change nothing until the author answers'))
                    break
    return out


def _c_manual_enumeration_gap(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A hand-typed (1) (2) (4) run in the prose, which is what deleting the third item
    of a rewritten list leaves. Only a run that starts at (1) and holds three or more
    markers counts. A repeat cannot be reported here, because a repeated number ends the
    run rather than extending it."""
    out = []
    for sp in ctx.get('_clean') or prose:
        seq = [(m.start(), int(m.group(1)), m.group(0))
               for m in re.finditer(r'\((\d{1,2})\)', sp.rendered)]
        runs, cur = [], []
        for item in seq:
            if cur and item[1] <= cur[-1][1]:
                runs.append(cur)
                cur = []
            cur.append(item)
        if cur:
            runs.append(cur)
        for run in runs:
            ns = [n for _, n, _ in run]
            if len(ns) >= 3 and ns[0] == 1 and ns != list(range(1, len(ns) + 1)):
                miss = [i for i in range(1, ns[-1] + 1) if i not in ns]
                out.append(_F('manual-enumeration-gap', _locate(sp, run[0][2]), 'query',
                              'free', True,
                              f'the hand-numbered run in this passage goes '
                              f'{", ".join("(%d)" % n for n in ns)}, skipping '
                              f'{", ".join("(%d)" % n for n in miss)}',
                              'Renumber the run, or restore the item that was deleted'))
    return out


# ----------------------------------------------------------- quotation and apparatus
_QUOTED = re.compile(r"``(.{12,600}?)''", re.S)
_QUOTE_LEAD = re.compile(
    r'(e\.g\.|i\.e\.|for example|for instance|such as|like|namely|reads?|says?|writes?|'
    r'labell?ed|called|termed?|named|prompt|template|output|example|answer|question|'
    r'response|string|token|word|phrase|option|entry|value|tag|field|column|:|,)\W{0,3}$',
    re.I)


def _c_quotation_no_source(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A quoted passage with no citation anywhere near it. Six words of quotation are
    required, and a quotation introduced as an example, a prompt or a label is skipped,
    because those quote the document's own material and need no source.

    A document that produces more than twelve of these is using `` '' for something other
    than quotation -- scare quotes, coined terms -- so the rule reports nothing rather
    than a page of noise."""
    out = []
    for sp in ctx.get('_clean') or prose:
        for m in _QUOTED.finditer(sp.rendered):
            q = m.group(1)
            if len(q.split()) < 6:
                continue
            if _QUOTE_LEAD.search(sp.rendered[max(0, m.start() - 70):m.start()]):
                continue
            if '\u2020' in sp.rendered[max(0, m.start() - 200):m.end() + 200]:
                continue
            out.append(_F('quotation-without-source', _locate(sp, q), 'query', 'lookup',
                          True,
                          f'this quotation carries no citation: "{q.strip()[:60]}"',
                          'Attribute the quotation, with the page or section it came from'))
    return out if len(out) <= 12 else []


_DOUBLED = re.compile(r'\b([a-z]{2,})\s+\1\b', re.I)
_DOUBLE_OK = {'that', 'had', 'very', 'no', 'blah', 'ha', 'la', 'di'}
_TYPO = frozenset("""teh recieve recieved recieving seperate seperated seperately occured
occuring definately alot thier adress arguement comparision consistant enviroment
existance futher independant occurance paralell perfomance prefered refered relevent
resonable sucess supress transfered wich accomodate acheive apparant becuase begining
beleive collegue commited concious dependant embarass goverment harrass immediatly
neccessary noticable occassion persistant posession publically recomend rythm sieze
succesful tendancy tommorow untill wierd langauge lenght managment measurment
occurence responce speach strenght""".split())


def _c_error_in_quotation(src, code, spans, prose, body, envs, labels, ctx, sub):
    """An error inside quoted material. Reported and never repaired: correcting inside a
    quotation misquotes the source, and the only correct outputs are a [sic] or a
    correction from the source itself, which nothing in this file can decide between."""
    out = []
    for sp in ctx.get('_clean') or prose:
        for m in _QUOTED.finditer(sp.rendered):
            q = m.group(1)
            d = _DOUBLED.search(q)
            if d and d.group(1).lower() not in _DOUBLE_OK:
                out.append(_F('error-inside-quotation', _locate(sp, q), 'query', 'lookup',
                              True,
                              f'the quotation repeats a word, "{d.group(0)}", in: '
                              f'"{q.strip()[:60]}"',
                              'Query the author against the source. Do not correct inside '
                              'the quotation; if the source reads this way, mark it [sic]'))
                continue
            for w in re.finditer(r"[A-Za-z]{4,}", q):
                if w.group(0).lower() in _TYPO:
                    out.append(_F('error-inside-quotation', _locate(sp, q), 'query',
                                  'lookup', True,
                                  f'the quotation contains "{w.group(0)}" in: '
                                  f'"{q.strip()[:60]}"',
                                  'Query the author against the source. Do not correct '
                                  'inside the quotation; if the source reads this way, '
                                  'mark it [sic]'))
                    break
    return out


_ATTRIB = re.compile(
    r'\b(it is (?:well[- ]known|widely (?:known|accepted|agreed|reported)|established)'
    r'|it has (?:been )?(?:repeatedly )?been (?:shown|demonstrated|established|found|'
    r'observed|reported)'
    r'|(?:prior|previous|earlier|recent|past) work has (?:shown|demonstrated|found|'
    r'established|argued|reported)'
    r'|studies have (?:shown|found|demonstrated|reported)|research has shown'
    r'|it is (?:generally|widely) (?:accepted|agreed|believed)'
    r'|the literature (?:shows|reports|suggests|establishes))\b', re.I)


def _c_attributed_claim_no_cite(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A sentence that attributes a result to the literature and cites nobody. Only the
    explicit attribution cues count, because deciding which other sentences carry a
    citable claim is a judgement no pattern makes. The abstract is excluded, where a
    venue's own style bars citations, and a file with fewer than three citations is
    excluded, because it is not the file that carries the document's references."""
    if len(ctx.get('_cites') or []) < 3:
        return []
    skip = []
    for m in re.finditer(r'\\begin\s*\{abstract\}.*?\\end\s*\{abstract\}', code, re.S):
        skip.append((m.start(), m.end()))
    out = []
    for s, sp in _sentences(ctx.get('_clean') or prose):
        if not _ATTRIB.search(s):
            continue
        off = _locate(sp, s)
        if any(a <= off < b for a, b in skip):
            continue
        tail = sp.rendered[sp.rendered.find(s[:24]):][:len(s) + 200] if s[:24] else s
        if '\u2020' in tail:
            continue
        out.append(_F('attributed-claim-without-citation', off, 'query', 'lookup', True,
                      f'this sentence attributes a result to the literature and cites '
                      f'nobody: "{s[:80]}"',
                      'Cite the work the claim rests on, or state it as this project\'s '
                      'own finding'))
    return out


_SECTION_STOP = frozenset("""this that these those the each next following previous
present current same above below whole entire first last main our every another later
earlier preceding remaining final other such one two three both either neither its their
his her a an my new old""".split())


def _c_named_section_missing(src, code, spans, prose, body, envs, labels, ctx, sub):
    """"the Methods section" where no heading is called Methods. A pointer by title
    breaks the same way a \\ref does, and nothing in the build reports it. Demonstratives
    ("this section") and lowercase generics are excluded."""
    heads = []
    for m in re.finditer(r'\\(?:(?:sub)*section|chapter|paragraph)\*?\s*(?:\[[^\]]*\])?\s*'
                         r'(?=\{)', code):
        b, _ = _arg(code, m.end())
        if b:
            heads.append(_norm(b))
    if len(heads) < 2:
        return []
    out = []
    for sp in ctx.get('_clean') or prose:
        for m in re.finditer(r'\b([A-Z][a-z]{3,15}(?:\s+(?:and\s+)?[A-Z][a-z]{3,15}){0,2})'
                             r'\s+(section|subsection|appendix)\b', sp.rendered):
            name = m.group(1)
            if name.split()[0].lower() in _SECTION_STOP:
                continue
            key = _norm(name)
            if any(key in h for h in heads):
                continue
            out.append(_F('named-section-not-found', _locate(sp, m.group(0)), 'query',
                          'free', True,
                          f'the text points at "{m.group(0)}" and no heading in this '
                          f'document carries that title',
                          'Name the section as its heading reads, or point at it with '
                          '\\ref'))
    return out


# ------------------------------------------------------------- the bibliography apparatus
def _defs(code):
    """Single-argument \\def and \\newcommand bodies, for a \\bibliography{\\macro}."""
    d = {}
    for m in re.finditer(r'\\(?:def|newcommand|renewcommand)\*?\s*\{?\s*\\([A-Za-z@]+)\s*'
                         r'\}?\s*(?=\{)', code):
        b, _ = _arg(code, m.end())
        if b is not None and '\\' not in b and len(b) < 80:
            d.setdefault(m.group(1), b.strip())
    return d


def _bib_files(code, ctx):
    """Every .bib on disk that this file names, expanding a one-macro file name."""
    d, files = _defs(code), []
    for m in re.finditer(r'\\(?:bibliography|addbibresource)\s*\{([^}]*)\}', code):
        for n in m.group(1).split(','):
            n = n.strip()
            mm = re.fullmatch(r'\\([A-Za-z@]+)', n)
            if mm:
                n = d.get(mm.group(1), '')
            if not n or '\\' in n:
                continue
            for root in _roots(ctx):
                hit = None
                for cand in (root / n, root / (n + '.bib')):
                    try:
                        if cand.is_file():
                            hit = cand
                            break
                    except OSError:
                        continue
                if hit:
                    files.append(hit)
                    break
    return files


def _bib_index(code, ctx):
    """cite key -> (entry type, entry body) for every .bib this file names."""
    idx = {}
    for f in _bib_files(code, ctx):
        try:
            txt = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for m in re.finditer(r'@([A-Za-z]+)\s*\{\s*([^,\s}]+)\s*,', txt):
            i = txt.find('{', m.start())
            body, _ = _arg(txt, i)
            if body is not None:
                idx.setdefault(m.group(2).strip(), (m.group(1).lower(), body))
    return idx


def _field(body, name):
    """A bib field's value, or None when the field is absent."""
    m = re.search(r'(?<![A-Za-z])' + name + r'\s*=\s*', body, re.I)
    if not m:
        return None
    j = m.end()
    if j < len(body) and body[j] == '{':
        v, _ = _arg(body, j)
        return v if v is not None else ''
    if j < len(body) and body[j] == '"':
        k = body.find('"', j + 1)
        return body[j + 1:k] if k > 0 else ''
    return re.match(r'[^,}\n]*', body[j:]).group(0).strip()


_PREPRINT_HOSTS = re.compile(r'arxiv|biorxiv|medrxiv|ssrn|openreview|preprint|hal\.|'
                             r'techrxiv|osf\.io|working paper', re.I)


def _is_preprint(t, bd):
    if t in ('unpublished', 'misc', 'online', 'electronic', 'techreport', 'software',
             'dataset', 'standard', 'manual'):
        return True
    for f in ('journal', 'booktitle', 'note', 'howpublished', 'series'):
        v = _field(bd, f)
        if v and _PREPRINT_HOSTS.search(v):
            return True
    return bool(_field(bd, 'eprint') or _field(bd, 'archiveprefix'))


def _has_identifier(bd):
    if any(_field(bd, f) for f in ('doi', 'eprint', 'archiveprefix', 'isbn', 'issn')):
        return True
    return bool(re.search(r'https?://|doi\.org|arXiv:|\bRFC\s*\d|\bISO\s*\d|CELEX', bd,
                          re.I))


def _cited(ctx):
    ks = set()
    for _off, keys in ctx.get('_cites') or []:
        ks.update(keys)
    return ks


def _first_cite(ctx, key):
    for off, keys in ctx.get('_cites') or []:
        if key in keys:
            return off
    return 0


def _cap(out, summary):
    """Sixteen findings from one rule is a batch to work through, not sixteen findings."""
    if len(out) <= 15:
        return out
    f = dict(out[0])
    f['tier'] = 'batch'
    f['offset'] = 0
    f['text'] = summary(len(out))
    return [f]


_ABBREV_AUTHORS = re.compile(r'\band others\b|\bet\.? al\b|\.\.\.|\u2026', re.I)


def _c_bib_abbreviated_authors(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A cited entry whose author list is truncated. BibTeX's "and others" prints as
    et al., so the reference list credits some of the authors and hides the rest, and a
    reader cannot tell whether the applicant is among the ones hidden."""
    idx = ctx.get('_bib') or {}
    # A funder that asks for every author in published order makes this a defect that
    # holds up the application. In a paper's own bibliography an et al. is house style.
    # CUT after a real trial: 1 true against 3 false. "and others" is the BibTeX idiom for
    # et al., so a truncated author list is not a defect, and the one genuine case is
    # already reported by bib-note-scaffolding-printed.
    return []


_PUBDATA = {'article': ('journal', 'volume', 'pages', 'year'),
            'book': ('publisher', 'year'),
            'inbook': ('booktitle', 'publisher', 'year'),
            'incollection': ('booktitle', 'publisher', 'year')}


def _c_bib_missing_pubdata(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A cited journal article, book or book chapter with no journal, volume, page range,
    publisher or year. Preprints are excluded and handled by their own rule, because an
    absent volume is not a defect for something that was never in an issue."""
    idx = ctx.get('_bib') or {}
    out = []
    for k in sorted(_cited(ctx)):
        if k not in idx:
            continue
        t, bd = idx[k]
        if t not in _PUBDATA or _is_preprint(t, bd):
            continue
        miss = [f for f in _PUBDATA[t] if not _field(bd, f)]
        if t == 'article' and not _field(bd, 'pages') and _field(bd, 'articleno'):
            miss = [f for f in miss if f != 'pages']
        if miss:
            out.append(_F('bib-entry-missing-publication-data', _first_cite(ctx, k),
                          'query', 'lookup', False,
                          f'the {t} entry {k} names no '
                          f'{", ".join(miss)}, so the reference does not locate the work',
                          'Complete the entry from the published item'))
    return _cap(out,
                lambda n: f'{n} cited article, book or chapter entries are missing a '
                          f'journal, volume, page range, publisher or year')


def _c_bib_preprint_no_id(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A cited preprint, dataset, software release or report with no persistent
    identifier: no DOI, no arXiv eprint, no ISBN or ISSN, not even a URL. Nothing in the
    reference list tells the reader which version was read."""
    idx = ctx.get('_bib') or {}
    out = []
    for k in sorted(_cited(ctx)):
        if k not in idx:
            continue
        t, bd = idx[k]
        if not _is_preprint(t, bd) or _has_identifier(bd):
            continue
        out.append(_F('bib-preprint-without-identifier', _first_cite(ctx, k), 'query',
                      'lookup', True,
                      f'the {t} entry {k} carries no DOI, arXiv eprint, identifier or '
                      f'URL, so the reader cannot reach the version cited',
                      'Add the DOI, the arXiv id, or a versioned repository link'))
    return _cap(out,
                lambda n: f'{n} cited preprint, dataset or report entries carry no '
                          f'persistent identifier')


_BIB_SCAFFOLD = re.compile(
    r'\bTODO\b|\bFIXME\b|\bXXX\b|\bTBD\b|before submission|complete it|replace with|'
    r'truncated here|fill in|placeholder|\?\?|check (?:the|this|whether)|not sure|'
    r'\bMISSING\b', re.I)


def _c_bib_note_scaffolding(src, code, spans, prose, body, envs, labels, ctx, sub):
    """An author-to-author note in a bib entry's note field. Most styles print note, so
    the instruction lands in the printed reference list. Submission only: a draft is
    supposed to carry its own working notes."""
    if not sub:
        return []
    idx = ctx.get('_bib') or {}
    out = []
    for k in sorted(_cited(ctx)):
        if k not in idx:
            continue
        for f in ('note', 'annote', 'addendum'):
            v = _field(idx[k][1], f)
            if v and _BIB_SCAFFOLD.search(v):
                out.append(_F('bib-note-scaffolding-printed', _first_cite(ctx, k), 'batch',
                              'lookup', True,
                              f'the {f} field of bib entry {k} holds a working note that '
                              f'will print in the reference list: '
                              f'"{re.sub(chr(92) + "s+", " ", v)[:70]}"',
                              'Do what the note says, then delete the field'))
                break
    return _cap(out,
                lambda n: f'{n} cited bib entries hold working notes that will print in '
                          f'the reference list')


_UNPUB = re.compile(r'\bin preparation\b|\bin prep\b|\bsubmitted\b|\bunder review\b|'
                    r'\bforthcoming\b|\bmanuscript\b|\bpreprint\b|\bunpublished\b', re.I)


def _c_sole_unpublished_support(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A claim whose only support is a work that is unpublished and has no identifier.
    Counted once per entry, at the first citation that stands alone, because the fix is
    one act -- publish it, or deposit it -- however many sentences lean on it."""
    idx = ctx.get('_bib') or {}
    hits = collections.OrderedDict()
    for off, keys in ctx.get('_cites') or []:
        if len(keys) != 1 or keys[0] not in idx:
            continue
        t, bd = idx[keys[0]]
        status = ' '.join(x for x in (_field(bd, 'note'), _field(bd, 'journal'),
                                      _field(bd, 'howpublished'), _field(bd, 'series'),
                                      t) if x)
        if not _UNPUB.search(status):
            continue
        if _field(bd, 'doi') or _field(bd, 'eprint') or re.search(r'arXiv:\s*\d', bd, re.I):
            continue
        hits.setdefault(keys[0], [off, 0])
        hits[keys[0]][1] += 1
    out = []
    for k, (off, n) in hits.items():
        out.append(_F('sole-support-unpublished-work', off, 'query', 'rework', True,
                      f'{n} claim{"s" if n > 1 else ""} in this file '
                      f'{"rest" if n > 1 else "rests"} on {k} alone, which the bib records '
                      f'as unpublished with no DOI or arXiv id',
                      'Deposit the work and cite the identifier, or support the claim '
                      'with something a reader can read'))
    return out


def _c_output_entry_no_date(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A track-record or publication entry with no year. Only runs on a file that carries
    a CV apparatus (\\cventry, \\cvsubsection, \\biblegend), and only on paragraphs shaped
    like an output entry: a bold name and an italic title."""
    if not re.search(r'\\cventry|\\cvsubsection|\\biblegend|\\cvsection', code):
        return []
    out = []
    for m in re.finditer(r'\\noindent[^\n]*(?:\n(?!\s*\n)[^\n]*)*', code):
        blk = m.group(0)
        if '\\emph{' not in blk or not re.search(r'\\textbf\s*\{[A-Z]', blk):
            continue
        if len(blk) < 120 or re.search(r'\b(19|20)\d{2}\b', blk):
            continue
        title = ''
        for _o, b in _cmd_args(blk, 'emph'):
            title = _norm(b)[:60]
            break
        out.append(_F('output-entry-without-date', m.start(), 'query', 'lookup', True,
                      f'this output entry gives no year: "{title}"',
                      'Give the year, and the venue or archive it appeared in'))
    return out


def _c_uncited_bibitem(src, code, spans, prose, body, envs, labels, ctx, sub):
    """A \\bibitem no citation reaches. A hand-written bibliography prints every item, so
    an uncited one appears in the reference list attached to nothing in the text. This is
    silent about .bib entries, where BibTeX prints only what is cited."""
    keys = _cited(ctx)
    out = []
    for off, b in _cmd_args(code, 'bibitem'):
        k = b.strip()
        if k and k not in keys:
            out.append(_F('uncited-bibitem', off, 'query', 'free', False,
                          f'\\bibitem{{{k}}} prints in the reference list and no citation '
                          f'in this file reaches it',
                          'Cite it where its content is used, or remove the entry'))
    return _cap(out,
                lambda n: f'{n} \\bibitem entries print in the reference list with no '
                          f'citation reaching them')


# ------------------------------------------------------------------------- runner
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    stage = 'draft' if '--draft' in sys.argv else 'submission'
    verbose = '--quiet' not in sys.argv
    tot = collections.Counter()
    per_file = collections.Counter()
    for p in args:
        src = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        spans = ex.extract(src)
        found = checks(src, spans, {'stage': stage, 'path': p, 'style': {}})
        for f in found:
            tot[f['rule']] += 1
            per_file[(os.path.basename(p), f['rule'])] += 1
            if verbose:
                line = src.count('\n', 0, f['offset']) + 1
                print(f"{os.path.basename(p)}:{line}  [{f['tier']}/{f['cost']}"
                      f"{'/BLOCKS' if f['blocks'] else ''}]  {f['rule']}: {f['text']}")
    print(f'\n--- {sum(tot.values())} findings, stage={stage} ---')
    for r, c in tot.most_common():
        print(f'  {c:4d}  {r}')
    if len({k[0] for k in per_file}) > 1:
        print('\nby file:')
        for (fn, r), c in sorted(per_file.items()):
            print(f'  {fn:20s} {c:4d}  {r}')
