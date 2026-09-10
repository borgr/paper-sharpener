#!/usr/bin/env python3
"""naming-notation checks: one concept one name, symbol hygiene, abbreviation
discipline, citation-key correctness.

Detection in this family is mechanical; the repair almost never is. Two names for
one quantity looks identical to one real distinction drawn badly (latency vs CPU
time, Mb vs MB, LM vs LLM), so most rules here report a pair and ask, and only the
provably-ordered faults (an expansion that arrives after the first bare use, a
symbol defined after the equation that uses it) carry a mechanical fix.

Everything is read through byte-aligned views built from the extractor's spans:
    V.prose  prose bytes only, from `text` spans, with macro names, macro
             arguments that a reader never sees (\\cite, \\label, review markers)
             and the whole preamble blanked to spaces.
    V.math   math bytes only, from `mask` spans that are actually math.
    V.float  caption bodies and tabular cells lifted out of the masked floats,
             so an expansion that lives only in a caption or a column header is
             visible to the acronym rules and to nothing else.
Both views are the same length as `src`, so any regex offset into them is already
a source offset. Nothing here reads `.rendered`: macro unwrapping there turns
`\end{minipage}\begin{minipage}` into the words "minipage minipage", and every rule
in this family compares adjacent words, so all of them read source slices with the
macro names blanked to spaces instead.

Coverage of impl_naming-notation.jsonl, second pass. COVERED by a rule above,
NEW in this pass, or BLOCKED on the named missing evidence.
   1 per-section re-expansion      BLOCKED  house/venue convention: at ICLR a second
                                            expansion is an error, in grant prose it is
                                            required, and `style` carries no such key
   2 clipped informal forms        COVERED  clipped-informal-form
   3 project acronym byte-identical COVERED  project-acronym-variant (the 20-character
                                            ERC cap needs the call, so it is not tested)
   4 objective ids across parts     BLOCKED  needs both attachments in one scope (this
                                            checker sees one file) plus the judgement of
                                            whether a split objective was declared
   5 acronym per attachment        NEW      acronym-never-expanded
   6 abstract notation             COVERED  abstract-contains-notation
   7 proposal names the research   COVERED  proposal-names-the-research
   8 acronym too rare / too far    ELSEWHERE the "fewer than three uses" half already runs
                                            as acronym-barely-used in
                                            checks_register_redundancy, so repeating it here
                                            would double-report. The two-page distance is
                                            BLOCKED: it is not a source quantity, a
                                            figure-heavy page holds 200 bytes of .tex
   9 name/date factually wrong     PARTLY   cite-key-author-mismatch, cite-key-year-mismatch
                                            cover the pair a .bib settles; the rest needs
                                            the published record
  10 house-style variant sweep     BLOCKED  needs the style sheet; `style` has no key
  11 symbol used before definition COVERED  symbol-defined-after-first-use
  12 symbol with two meanings      COVERED  symbol-two-definitions
  13 acronym bare at first use     COVERED  acronym-defined-after-first-use + rule 5 above
  14 one concept, two names        NEW      name-variant-against-canonical (only where a
                                            macro body or a .bib title proves which
                                            spelling is the name)
  15 figure labels vs text symbols BLOCKED  the labels are inside the .pdf/.png
  16 unnumbered / overpacked display COVERED unnumbered-display-equation (the "several
                                            steps in one line" half is a judgement)
  17 symbol table, two symbols one NEW      two-symbols-one-concept, an identical-definiens
     concept                                test beside symbol-two-definitions. It finds
                                            nothing on the four documents: _defsites
                                            recognises 2 definitions in 14 files
  18 symbol used exactly once      BLOCKED  measured: the four one-occurrence symbols in
                                            the corpus are $R^2$, $\Delta$ and the $X$/$O$
                                            of TicTacToe. Deciding "introduced and dropped"
                                            from "standard notation" is the judgement, and
                                            no definition site exists for any of them
  19 "also satisfies (n)" with a   BLOCKED  needs the semantics of the referenced display:
     different symbol                      a placeholder-written relation makes it correct
  20 symbol opens a sentence       COVERED  sentence-opens-with-symbol, adjacent-symbols
                                            (adjacent-symbols-one-punctuation now vetoes
                                            serial lists and parallel symbol pairs, which
                                            were both correct as written, and reports the
                                            residue at `query` with no fix: inserting a
                                            word is wrong across a clause boundary)
  21 relational symbol read two ways BLOCKED the verbal reading of a relation is a judgement
  22 logic symbols in prose        COVERED  logic-symbol-in-prose
  23 expansion in caption / header  NEW     the float view feeds acronym-expansion-conflict
  24 one quantity, two labels      BLOCKED  measured: prefix matching over table headers
                                            returned only false pairs ("Arabic" against
                                            "English--Arabic", the script "Arab" against
                                            "North Levantine Arabic"). Axis labels are in
                                            the image files
  25 unit spelled two ways         COVERED  unit-spelling-variant
Demoted from `batch` to `query` with no fix: term-spelling-variant. It counted the two
spellings and told the author to adopt the majority, which is whichever form was typed more
often and can be the wrong one, under an escape clause that stated the grammar backwards
(the hyphen belongs before the noun, not after the copula) and that could never fire because
every counted occurrence was already attributive. Grammar settles the direction only for an
adjective + noun compound; for a noun + noun compound ("token space", "language modeling")
both spellings are correct before a noun, so no single repair exists to apply. The slot
filter now uses `_is_predicative`, which had the direction right, and the finding reports the
split alone.
  26 dimensioned column, no unit   COVERED  table-column-without-unit
  27 two tables, opposite orientation BLOCKED needs the judgement that two tables present
                                            the same comparison, and the fit decision needs
                                            the rendered width
  28 jargon absent from the panel  BLOCKED  the funder's published descriptor and keywords
     descriptor (B1 / Summary)
  29 same, specialist parts        BLOCKED  same descriptor, plus which panel was selected
  30 expansion later than first use COVERED acronym-defined-after-first-use
  31 acronym never expanded        NEW      acronym-never-expanded. check.py still carries
                                            the v0 undefined-acronym, which reads the
                                            rendered body, reports offset 0 and knows
                                            nothing about captions; run.py should supersede
                                            it here the way it already supersedes
                                            dangling-reference
  32 expanded twice in prose       COVERED  acronym-expanded-twice
  33 numbered display never cited  NEW      equation-label-never-referenced
Also new, from the same family but not a numbered rule: macro-arity-mismatch, because a
name bound to a macro is the authority the naming rules lean on, and a call that supplies
the wrong number of arguments silently eats the prose after it.
"""
import os
import re
import unicodedata

FAM = 'naming-notation'

# ---------------------------------------------------------------- byte views --

# macro name + every following optional/brace argument goes away
_KILL_ALL = (
    r'cite[a-zA-Z]*|nocite|label|(?:auto|c|C|eq|page|name|v)?ref\*?|url|'
    r'includegraphics|input|include|bibliography|bibliographystyle|bibliographyfile|'
    r'usepackage|documentclass|newcommand|renewcommand|providecommand|'
    r'DeclareRobustCommand|DeclareMathOperator|def|acronym|institution|granttypeyear|'
    r'hypersetup|definecolor|setlist|Crefname|crefalias|AddToHook|pretocmd|'
    r'extrafloats|setlength|vspace|hspace|todo|note|marginpar|cready|temp|'
    r'lc|adam|uriel|ym|bob|sy|yp|oa|wzm|thanks|author|affil|email|texttt|verb|'
    r'ercblock|ercscore|ercpolish|ercnoteimpl'
)
# Kept even though extract.py now masks \lc{}, \todo{} and friends as their own span
# kind: that masking only matches the brace-first form, so \note[#1]{a}{b}{c} and
# \bob[]{...} still arrive inside a text span. The ERC review macros are not in
# extract's ANNOT_MACROS at all, and their second argument is author-to-author traffic.
# macro name + first argument goes away, later arguments are prose
_KILL_FIRST = r'textcolor|color|href|hyperref|footnotemark'

_GREEK = (r'alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|'
          r'kappa|lambda|mu|nu|xi|pi|varpi|rho|varrho|sigma|varsigma|tau|upsilon|phi|'
          r'varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega')

_MATH_START = re.compile(r'\$|\\\[|\\begin\{(?:equation|align|gather|multline|eqnarray|array|math)')


class _View:
    pass


def _blank(buf, s, e):
    for i in range(s, e):
        if buf[i] != '\n':
            buf[i] = ' '


def _brace_end(s, i):
    """Index just past the balanced group starting at s[i] == '{'; -1 if unbalanced."""
    if i >= len(s) or s[i] != '{':
        return -1
    d = 0
    while i < len(s):
        if s[i] == '{':
            d += 1
        elif s[i] == '}':
            d -= 1
            if d == 0:
                return i + 1
        i += 1
    return -1


def _kill_cmd(buf, txt, base, m, first_only=False):
    """Blank a macro call in `buf`. Returns index in txt just past the call."""
    i = m.end()
    _blank(buf, base + m.start(), base + i)
    args = 0
    while i < len(txt):
        j = i
        while j < len(txt) and txt[j] in ' \t':
            j += 1
        if j < len(txt) and txt[j] == '[':
            k = txt.find(']', j)
            if k < 0:
                break
            _blank(buf, base + i, base + k + 1)
            i = k + 1
            continue
        if j < len(txt) and txt[j] == '{':
            k = _brace_end(txt, j)
            if k < 0:
                break
            if first_only and args >= 1:
                break
            _blank(buf, base + i, base + k)
            i = k
            args += 1
            continue
        break
    return i


def _macro_defs(src, ctx):
    """Zero-argument \\newcommand bodies short enough to substitute in place.

    Needed because a name bound to a macro (\\fkd -> FKD) is invisible in
    `.rendered`, which would hide every acronym the paper defines that way.
    One level of \\input is followed, since macro files are always separate.
    """
    txt = src
    d = os.path.dirname(os.path.abspath(ctx.get('path') or '.')) or '.'
    for m in re.finditer(r'\\(?:input|include)\s*\{([^}]*)\}', src):
        n = m.group(1).strip()
        for root in (d, os.path.dirname(d)):
            for cand in (n, n + '.tex'):
                p = os.path.join(root, cand)
                if os.path.isfile(p):
                    try:
                        txt += '\n' + open(p, encoding='utf-8', errors='replace').read()
                    except OSError:
                        pass
                    break
    out = {}
    for m in re.finditer(r'\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand)'
                         r'\s*\*?\s*\{?\\([a-zA-Z]+)\}?\s*(\[[^\]]*\])?\s*\{', txt):
        if m.group(2):
            continue
        k = _brace_end(txt, m.end() - 1)
        if k < 0:
            continue
        body = re.sub(r'\\[a-zA-Z]+\s*|[{}]', '', txt[m.end():k - 1]).strip()
        tok = '\\' + m.group(1)
        if body and len(body) <= len(tok) and re.fullmatch(r'[A-Za-z0-9\-]{2,}', body):
            out[tok] = body
    return out


def _prose_view(src, spans, macros=None):
    buf = [c if c == '\n' else ' ' for c in src]
    for sp in spans:
        if sp.kind != 'text':
            continue
        txt = sp.text
        for i, c in enumerate(txt):
            if c != '\n':
                buf[sp.start + i] = c
        # macros whose arguments a reader never sees
        for pat, first in ((_KILL_ALL, False), (_KILL_FIRST, True)):
            pos = 0
            rx = re.compile(r'\\(?:' + pat + r')(?![a-zA-Z])')
            while True:
                m = rx.search(txt, pos)
                if not m:
                    break
                pos = _kill_cmd(buf, txt, sp.start, m, first)
                if pos <= m.start():
                    pos = m.end()
        # remaining macro names, braces and separators
        for m in re.finditer(r'\\[a-zA-Z@]+\*?|\\\\|\\[,;:!%&#$_{}\[\]()~^ ]|[{}&~]|\$', txt):
            _blank(buf, sp.start + m.start(), sp.start + m.end())
        # a name bound to a macro is a name: put the body back, padded to width
        for tok, body in (macros or {}).items():
            for m in re.finditer(re.escape(tok) + r'(?![a-zA-Z])', txt):
                pad = body + ' ' * (m.end() - m.start() - len(body))
                for i, c in enumerate(pad):
                    buf[sp.start + m.start() + i] = c
    # the preamble is not prose; keep only the title argument
    d = src.find(r'\begin{document}')
    if d > 0:
        _blank(buf, 0, d)
        for m in re.finditer(r'\\title\s*\{', src[:d]):
            k = _brace_end(src, m.end() - 1)
            if k > 0:
                for i in range(m.end(), k - 1):
                    if src[i] not in '{}\\':
                        buf[i] = src[i]
    return ''.join(buf)


_VERBISH = ('Verbatim', 'verbatim', 'lstlisting', 'minted', 'alltt', 'gamebox',
            'pythonbox', 'gameboxstyle', 'pythonboxstyle')


def _verbatim_regions(src):
    """Literal-text environments, including the ones extract.py does not mask.

    extract's MASK_ENVS matches `verbatim` case-sensitively, so a fancyvrb
    `\begin{Verbatim}` block and every tcolorbox wrapper around one arrive as prose.
    On one real appendix that put six model transcripts into the prose view and made
    the bracket tags [GAME], [JEU] and [SPIEL] look like undefined acronyms.
    """
    out = []
    for env in _VERBISH:
        for m in re.finditer(r'\\begin\{' + env + r'\*?\}.*?\\end\{' + env + r'\*?\}', src, re.S):
            out.append((m.start(), m.end()))
    return out


def _devoice(buf, txt, base):
    """Blank, in `buf`, everything a reader does not see as words in `txt`."""
    for m in re.finditer(r'(?<!\\)\$[^$]*(?<!\\)\$', txt):
        _blank(buf, base + m.start(), base + m.end())
    for pat, first in ((_KILL_ALL, False), (_KILL_FIRST, True)):
        rx = re.compile(r'\\(?:' + pat + r')(?![a-zA-Z])')
        pos = 0
        while True:
            m = rx.search(txt, pos)
            if not m:
                break
            pos = _kill_cmd(buf, txt, base, m, first)
            if pos <= m.start():
                pos = m.end()
    for m in re.finditer(r'\\[a-zA-Z@]+\*?|\\\\|\\[,;:!%&#$_{}\[\]()~^ ]|[{}&~]|\$', txt):
        _blank(buf, base + m.start(), base + m.end())


def _float_view(src, spans, macros=None):
    """Byte view of caption bodies and tabular cells inside the masked floats.

    A different expansion of the same acronym in a caption or a column header is the
    same fault as one in the body, and the reader who reaches the float out of order
    is the one it misleads. Everything else in this module reads only `text` spans,
    so without this view a float is invisible.
    """
    buf = [c if c == '\n' else ' ' for c in src]
    filled = []
    for sp in spans:
        if sp.kind != 'mask':
            continue
        regions = []
        for m in re.finditer(r'\\caption(?:of)?\*?\s*(?:\[[^\]]*\])?\{', sp.text):
            k = _brace_end(sp.text, m.end() - 1)
            if k > 0:
                regions.append((m.end(), k - 1))
        for m in re.finditer(r'\\begin\{tabular\}\s*(?:\[[^\]]*\])?\s*\{[^{}]*\}', sp.text):
            e = sp.text.find(r'\end{tabular}', m.end())
            regions.append((m.end(), e if e > 0 else len(sp.text)))
        for s0, e0 in regions:
            for i in range(s0, e0):
                if sp.text[i] != '\n':
                    buf[sp.start + i] = sp.text[i]
            _devoice(buf, sp.text[s0:e0], sp.start + s0)
            filled.append((sp.start + s0, sp.start + e0))
    for tok, body in (macros or {}).items():
        for m in re.finditer(re.escape(tok) + r'(?![a-zA-Z])', src):
            if not _inside(filled, m.start()):
                continue
            pad = body + ' ' * (m.end() - m.start() - len(body))
            for i, c in enumerate(pad):
                buf[m.start() + i] = c
    return ''.join(buf)


def _math_view(src, spans):
    buf = [c if c == '\n' else ' ' for c in src]
    out = []
    for sp in spans:
        if sp.kind != 'mask' or not _MATH_START.match(sp.text):
            continue
        txt = sp.text
        for i, c in enumerate(txt):
            if c != '\n':
                buf[sp.start + i] = c
        rx = re.compile(r'\\(?:text|textrm|textit|textbf|mbox|operatorname|mathrm|'
                        r'label|intertext|begin|end|tag|hspace|quad|qquad)(?![a-zA-Z])')
        pos = 0
        while True:
            m = rx.search(txt, pos)
            if not m:
                break
            pos = _kill_cmd(buf, txt, sp.start, m)
            if pos <= m.start():
                pos = m.end()
        out.append(sp)
    return ''.join(buf), out


def _symbols(math, s, e):
    """Distinct symbol identities in math[s:e]: single letters and greek macros."""
    got = {}
    for m in re.finditer(r'\\(' + _GREEK + r')(?![a-zA-Z])', math[s:e]):
        got.setdefault('\\' + m.group(1), s + m.start())
    for m in re.finditer(r'(?<![A-Za-z\\])([A-Za-z])(?![A-Za-z])', math[s:e]):
        got.setdefault(m.group(1), s + m.start())
    return got


_WRAP = re.compile(r'^\\(?:mathcal|mathbf|mathbb|mathrm|mathsf|bm|boldsymbol|vec|hat|tilde|'
                   r'bar|overline)\{(.*)\}$')
_BARE = re.compile(r'\\?[A-Za-z]+(?:_\{?[A-Za-z0-9,+\-\s]{1,8}\}?)?(?:\^\{?[A-Za-z0-9,+\-]{1,4}\}?)?')


def _bare_symbol(math_text):
    """True when the inline math holds one symbol and nothing else.

    Guards the definition detector against reading '$\\mathrm{acc}_B$ denote the
    number of ...' as a definition of B, or '$p = 90\\%$' as a definition of p.
    """
    core = math_text.strip('$').strip()
    m = _WRAP.match(core)
    if m:
        core = m.group(1).strip()
    return bool(_BARE.fullmatch(core))


def _env_regions(src, envs):
    out = []
    for env in envs:
        for m in re.finditer(r'\\begin\{' + env + r'\*?\}(.*?)\\end\{' + env + r'\*?\}', src, re.S):
            out.append((m.start(1), m.end(1)))
    return out


def _cmd_regions(src, cmds):
    out = []
    for m in re.finditer(r'\\(?:' + '|'.join(cmds) + r')\*?\s*(?:\[[^\]]*\])?\{', src):
        k = _brace_end(src, m.end() - 1)
        if k > 0:
            out.append((m.end(), k - 1))
    return out


def _inside(regions, off):
    return any(s <= off < e for s, e in regions)


def _sections(src):
    """[(offset, title)] for every sectioning command, in order."""
    out = [(0, '(front matter)')]
    for m in re.finditer(r'\\(?:section|subsection|paragraph|part|chapter)\*?\s*\{([^}]*)\}', src):
        out.append((m.start(), m.group(1)))
    return sorted(out)


def _section_of(secs, off):
    n = 0
    for i, (s, _) in enumerate(secs):
        if s <= off:
            n = i
    return n


def _norm(s):
    s = s.replace('{', '').replace('}', '').replace('\\', '')
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())


def _line(src, off):
    return src.count('\n', 0, off) + 1


def _F(rule, off, tier, cost, blocks, text, fix=''):
    return {'rule': rule, 'family': FAM, 'offset': off, 'tier': tier, 'cost': cost,
            'blocks': blocks, 'text': text, 'fix': fix}


# ------------------------------------------------------------------ acronyms --

_ACR_STOP = {'of', 'the', 'for', 'and', 'in', 'to', 'a', 'an', 'on', 'with', 'at', 'by',
             'from', 'as', 'or', 'per', 'via'}
# forms that are names, not initialisms: expanding them tells the reader nothing
# tokens that are never initialisms, so a mismatched or repeated "expansion" of them
# is not an abbreviation fault
_NOT_INITIALISM = {'TODO', 'FIXME', 'XXX', 'TBD', 'OK', 'FIG', 'TAB', 'EQ', 'APP', 'CF'}

_ACR_RX = r'[A-Z][A-Za-z]*[A-Z][A-Za-z0-9]*'


def _sh_match(pre, acr):
    """Schwartz-Hearst: longest suffix of `pre` that the short form abbreviates."""
    a = [c.lower() for c in acr if c.isalnum()]
    if not a:
        return None
    li, ai = len(pre) - 1, len(a) - 1
    while ai >= 0:
        c, found = a[ai], False
        while li >= 0:
            ch = pre[li].lower()
            if ch == c and (ai > 0 or li == 0 or not pre[li - 1].isalnum()):
                found = True
                break
            li -= 1
        if not found:
            return None
        li -= 1
        ai -= 1
    st = li + 1
    while st > 0 and pre[st - 1].isalnum():
        st -= 1
    exp = pre[st:].strip(' \t-')
    words = [w for w in re.split(r'[\s\-]+', exp) if w]
    if not words or len(words) > len(a) + 3 or len(exp) > 90:
        return None
    if sum(1 for w in words if w.lower() not in _ACR_STOP) < max(1, len(a) - 1):
        return None
    return exp


def _expansions(P):
    """[(offset_of_acronym, acronym, expansion)] for both `long (SHORT)` orders."""
    out = []
    for m in re.finditer(r'\(\s*(' + _ACR_RX + r')s?\s*\)', P):
        acr = m.group(1)
        pre = P[max(0, m.start() - 130):m.start()]
        pre = pre[pre.rfind('.') + 1:] if '.' in pre[-90:] else pre
        exp = _sh_match(pre.rstrip(' \t('), acr)
        if exp:
            out.append((m.start(1), acr, exp))
    for m in re.finditer(r'\b(' + _ACR_RX + r')s?\s*\(([^()]{5,90})\)', P):
        acr, inner = m.group(1), m.group(2).strip()
        if re.search(r'[=\d]', inner) or ',' in inner:
            continue
        if _sh_match(inner, acr):
            out.append((m.start(1), acr, inner))
    return out


def _bare_uses(P, acr):
    return [m.start() for m in re.finditer(r'(?<![A-Za-z])' + re.escape(acr) + r's?(?![A-Za-z])', P)]


# ---------------------------------------------------------------------- bib ---

def _bib_text(ctx, src):
    d = os.path.dirname(os.path.abspath(ctx.get('path') or '.')) or '.'
    names, txt = [], ''
    for m in re.finditer(r'\\bibliography\s*\{([^}]*)\}|\\def\\bibliographyfile\{([^}]*)\}|'
                         r'\\addbibresource\s*\{([^}]*)\}', src):
        for g in m.groups():
            if g:
                names += [n.strip() for n in g.split(',')]
    cand = []
    for root in (d, os.path.dirname(d)):
        for n in names:
            cand.append(os.path.join(root, n if n.endswith('.bib') else n + '.bib'))
        try:
            cand += [os.path.join(root, f) for f in sorted(os.listdir(root)) if f.endswith('.bib')]
        except OSError:
            pass
    seen = set()
    for p in cand:
        rp = os.path.realpath(p)
        if rp in seen or not os.path.isfile(rp):
            continue
        seen.add(rp)
        try:
            txt += open(rp, encoding='utf-8', errors='replace').read() + '\n'
        except OSError:
            pass
    return txt


def _bib_entries(bib):
    """{key: {'author': str, 'year': str, 'title': str}} — brace-balanced parse."""
    ent = {}
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,\s{}]+)\s*,', bib):
        if m.group(1).lower() in ('comment', 'string', 'preamble'):
            continue
        i = bib.find('{', m.start())
        j = _brace_end(bib, i)
        body = bib[m.end():(j - 1 if j > 0 else min(len(bib), m.end() + 6000))]
        f = {}
        for fm in re.finditer(r'(?:^|,)\s*([a-zA-Z]+)\s*=\s*', body):
            k, s = fm.group(1).lower(), fm.end()
            if s >= len(body):
                break
            if body[s] == '{':
                e = _brace_end(body, s)
                val = body[s + 1:e - 1] if e > 0 else ''
            elif body[s] == '"':
                e = s + 1
                while e < len(body) and not (body[e] == '"' and body[e - 1] != '\\'):
                    e += 1
                val = body[s + 1:e]
            else:
                e = s
                while e < len(body) and body[e] not in ',\n':
                    e += 1
                val = body[s:e]
            f.setdefault(k, ' '.join(val.split()))
        ent[m.group(2)] = f
    return ent


def _surnames(author):
    out = []
    for a in re.split(r'\s+and\s+', author.strip()):
        a = a.strip().strip(',')
        if not a:
            continue
        if ',' in a:
            out.append(_norm(a.split(',')[0]))
            continue
        a = re.sub(r'\\[\'"`^~=.]|[{}]', '', a)
        toks = [t for t in re.split(r'\s+', a) if t]
        if not toks:
            continue
        sur = toks[-1]
        for i, t in enumerate(toks[:-1]):
            if t.lower().strip('.') in ('von', 'van', 'de', 'der', 'den', 'di', 'del',
                                        'da', 'la', 'le', 'ben', 'bin', 'al', 'dos'):
                sur = ' '.join(toks[i:])
                break
        out.append(_norm(sur))
        out.append(_norm(a))
    return [x for x in out if x]


def _close(a, b):
    """Same name allowing a prefix, a containment, or one dropped/changed letter.

    A key segment often loses a diacritic vowel (akyrek for Aky{\\"u}rek), which is a
    spelling choice, not a wrong entry.
    """
    if not a or not b:
        return False
    if a == b or a.startswith(b) or b.startswith(a) or a in b:
        return True
    if abs(len(a) - len(b)) > 1 or min(len(a), len(b)) < 5:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= 1


_VENUE = {'neurips', 'nips', 'icml', 'iclr', 'acl', 'emnlp', 'naacl', 'eacl', 'coling',
          'tacl', 'jmlr', 'aaai', 'ijcai', 'cvpr', 'iccv', 'eccv', 'arxiv', 'openreview',
          'proceedings', 'anonymous', 'eval', 'openai', 'google', 'deepmind', 'meta'}


def _cited_keys(src):
    out = {}
    for m in re.finditer(r'\\(?:cite|citep|citet|citealp|citealt|citeyear|citeauthor|'
                         r'parencite|textcite|footcite)\*?\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}', src):
        base = m.end() - len(m.group(1)) - 1
        off = 0
        for part in m.group(1).split(','):
            k = part.strip()
            if k and not k.startswith('%'):
                out.setdefault(k, base + off + (len(part) - len(part.lstrip())))
            off += len(part) + 1
    return out


# ------------------------------------------------------------------- rules ----

def _r_cite_author(src, spans, ctx, V):
    out = []
    for key, off in sorted(V.cites.items(), key=lambda x: x[1]):
        f = V.bib.get(key)
        if not f or not f.get('author'):
            continue
        m = re.match(r'^([A-Za-z\u00c0-\u024f\'`]+?)(?:19|20)\d\d', key)
        if not m:
            continue
        seg_raw = m.group(1)
        if seg_raw.isupper() or len(seg_raw) < 3:
            continue
        seg = re.sub(r'(etal|et)$', '', _norm(seg_raw))
        if not seg or seg in _VENUE:
            continue
        sur = _surnames(f['author'])
        if not sur:
            continue
        if any(_close(seg, s) for s in sur):
            continue
        # a key named after the paper or the model claims nothing about authorship
        if len(seg) >= 4 and seg in _norm(f.get('title', '')):
            continue
        first = ' '.join(re.split(r'\s+and\s+', f['author'].strip())[0].split())
        out.append(_F('cite-key-author-mismatch', off, 'query', 'lookup', True,
                      f'citation key {key} names "{seg_raw}" but the entry\'s authors are '
                      f'{first}{" et al." if " and " in f["author"] else ""} '
                      f'({f.get("title", "")[:60]})',
                      'check whether the key points at the intended entry, or rename the key '
                      'to the first author; the bib entry may have been pasted over'))
    return out


def _r_cite_year(src, spans, ctx, V):
    out = []
    for key, off in sorted(V.cites.items(), key=lambda x: x[1]):
        f = V.bib.get(key)
        if not f or not f.get('year'):
            continue
        m = re.search(r'((?:19|20)\d\d)', key)
        y = re.search(r'((?:19|20)\d\d)', f['year'])
        # a one-year gap is the ordinary preprint-to-proceedings drift, not a fault
        if not m or not y or abs(int(m.group(1)) - int(y.group(1))) < 2:
            continue
        out.append(_F('cite-key-year-mismatch', off, 'query', 'lookup', False,
                      f'citation key {key} says {m.group(1)}, the entry\'s year field says '
                      f'{y.group(1)} ({f.get("title", "")[:50]})',
                      'confirm which year is the one you cite (preprint vs proceedings is a '
                      'real difference), then make the key and the field agree'))
    return out


def _defsites(V):
    """{symbol: [(offset, definiens)]} from explicit defining phrasings only."""
    if getattr(V, '_ds', None) is not None:
        return V._ds
    pre_cue = re.compile(r'\b(?:let|where|denote[sd]? by|we denote|we define|define[sd]?)\s*$',
                         re.I)
    # `is`/`are` alone is predication, not definition ("$M$ are unaffected"): a
    # definiens has to open with a determiner, or the cue itself has to be definitional.
    post_cue = re.compile(r'^\s*(?:is\s+defined\s+as|:=|denotes?|represents?|refers?\s+to|'
                          r'stands\s+for|(?:is|are|be)\s+'
                          r'(?=(?:the|a|an|our|its|this|these|that|all|each|any)\b))'
                          r'\s*([^.;]{0,90})', re.I)
    sites = {}
    for i, sp in enumerate(V.spans):
        if sp.kind != 'mask' or not sp.text.startswith('$') or len(sp.text) > 40:
            continue
        if not _bare_symbol(sp.text):
            continue
        syms = _symbols(V.math, sp.start, sp.end)
        if len(syms) != 1:
            continue
        sym = next(iter(syms))
        before = V.prose[max(0, sp.start - 120):sp.start]
        after = V.prose[sp.end:sp.end + 110]
        pm, am = pre_cue.search(before.rstrip(' ')), post_cue.match(after)
        d = None
        if am:
            d = am.group(1)
        elif pm:
            bm = re.match(r'^\s*(?:be|is|as|denotes?|to be)\s+'
                          r'(?=(?:the|a|an|our|its|this|these|that)\b)([^.;]{0,90})', after, re.I)
            d = bm.group(1) if bm else None
        if not d or len(d.strip()) < 4:
            continue
        sites.setdefault(sym, []).append((sp.start, ' '.join(d.split())))
    V._ds = sites
    return sites


def _r_symbol_late_definition(src, spans, ctx, V):
    out = []
    sites = _defsites(V)
    abst = _env_regions(src, ['abstract'])
    for sym, ds in sites.items():
        first_def = min(o for o, _ in ds)
        uses = [sp.start for sp in V.mspans if sym in _symbols(V.math, sp.start, sp.end)]
        uses = [u for u in uses if not _inside(abst, u)]
        if not uses or len(uses) < 2:
            continue
        u = min(uses)
        if u >= first_def - 200:
            continue
        if any(abs(o - u) < 150 for o, _ in ds):
            continue
        out.append(_F('symbol-defined-after-first-use', u, 'query', 'rework', True,
                      f'{sym} is used in math on line {_line(src, u)} but only defined on '
                      f'line {_line(src, first_def)} ("{ds[0][1][:50]}")',
                      'move the definition to the first use, or state the symbol\'s meaning in '
                      'the sentence that introduces the earlier equation'))
    return out


def _r_symbol_two_definitions(src, spans, ctx, V):
    out = []
    for sym, ds in _defsites(V).items():
        if len(ds) < 2:
            continue
        ds = sorted(ds)
        base = ds[0][1].lower()
        for off, d in ds[1:]:
            a = set(re.findall(r'[a-z]{4,}', base))
            b = set(re.findall(r'[a-z]{4,}', d.lower()))
            if not a or not b or a & b or d.lower() in base or base in d.lower():
                continue
            out.append(_F('symbol-two-definitions', off, 'query', 'rework', True,
                          f'{sym} is defined twice with unrelated definitions: '
                          f'"{ds[0][1][:45]}" (line {_line(src, ds[0][0])}) and '
                          f'"{d[:45]}" (line {_line(src, off)})',
                          'say whether these are one object or two; if two, rename the second '
                          'use, if one, delete the second definition'))
            break
    return out


def _r_two_symbols_one_concept(src, spans, ctx, V):
    """Rule 17, second half: two symbols defined with the same words.

    The mirror image of symbol-two-definitions, and a different repair: there the
    second use has to be renamed, here one of the two letters has to go. Only an
    identical definiens counts, because two definitions that merely overlap are the
    ordinary case of a family of related quantities ("the loss on A", "the loss on B").
    """
    out = []
    seen = {}
    for sym, ds in sorted(_defsites(V).items()):
        for off, d in sorted(ds):
            k = _norm(d)
            if len(k) < 12:
                continue  # too short to be a distinguishing definition
            if k in seen and seen[k][0] != sym:
                (a, ao), (b, bo) = sorted([seen[k], (sym, off)], key=lambda x: x[1])
                out.append(_F('two-symbols-one-concept', max(ao, bo), 'query', 'rework', True,
                              f'{a} (line {_line(src, ao)}) and {b} '
                              f'(line {_line(src, bo)}) are both defined as "{d[:45]}"',
                              'say whether these are one object under two letters or two '
                              'objects the definitions fail to separate; if one, drop a '
                              'letter, if two, sharpen the second definition'))
                continue
            seen.setdefault(k, (sym, off))
    return out


def _r_acronym_late_expansion(src, spans, ctx, V):
    out = []
    skip = _cmd_regions(src, ['caption', 'section', 'subsection', 'subsubsection',
                              'paragraph', 'title', 'textbf'])
    for acr, sites in V.acr.items():
        exp = [(o, e) for o, e in sites if not _inside(skip, o)]
        if not exp:
            continue
        first_exp = min(o for o, _ in exp)
        uses = [u for u in _bare_uses(V.prose, acr)
                if not any(abs(u - o) < 2 for o, _ in sites)]
        early = [u for u in uses if u < first_exp - 5 and not _inside(skip, u)]
        if not early:
            continue
        out.append(_F('acronym-defined-after-first-use', early[0], 'batch', 'free', False,
                      f'{acr} is used bare on line {_line(src, early[0])} and only expanded on '
                      f'line {_line(src, first_exp)} as "{dict(exp)[first_exp][:50]}"',
                      f'move the expansion up to the first occurrence, keeping "{acr}" in '
                      'parentheses, and reduce the later occurrence to the bare form'))
    return out


def _r_acronym_expanded_twice(src, spans, ctx, V):
    out = []
    skip = _cmd_regions(src, ['caption', 'section', 'subsection', 'subsubsection',
                              'paragraph', 'title'])
    skip += _env_regions(src, ['abstract'])
    secs = _sections(src)
    for acr, sites in V.acr.items():
        s = sorted((o, e) for o, e in sites if not _inside(skip, o))
        if len(s) < 2:
            continue
        for (prev, pe), (o, e) in zip(s, s[1:]):
            if _section_of(secs, prev) != _section_of(secs, o):
                continue  # a per-section re-expansion is deliberate in grant prose
            if _norm(pe) != _norm(e) and _norm(pe) not in _norm(e) and _norm(e) not in _norm(pe):
                continue  # two different expansions is the conflict rule's finding, not this one
            out.append(_F('acronym-expanded-twice', o, 'batch', 'free', False,
                          f'{acr} is expanded twice inside one section, on lines '
                          f'{_line(src, prev)} and {_line(src, o)}',
                          'keep the first expansion and reduce this one to the bare acronym'))
            break
    return out


def _r_acronym_expansion_conflict(src, spans, ctx, V):
    out = []
    acrs = {a: list(v) for a, v in V.acr.items()}
    # a caption or a column header is read out of sequence, so a different expansion
    # there misleads exactly the reader who arrives at the float first
    for a, v in V.acr_float.items():
        for o, e in v:
            if not any(abs(o - o2) < 40 for o2, _ in acrs.get(a, [])):
                acrs.setdefault(a, []).append((o, e))
    for acr, sites in acrs.items():
        seen = {}
        for o, e in sorted(sites):
            k = _norm(e)
            seen.setdefault(k, (o, e))
        if len(seen) < 2:
            continue
        vals = list(seen.values())
        a, b = vals[0], vals[1]
        if _norm(a[1]) in _norm(b[1]) or _norm(b[1]) in _norm(a[1]):
            continue
        out.append(_F('acronym-expansion-conflict', b[0], 'query', 'lookup', True,
                      f'{acr} is expanded two different ways: "{a[1][:45]}" (line '
                      f'{_line(src, a[0])}) and "{b[1][:45]}" (line {_line(src, b[0])})',
                      'say which expansion is the name of the thing; if the two expansions are '
                      'two things, the acronym has to split'))
    return out


_SPACED_OK = {'et al', 'e g', 'i e', 'de facto'}
# a compound is hyphenated before the noun it modifies and open after a copula, so
# the two spellings are only evidence of inconsistency in the same syntactic slot
_COPULA = re.compile(r'\b(?:is|are|was|were|be|been|being|becomes?|became|remains?|'
                     r'stays?|seems?|appears?|looks?|not|only|both|either|neither)\s+$', re.I)
_FUNCTION = (r'of|in|on|for|with|over|under|to|as|by|from|than|that|which|and|or|but|is|are|'
             r'was|were|we|they|it|this|these|those|the|a|an|at|into|during|per|via|between|'
             r'across|when|where|while|if|then|thus|also|however|therefore|still|only|both|'
             r'each|its|our|their|can|may|must|does|do|has|have|had|not|no')
_ATTRIBUTIVE = re.compile(r'^\s+(?!(?:' + _FUNCTION + r')\b)[a-z]{3,}', re.I)


def _r_term_spelling_variant(src, spans, ctx, V):
    out, P = [], V.prose

    def slotted(offs, phrase):
        """Keep only occurrences in the attributive slot, where a following noun is
        modified. English hyphenates a compound modifier there and leaves it open in
        predicative position -- "a per-language cost" against "built per language" --
        so the two slots are not two spellings of one choice, and only occurrences
        sharing the attributive slot are evidence of anything."""
        keep = []
        for o in offs:
            pre = P[max(0, o - 40):o]
            post = P[o + len(phrase):o + len(phrase) + 30]
            if not _ATTRIBUTIVE.match(post) or _COPULA.search(pre):
                continue
            if _is_predicative(P, o, phrase):
                continue
            keep.append(o)
        return keep

    hyph = {}
    for m in re.finditer(r'(?<![A-Za-z\-])([a-z]{3,})-([a-z]{3,})(?![A-Za-z\-])', P):
        hyph.setdefault((m.group(1).lower(), m.group(2).lower()), []).append(m.start())
    for (w1, w2), hs in sorted(hyph.items(), key=lambda x: x[1][0]):
        if f'{w1} {w2}' in _SPACED_OK or w2 in ('like', 'wise', 'based', 'level', 'free'):
            continue
        # adverb + participle is hyphenated before a noun and open after one by rule,
        # and an -ly adverb is never hyphenated, so neither pair is a naming choice
        if w1.endswith('ly') or w1 in ('already', 'well', 'ill', 'much', 'very'):
            continue
        sp = [m.start() for m in re.finditer(r'(?<![A-Za-z\-])' + w1 + r' +' + w2 +
                                            r'(?![A-Za-z\-])', P)]
        cl = [m.start() for m in re.finditer(r'(?<![A-Za-z\-])' + w1 + w2 + r'(?![A-Za-z\-])', P)]
        hs = slotted(hs, f'{w1}-{w2}')
        sp = slotted(sp, f'{w1} {w2}')
        cl = slotted(cl, w1 + w2)
        forms = [('hyphenated', hs), ('spaced', sp), ('closed', cl)]
        live = [(n, v) for n, v in forms if v]
        if len(live) < 2 or len(hs) + len(sp) + len(cl) < 3:
            continue
        if {n for n, _ in live} == {'hyphenated', 'closed'}:
            continue  # that pair is checks_integrity's hyphenation-variant, not a second finding
        live.sort(key=lambda x: len(x[1]))
        minor, major = live[0], live[-1]
        # Reports the split and proposes nothing. The count carries no authority: the
        # majority form is whichever the author typed more often, which can be the wrong
        # one, and grammar settles the direction only for an adjective + noun compound.
        # For a noun + noun compound ("token space", "language modeling") both spellings
        # are correct before a noun, so there is no single repair to apply.
        out.append(_F('term-spelling-variant', minor[1][0], 'query', 'free', False,
                      f'"{w1} {w2}" modifies a following noun in both spellings, '
                      f'{major[0]} {len(major[1])}x and {minor[0]} {len(minor[1])}x '
                      f'(line {_line(src, minor[1][0])})',
                      ''))
    return out


# grouped by magnitude, not by dimension: 'sec' beside 'ms' is two magnitudes and
# no fault, while 'Mb' beside 'MB' is one magnitude spelled two ways and a factor of 8
_UNITS = {
    'second': ['s', 'sec', 'secs', 'second', 'seconds'],
    'millisecond': ['ms', 'msec', 'msecs', 'millisecond', 'milliseconds'],
    'minute': ['min', 'mins', 'minute', 'minutes'],
    'hour': ['h', 'hr', 'hrs', 'hour', 'hours'],
    'kilobyte or kilobit': ['KB', 'Kb', 'kB', 'kb', 'KiB', 'Kbyte', 'kilobyte',
                            'kilobytes', 'kilobit', 'kilobits'],
    'megabyte or megabit': ['MB', 'Mb', 'MiB', 'Mbyte', 'megabyte', 'megabytes',
                            'megabit', 'megabits'],
    'gigabyte or gigabit': ['GB', 'Gb', 'GiB', 'Gbyte', 'gigabyte', 'gigabytes',
                            'gigabit', 'gigabits'],
    'terabyte or terabit': ['TB', 'Tb', 'TiB', 'Tbyte', 'terabyte', 'terabytes'],
}
_UNIT_DIM = {}
for _d, _us in _UNITS.items():
    for _u in _us:
        _UNIT_DIM[_u] = _d


def _r_unit_spelling_variant(src, spans, ctx, V):
    out = []
    hits = {}
    for m in re.finditer(r'(?<![\w.])\d[\d.,]*\s{0,2}([A-Za-z]{1,10})(?![\w])', V.prose):
        u = m.group(1)
        d = _UNIT_DIM.get(u)
        if d:
            hits.setdefault(d, {}).setdefault(u, m.start(1))
    for d, us in sorted(hits.items()):
        if len(us) < 2:
            continue
        items = sorted(us.items(), key=lambda x: x[1])
        names = ', '.join(u for u, _ in items)
        out.append(_F('unit-spelling-variant', items[-1][1], 'query', 'lookup', True,
                      f'{d} quantities are written with {len(us)} different unit spellings '
                      f'({names})',
                      'say which unit each column actually reports — Mb and MB differ by eight, '
                      'MiB and MB by 4.9% — then fix one spelling per unit and apply it '
                      'everywhere; propose no unification until that answer is in'))
    return out


_LOGIC = (r'\\forall|\\exists|\\nexists|\\implies|\\impliedby|\\Rightarrow|\\Leftarrow|'
          r'\\iff|\\Leftrightarrow|\\therefore|\\because|\\land|\\lor|\\neg|\\wedge|\\vee')


def _r_logic_symbol_in_prose(src, spans, ctx, V):
    out = []
    for sp in V.mspans:
        if not sp.text.startswith('$') or sp.text.startswith('$$') or len(sp.text) > 120:
            continue
        m = re.search(_LOGIC, sp.text)
        if m:
            out.append(_F('logic-symbol-in-prose', sp.start + m.start(), 'batch', 'free', False,
                          f'{m.group(0)} appears in running prose inside inline math '
                          f'({sp.text[:40]})',
                          'write the connective as a word in prose and keep the symbol for '
                          'displays and formal statements'))
    for m in re.finditer(r'(?<![A-Za-z])s\.t\.', V.prose):
        out.append(_F('logic-symbol-in-prose', m.start(), 'batch', 'free', False,
                      '"s.t." abbreviates "such that" in running prose',
                      'write "such that"'))
    return out


_ABBR = {'eq', 'eqs', 'fig', 'figs', 'tab', 'tabs', 'app', 'sec', 'secs', 'cf', 'eg', 'ie',
         'etc', 'vs', 'al', 'no', 'ref', 'refs', 'ch', 'pp', 'resp', 'approx'}


def _r_sentence_opens_with_symbol(src, spans, ctx, V):
    out = []
    for sp in V.mspans:
        if not sp.text.startswith('$'):
            continue
        before = V.prose[max(0, sp.start - 60):sp.start]
        tail = before.rstrip()
        if not tail.endswith(('.', '!', '?')):
            continue
        w = re.search(r'([A-Za-z]+)\.$', tail)
        if w and w.group(1).lower() in _ABBR:
            continue
        if re.search(r'\d\.$', tail):
            continue
        out.append(_F('sentence-opens-with-symbol', sp.start, 'batch', 'free', False,
                      f'a sentence opens with the symbol {sp.text[:28]}',
                      'put the noun the symbol names in apposition before it, e.g. '
                      '"The loss $L$ ..."'))
    return out


def _shape(tex):
    """Crude shape of a math span: identifiers collapsed to M, numbers to N, space gone.
    Two spans of one shape are parallel by construction, so a sequence of them is an
    enumeration ($A$, $B$; $\\beta_1 = 0.9$, $\\beta_2 = 0.95$) and not a fault."""
    body = tex.strip('$').strip()
    body = re.sub(r'\\[A-Za-z]+', 'M', body)
    body = re.sub(r'[A-Za-z]', 'M', body)
    body = re.sub(r'\d+(?:\.\d+)?', 'N', body)
    return re.sub(r'\s+', '', body)


def _r_adjacent_symbols(src, spans, ctx, V):
    out, sp = [], V.spans
    for i in range(max(0, len(sp) - 2)):
        a, mid, b = sp[i], sp[i + 1], sp[i + 2]
        if a.kind != 'mask' or b.kind != 'mask' or mid.kind != 'text':
            continue
        if not (a.text.startswith('$') and b.text.startswith('$')):
            continue
        if not re.fullmatch(r'\s*[,.]\s*', mid.text):
            continue
        # A serial list is the commonest construction in mathematical prose and is correct
        # as written. A third item after the pair, with or without "and"/"or", means these
        # two are list members rather than two formulas run together.
        tail = ''.join(x.text for x in sp[i + 3:i + 6])
        if re.match(r'\s*,?\s*(?:and|or)\b', tail) or re.match(r'\s*,\s*\$', tail):
            continue
        if _shape(a.text) == _shape(b.text):
            continue
        # Reports and proposes nothing. The remaining pair is either a two-item list whose
        # conjunction is missing or a clause boundary, and inserting a word is wrong in the
        # second case: "for all $x$, $y \\le 1$ holds" needs the comma it has.
        out.append(_F('adjacent-symbols-one-punctuation', mid.start, 'query', 'free', False,
                      f'{a.text[:18]} and {b.text[:18]} are separated only by '
                      f'"{mid.text.strip()}", with no word between them',
                      ''))
    return out


# --------------------------------------------------------------- grant scope --

_GRANT_MARK = (r'\\acronym\{|ercformatting|Extended Synopsis|Horizon Europe|'
               r'ERC (?:Starting|Consolidator|Advanced) Grant|Principal Investigator|'
               r'Project Summary|Specific Aims|Intellectual Merit|Broader Impacts')


def _is_grant(src, ctx):
    if re.search(_GRANT_MARK, src):
        return True
    b = os.path.basename(ctx.get('path') or '').lower()
    return bool(re.match(r'^(b1|b2|part[_-]?b)', b))


_CLIP = (r'lab|labs|math|temp|temps|prep|config|configs|stats|spec|specs|demo|demos|info|'
         r'exp|exps|sim|sims|vocab')
_CLIP_FULL = {'lab': 'laboratory', 'labs': 'laboratories', 'math': 'mathematics',
              'temp': 'temperature', 'prep': 'preparation', 'config': 'configuration',
              'configs': 'configurations', 'stats': 'statistics', 'spec': 'specification',
              'specs': 'specifications', 'demo': 'demonstration', 'demos': 'demonstrations',
              'info': 'information', 'exp': 'experiment', 'exps': 'experiments',
              'sim': 'simulation', 'sims': 'simulations', 'vocab': 'vocabulary'}


def _r_clipped_informal(src, spans, ctx, V):
    if not _is_grant(src, ctx):
        return []
    out = []
    for m in re.finditer(r'(?<![A-Za-z\-])(' + _CLIP + r')(?![A-Za-z\-\.])', V.prose):
        w = m.group(1)
        if w.lower() in TERM_OF_ART:
            continue  # executable counter-case: the field's own term, not a clipping
        out.append(_F('clipped-informal-form', m.start(), 'batch', 'free', False,
                      f'clipped form "{w}" in narrative prose',
                      f'write "{_CLIP_FULL[w.lower()]}", unless the clipping is the field\'s '
                      'own term of art'))
    return out


_PROPOSAL_RX = (
    r'(?:this|the|our)\s+proposals?\s+(?:will|aims?|shows?|seeks?|develops?|investigates?|'
    r'studies|measures?|introduces?|proposes?|explores?|tests?|builds?|delivers?|'
    r'demonstrates?|establishes?)'
    r'|(?:goals?|aims?|objectives?|purpose|hypothes[ie]s|results?|findings?|methods?|'
    r'contributions?|work\s+packages?)\s+of\s+(?:this|the|our)\s+proposal'
    r'|(?:this|the|our)\s+proposal[\u2019\']s\s+(?:goals?|aims?|results?|findings?|'
    r'hypothes[ie]s|methods?|objectives?)')


def _r_proposal_names_research(src, spans, ctx, V):
    if not _is_grant(src, ctx):
        return []
    out = []
    for m in re.finditer(_PROPOSAL_RX, V.prose, re.I):
        out.append(_F('proposal-names-the-research', m.start(), 'batch', 'free', False,
                      f'"{" ".join(m.group(0).split())}" gives the document a property of the '
                      'research',
                      'use "proposal" for the document and "project" (or "we") for the work'))
    return out


def _r_abstract_notation(src, spans, ctx, V):
    if not _is_grant(src, ctx):
        return []
    out = []
    for s, e in _env_regions(src, ['abstract']):
        bad = []
        for sp in V.spans:
            if sp.kind == 'mask' and s <= sp.start < e and _MATH_START.match(sp.text):
                bad.append((sp.start, sp.text[:24]))
        math = [(sp.start, sp.end) for sp in V.spans if sp.kind == 'mask']
        for m in re.finditer(r'\\(?:textsuperscript|textsubscript|times|leq|geq|pm|approx|'
                             r'rightarrow|to)(?![a-zA-Z])', src[s:e]):
            if not _inside(math, s + m.start()):
                bad.append((s + m.start(), m.group(0)))
        if not bad:
            continue
        bad.sort()
        out.append(_F('abstract-contains-notation', bad[0][0], 'query', 'rework', True,
                      f'the abstract carries {len(bad)} piece(s) of notation or markup '
                      f'({", ".join(t for _, t in bad[:3])})',
                      'state each in words, or keep the symbol once in parentheses after its '
                      'name, and check the abstract survives a plain-text round trip'))
    return out


def _r_project_acronym_variant(src, spans, ctx, V):
    out = []
    m = re.search(r'\\acronym\s*\{', src)
    if not m:
        return []
    k = _brace_end(src, m.end() - 1)
    if k < 0:
        return []
    raw = src[m.end():k - 1]
    canon = re.sub(r'\\[a-zA-Z]+|[{}\s]', '', raw)
    if len(canon) < 3:
        return []
    key = _norm(canon)
    wordlike = canon.isalpha() and len(canon) <= 6
    rx = re.compile(r'(?<![A-Za-z0-9])([A-Za-z0-9][A-Za-z0-9\-\u2011.]{0,' +
                    str(len(canon) + 3) + r'}[A-Za-z0-9])(?![A-Za-z0-9])')
    for mm in rx.finditer(V.prose):
        tok = mm.group(1)
        if _norm(tok) != key or tok == canon:
            continue
        # an acronym that is also an English word would flag every ordinary use
        if wordlike and tok.lower() == tok:
            continue
        out.append(_F('project-acronym-variant', mm.start(1), 'batch', 'free', True,
                      f'the project acronym is declared "{canon}" but appears as "{tok}" here',
                      f'bind every mention to one macro so the panel sees "{canon}" '
                      'byte-identically in the header, the abstract and the body'))
    return out


def _r_unnumbered_display(src, spans, ctx, V):
    out = []
    for sp in V.spans:
        if sp.kind != 'mask':
            continue
        m = re.match(r'\\\[|\$\$|\\begin\{(?:equation|align|gather|multline|eqnarray)\*\}',
                     sp.text)
        if not m:
            continue
        if r'\label' in sp.text:
            continue
        out.append(_F('unnumbered-display-equation', sp.start, 'batch', 'free', False,
                      f'display equation with no number ({m.group(0)})',
                      'number the display so a reviewer can cite the step they are questioning'))
    return out


_DIMENSIONED = (r'time|latency|runtime|duration|size|memory|footprint|bandwidth|throughput|'
                r'speed|temperature|mass|energy|power|voltage|current|distance|wavelength')
_UNIT_TOKEN = (r'\b(?:s|ms|sec|secs|min|mins|h|hr|hrs|B|KB|MB|GB|TB|KiB|MiB|GiB|bytes?|bits?|'
               r'tokens?|words?|chars?|steps?|epochs?|examples?|%|percent|m|cm|mm|km|kg|g|mg|'
               r'K|C|F|J|W|V|A|Hz|kHz|MHz|GHz|FLOPs?|params?)\b|\\%|\\times')


def _r_table_column_no_unit(src, spans, ctx, V):
    out = []
    for sp in V.spans:
        if sp.kind != 'mask' or r'\begin{tabular}' not in sp.text:
            continue
        i = sp.text.find(r'\begin{tabular}')
        head = sp.text[i:]
        head = head[:min(len(head), (head.find('\\\\') + 2) if '\\\\' in head else 400)]
        if re.search(_UNIT_TOKEN, sp.text):
            continue
        for cell in head.split('&'):
            c = re.sub(r'\\[a-zA-Z]+|[{}\[\]\\]', ' ', cell)
            m = re.search(r'(?<![A-Za-z])(' + _DIMENSIONED + r')(?![A-Za-z])', c, re.I)
            if not m or '(' in cell:
                continue
            out.append(_F('table-column-without-unit', sp.start, 'query', 'lookup', True,
                          f'table column "{" ".join(c.split())[:40]}" reports a dimensioned '
                          'quantity with no unit in the header, caption or notes',
                          'ask the author for the unit; do not infer one from a sibling table '
                          'or from the magnitudes, since a guess rescales the whole column'))
            break
    return out


# ------------------------------------------------- acronyms with no expansion --

# Forms whose expansion is dead weight: the short form is the field's actual name, or
# the venue's readership treats it as a word. Firing on these was a 43% false-positive
# rate on one real proposal, measured in check.py's own WELL_KNOWN.
_UNIVERSAL = frozenset(
    'MIT IBM ACL ICML ICLR NAACL EMNLP NEURIPS NIPS AAAI IJCAI CVPR ECCV ICCV SIGIR KDD '
    'EUR USD GBP ILS USA UK EU UN NSF NIH ERC EPSRC UKRI DFG ANR JSPS COST '
    'API CPU GPU TPU RAM SSD HTTP HTTPS URL PDF HTML XML JSON CSV TSV SQL IDE CLI SDK '
    'NLP NLU NLG LLM LLMS ASR OCR CNN RNN LSTM GAN VAE MLP SGD MSE MAE RMSE STD '
    'PHD MSC BSC ORCID DOI ISBN ISSN ARXIV IEEE ACM AAAS NASA CERN ISO '
    'FAQ ETC USB GPS SIM PIN ATM CEO WWW TBD '
    'KB MB GB TB PPM RGB SI PPL SFT RLHF LORA MOE '
    # method and layer names a venue's readership reads as words, measured on 40 papers:
    # expanding these was most of what this rule found and none of it was worth a query
    'MLM CLS SEP MLE MAP EM POS NER SRL DNN BOW LDA SVM CRF HMM KNN PCA AUC ROC IOU '
    'TFIDF LSTM GRU BPTT CTC KL JS EMD OOV UNK '
    # Universal Dependencies tag names are the scheme's own codes, not this paper's
    'ADJ ADV ADP PRON PROPN NOUN VERB DET AUX CONJ CCONJ SCONJ PART PUNCT SYM INTJ NUM '
    'UPOS XPOS'.split())
# proper names rather than initialisms: rule 31's own exclusion list, extended with the
# forms that appear as model or dataset names in this literature
_PROPER_NAME = frozenset(
    'GPT BERT ROBERTA ALBERT SQUAD CUDA GLUE SUPERGLUE BLEU ROUGE CHRF COMET METEOR '
    'MMLU MMLUPRO GSM ARC HELM BIG BBH IFEVAL TREC CONLL WMT IWSLT OPUS NLLB FLORES '
    'LAION IMAGENET MNIST CIFAR COCO PILE C4 MC4 OSCAR REDPAJAMA DOLMA FINEWEB '
    'ADAM ADAMW RELU GELU SILU BPE T5 XLM MBART MT5 LLAMA MISTRAL QWEN GEMMA PHI OLMO '
    # task codes inside a benchmark suite are that suite's names for its parts, and an
    # NLP reviewer reads them as words. Measured on 100 papers, they were most of what
    # this rule found and none of them is a query worth an author's time.
    'MNLI QNLI WNLI RTE QQP SST SST2 COLA STSB MRPC ANLI SNLI XNLI COPA WSC BOOLQ '
    'MULTIRC RECORD WIC CB PASCAL VOC XSUM CNNDM '
    'WP PI CV OK ID TV PC'.split())


def _acr_counts(P, skip):
    """{ACRONYM: [offsets]} for all-caps tokens in prose, outside `skip` regions."""
    got = {}
    for m in re.finditer(r'(?<![A-Za-z0-9\\])([A-Z]{3,6}\d?)s?(?![A-Za-z0-9])', P):
        if _inside(skip, m.start()):
            continue
        got.setdefault(m.group(1), []).append(m.start())
    return got


def _r_acronym_never_expanded(src, spans, ctx, V):
    """Rules 5 and 31: an acronym this attachment never expands anywhere in itself.

    Every filter here is one the rule states or one a measurement forced. Without the
    "also written as a word" test, an uppercased ordinary word (GAME, JEU, SPIEL in a
    localisation appendix) reads as an undefined acronym; without the cited-title test,
    every benchmark name the prior work introduced does. Three occurrences is the floor,
    because a token used once or twice is a mention, not an abbreviation the reader has
    to carry.
    """
    out = []
    skip = _verbatim_regions(src) + _cmd_regions(src, ['url', 'href', 'texttt', 'path'])
    expanded = {a for a in V.acr} | {a for a in V.acr_float}
    expanded |= {a.rstrip('s') for a in expanded}
    titles = _norm(' '.join(V.bib.get(k, {}).get('title', '') for k in V.cites))
    for acr, offs in sorted(_acr_counts(V.prose, skip).items(), key=lambda x: x[1][0]):
        if len(offs) < 3:
            continue
        if acr in expanded or acr.rstrip('s') in expanded:
            continue
        if acr in _UNIVERSAL or acr in _PROPER_NAME or acr in _NOT_INITIALISM:
            continue
        if re.sub(r'\d', '', acr) in _PROPER_NAME:
            continue
        # the same string written with lowercase letters somewhere: it is a word in
        # capitals, not an initialism. `[a-z]` under re.I matches capitals, so the case
        # test has to be done on the matched text.
        if any(mm.group(0) != mm.group(0).upper() for mm in
               re.finditer(r'(?<![A-Za-z])' + acr + r'(?![A-Za-z])', V.prose, re.I)):
            continue
        # a name the cited literature introduced is not this document's to expand
        if len(acr) >= 3 and _norm(acr) in titles:
            continue
        out.append(_F('acronym-never-expanded', offs[0], 'query', 'lookup', False,
                      f'{acr} is used {len(offs)}x and never expanded anywhere in this file '
                      f'(first use line {_line(src, offs[0])})',
                      'supply the expansion at the first occurrence with the acronym in '
                      'parentheses, and confirm which expansion is meant: the document does '
                      'not contain it and near-identical expansions exist for most short forms'))
    return out


# ------------------------------------------------- displays nobody points at --

def _project_refs(ctx, src):
    """Every \\ref target in this file and in its sibling .tex files.

    A per-file check would report every label in a paper split into sections, because
    the reference lives in the file that discusses the equation, not the one that
    holds it. Comments are stripped first: a commented-out \\eqref is not a reference.
    """
    out = set()
    d = os.path.dirname(os.path.abspath(ctx.get('path') or '.')) or '.'
    seen = set()
    # this directory and its subdirectories, plus the parent's own .tex files, which is
    # the main.tex-beside-section/ layout. The parent's SUBdirectories are not scanned:
    # in a corpus of papers that is every other paper, and a \ref in an unrelated one
    # would silently suppress a real finding here.
    try:
        subs = [os.path.join(d, n) for n in sorted(os.listdir(d))
                if os.path.isdir(os.path.join(d, n)) and not n.startswith('.')]
    except OSError:
        subs = []
    for sub in [d] + subs[:12] + [os.path.dirname(d)]:
            try:
                fs = [f for f in sorted(os.listdir(sub)) if f.endswith('.tex')]
            except OSError:
                continue
            for f in fs[:60]:
                rp = os.path.realpath(os.path.join(sub, f))
                if rp in seen:
                    continue
                seen.add(rp)
                try:
                    t = open(rp, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                t = re.sub(r'(?<!\\)%[^\n]*', '', t)
                out |= set(re.findall(r'\\(?:auto|c|C|eq|page|name|v|labelc)?ref\*?\s*'
                                     r'\{([^}]*)\}', t))
    for m in re.finditer(r'\\(?:auto|c|C|eq|page|name|v)?ref\*?\s*\{([^}]*)\}',
                         re.sub(r'(?<!\\)%[^\n]*', '', src)):
        out.add(m.group(1))
    return {k.strip() for r in out for k in r.split(',')}


_NUMBERED = re.compile(r'\\begin\{(?:equation|align|gather|multline|eqnarray)\}')


def _r_equation_label_unreferenced(src, spans, ctx, V):
    """Rule 33: a numbered display carries a label that no reference points at.

    Report only. The label may be the target of a reference in a rebuttal, in an
    appendix built from another file, or in a published earlier version, and some
    venues require every display numbered, so proposing to unnumber it is wrong.
    """
    out = []
    refs = _project_refs(ctx, src)
    for sp in V.spans:
        if sp.kind != 'mask' or not _NUMBERED.match(sp.text):
            continue
        for m in re.finditer(r'\\label\s*\{([^}]*)\}', sp.text):
            if m.group(1).strip() in refs:
                continue
            out.append(_F('equation-label-never-referenced', sp.start + m.start(),
                          'query', 'free', False,
                          f'numbered display \\label{{{m.group(1)}}} is referenced nowhere '
                          f'in this file or its siblings',
                          ''))
    return out


# ------------------------------------------ a name an authority already settles --

_NAMEY = re.compile(r'(?<![A-Za-z0-9\\])([A-Za-z][A-Za-z0-9]{2,23})(?![A-Za-z0-9])')


def _macro_name_bodies(src, ctx):
    """0-argument macro bodies that read as a name, whatever their width.

    _macro_defs keeps only bodies no wider than the token, because it writes them into
    a byte-aligned view. An authority on spelling has no such constraint: \tool ->
    FineWeb is still the canonical spelling of FineWeb.
    """
    out = {}
    for tok, body in _macro_defs(src, ctx).items():
        out[tok] = body
    txt = src
    for m in re.finditer(r'\\(?:newcommand|renewcommand|providecommand|'
                         r'DeclareRobustCommand)\s*\*?\s*\{?\\([a-zA-Z]+)\}?\s*\{', txt):
        k = _brace_end(txt, m.end() - 1)
        if k < 0:
            continue
        body = re.sub(r'\\[a-zA-Z]+\s*|[{}]', '', txt[m.end():k - 1]).strip()
        if re.fullmatch(r'[A-Za-z0-9\-]{2,24}', body or ''):
            out.setdefault('\\' + m.group(1), body)
    return out


def _canonical_names(V):
    """{spelling: authority} for names a macro body or a cited title already fixes."""
    out = {}
    # mixed case only. An all-caps body is either an acronym, which the acronym rules
    # own, or a review marker: \new -> NEW made every ordinary "new" a name variant.
    mixed = lambda t: bool(re.search(r'[a-z]', t) and re.search(r'[A-Z]', t[1:]))
    for tok, body in V.names.items():
        if len(body) >= 4 and mixed(body):
            out.setdefault(body, f'the body of {tok}')
    for k in V.cites:
        for m in _NAMEY.finditer(V.bib.get(k, {}).get('title', '')):
            t = m.group(1)
            if len(t) >= 4 and mixed(t):
                out.setdefault(t, f'the title of {k}')
    return out


def _r_name_variant_canonical(src, spans, ctx, V):
    """Rule 14, restricted to the half an authority decides.

    Two spellings of one name is normally a query, because the author has to say which
    is the name. Where a macro body or a cited entry's title holds one spelling, the
    question is already answered, so this reports the variant against that authority.
    A difference in the first letter's case only is sentence capitalisation, not a
    variant, and quoted material is skipped because a title must not be rewritten.
    """
    out = []
    canon = _canonical_names(V)
    # `import textarena as ta` inside a tcolorbox-wrapped Verbatim is a code identifier,
    # and extract.py masks only lowercase `verbatim`, so the guard has to be local
    skip = _verbatim_regions(src) + _cmd_regions(src, ['url', 'href', 'texttt', 'path',
                                                      'lstinline', 'code'])
    for name, why in sorted(canon.items()):
        key = _norm(name)
        if len(key) < 3:
            continue
        for m in _NAMEY.finditer(V.prose):
            tok = m.group(1)
            if tok == name or _norm(tok) != key:
                continue
            if _inside(skip, m.start()):
                continue
            if tok[:1].swapcase() + tok[1:] == name:
                continue  # sentence-initial capital
            q = V.prose.rfind('``', max(0, m.start() - 90), m.start())
            if q >= 0 and V.prose.find("''", q, m.start()) < 0:
                continue  # inside a quotation: the wording is not ours to change
            out.append(_F('name-variant-against-canonical', m.start(), 'query', 'free', False,
                          f'"{tok}" on line {_line(src, m.start())} spells a name that '
                          f'{why} writes "{name}"',
                          f'write "{name}" here, unless this occurrence is quoting a title, '
                          'a code identifier or a released artefact name, which keep their '
                          'own spelling'))
            break
    return out


# ----------------------------------------------------- macros and their arity --

def _macro_arity(src):
    """{name: mandatory_arg_count} for \\newcommand-style definitions in this file."""
    out, bodies = {}, []
    for m in re.finditer(r'\\(?:newcommand|renewcommand|providecommand|'
                         r'DeclareRobustCommand)\s*\*?\s*\{?\\([a-zA-Z]+)\}?\s*'
                         r'(?:\[(\d)\])?\s*(\[[^\]]*\])?\s*\{', src):
        k = _brace_end(src, m.end() - 1)
        if k < 0:
            continue
        bodies.append((m.start(), k))
        n = int(m.group(2) or 0)
        if m.group(3):
            n -= 1  # the first argument has a default and is optional
        out[m.group(1)] = max(0, n)
    return out, bodies


def _r_macro_arity(src, spans, ctx, V):
    """A call that supplies fewer arguments than the macro declares.

    LaTeX then takes the next token as the argument, so the macro eats the first
    letter of the following word and the rest of that word lands outside it. Only the
    unambiguous case is reported: the next thing is a word of two or more letters, or
    there is no argument at all. `\\vec x` with one single-token argument is correct
    LaTeX and is not matched. Definition bodies are skipped, where `#1` stands in for
    the argument.
    """
    out = []
    arity, bodies = _macro_arity(src)
    doc = src.find(r'\begin{document}')
    # only real call sites: a commented-out usage note ("\lc shows, \cready hidden") and
    # \string\lc inside a warning message were all five hits on one macro file
    live = [(sp.start, sp.end) for sp in V.spans if sp.kind == 'text']
    for name, n in sorted(arity.items()):
        if n < 1:
            continue
        for m in re.finditer(r'\\' + name + r'(?![a-zA-Z])', src):
            if doc >= 0 and m.start() < doc:
                continue
            if not _inside(live, m.start()) or _inside(bodies, m.start()):
                continue
            if re.search(r'\\(?:string|noexpand|protect|show|meaning|let|def|csname)\s*$',
                         src[max(0, m.start() - 12):m.start()]):
                continue
            i, got = m.end(), 0
            while i < len(src):
                j = i
                while j < len(src) and src[j] in ' \t\n':
                    j += 1
                if j < len(src) and src[j] == '[':
                    k = src.find(']', j)
                    if k < 0:
                        break
                    i = k + 1
                    continue
                if j < len(src) and src[j] == '{':
                    k = _brace_end(src, j)
                    if k < 0:
                        break
                    i = k
                    got += 1
                    continue
                break
            if got >= n:
                continue
            rest = src[i:i + 40].lstrip(' \t')
            if not (re.match(r'[A-Za-z]{2,}', rest) or re.match(r'[.,;:)\n%]', rest)):
                continue
            out.append(_F('macro-arity-mismatch', m.start(), 'batch', 'free', True,
                          f'\\{name} takes {n} argument(s) but is called with {got} on line '
                          f'{_line(src, m.start())} (followed by "{rest[:24].strip()}")',
                          f'brace the argument, so \\{name} does not consume the text after it'))
    return out


_RULES = (_r_cite_author, _r_cite_year, _r_symbol_late_definition, _r_symbol_two_definitions,
          _r_two_symbols_one_concept, _r_acronym_late_expansion,
          _r_acronym_expanded_twice, _r_acronym_expansion_conflict,
          _r_term_spelling_variant, _r_unit_spelling_variant, _r_logic_symbol_in_prose,
          _r_sentence_opens_with_symbol, _r_adjacent_symbols, _r_clipped_informal,
          _r_proposal_names_research, _r_abstract_notation, _r_project_acronym_variant,
          _r_unnumbered_display, _r_table_column_no_unit,
          _r_acronym_never_expanded, _r_equation_label_unreferenced,
          _r_name_variant_canonical, _r_macro_arity)




# --- executable counter-cases -------------------------------------------------
# A counter-case that only gets printed is advice. Where it can be decided
# mechanically, the check must apply it and stay silent.

TERM_OF_ART = frozenset(
    'labs lab pretraining finetuning finetune multimodal multilingual crosslingual '
    'benchmark benchmarks logits softmax dropout embeddings transformer transformers '
    'zeroshot fewshot oneshot ablation ablations checkpoint checkpoints tokenizer '
    'tokenizers dataloader hyperparameter hyperparameters preprint preprints repo '
    'repos config configs eval evals sota'.split())


def _is_predicative(text, idx, phrase):
    """A compound is hyphenated only when it modifies a following noun.
    'built per language' is predicative and takes no hyphen."""
    before = text[max(0, idx - 40):idx].rstrip()
    after = text[idx + len(phrase):idx + len(phrase) + 30].lstrip()
    # A verb or preposition immediately before means the phrase is not modifying a noun.
    if re.search(r'\b(is|are|was|were|be|been|being|built|made|done|held|kept|'
                 r'measured|reported|computed|trained|evaluated|written|stored)\s*$', before, re.I):
        return True
    # Nothing nounlike follows, so it modifies nothing.
    if not re.match(r'[a-z]{3,}', after):
        return True
    return False


def checks(src, spans, ctx):
    """Return naming-notation findings. Never raises."""
    try:
        V = _View()
        V.spans = list(spans)
        # a name bound to a macro is a name: \fkd is FKD to the reader, and without the
        # substitution every acronym a paper defines that way is invisible to these rules
        V.macros = _macro_defs(src, ctx)
        V.names = _macro_name_bodies(src, ctx)
        V.prose = _prose_view(src, V.spans, V.macros)
        V.float = _float_view(src, V.spans, V.macros)
        V.math, V.mspans = _math_view(src, V.spans)
        V.cites = _cited_keys(src)
        V.bib = _bib_entries(_bib_text(ctx, src)) if V.cites else {}
        V._ds = None
        V.acr, V.acr_float = {}, {}
        for view, dest in ((V.prose, 'acr'), (V.float, 'acr_float')):
            got = getattr(V, dest)
            for off, acr, exp in sorted(_expansions(view)):
                if acr.upper() in _NOT_INITIALISM:
                    continue
                here = got.setdefault(acr, [])
                if any(abs(off - o) < 40 for o, _ in here):
                    continue  # the same site matched in both orders
                here.append((off, exp))
    except Exception:
        return []
    out = []
    for fn in _RULES:
        try:
            out.extend(fn(src, spans, ctx, V) or [])
        except Exception:
            continue
    return sorted(out, key=lambda f: (f['offset'], f['rule']))


if __name__ == '__main__':
    import collections
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import extract as ex

    tot = collections.Counter()
    stage = 'submission'
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--draft' in sys.argv[1:]:
        stage = 'draft'
    for p in args:
        src = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        fs = checks(src, ex.extract(src), {'stage': stage, 'path': p, 'style': {}})
        for f in fs:
            tot[f['rule']] += 1
            ln = src.count('\n', 0, f['offset']) + 1
            print(f'{pathlib.Path(p).name}:{ln}  [{f["tier"]}/{f["cost"]}'
                  f'{"/BLOCKS" if f["blocks"] else ""}]  {f["rule"]}: {f["text"]}')
            if f['fix']:
                print(f'        -> {f["fix"]}')
    print(f'\n--- {sum(tot.values())} findings ---')
    for r, c in tot.most_common():
        print(f'  {c:4d}  {r}')
