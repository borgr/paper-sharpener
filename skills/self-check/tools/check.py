#!/usr/bin/env python3
"""v0 checks: only rules that are script-decidable with a unique detection.
Every finding carries a source offset, a family, and a human_cost estimate.
"""
import re, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex

# `offset` is a byte offset into the source, or 0 when the check has no position — a
# document-level count has none. `line` is derived from `offset`, so the two can never
# disagree, and an offset of 0 reports line 0 rather than a plausible wrong line.
F = collections.namedtuple('F', 'rule family cost blocks offset line text')
# Acronyms a reader in this field already knows. Expanding these is not an improvement,
# and firing on them was a 43% false-positive rate on one real proposal.
WELL_KNOWN = frozenset(
    'MIT IBM ACL ICML ICLR NAACL EMNLP NEURIPS AAAI IJCAI CVPR ECCV ICCV SIGIR KDD WWW '
    'EUR USD GBP ILS USA UK EU UN NSF NIH ERC EPSRC UKRI DFG ANR JSPS '
    'API CPU GPU TPU RAM SSD HTTP HTTPS URL PDF HTML XML JSON CSV SQL OS IDE CLI SDK '
    'AI ML NLP NLU NLG LLM LLMS ASR OCR RL CNN RNN LSTM GAN VAE MLP SGD ADAM '
    'PHD MSC BSC MD DVM CV ORCID DOI ISBN ISSN ARXIV IEEE ACM AAAS NASA CERN '
    'FAQ EG IE ETC VS OK ID TV PC USB GPS SIM PIN ATM CEO PI CO '
    'MB GB KB TB MS NS PPM RGB SI'.split())


PREAMBLE_HINT = re.compile(r'\\(newcommand|renewcommand|def|DeclareRobustCommand|ProvidesPackage)')


def _is_definition_file(src, path=''):
    """A file that is mostly macro definitions carries no prose defects."""
    name = pathlib.Path(path).name.lower() if path else ''
    if name in ('lcommands.tex', 'math_commands.tex', 'lc_macros.tex', 'macros.tex',
                'preamble.tex', 'three_macros.tex', 'four_macros.tex'):
        return True
    if re.search(r'(^|[_-])(macros?|commands?|preamble|style)([_-]|\.|$)', name):
        return True
    # A file holding \begin{document} is a document, however many macros its preamble
    # defines. The previous test returned zero findings for any short paper whose preamble
    # carried eight \newcommands, which is silent under-reporting — the worst failure a
    # checker can have, because it looks identical to a clean result.
    if re.search(r'\\begin\{document\}', src):
        return False
    defs = len(PREAMBLE_HINT.findall(src))
    body = len([l for l in src.splitlines()
                if l.strip() and not l.lstrip().startswith('%')
                and not PREAMBLE_HINT.search(l)])
    # Definitions must dominate the file, not merely be numerous.
    return defs >= 8 and defs > body


def _in_definition(src, off):
    """True when this offset sits inside a macro definition body."""
    line_start = src.rfind('\n', 0, off) + 1
    return bool(PREAMBLE_HINT.search(src, line_start, off)) or '#1' in src[line_start:off + 40]



def _lineof(src, off):
    return src.count('\n', 0, off) + 1


_WORD = re.compile(r'[A-Za-z0-9]+')


def locate(src, fragment, lo=0, hi=None):
    """Find `fragment` in `src` when the fragment is a NORMALISED rendering of it.

    Rendering unwraps macros, and a check's own tokeniser drops digits and punctuation, so a
    fragment lifted from `.rendered` is usually absent from `src` verbatim. Anchor on the
    fragment's first word, then require the remaining words to appear in order inside a
    bounded window. Returns `(offset, verbatim_source_slice)`, or `(None, None)`.
    """
    hi = len(src) if hi is None else hi
    words = _WORD.findall(fragment or '')
    if not words:
        return None, None
    hit = src.find(fragment, lo, hi)
    if hit != -1:
        return hit, fragment
    span = max(len(fragment) * 3, 120)
    # Second pass ignores case, because a check that lower-cases its tokens reports
    # `optimisation` for a source that reads `Optimisation`.
    for fold in (False, True):
        anchor = re.compile(r'(?<![A-Za-z0-9])' + re.escape(words[0]),
                            re.IGNORECASE if fold else 0)
        ws = [w.lower() for w in words] if fold else words
        for m in anchor.finditer(src, lo, hi):
            window = src[m.start():min(hi, m.start() + span)]
            hay = window.lower() if fold else window
            if len(hay) != len(window):
                continue        # case folding changed length; offsets would drift
            pos, ok = 0, True
            for w in ws:
                j = hay.find(w, pos)
                if j == -1:
                    ok = False
                    break
                pos = j + len(w)
            if ok:
                return m.start(), window[:pos]
    return None, None


def oneline(text):
    """Longest line-internal run of `text`, plus a flag for each end that was cut.

    A finding is one line, and a quote that spans a source line break is not findable by a
    search — collapsing the break to a space only hides that. Keep the bytes exactly as the
    file holds them and let the caller mark the cut with an ellipsis.
    """
    if '\n' not in text:
        return text, False, False
    parts = text.split('\n')
    i = max(range(len(parts)), key=lambda k: len(parts[k].strip()))
    return parts[i].strip(), i > 0, i < len(parts) - 1


# Rules that are defects only at submission. A draft is supposed to contain scaffolding,
# and an unreferenced float is a reasonable thing to leave for later while writing.
SCAFFOLD_RULES = ('surviving-annotation', 'surviving-todo', 'placeholder-citation',
                  'cready-guards-placeholder', 'uncalled-float')


def _blank_comments(src):
    """Replace comment bodies with spaces, preserving every byte offset.

    Deleting them would shift offsets and break line reporting. Blanking keeps a regex from
    matching commented-out LaTeX while leaving positions exact.
    """
    return re.sub(r'(?<!\\)%[^\n]*', lambda m: ' ' * len(m.group(0)), src)


def run(src, path='', stage='submission'):
    if _is_definition_file(src, path):
        return []
    spans = ex.extract(src)
    live = _blank_comments(src)   # structural checks read this, never raw src
    out = []
    body = ''.join(s.rendered for s in spans if s.kind == 'text')

    def emit(rule, family, cost, blocks, off, text):
        """Record one finding. `off` is a byte offset into `src`, or 0 for no position.

        Every site routes through here so that `line` is always derived from `offset` and
        an unlocalised finding reports line 0 instead of a plausible wrong line.
        """
        off = int(off or 0)
        out.append(F(rule, family, cost, blocks, off,
                     _lineof(src, off) if off else 0, text))

    # --- integrity: dangling and uncalled cross-references -------------------
    labels = set(re.findall(r'\\label\{([^}]*)\}', live))
    refs = set(re.findall(r'\\(?:auto|c|C|eq)?ref\*?\{([^}]*)\}', live))
    for r in sorted(refs - labels):
        if '#' in r:
            continue
        m = re.search(r'\\(?:auto|c|C|eq)?ref\*?\{' + re.escape(r) + r'\}', src)
        emit('dangling-reference', 'integrity', 'free', True,
             m.start() if m else 0, f'\\ref{{{r}}} has no \\label')

    for l in sorted(labels - refs):
        if re.search(r'(fig|tab|alg)', l, re.I):
            m = re.search(r'\\label\{' + re.escape(l) + r'\}', src)
            emit('uncalled-float', 'integrity', 'free', False,
                 m.start() if m else 0,
                 f'\\label{{{l}}} is never referenced, so the float may be placed anywhere')

    # --- integrity: placeholder citations and empty cite keys ----------------
    for m in re.finditer(r'\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{\s*([^}]*)\}', live):
        key = m.group(1).strip()
        if not key:
            emit('empty-citation', 'integrity', 'lookup', True, m.start(), r'\cite{} with no key')
        elif re.search(r'[\[\]]|^[A-Z ]{6,}$|\bTODO\b|\bXXX\b', key):
            emit('placeholder-citation', 'integrity', 'lookup', True,
                 m.start(), f'citation key looks like a placeholder: {key[:40]}')

    # --- integrity: a citation written as bare brackets, never wired to \cite ---
    for sp in spans:
        if sp.kind != 'text':
            continue
        for m in re.finditer(r'\[([A-Za-z][A-Za-z.&\-]{2,}\d{2,4}[A-Za-z]*)\]', sp.text):
            emit('bracket-citation-not-wired', 'integrity', 'lookup', True,
                 sp.start + m.start(),
                 f'[{m.group(1)}] looks like a citation key but is literal text, so it renders as brackets')
        for m in re.finditer(r'\[(?:CITE|REF|CITATION|TODO)[^\]]{0,40}\]', sp.text, re.I):
            emit('bracket-citation-placeholder', 'integrity', 'lookup', True,
                 sp.start + m.start(),
                 f'placeholder citation marker in prose: {m.group(0)[:40]}')

    # --- integrity: a rewrite that left both versions live -------------------
    # Discovered from the corpus: an in-place rewrite often ships as two inputs, or as a
    # spliced sentence, because the author replaced text without removing the original.
    inputs = [(m.start(), m.group(1).strip()) for m in
              re.finditer(r'\\(?:input|include|subfile)\s*\{([^}]*)\}', live)]
    stems = {}
    for off, name in inputs:
        stem = re.sub(r'[_-]?(v\d+|old|new|final|copy|backup|bak|draft|rev\d*|\d+)$', '',
                      pathlib.Path(name).stem, flags=re.I)
        stems.setdefault(stem.lower(), []).append((off, name))
    for stem, group in stems.items():
        names = sorted({n for _, n in group})
        if len(names) > 1:
            emit('both-versions-included', 'integrity', 'free', True,
                 group[0][0],
                 f'two variants of the same file are both input: {", ".join(names[:4])}')

    # A spliced sentence: a lowercase word directly after a sentence-final stop, which is
    # what a half-applied replacement leaves behind.
    for sp in spans:
        if sp.kind != 'text':
            continue
        for m in re.finditer(r'[a-z]{3,}\.[ \t]{1,2}[a-z]{3,}\s+[a-z]{3,}', sp.rendered):
            seg = m.group(0)
            if '\n' in seg:
                continue
            if re.search(r'\b(et al|e\.g|i\.e|vs|cf|resp|approx|fig|eq|sec|tab|no|vol)\.', seg, re.I):
                continue
            # `m` indexes `sp.rendered`, which is not a source position — macro unwrapping
            # shifts every character after the first macro. Locate the segment in the span's
            # own bytes, so the offset is real and the quote is a string the file contains.
            off, hit = locate(sp.text, seg)
            piece, cut_l, cut_r = oneline(hit) if hit else (seg, False, False)
            quote = ('... ' if cut_l else '') + piece[:60] + (' ...' if cut_r else '')
            emit('spliced-sentence', 'integrity', 'free', True,
                 sp.start + off if off is not None else 0,
                 'sentence-final stop followed by lowercase, so a replacement may be '
                 f'half-applied: "{quote}"'
                 + ('' if hit else ' [quoted text is normalised, not a source string]'))

    # --- integrity: unbalanced math delimiters -------------------------------
    for sp in spans:
        if sp.kind != 'mask':
            continue
        # An inline verbatim span holds characters, not delimiters. `\verb|{|` is one brace
        # on purpose, and reporting it as an imbalance is a manufactured finding.
        if sp.text.startswith(('\\verb', '\\lstinline')):
            continue
        for op, cl, name in (('{', '}', 'brace'), ('(', ')', 'paren'), ('[', ']', 'bracket')):
            if sp.text.count(op) != sp.text.count(cl):
                emit('unbalanced-delimiter', 'integrity', 'free', True,
                     sp.start, f'{name} imbalance inside math/float span')
                break

    # --- integrity: surviving annotation markers (the corpus finding) --------
    for m in re.finditer(r'\\(lc|ym|temp|todo|wzm|oa|sy|yp|uriel|adam|bob)\b\s*\{', live):
        if _in_definition(src, m.start()):
            continue
        emit('surviving-annotation', 'integrity', 'free', True,
             m.start(), f'review marker \\{m.group(1)}{{...}} still present')
    for m in re.finditer(r'(?<!\\)%[^\n]*\b(TODO|FIXME|XXX|TBD|HERE GOES)\b[^\n]*', src, re.I):
        emit('surviving-todo', 'integrity', 'free', False,
             m.start(), m.group(0).strip()[:70])

    # --- integrity: camera-ready reminder guarding text that still has a placeholder
    for m in re.finditer(r'\\cready\s*\{([^}]*)\}', live):
        window = src[max(0, m.start() - 400):m.end() + 200]
        if re.search(r'XXXX+|\bTBD\b|\bTODO\b|/XXX', window):
            emit('cready-guards-placeholder', 'integrity', 'lookup', True,
                 m.start(),
                 f'\\cready reminder is hidden in draft mode while guarded text still holds a placeholder: {m.group(1)[:50]}')

    # --- naming-notation: acronym used before definition --------------------
    defined = set()
    for m in re.finditer(r'\(([A-Z][A-Za-z]*[A-Z][A-Za-z]*)\)', body):
        defined.add(m.group(1))
    seen = {}
    for m in re.finditer(r'\b([A-Z]{2,6})\b', body):
        seen.setdefault(m.group(1), m.start())
    for a, first in sorted(seen.items(), key=lambda x: x[1]):
        if a in defined or len(a) < 3:
            continue
        if a in WELL_KNOWN or a.rstrip('S') in WELL_KNOWN:
            continue
        if body.count(a) >= 3 and a not in ('THE', 'AND', 'FOR', 'NOT', 'ARE'):
            # A count over the whole document. `first` indexes the rendered body, which is
            # not a source position, so report it rather than inventing one.
            emit('undefined-acronym', 'naming-notation', 'free', False, 0,
                 f'{a} used {body.count(a)}x with no parenthetical expansion')

    # --- evidence-surface: plus-minus with no stated meaning -----------------
    if re.search(r'\\pm|±', src) and not re.search(
            r'(standard (deviation|error)|std|s\.?d\.?|s\.?e\.?m?\.?|confidence interval|CI)\b', body, re.I):
        m = re.search(r'\\pm|±', src)
        emit('undefined-pm', 'evidence-surface', 'free', True,
             m.start(), 'plus-minus used, meaning never stated')

    if stage != 'submission':
        out = [f for f in out if f.rule not in SCAFFOLD_RULES]
    return out


if __name__ == '__main__':
    tot = collections.Counter()
    for p in sys.argv[1:]:
        src = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        for f in run(src, p):
            tot[f.rule] += 1
            print(f'{pathlib.Path(p).name}:{f.line}  [{f.family}/{f.cost}{"/BLOCKS" if f.blocks else ""}]  {f.rule}: {f.text}')
    print(f'\n--- {sum(tot.values())} findings ---')
    for r, c in tot.most_common():
        print(f'  {c:4d}  {r}')
