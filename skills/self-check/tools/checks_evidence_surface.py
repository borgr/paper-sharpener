#!/usr/bin/env python3
"""evidence-surface checks: tables, figures, numbers, error terms, captions.

Implements the script-decidable subset of impl_evidence-surface.jsonl. Two family
constraints are enforced structurally rather than per rule:

* no precision or rounding rule is allowed to reach an exact value, so every numeric
  comparison here runs behind ``_EXACT_HEAD`` and ``_SETTING_HEAD`` and refuses any column
  holding counts, seeds, sizes, hashes, identifiers, versions, step indices, swept
  parameter grids, or a single integer among decimals;
* every rule whose right answer is a house-style decision reads ``ctx['style']`` and
  returns nothing when the key it needs is absent.

Floats, tabulars and math arrive from ``extract`` as ``mask`` spans, so their content is
read from ``span.text``. Prose is read from ``span.rendered`` on ``text`` spans.

Bracketed numbers in the comments are 0-based indices into ``impl_evidence-surface.jsonl``.

Second pass
-----------
``extract`` now masks review annotations (``\lc{}``, ``\wzm{}``, ``\todo{}``) and
``comment`` blocks as their own span kinds, so nothing here has to guard against reading a
co-author's note as prose. It also merges a per-cent comment that sits *inside* a float into
that float's single mask span, which makes ``live()`` blind there; an audit caught two
commented-out ``\includegraphics`` lines reported as raster figures, so the new float-body
checks go through ``shown()``, which re-derives comment ranges from the raw source.

Fourteen further checks, reaching eleven rules the first pass did not touch and completing a
half of three it left open:

* [24] ``float-never-referenced`` — a labelled float no ``\ref`` points at.
* [12] ``figure-raster-not-vector`` — the vector-format half of the rule.
* [16] ``figure-reproduces-typeset-material`` — an image whose name says it holds a table.
* [39] ``table-decimals-unaligned`` — the decimal-point half of the alignment rule.
* [11] ``statistical-test-unnamed``.
* [29] ``number-selection-rule-unstated``.
* [9]  ``error-bar-over-tiny-n``.
* [60][41] ``plot-axis-name-missing`` and ``plot-axis-unit-missing`` — two ids, because a
  missing quantity name and a missing unit are different repairs.
* [0][10] ``plot-gridlines-not-lightened``, [43] ``plot-rainbow-colormap``,
  [1] ``plot-depth-effect``. These read pgfplots option lists, the only graph internals that
  live in the ``.tex`` at all.
* [17] ``workplan-tasks-unquantified`` and ``workplan-task-owner-unnamed`` — two ids, one
  document-level finding each.

Blocked, needs the rendered document (13 rules). [2] axis range, tick spacing, aspect ratio
and physical size compared across panels; [3] whether an intermediate measurement could exist
between two plotted points; [4] whether a magnitude axis starts at zero and which way it
runs; [5] which visual channel each quantity is encoded in; [7] whether juxtaposed panels
share and align on one axis; [22] whether figure text is too small or too crowded at printed
size; [35] which axis carries the quantity the experimenter set; [36] whether a discrete
series carries markers at the measured points; [45] the count of distinct category colours;
[47][48] Tufte's lie factor, which needs the drawn effect measured on the page; [49][50] the
cell count of the plotted data matrix and the printed area it occupies. Nine further rules
are half blocked the same way: [0][10] gridline and axis stroke weight against the data
marks, [12] the smallest text in points and the minimum line thickness, [14] axis labels,
units and keys of figures that arrive as external files, [18] caption font size against the
call's minimum, [41] axis units for the same external files, [43] the colour map of an
external figure, [6] whether a figure was generated at its final printed size, [21] whether a
generalisation is supported. Every one of these would need the compiled PDF plus the figure
sources, which the checker is not given.

Blocked, needs outside knowledge (7 rules). [20] citation form and missing citations — which
claim needs one is a judgement, and citation form belongs to another family; [27] whether the
released code runs — needs the artifact; [30] ablation coverage — needs the count of changes
against the closest prior system, which is a reading of the published record; [42] grouping
every reported number by the quantity it measures — needs to know which numbers measure the
same thing, and the exact-value guard forbids the rest; [57][58][59] the ERC, Wellcome and
UKRI track-record rules — need the funder's call text and the applicant's actual role in each
output, and ``ctx`` carries no funder key; [61] whether a table's rows hold the condition and
its columns the outcome — deciding which variable is which is a judgement about the design.

[19] is the exact-value constraint itself, not a check; it is enforced structurally above.

Dropped after measurement, with the count that caused it:

* [34] "the reference says only that the float exists". The narrow form — every ``\ref`` to a
  label appears as a bare parenthetical — returned 12 on ``iclr_latex.tex``, where the
  statement sits in the sentence and the pointer is appended in brackets afterwards. A
  false-positive machine on any paper with that house style.
* [21], quotation half. Double-quoted runs of six words or more with no citation in the
  sentence returned 4 on ``iclr_latex.tex``, every one a synthetic training-data example
  rather than a quotation. The float-source half of [21] is kept.
* [17] per task. Firing once per task heading gave 11 of 12 and 10 of 12 on ``b2.tex``, which
  is a blanket criticism rather than a defect class, so both halves report once per document
  and carry the count.
* [24] for unlabelled floats. A float with no ``\label`` may still be discussed where it
  stands, so only labelled-and-unreferenced floats are reported.
* [12] for ``.jpg``. A photograph is raster by nature and has no vector original, so the
  extension is never flagged, and names reading as photographic material are skipped.

New-check counts on the three audit documents: ``iclr_latex.tex`` 2
figure-reproduces-typeset-material and 2 table-decimals-unaligned; ``b1.tex`` 1
float-never-referenced; ``b2.tex`` 1 workplan-tasks-unquantified and 1
workplan-task-owner-unnamed. The five pgfplots checks, error-bar-over-tiny-n,
statistical-test-unnamed, number-selection-rule-unstated and figure-raster-not-vector are
silent on all three and were verified against a constructed positive for each.
"""
import re
import sys
import pathlib
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex

FAMILY = 'evidence-surface'
PREAMBLE_HINT = re.compile(r'\\(newcommand|renewcommand|def|DeclareRobustCommand|ProvidesPackage)')
FLOAT_ENVS = ('figure', 'table', 'algorithm', 'wrapfigure', 'wraptable',
              'sidewaysfigure', 'sidewaystable', 'SCfigure', 'SCtable')
CAP = 12  # per-rule emission cap; a rule at its cap is reported as too loose


# --------------------------------------------------------------------------- utils
def _is_definition_file(src, path=''):
    """A file that is mostly macro definitions carries no evidence surface."""
    name = pathlib.Path(path).name.lower() if path else ''
    if name in ('lcommands.tex', 'math_commands.tex', 'lc_macros.tex', 'macros.tex',
                'preamble.tex', 'four_macros.tex', 'three_macros.tex'):
        return True
    if re.search(r'\\begin\s*\{document\}', src):
        return False          # a macro file never opens a document
    defs = len(PREAMBLE_HINT.findall(src))
    return defs >= 8 and defs > src.count('\\section') * 4


def _f(rule, offset, tier, cost, blocks, text, fix=''):
    return {'rule': rule, 'family': FAMILY, 'offset': int(offset), 'tier': tier,
            'cost': cost, 'blocks': bool(blocks), 'text': text, 'fix': fix}


def _arg(src, i):
    """Balanced-brace argument starting at the '{' at or after i. -> (body, end_index)."""
    while i < len(src) and src[i] not in '{':
        if src[i] not in ' \t\r\n':
            return '', i
        i += 1
    if i >= len(src):
        return '', i
    depth, j = 0, i
    while j < len(src):
        c = src[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return src[i + 1:j], j + 1
        j += 1
    return src[i + 1:], len(src)


def _env_blocks(src, name):
    """(start, end, body_start, body_end) for each \\begin{name}...\\end{name}, nesting aware."""
    out = []
    op = re.compile(r'\\begin\s*\{' + name + r'\*?\}')
    cl = re.compile(r'\\end\s*\{' + name + r'\*?\}')
    marks = sorted([(m.start(), m.end(), 1) for m in op.finditer(src)] +
                   [(m.start(), m.end(), -1) for m in cl.finditer(src)])
    stack = []
    for s, e, kind in marks:
        if kind == 1:
            stack.append((s, e))
        elif stack:
            bs, be = stack.pop()
            out.append((bs, e, be, s))   # every matched pair, so one stray \begin
    out.sort()                           # cannot swallow the floats that follow it
    return out


def _captions(src):
    """(start, body) for every \\caption / \\captionof, balanced."""
    return [(s, b) for s, b, _ in _captions_ex(src)]


def _captions_ex(src):
    """(start, body, is_captionof) for every caption macro."""
    out = []
    for m in re.finditer(r'\\caption(of)?\s*(?:\{[a-z]*\})?(?![a-zA-Z])\s*'
                         r'(?:\[[^\]]*\])?\s*', src):
        body, _ = _arg(src, m.end())
        out.append((m.start(), body, bool(m.group(1))))
    return out


CAPTIONABLE = ('figure', 'table', 'algorithm', 'wrapfigure', 'wraptable', 'sidewaysfigure',
               'sidewaystable', 'longtable', 'SCfigure', 'SCtable', 'subfigure', 'subtable',
               'minipage', 'threeparttable', 'adjustbox', 'listing', 'lstlisting', 'floatrow',
               'algorithm2e', 'margintable', 'marginfigure', 'tcolorbox', 'boxedminipage')


def _plain(tex):
    """Reader-visible text of a source fragment (captions, headers, cells)."""
    t = re.sub(r'\\(?:cite|citep|citet|citealp|autocite)[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{[^}]*\}', ' \u2020 ', tex)
    t = re.sub(r'\\(?:ref|autoref|cref|Cref|eqref|label)\s*\{[^}]*\}', ' \u2021 ', t)
    t = re.sub(r'\$[^$]*\$', ' \u00a4 ', t)
    for _ in range(3):
        t = re.sub(r'\\multicolumn\s*\{[^{}]*\}\s*\{[^{}]*\}\s*\{([^{}]*)\}', r'\1', t)
        t = re.sub(r'\\multirow\s*\{[^{}]*\}\s*\{[^{}]*\}\s*\{([^{}]*)\}', r'\1', t)
    for _ in range(4):
        t = re.sub(r'\\[a-zA-Z@]+\s*(\[[^\]]*\])?\s*\{([^{}]*)\}', r'\2', t)
    t = t.replace(r'\%', '%').replace(r'\&', '&').replace(r'\_', '_')
    t = re.sub(r'\\[a-zA-Z@]+\s*', ' ', t)
    t = re.sub(r'[{}~]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def _split_cells(row):
    """Split a tabular row on unescaped &, honouring braces and brackets."""
    cells, depth, buf, i = [], 0, [], 0
    while i < len(row):
        c = row[i]
        if c == '\\' and i + 1 < len(row):
            buf.append(row[i:i + 2])
            i += 2
            continue
        if c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
        if c == '&' and depth <= 0:
            cells.append(''.join(buf))
            buf = []
        else:
            buf.append(c)
        i += 1
    cells.append(''.join(buf))
    return cells


_RULE_MACROS = re.compile(r'\\(?:hline|toprule|midrule|bottomrule|cmidrule|cline|specialrule|addlinespace|'
                          r'morecmidrules|rowcolor|noalign)\s*(\([^)]*\))?\s*(\{[^{}]*\})?')


def _tab_rows(body):
    """Data rows of a tabular body: list of (raw_row, n_rule_macros_before)."""
    parts = re.split(r'\\\\', body)
    rows = []
    for p in parts:
        p = re.sub(r'^\s*\[[^\]]*\]', '', p)
        nrules = len(_RULE_MACROS.findall(p))
        clean = _RULE_MACROS.sub('', p)
        if clean.strip():
            rows.append((clean, nrules))
    return rows


def _tab_spec(src, bs):
    """(column spec, body start) for a tabular whose \\begin ends at bs."""
    i = bs
    m = re.match(r'\s*\[[^\]]*\]', src[i:])
    if m:
        i += m.end()
    spec, end = _arg(src, i)
    if re.search(r'\\(?:text|line|column|hsize)width|\\dimexpr|^\s*$', spec):
        spec2, end2 = _arg(src, end)
        if spec2:
            return spec2, end2
    return spec, end


def _head_row(rows):
    """(cells, index) of the label row: the first row of non-numeric cells."""
    if not rows:
        return None, -1
    ncol = max(len(_split_cells(r)) for r, _ in rows)
    for i, (r, _) in enumerate(rows[:3]):
        cells = _split_cells(r)
        if len(cells) != ncol or ncol < 2:
            continue
        filled = [c for c in cells if _plain(c).strip()]
        if len(filled) >= 2 and not any(_cellnum(c) for c in filled):
            return cells, i
    return None, -1


_NUMCELL = re.compile(r'^\s*[-+(\[]?\s*(\d[\d,]*)(?:\.(\d+))?\s*\)?\s*%?\s*$')


def _cellnum(cell):
    """(integer_digits, decimal_digits) for a bare numeric cell, else None."""
    t = _plain(cell)
    t = t.replace('\u00a4', '').replace('$', '').replace('*', '').strip()
    t = re.sub(r'\\,|\\;|\\ |\u2009', '', t)
    t = t.replace('{,}', '').replace(',', '')
    t = re.sub(r'(?<=\d)\s+(?=\d)', '', t)
    t = re.sub(r'\s*(\u2020|\u2021)\s*', '', t)
    if not t or re.search(r'[a-zA-Z]', t):
        return None
    m = _NUMCELL.match(t)
    if not m:
        return None
    return len(m.group(1)), len(m.group(2) or '')


# Heads whose values are exact: never let a precision rule touch these columns.
_EXACT_HEAD = re.compile(
    r'\b(n|count|counts|#|num|number|size|sizes|bytes|kb|mb|gb|tb|param|params|parameters|'
    r'seed|seeds|id|ids|index|indices|step|steps|epoch|epochs|iter|iters|iteration|iterations|'
    r'version|hash|layer|layers|head|heads|dim|dims|dimension|token|tokens|examples|instances|'
    r'sentences|documents|docs|split|splits|rows|batch|vocab|vocabulary|year|years)\b', re.I)

# Heads that are a swept setting rather than a measurement.
_SETTING_HEAD = re.compile(
    r'\b(rate|ratio|share|fraction|proportion|overlap|coverage|threshold|temperature|'
    r'lr|learning rate|weight decay|dropout|alpha|beta|gamma|lambda|scale|scales|p|prob|'
    r'probability|budget|target|targets|setting|settings|config|configuration)\b', re.I)

_DIMENSIONAL = re.compile(
    r'\b(time|times|runtime|wall[- ]?clock|latency|duration|delay|memory|ram|vram|footprint|'
    r'bandwidth|throughput|speed|power|energy|voltage|current|temperature|mass|weight|length|'
    r'width|height|distance|area|volume|pressure|frequency|cost|price|salary|budget|storage|disk)\b',
    re.I)

_UNIT_IN_HEAD = re.compile(
    r'[(\[/]\s*(%|s|ms|us|\u00b5s|ns|min|mins|minutes|h|hr|hrs|hours|days|'
    r'b|kb|mb|gb|tb|kib|mib|gib|bit|bits|byte|bytes|bpb|bpc|'
    r'm|cm|mm|km|kg|g|mg|hz|khz|mhz|ghz|w|kw|kwh|j|kj|v|a|k|c|f|'
    r'usd|eur|\$|\u20ac|gpu[- ]?h|gpu[- ]?hours|core[- ]?h|flops?|tflops|petaflops)\s*[)\]]?',
    re.I)

_GRAPHICS = re.compile(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{\s*([^}]*?)\s*\}')

# A plot exported as a bitmap is a production defect; a photograph is raster by nature, so
# .jpg never counts and names that read as photographic material are skipped outright.
_RASTER_EXT = ('.png', '.bmp', '.tif', '.tiff', '.gif', '.ppm', '.pgm')
_PHOTO_NAME = re.compile(r'photo|portrait|headshot|logo|screen-?shot|scan\b|micrograph|'
                         r'microscop|qr[-_]?code|camera|picture|insect|icon', re.I)

# An image whose file name says it holds a table or code is typeset material shipped as a
# picture: unsearchable, unselectable, and set at whatever size the export happened to use.
_TABLE_IMAGE = re.compile(r'(?:^|[_\-. /])(tables?|tabular|listing|code|snippet|equations?|'
                          r'formula|pseudo-?code|screen-?shot)(?:$|[_\-. (\d])', re.I)

_REF_KEY = re.compile(r'\\(?:auto|c|C|name|page|v|eq|labelc|sub|full|)ref\*?\s*\{([^}]*)\}'
                      r'|\\hyperref\s*\[([^\]]*)\]')
_HARDCODED_FLOAT_NUM = re.compile(r'\b(?:Figure|Table|Fig\.|Tab\.)~?\s*\d')

_TESTNAME = re.compile(
    r'\bt-?test\b|\bANOVA\b|\bWilcoxon\b|\bMann-?Whitney\b|\bMcNemar\b|\bchi-?squared?\b|'
    r'\b\\chi\^?2|\bFisher(?:\'s)? exact\b|\bKolmogorov\b|\bShapiro\b|\bKruskal\b|\bTukey\b|'
    r'\bbootstrap\w*|\bpermutation (?:test|resampl\w+)\b|\bsign test\b|\bbinomial test\b|'
    r'\blikelihood[- ]ratio test\b|\bpaired (?:test|comparison|bootstrap)\b|\brandomi[sz]ation test\b|'
    r'\bZ-?test\b|\bF-?test\b|\bmixed[- ]effects? model\b|\bBayes factor\b', re.I)

_SELECTION_RULE = re.compile(
    r'\bmean\b|\bmeans\b|\baverag\w+|\bmedian\b|\bbest of\b|\bbest-of\b|\bsingle run\b|'
    r'\bone run\b|\bbest checkpoint\b|\blast checkpoint\b|\bfinal checkpoint\b|\bmaximum over\b|'
    r'\bmax over\b|\bwe report the\b|\bacross seeds\b|\bover seeds\b|\bper-?seed\b|\bmedian of\b',
    re.I)

_TINY_N = re.compile(r'\bn\s*=\s*([123])\b(?!\d)|'
                     r'\b(two|three|2|3)\s+(seeds?|runs?|replicates?|folds?|repetitions?|'
                     r'trials?|subjects?|participants?)\b', re.I)

_TASK_HEAD = re.compile(r'\\(?:paragraph|subsubsection|subsection|section)\*?\s*\{\s*'
                        r'((?:T|WP|Task\s*|Objective\s*)\s*\d+(?:\.\d+)?)\b[^}]*\}')
_WORKPLAN_HINT = re.compile(r'\\begin\s*\{ganttchart\}|\bwork ?packages?\b|\bdeliverable\b|'
                            r'\bmilestone\b|\bperson-?months?\b', re.I)
_QUANTIFIED = re.compile(
    r'(?<![A-Za-z\\])\d+(?:[.,]\d+)?\s*(?:\\?%|M\b|B\b|k\b|models?|languages?|runs?|seeds?|'
    r'subjects?|participants?|datasets?|benchmarks?|tasks?|measurements?|protocols?|outputs?|'
    r'experiments?|papers?|sites?|cohorts?|conditions?|hours?|GPU|person-?months?)|'
    r'\b(?:two|three|four|five|six|seven|eight|nine|ten|twelve)\s+'
    r'(?:models?|languages?|runs?|seeds?|subjects?|participants?|datasets?|benchmarks?|'
    r'experiments?|protocols?|outputs?|measurements?|conditions?)\b', re.I)
_OWNER = re.compile(r'\bPhD student\b|\bdoctoral (?:student|researcher)\b|\bpost-?doc\w*|'
                    r'\bresearch (?:assistant|engineer|associate|fellow)\b|\bthe PI\b|'
                    r'\bprincipal investigator\b|\bI will\b|\bI plan\b|\bI shall\b|'
                    r'\bthe candidate\b|\bhire\b|\brecruit\w*|\bteam member\b|\bwe hire\b', re.I)

# pgfplots axes are the only graphs whose insides live in the .tex; an \includegraphics of a
# plot is a rendered-document question, not a source one.
_AXIS_ENVS = ('axis', 'semilogxaxis', 'semilogyaxis', 'loglogaxis', 'polaraxis',
              'ternaryaxis', 'smithchart')


_PVAL = re.compile(r'(?<![a-zA-Z\\])([pP])\s*(=|<|>|\\leq|\\geq|\\le|\\ge|\u2264|\u2265)?\s*'
                   r'(0?\.\d+|0|1\.0+|1)\b')


_PCTX = re.compile(r'p[- ]?values?|signific\w+|hypothes\w+|null\b|permutation|bootstrap|'
                   r'\bt-test|\bANOVA\b|chi-?squared?|Wilcoxon|Mann-?Whitney|McNemar|'
                   r'Bonferroni|Holm|false discovery|\\alpha\s*=|\bFDR\b|corrected', re.I)


def _is_pvalue(src, off):
    """True when the p at off is a probability from a test, not a variable named p."""
    return bool(_PCTX.search(src[max(0, off - 400):off + 400]))


def _sig_digits(numstr):
    t = numstr.lstrip('-+').replace(',', '')
    if '.' in t:
        ip, dp = t.split('.', 1)
        if ip.strip('0') == '':
            return len(dp.lstrip('0'))
        return len(ip.lstrip('0')) + len(dp)
    return len(t.strip('0')) or 1


def _spec_letters(spec):
    """Column type letters of a tabular spec, in column order."""
    clean = spec
    for _ in range(4):
        clean = re.sub(r'\{[^{}]*\}', '', clean)
    clean = re.sub(r'\[[^\]]*\]', '', clean)
    clean = re.sub(r'[<>@!|*]', '', clean)
    return re.findall(r'[lcrpmbXSs]', clean)


def _opts(src, i):
    """Bracketed option list beginning at or after i. -> (body, end_index)."""
    while i < len(src) and src[i] in ' \t\r\n':
        i += 1
    if i >= len(src) or src[i] != '[':
        return '', i
    depth, j = 0, i
    while j < len(src):
        c = src[j]
        if c == '\\':
            j += 2
            continue
        if c in '[{':
            depth += 1
        elif c in ']}':
            depth -= 1
            if depth == 0:
                return src[i + 1:j], j + 1
        j += 1
    return src[i + 1:], len(src)


def _find(span, phrase, default=None):
    """Offset in src of a rendered phrase, located by its first real words."""
    base = span.start if default is None else default
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", phrase)][:4]
    for n in (4, 3, 2, 1):
        if len(words) < n:
            continue
        pat = r'\s*'.join(re.escape(w) for w in words[:n])
        m = re.search(pat, span.text)
        if m:
            return span.start + m.start()
    return base


# --------------------------------------------------------------------------- checks
def checks(src, spans, ctx):
    """Return evidence-surface findings. Never raises: a broken check yields nothing."""
    try:
        return _checks(src, spans, ctx)
    except Exception:
        return []


def _checks(src, spans, ctx):
    style = (ctx or {}).get('style') or {}
    if _is_definition_file(src, (ctx or {}).get('path', '')):
        return []
    out = []
    text_spans = [s for s in spans if s.kind == 'text']
    body = ' '.join(sp.rendered for sp in text_spans)
    visible = body + ' ' + ' '.join(sp.text for sp in spans if sp.kind == 'mask')
    sents = ex.sentences(spans)
    cmts = [(sp.start, sp.end) for sp in spans if sp.kind == 'comment']

    def live(off):
        """False for material that is commented out, which a reader never sees."""
        return not any(a <= off < b for a, b in cmts)

    # extract merges a comment that sits inside a float into the float's mask span, so a
    # per-cent comment inside a figure is invisible to live(). These ranges see it.
    raw_cmts = [(m.start(), m.end()) for m in re.finditer(r'(?<!\\)%[^\n]*', src)]

    def shown(off):
        """False for an offset inside any comment, including one nested in a float."""
        return live(off) and not any(a <= off < b for a, b in raw_cmts)

    floats = []
    for env in FLOAT_ENVS:
        for s, e, bs, be in _env_blocks(src, env):
            if live(s):
                floats.append((env, s, e, src[bs:be]))
    floats.sort(key=lambda t: t[1])

    tabs = []          # (start, end, body_start, body_end, spec)
    for s, e, bs, be in _env_blocks(src, 'tabular'):
        if not live(s):
            continue
        spec, bstart = _tab_spec(src, bs)
        tabs.append((s, e, bstart, be, spec))

    whole_doc = bool(re.search(r'\\begin\s*\{document\}', src))
    numeric_tabs = sum(1 for s, e, bs, be, _ in tabs
                       if len(re.findall(r'\d+\.\d+', src[bs:be])) >= 4)
    reports_results = numeric_tabs >= 2

    abstract = [(bs, be) for _, _, bs, be in _env_blocks(src, 'abstract')]

    def in_abstract(off):
        return any(a <= off < b for a, b in abstract)

    def add(fn):
        try:
            got = fn() or []
        except Exception:
            return
        out.extend(got[:CAP])

    # ---- [16][24] a float with no caption ---------------------------------
    def r_float_missing_caption():
        got = []
        for env, s, e, inner in floats:
            if re.search(r'\\caption', inner):
                continue
            got.append(_f('float-missing-caption', s, 'query', 'rework', True,
                          f'\\begin{{{env}}} carries no \\caption',
                          'add a caption stating what the reader should take from it'))
        return got

    # ---- [16] a caption with no float ------------------------------------
    def r_caption_outside_float():
        holders = []
        for env in CAPTIONABLE:
            holders += [(bs, be) for bs, be, _, _ in _env_blocks(src, env)]
        got = []
        for coff, cbody, is_of in _captions_ex(src):
            if is_of or not cbody.strip() or not live(coff):
                continue          # \\captionof exists precisely for non-float material
            if any(a <= coff < b for a, b in holders):
                continue
            got.append(_f('caption-outside-float', coff, 'query', 'rework', True,
                          f'\\caption sits in no float or captionable environment, so it will not '
                          f'be numbered: {_plain(cbody)[:50]!r}',
                          'wrap the material in a figure or table environment, or use \\captionof'))
        return got

    # ---- [23] caption that cannot be read alone --------------------------
    def r_caption_not_standalone():
        verb = re.compile(
            r'\b(is|are|was|were|be|been|has|have|had|does|do|did|can|will|would|shows?|showing|'
            r'compares?|reports?|gives?|lists?|summari[sz]es?|illustrates?|depicts?|plots?|'
            r'presents?|indicates?|demonstrates?|achieves?|outperforms?|improves?|reduces?|'
            r'raises?|lowers?|holds?|remains?|varies|differs?|means?|denotes?|marks?|'
            r'trained|tested|measured|evaluated|computed|obtained|used|shown|reported|fitted|'
            r'preserved|estimated|normali[sz]ed|leaves?|excludes?)\b', re.I)
        got = []
        for env, s, e, inner in floats:
            for coff, cbody in _captions(inner):
                txt = _plain(cbody)
                words = re.findall(r"[\w'-]+", txt)
                if len(words) > 9 or not words:
                    continue
                if verb.search(txt):
                    continue
                if re.search(r'\b(hyper-?parameters?|configuration|config|settings?|architecture|'
                             r'notation|symbols?|prompts?|template|glossary|statistics|'
                             r'examples?|abbreviations?)\b', txt, re.I):
                    continue          # a listing, not a result: no take-away to state
                got.append(_f('caption-not-standalone', s + coff, 'query', 'rework', False,
                              f'caption is a {len(words)}-word label with no statement of the '
                              f'take-away: {txt[:60]!r}',
                              'state in the caption what the reader should conclude from the float'))
        return got

    # ---- results in prose with no float reference ------------------------
    def r_result_without_float_ref():
        claim = re.compile(r'\b(outperform\w*|improv\w+|gain\w*|increase[sd]?|decrease[sd]?|'
                           r'reduce[sd]?|reduction|higher|lower|better|worse|exceed\w*|'
                           r'drop[s]?|rise[s]?)\b', re.I)
        pointer = re.compile(r'\\(?:auto|c|C|eq)?ref\*?\{|\b(Table|Figure|Fig\.|Tab\.|Appendix|'
                             r'Section|\u00a7|Eq)\b')
        got = []
        for sent, si, _ in sents:
            if '\u2021' in sent or pointer.search(sent):
                continue
            if '&' in sent or '\\\\' in sent:
                continue          # tabular rows leaking out of an unmasked long table
            if not floats:
                continue          # nothing to point at in this file
            if not claim.search(sent):
                continue
            # a measured value, never a bare integer
            if not re.search(r'(?<![A-Za-z\d.])\d+(?:\.\d+)?\s*\\?%|'
                             r'(?<![A-Za-z\d.])\d+\.\d+(?![.\d])', sent):
                continue
            sp = spans[si]
            off = _find(sp, sent)
            if in_abstract(off):
                continue          # an abstract does not point at floats
            window = src[max(0, off - 900):off + 900]
            if pointer.search(window):
                continue          # the paragraph already points at the evidence
            got.append(_f('result-without-float-reference', off, 'query', 'lookup', False,
                          f'numeric result claimed with no table or figure reference anywhere in '
                          f'the paragraph: {sent[:80]!r}',
                          'point the paragraph at the table or figure the number is read from'))
        return got

    # ---- percentage confused with percentage points ----------------------
    def r_percent_vs_points():
        move = re.compile(r'\b(increase[sd]?|improv\w+|gain\w*|rise[sd]?|grow\w*|decrease[sd]?|'
                          r'drop\w*|fall\w*|decline[sd]?|reduc\w+|higher|lower|better|worse)\b', re.I)
        pctmetric = re.compile(r'\b(accurac\w+|precision|recall|f1|f-?score|rate|percentage|'
                               r'share|proportion|coverage|success|error rate|win rate)\b', re.I)
        got = []
        for sent, si, _ in sents:
            if re.search(r'percentage[- ]point|\bpp\b|relative(?:ly)?\b|\bfactor of\b', sent, re.I):
                continue
            if not move.search(sent) or not pctmetric.search(sent):
                continue
            m = re.search(r'\b(?:by|of)\s+(\d+(?:\.\d+)?)\s*\\?(?:%|percent\b)', sent)
            if not m:
                continue
            sp = spans[si]
            got.append(_f('percent-vs-percentage-points', _find(sp, sent), 'query', 'lookup', True,
                          f'a change in a percentage-valued quantity is stated as "{m.group(0)}", '
                          f'which reads as relative rather than as a difference',
                          'say percentage points if the figure is a difference of two percentages, '
                          'or say relative if it is a ratio'))
        return got

    # ---- [28] what the variability is over is never named ----------------
    def r_variability_population():
        if not whole_doc:
            return []
        has = re.search(r'\\pm|\u00b1|\bconfidence interval|\bCI\b|standard (deviation|error)|'
                        r'\bs\.?d\.?\b|\bSEM\b', src)
        if not has:
            return []
        named = re.search(r'\b(over|across|from|of)\s+(\d+|\w+)\s+'
                          r'(seeds?|runs?|folds?|replicates?|repetitions?|trials?|subjects?|'
                          r'participants?|samples?|bootstrap\w*|resamples?|splits?|models?)\b'
                          r'|\bbootstrap\w*|\bacross seeds\b|\bover seeds\b|\bn\s*=\s*\d+', body, re.I)
        if named:
            return []
        return [_f('variability-population-unnamed', has.start(), 'query', 'lookup', True,
                   'an error term is reported but the text never names what the variability is '
                   'over (seeds, runs, folds, subjects)',
                   'state the population the interval is computed over and how many units it has')]

    # ---- [51] the second term is not named locally ------------------------
    def r_pm_local_meaning():
        if not re.search(r'\\pm|\u00b1', src):
            return []
        names = re.compile(r'standard (deviation|error)|\bstd\b|\bs\.?d\.?\b|\bs\.?e\.?m?\.?\b|'
                           r'confidence interval|\bCI\b|\bIQR\b|inter[- ]?quartile|range', re.I)
        if not names.search(body):
            return []  # check.py's undefined-pm owns the document-level case
        got = []
        for env, s, e, inner in floats:
            if not re.search(r'\\pm|\u00b1', inner):
                continue
            if names.search(_plain(inner)):
                continue
            got.append(_f('pm-meaning-unnamed-in-float', s, 'query', 'free', False,
                          f'this {env} reports \\pm but neither its caption nor its header names '
                          f'the term as a deviation, an error or an interval half-width',
                          'name the second term in the caption or the column head'))
        return got

    # ---- [46] uncertainty carried to more than two significant digits ----
    def r_uncertainty_digits():
        got = []
        for sp in spans:
            if sp.kind == 'comment':
                continue
            hits = []
            for m in re.finditer(r'(?:\\pm|\u00b1)\s*\$?\s*(\d+(?:\.\d+)?)', sp.text):
                tok = m.group(1)
                if '.' not in tok:
                    continue          # an integer uncertainty is exact as printed
                if _sig_digits(tok) <= 2:
                    continue
                hits.append((sp.start + m.start(), tok))
            if not hits:
                continue
            worst = max(hits, key=lambda h: _sig_digits(h[1]))
            more = f' and {len(hits) - 1} more in the same block' if len(hits) > 1 else ''
            got.append(_f('uncertainty-excess-digits', hits[0][0], 'batch', 'free', False,
                          f'uncertainty printed to {_sig_digits(worst[1])} significant digits: '
                          f'\u00b1{worst[1]}{more}',
                          'round every uncertainty to at most two significant digits and round the '
                          'point estimate to match'))
        return got

    # ---- [53] a p value printed as zero -----------------------------------
    def r_p_zero():
        got = []
        for sp in spans:
            if sp.kind == 'comment':
                continue
            for m in re.finditer(r'(?<![a-zA-Z\\])[pP]\s*(?:=|<|\\leq|\\le|\u2264)\s*(0?\.0+|0)(?![\d.])',
                                 sp.text):
                if not _is_pvalue(src, sp.start + m.start()):
                    continue
                got.append(_f('p-value-reported-zero', sp.start + m.start(), 'batch', 'free', True,
                              f'p value printed as {m.group(0).strip()}, which asserts an '
                              f'impossible probability',
                              'report it as p < 0.001, or give the exact value to two significant digits'))
        return got

    # ---- [56] leading zero on p values is mixed within the document ------
    def r_p_leading_zero_mixed():
        with_zero, without = [], []
        for sp in spans:
            if sp.kind == 'comment':
                continue
            for m in _PVAL.finditer(sp.text):
                if not m.group(2) or not _is_pvalue(src, sp.start + m.start()):
                    continue
                v = m.group(3)
                if v.startswith('0.'):
                    with_zero.append(sp.start + m.start())
                elif v.startswith('.'):
                    without.append(sp.start + m.start())
        if with_zero and without:
            return [_f('p-leading-zero-mixed', min(with_zero + without), 'batch', 'free', False,
                       f'p values appear both with a leading zero ({len(with_zero)}x) and without '
                       f'it ({len(without)}x)',
                       'pick one form and apply it throughout; which one is the venue\u2019s call')]
        return []

    # ---- [56] leading zero against a recorded house style -----------------
    def r_p_leading_zero_style():
        if 'p_leading_zero' not in style:
            return []
        want = bool(style['p_leading_zero'])
        got = []
        for sp in spans:
            if sp.kind == 'comment':
                continue
            for m in _PVAL.finditer(sp.text):
                if not m.group(2) or not _is_pvalue(src, sp.start + m.start()):
                    continue
                v = m.group(3)
                has = v.startswith('0.')
                if v.startswith('.') or v.startswith('0.'):
                    if has != want:
                        got.append(_f('p-leading-zero-style', sp.start + m.start(), 'batch', 'free',
                                      False,
                                      f'{m.group(0).strip()} disagrees with the recorded convention '
                                      f'(leading zero: {want})',
                                      'write ' + ('0' + v if want else v.lstrip('0'))))
        return got

    # ---- [54] a result called not significant with no p value ------------
    def r_ns_without_p():
        got = []
        for sent, si, _ in sents:
            if not re.search(r'\bnot statistically significant\b|\bnot significant\b|'
                             r'\bnon-?significant\b|\bn\.s\.\b|\(NS\)', sent, re.I):
                continue
            if re.search(r'[pP]\s*(=|<|>|\u2264|\u2265)\s*\.?\d', sent):
                continue
            sp = spans[si]
            got.append(_f('not-significant-without-p', _find(sp, sent), 'query', 'lookup', False,
                          f'a comparison is called not significant with no p value in the sentence: '
                          f'{sent[:80]!r}',
                          'give the p value, or the effect size with its interval'))
        return got

    # ---- [55] a p value bounded at a threshold the scheme does not define -
    def r_p_odd_inequality():
        ok = {'0.05', '.05', '0.01', '.01', '0.001', '.001', '0.0001', '.0001',
              '0.1', '.1', '0.10', '.10', '0.99', '.99', '1'}
        got = []
        for sp in spans:
            if sp.kind == 'comment':
                continue
            for m in _PVAL.finditer(sp.text):
                opv = (m.group(2) or '')
                if not _is_pvalue(src, sp.start + m.start()):
                    continue
                if opv not in ('<', '>', '\\leq', '\\geq', '\\le', '\\ge', '\u2264', '\u2265'):
                    continue
                v = m.group(3)
                if v in ok or v.rstrip('0') in ok:
                    continue
                got.append(_f('p-inequality-nonstandard-bound', sp.start + m.start(), 'query',
                              'lookup', False,
                              f'p value bounded at a threshold no reporting scheme defines: '
                              f'{m.group(0).strip()}',
                              'report the exact p value, or bound it at the venue\u2019s threshold'))
        return got

    # ---- [52] a standard error used to describe variability --------------
    def r_se_as_variability():
        got = []
        for sent, si, _ in sents:
            if not re.search(r'\bstandard error\b|\bSEM\b|\bs\.e\.m\.\b|\bSE\b', sent):
                continue
            if not re.search(r'\bvariab\w+|\bspread\b|\bconsisten\w+|\bstab\w+|\bdispers\w+|'
                             r'\bhow much .* var\w+', sent, re.I):
                continue
            sp = spans[si]
            got.append(_f('standard-error-read-as-spread', _find(sp, sent), 'query', 'rework', True,
                          f'a standard error is used to describe how variable or consistent the data '
                          f'are: {sent[:80]!r}',
                          'report a standard deviation for spread; the standard error is the '
                          'precision of the mean'))
        return got

    # ---- [8] significance read off overlapping error bars ----------------
    def r_significance_from_bars():
        got = []
        for sent, si, _ in sents:
            if not re.search(r'error bars? (do not |don\u2019t |dont |do )?overlap|'
                             r'intervals? overlap|non-?overlapping (error )?(bars?|intervals?)|'
                             r'clearly separated', sent, re.I):
                continue
            if not re.search(r'signific\w+|\bdifference|\bdiffer\w*|distinguish\w*|'
                             r'\bno effect\b|equivalent|reliab\w+', sent, re.I):
                continue          # not a claim about significance, just a description
            if re.search(r'standard (deviation|error)|\bSEM\b|\bCI\b|confidence interval', sent) \
                    and re.search(r'\bn\s*=\s*\d+', sent):
                continue
            sp = spans[si]
            got.append(_f('significance-read-from-error-bars', _find(sp, sent), 'query', 'rework', True,
                          f'significance is read off whether error bars overlap: {sent[:80]!r}',
                          'name the bar type and n, and report the test the claim rests on'))
        return got

    # ---- [26] main results with no variability anywhere -------------------
    def r_no_variability():
        if not whole_doc:
            return []
        numeric = 0
        for s, e, bs, be, spec in tabs:
            if len(re.findall(r'\d+\.\d+', src[bs:be])) >= 4:
                numeric += 1
        if numeric < 2:
            return []
        if re.search(r'\\pm|\u00b1|confidence interval|\bCI\b|standard (deviation|error)|'
                     r'\bstd\b|\bs\.?d\.?\b|\bSEM\b|\bseeds?\b|significance|bootstrap|'
                     r'\bp\s*[<=]\s*\.?\d', src, re.I):
            return []
        return [_f('point-estimates-no-variability', tabs[0][0] if tabs else 0, 'query', 'rework', True,
                   f'{numeric} numeric result tables and no error bar, deviation, seed count or '
                   f'significance test anywhere in the source',
                   'report variability over repeated runs, or state that each number is one run')]

    # ---- [40] a column with no unit where sibling columns carry one ------
    def r_column_unit_missing():
        got = []
        for s, e, bs, be, spec in tabs:
            rows = _tab_rows(src[bs:be])
            head, hi = _head_row(rows)
            if not head or len(head) < 3:
                continue
            data = [_split_cells(r) for r, _ in rows[hi + 1:]]
            with_unit = sum(1 for h in head if _UNIT_IN_HEAD.search(_plain(h)))
            if with_unit < 1:
                continue
            for ci, h in enumerate(head):
                ht = _plain(h)
                if not ht or _UNIT_IN_HEAD.search(ht) or not _DIMENSIONAL.search(ht):
                    continue
                col = [r[ci] for r in data if len(r) > ci]
                if sum(1 for c in col if _cellnum(c)) < 2:
                    continue
                got.append(_f('table-column-unit-missing', s, 'query', 'lookup', True,
                              f'column head {ht[:40]!r} names a dimensional quantity with no unit '
                              f'while {with_unit} sibling column head(s) carry one',
                              'put the unit in the column head, in parentheses'))
        return got

    # ---- [42][39] a column of decimals with inconsistent precision -------
    def r_column_decimals():
        got = []
        for s, e, bs, be, spec in tabs:
            rows = _tab_rows(src[bs:be])
            head, hi = _head_row(rows)
            if not head:
                continue          # no head means no way to rule the column exact
            data = [_split_cells(r) for r, _ in rows[hi + 1:]
                    if '\\multicolumn' not in r and '\\multirow' not in r]
            if len(data) < 3:
                continue
            ncol = max(len(r) for r in data)
            for ci in range(1, ncol):   # column 0 is the condition column
                ht = _plain(head[ci]) if ci < len(head) else ''
                if _EXACT_HEAD.search(ht) or _SETTING_HEAD.search(ht):
                    continue          # exact values: a precision rule must not reach them
                cells = [r[ci] for r in data if len(r) > ci and _plain(r[ci]).strip()]
                if len(cells) < 3:
                    continue
                parsed = [_cellnum(c) for c in cells]
                if any(pv is None for pv in parsed):
                    continue          # not a pure numeric column
                if any(pv[1] == 0 for pv in parsed):
                    continue          # an integer in the column: the quantity may be exact
                if any(re.search(r'\d+\.\d+\.\d+', _plain(c)) for c in cells):
                    continue          # version strings
                vals = [float(re.sub(r'[^\d.]', '', _plain(c)) or 0) for c in cells]
                if vals == sorted(vals) or vals == sorted(vals, reverse=True):
                    continue          # a swept design grid, which is exact
                dp = {pv[1] for pv in parsed}
                if len(dp) > 1:
                    got.append(_f('table-column-decimals-inconsistent', s, 'batch', 'free', False,
                                  f'column {ci + 1} ({ht[:30]!r} in the head) mixes '
                                  f'{sorted(dp)} decimal places across {len(cells)} measured values',
                                  f'print every entry in the column to {max(dp)} decimal places'))
        return got

    # ---- [37] a rule between every pair of rows or columns ---------------
    def r_table_full_grid():
        got = []
        for s, e, bs, be, spec in tabs:
            cols = len(re.findall(r'[lcrpmbXS]', re.sub(r'\{[^{}]*\}|\[[^\]]*\]', '', spec)))
            bars = spec.count('|')
            rows = _tab_rows(src[bs:be])
            if bars >= 2 and cols and bars >= cols - 1:
                got.append(_f('table-vertical-rules', s, 'query', 'free', False,
                              f'tabular spec {spec[:40]!r} rules every column boundary',
                              'drop the vertical rules and separate groups with booktabs '
                              'horizontal rules instead'))
            elif len(rows) >= 4:
                inner = sum(1 for r, n in rows[1:-1] if n)
                if inner >= len(rows) - 2 and inner >= 2:
                    got.append(_f('table-horizontal-rules-every-row', s, 'query', 'free', False,
                                  f'a horizontal rule separates every pair of {len(rows)} rows',
                                  'keep a rule under the head row and above the last row only'))
        return got

    # ---- [14] a table whose first row is data, not column labels ---------
    def r_table_no_head():
        got = []
        for s, e, bs, be, spec in tabs:
            rows = _tab_rows(src[bs:be])
            if len(rows) < 3:
                continue
            first = _split_cells(rows[0][0])
            if len(first) < 3:
                continue
            nums = sum(1 for c in first if _cellnum(c))
            if nums >= len(first) - 1 and nums >= 2:
                got.append(_f('table-missing-column-labels', s, 'query', 'rework', True,
                              f'the first row of this tabular is {nums} numbers, so the columns '
                              f'carry no labels',
                              'add a head row naming each column and its unit'))
        return got

    # ---- [38] an empty cell in a numeric column --------------------------
    def r_table_empty_cell():
        got = []
        for s, e, bs, be, spec in tabs:
            btxt = src[bs:be]
            if '\\multirow' in btxt or '\\multicolumn' in btxt:
                continue          # a spanned cell makes column identity unreliable
            rows = _tab_rows(btxt)
            head, hi = _head_row(rows)
            if not head or len(rows) - hi < 4:
                continue
            data = [_split_cells(r) for r, _ in rows[hi + 1:]]
            ncol = max(len(r) for r in data) if data else 0
            for ci in range(1, ncol):
                col = [r[ci] for r in data if len(r) > ci]
                blanks = [i for i, c in enumerate(col) if not _plain(c).strip()]
                nums = sum(1 for c in col if _cellnum(c))
                if blanks and nums >= 2 and nums + len(blanks) == len(col):
                    got.append(_f('table-empty-cell', s, 'query', 'lookup', False,
                                  f'column {ci + 1} ({_plain(head[ci])[:25]!r}) has {len(blanks)} '
                                  f'empty cell(s) among {nums} numeric ones',
                                  'give the value, or mark it not measured with a dash the caption '
                                  'explains'))
        return got

    # ---- [6] caption placement is inconsistent between floats -----------
    def r_caption_position():
        pos = {'table': [], 'figure': []}
        for env, s, e, inner in floats:
            if env not in pos:
                continue
            cm = re.search(r'\\caption', inner)
            content = re.search(r'\\begin\s*\{tabular|\\includegraphics|'
                                r'\\begin\s*\{tikzpicture|\\input\s*\{|'
                                r'\\begin\s*\{tabu', inner)
            if not cm or not content:
                continue
            pos[env].append(('above' if cm.start() < content.start() else 'below', s))
        got = []
        for env, seen in pos.items():
            kinds = {k for k, _ in seen}
            if len(kinds) > 1:
                above = sum(1 for k, _ in seen if k == 'above')
                got.append(_f('caption-position-inconsistent', seen[0][1], 'batch', 'free', False,
                              f'{env} captions sit above in {above} float(s) and below in '
                              f'{len(seen) - above}',
                              'place every caption of this float type on the same side'))
        return got

    # ---- [18] caption longer than the recorded limit --------------------
    def r_caption_length():
        limit = style.get('caption_max_words')
        if not isinstance(limit, int):
            return []
        got = []
        for env, s, e, inner in floats:
            for coff, cbody in _captions(inner):
                n = len(re.findall(r"[\w'-]+", _plain(cbody)))
                if n > limit:
                    got.append(_f('caption-over-length', s + coff, 'query', 'rework', False,
                                  f'caption is {n} words against the recorded limit of {limit}',
                                  'move the method detail into the body text'))
        return got

    # ---- [21] a float that says it was taken from elsewhere, with no cite -
    def r_float_source():
        got = []
        for env, s, e, inner in floats:
            m = re.search(r'\b(adapted|reproduced|taken|redrawn|modified)\s+from\b|\bcourtesy of\b',
                          inner, re.I)
            if not m:
                continue
            if re.search(r'\\cite[a-zA-Z]*\s*(\[[^\]]*\])*\s*\{[^}]*\}', inner):
                continue
            got.append(_f('float-source-unattributed', s + m.start(), 'query', 'lookup', True,
                          f'{env} says its content is {m.group(0)!r} but carries no citation',
                          'cite the source in the caption and state the permission if one is needed'))
        return got

    # ---- [14][44] meaning that survives only in colour -------------------
    def r_colour_only():
        pat = re.compile(r'\b(red|blue|green|orange|purple|violet|yellow|brown|pink|cyan|magenta|'
                         r'grey|gray)\s+(line|lines|curve|curves|bar|bars|point|points|dot|dots|'
                         r'marker|markers|region|regions|area|shading|band)\b'
                         r'|\b(line|bar|point|marker|curve|dot)s?\s+colou?r\b'
                         r'|\bcolou?r\s+(marks|denotes|indicates|encodes|distinguishes|shows)\b'
                         r'|\bin\s+(red|blue|green|orange|purple)\b', re.I)
        got = []
        seen = set()
        for env, s, e, inner in floats:
            for coff, cbody in _captions(inner):
                m = pat.search(_plain(cbody))
                if m and s not in seen:
                    seen.add(s)
                    got.append(_f('colour-only-encoding', s + coff, 'query', 'rework', False,
                                  f'the caption keys the {env} on colour alone ({m.group(0)!r}), so '
                                  f'it fails in greyscale and for colour-blind readers',
                                  'add a redundant cue: marker shape, dash pattern or a direct label'))
        return got

    # ---- [33] a metric named with no implementation or version -----------
    def r_metric_implementation():
        if not (whole_doc and reports_results):
            return []
        pairs = [('BLEU', r'sacre-?bleu|signature|mteval|multi-bleu'),
                 ('ROUGE', r'rouge-?score|pyrouge|files2rouge|ROUGE-1\.5\.5'),
                 ('METEOR', r'meteor-?1\.[0-9]|nltk'),
                 ('BERTScore', r'roberta|deberta|bert-base|hash ?code|rescal'),
                 ('COMET', r'wmt\d\d|Unbabel|comet-?da|comet-?22'),
                 ('chrF', r'sacre-?bleu|chrf\+\+|word_order')]
        got = []
        for name, impl in pairs:
            if not re.search(r'\b' + name + r'\b', visible, re.I):
                continue
            if re.search(impl, src, re.I):
                continue
            m = re.search(r'\b' + name + r'\b', src, re.I)
            got.append(_f('metric-implementation-unnamed', m.start() if m else 0, 'query', 'lookup',
                          False,
                          f'{name} is reported with no implementation, version or parameter '
                          f'settings named',
                          f'name the {name} implementation and its version or signature'))
        return got

    # ---- [25][31] no hyperparameter values anywhere ----------------------
    def r_hyperparameters():
        if not (whole_doc and reports_results):
            return []
        if not re.search(r'\b(we (pre)?train|fine-?tun\w+|pretrain\w+|training run|we optimi[sz]e)\b',
                         body, re.I):
            return []
        if re.search(r'learning rate|\blr\b|batch size|\bepochs?\b|optimi[sz]er|\bAdamW?\b|'
                     r'weight decay|warm-?up|schedule', src, re.I):
            return []
        m = re.search(r'\b(we (pre)?train|fine-?tun)', src, re.I)
        return [_f('hyperparameters-absent', m.start() if m else 0, 'query', 'rework', True,
                   'models are trained but no learning rate, batch size, optimiser or schedule '
                   'appears anywhere in the source',
                   'give the training configuration, or point at the appendix table that holds it')]

    # ---- [32] split sizes never given -----------------------------------
    def r_split_sizes():
        if not (whole_doc and reports_results):
            return []
        hits = list(re.finditer(r'\b(training set|train split|test set|test split|validation set|'
                                r'dev set|held-?out set)\b', body, re.I))
        if not hits:
            return []
        for h in hits:
            w = body[max(0, h.start() - 250):h.end() + 250]
            if re.search(r'\b\d{1,3}(?:,\d{3})+\b|\b\d{3,}\b|\b\d+(?:\.\d+)?\s*[kKmM]\b|'
                         r'\b\d+\s*(?:examples|instances|sentences|documents|pairs|samples|'
                         r'items|questions|images|utterances|rows|articles)\b', w, re.I):
                return []
        m = re.search(re.escape(hits[0].group(0)), src, re.I)
        return [_f('split-sizes-absent', m.start() if m else 0, 'query', 'lookup', True,
                   'data splits are named but no split size or example count is reported',
                   'give the number of examples in each split and how the split was made')]

    # ---- [15] a beyond-the-state-of-the-art claim with no named search ---
    def r_sota_search():
        if not whole_doc:
            return []
        m = re.search(r'beyond the (current )?state of the art|no (existing|prior) (work|method|'
                      r'system) (has|can)\b|first (ever )?to\b', body, re.I)
        if not m:
            return []
        if re.search(r'systematic (review|search|sweep)|patent search|literature search|'
                     r'scoping review|we surveyed|our survey of|search of (the )?(literature|'
                     r'patents)', body, re.I):
            return []
        sp = next((s for s in text_spans if m.group(0)[:20].lower() in s.rendered.lower()), None)
        off = _find(sp, m.group(0)) if sp else 0
        return [_f('sota-claim-without-named-search', off, 'query', 'lookup', False,
                   f'a novelty claim ({m.group(0)[:40]!r}) rests on no named search of the '
                   f'literature or the patent record',
                   'name the search that establishes it: database, query, date, and what it returned')]

    # ---- [13] a summary that never states the outcome --------------------
    def r_abstract_outcome():
        if not whole_doc:
            return []
        blocks = _env_blocks(src, 'abstract')
        if not blocks:
            m = re.search(r'\\section\*?\{\s*(Abstract|Summary)\s*\}', src, re.I)
            if not m:
                return []
            nxt = re.search(r'\\section', src[m.end():])
            blocks = [(m.start(), m.end() + (nxt.start() if nxt else 600),
                       m.end(), m.end() + (nxt.start() if nxt else 600))]
        s, e, bs, be = blocks[0]
        txt = _plain(src[bs:be])
        if len(txt.split()) < 40:
            return []
        if re.search(r'\bwe (will |expect to |aim to )?(show|find|found|prove|demonstrate|'
                     r'report|obtain|observe|deliver|establish|produce|construct|build|measure[d]?|'
                     r'achieve)\b|\bresults?\b|\bfindings?\b|\byields?\b|\benables?\b|'
                     r'\bwill (deliver|produce|yield|establish|show|prove|demonstrate|make)\b|'
                     r'\bimpact\b|\bmatters?\b|\boutcome|\bwe (?:then )?(?:go on to )?\w+ that\b',
                     txt, re.I):
            return []
        return [_f('summary-states-no-outcome', bs, 'query', 'rework', True,
                   'the summary states the territory, the gap and the method but never says what '
                   'the work produces or why the outcome matters',
                   'add one sentence naming the expected result and one naming what it changes')]

    # ---- [24] a float the running text never points at ---------------------
    def r_float_never_referenced():
        keys = set()
        for m in _REF_KEY.finditer(src):
            if not shown(m.start()):
                continue
            for k in (m.group(1) or m.group(2) or '').split(','):
                if k.strip():
                    keys.add(k.strip())
        if len(keys) < 2:
            return []          # too few cross-references to conclude anything
        if len(_HARDCODED_FLOAT_NUM.findall(body)) >= 2:
            return []          # the document numbers its floats by hand in the prose
        got = []
        for env, s0, e, inner in floats:
            labs = [l for l in re.findall(r'\\label\s*\{([^}]*)\}', inner) if l.strip()]
            if not labs:
                continue       # an unlabelled float may still be discussed in place
            if any(l.strip() in keys for l in labs):
                continue
            got.append(_f('float-never-referenced', s0, 'query', 'rework', False,
                          f'{env} labelled {labs[0]!r} is numbered but no \\ref anywhere points at '
                          f'it, so the reader is never sent to it',
                          'reference it from the sentence that needs it, or drop the float'))
        return got

    # ---- [12] a plot shipped as a bitmap rather than as vector -------------
    def r_figure_raster():
        got = []
        for env, s0, e, inner in floats:
            for m in _GRAPHICS.finditer(src[s0:e]):
                if not shown(s0 + m.start()):
                    continue   # an \\includegraphics the author has commented out
                name = m.group(1)
                ext = pathlib.Path(name).suffix.lower()
                if ext not in _RASTER_EXT:
                    continue
                if _PHOTO_NAME.search(name):
                    continue   # a photograph has no vector original to export
                got.append(_f('figure-raster-not-vector', s0 + m.start(), 'batch', 'rework', False,
                              f'{env} includes {name!r}, a bitmap, so its axis and tick text is '
                              f'resampled rather than set in vector outlines',
                              'export the figure as PDF or another vector format with the fonts '
                              'embedded'))
        return got

    # ---- [16] typeset material shipped as a picture -----------------------
    def r_figure_is_table_image():
        got = []
        for env, s0, e, inner in floats:
            for m in _GRAPHICS.finditer(src[s0:e]):
                if not shown(s0 + m.start()):
                    continue
                name = pathlib.Path(m.group(1)).stem
                hit = _TABLE_IMAGE.search(name)
                if not hit:
                    continue
                got.append(_f('figure-reproduces-typeset-material', s0 + m.start(), 'query',
                              'rework', False,
                              f'{env} includes {m.group(1)!r}, whose name says it holds a '
                              f'{hit.group(1).lower()}, so text is reproduced as an image the '
                              f'reader cannot search, select or read at body size',
                              'typeset the material as a real table or listing instead of '
                              'including a picture of it'))
        return got

    # ---- [39] decimals that cannot line up in a centred or left column ----
    def r_table_decimals_unaligned():
        got = []
        for s0, e, bs, be, spec in tabs:
            btxt = src[bs:be]
            if '\\phantom' in btxt or '\\hphantom' in btxt:
                continue          # the author is aligning the column by hand
            letters = _spec_letters(spec)
            rows = _tab_rows(btxt)
            head, hi = _head_row(rows)
            if not head:
                continue
            data = [_split_cells(r) for r, _ in rows[hi + 1:]
                    if '\\multicolumn' not in r and '\\multirow' not in r]
            if len(data) < 3:
                continue
            ncol = max(len(r) for r in data)
            for ci in range(ncol):
                if ci >= len(letters) or letters[ci] not in 'lcpmbX':
                    continue      # r lines the digits up, S lines the point up
                ht = _plain(head[ci]) if ci < len(head) else ''
                if _EXACT_HEAD.search(ht) or _SETTING_HEAD.search(ht):
                    continue
                cells = [r[ci] for r in data if len(r) > ci and _plain(r[ci]).strip()]
                if len(cells) < 3:
                    continue
                parsed = [_cellnum(c) for c in cells]
                if any(v is None for v in parsed):
                    continue
                decs = {v[1] for v in parsed}
                ints = {v[0] for v in parsed}
                if len(decs) != 1 or 0 in decs or len(ints) < 2:
                    continue      # mixed decimal counts are a precision fault, reported apart
                got.append(_f('table-decimals-unaligned', s0, 'batch', 'free', False,
                              f'column {ci + 1} ({ht[:30]!r} in the head) is set {letters[ci]!r} '
                              f'and holds decimals of {sorted(ints)} integer digits, so the '
                              f'decimal points do not line up',
                              'align the column on the decimal point, with an S column or by '
                              'padding to a common width'))
        return got

    # ---- [11] a significance claim with no test named ---------------------
    def r_test_unnamed():
        if not whole_doc:
            return []
        trig = re.search(r'statistically significant|significance test|tests? of significance|'
                         r'\bsignificant(?:ly)? (?:better|worse|higher|lower|different|'
                         r'improve\w*|outperform\w*)\b', body, re.I)
        off = None
        if trig:
            sp = next((x for x in text_spans if trig.group(0)[:18].lower() in x.rendered.lower()),
                      None)
            off = _find(sp, trig.group(0)) if sp else 0
        else:
            for sp in spans:
                if sp.kind != 'text':
                    continue
                for m in _PVAL.finditer(sp.text):
                    if m.group(2) and _is_pvalue(src, sp.start + m.start()):
                        off = sp.start + m.start()
                        break
                if off is not None:
                    break
        if off is None:
            return []
        if _TESTNAME.search(src):
            return []
        return [_f('statistical-test-unnamed', off, 'query', 'lookup', True,
                   'the document claims statistical significance but never names the test it '
                   'rests on',
                   'name the test, its assumptions and what it was applied to')]

    # ---- [29] how each reported number was selected ----------------------
    def r_selection_rule():
        if not (whole_doc and reports_results):
            return []
        if _SELECTION_RULE.search(body) or re.search(r'\\pm|\u00b1', src):
            return []
        return [_f('number-selection-rule-unstated', tabs[0][0] if tabs else 0, 'query', 'lookup',
                   True,
                   f'{numeric_tabs} numeric result tables and the text never says whether an entry '
                   f'is one run, a mean, a median or the best of several',
                   'state the selection rule once and apply it to every table')]

    # ---- [9] a summary with an error bar over three units or fewer -------
    def r_error_bar_tiny_n():
        got = []
        for env, s0, e, inner in floats:
            whole = ''.join(src[a:b] for a, b in [(s0, e)])
            if not re.search(r'\\pm|\u00b1|error bars?|confidence interval|\bCI\b|whisker', whole):
                continue
            m = _TINY_N.search(_plain(whole))
            if not m:
                continue
            at = whole.find(m.group(0))
            if at >= 0 and not shown(s0 + at):
                continue
            got.append(_f('error-bar-over-tiny-n', s0 + max(at, 0), 'query', 'rework', False,
                          f'{env} summarises {m.group(0)!r} with an error term, which describes a '
                          f'spread three observations cannot support',
                          'plot the individual observations instead of a summary and its bar'))
        return got

    # ---- [60][41] a source-drawn plot whose axis names no quantity -------
    def r_plot_axis_name():
        if '\\pgfplotsset' in src:
            return []          # a global style may set the labels for every axis
        got = []
        for env in _AXIS_ENVS:
            for s0, e, bs, be in _env_blocks(src, env):
                if not live(s0):
                    continue
                opts, _ = _opts(src, bs)
                for ax in ('x', 'y'):
                    if re.search(r'\b' + ax + r'label\s*=', opts) or \
                            re.search(r'\b' + ax + r'label\s*=', src[bs:be]):
                        continue
                    got.append(_f('plot-axis-name-missing', s0, 'query', 'rework', True,
                                  f'the {ax} axis of this {env} carries no label, so the quantity '
                                  f'it plots is unnamed',
                                  f'set {ax}label to the quantity, with its unit when it has one'))
        return got

    # ---- [60][41] a source-drawn axis of a dimensional quantity, no unit --
    def r_plot_axis_unit():
        if '\\pgfplotsset' in src:
            return []
        got = []
        for env in _AXIS_ENVS:
            for s0, e, bs, be in _env_blocks(src, env):
                if not live(s0):
                    continue
                opts, _ = _opts(src, bs)
                for m in re.finditer(r'\b([xy])label\s*=\s*', opts):
                    lab, _ = _arg(opts, m.end())
                    if not lab:
                        mm = re.match(r'([^,\]]+)', opts[m.end():])
                        lab = mm.group(1) if mm else ''
                    ltxt = _plain(lab)
                    if not ltxt or _UNIT_IN_HEAD.search(ltxt) or not _DIMENSIONAL.search(ltxt):
                        continue
                    got.append(_f('plot-axis-unit-missing', s0, 'query', 'lookup', True,
                                  f'the {m.group(1)} axis label {ltxt[:40]!r} names a dimensional '
                                  f'quantity with no unit',
                                  'add the unit to the axis label, in parentheses'))
        return got

    # ---- [0][10] gridlines drawn at the weight of the data ---------------
    def r_plot_grid_ornament():
        if '\\pgfplotsset' in src:
            return []
        got = []
        for env in _AXIS_ENVS:
            for s0, e, bs, be in _env_blocks(src, env):
                if not live(s0):
                    continue
                opts, _ = _opts(src, bs)
                if not re.search(r'\bgrid\s*=\s*(both|major|minor|true)\b|(?:^|,)\s*grid\s*(?:,|$)',
                                 opts):
                    continue
                if re.search(r'(?:major |minor |)grid style\s*=', opts + src[bs:be]):
                    continue
                got.append(_f('plot-gridlines-not-lightened', s0, 'batch', 'free', False,
                              f'this {env} turns gridlines on and sets no grid style, so they are '
                              f'drawn at the default weight and compete with the data marks',
                              'set a light grid style, or drop the grid unless the reader has to '
                              'read absolute values off it'))
        return got

    # ---- [43] a rainbow colour map for a continuous quantity -------------
    def r_plot_rainbow():
        got = []
        for s0, e, bs, be in _env_blocks(src, 'tikzpicture'):
            if not live(s0):
                continue
            m = re.search(r'colormap\s*/\s*(jet|hsv|rainbow)\b|colormap name\s*=\s*\{?(jet|hsv|'
                          r'rainbow)\b|colormap\s*=\s*\{\s*(jet|rainbow)\b', src[bs:be], re.I)
            if not m:
                continue
            got.append(_f('plot-rainbow-colormap', s0 + m.start(), 'batch', 'rework', False,
                          f'a continuous quantity is coloured with the {m.group(0)!r} map, whose '
                          f'lightness is not monotone, so equal steps in the value read as unequal',
                          'use a perceptually uniform map such as viridis'))
        return got

    # ---- [1] depth on a chart of one value per category ------------------
    def r_plot_depth():
        got = []
        for s0, e, bs, be in _env_blocks(src, 'tikzpicture'):
            if not live(s0):
                continue
            inner = src[bs:be]
            m = re.search(r'\bbar3d\b|\bpie3d\b|\b3d\s*=\s*true\b|\bexplode\b.*\bpie\b', inner, re.I)
            if not m and re.search(r'\bybar\b|\bxbar\b', inner) and re.search(r'\bview\s*=', inner):
                m = re.search(r'\bview\s*=', inner)
            if not m:
                continue
            got.append(_f('plot-depth-effect', s0 + m.start(), 'batch', 'rework', True,
                          f'a categorical chart is drawn with a depth effect ({m.group(0)!r}), '
                          f'which shades and foreshortens the bars away from their values',
                          'redraw flat, with a zero baseline and one bar per category'))
        return got

    # ---- [17] work-plan tasks with no quantity attached -----------------
    def r_workplan_quantified():
        heads = [m for m in _TASK_HEAD.finditer(src) if live(m.start())]
        if len(heads) < 3 or not _WORKPLAN_HINT.search(src):
            return []
        bare = []
        for i, m in enumerate(heads):
            stop = heads[i + 1].start() if i + 1 < len(heads) else min(len(src), m.end() + 3500)
            if not _QUANTIFIED.search(_plain(src[m.end():stop])):
                bare.append(m.group(1).strip())
        if len(bare) < max(3, (2 * len(heads)) // 3):
            return []
        return [_f('workplan-tasks-unquantified', heads[0].start(), 'query', 'rework', True,
                   f'{len(bare)} of {len(heads)} work-plan items ({", ".join(bare[:5])}'
                   f'{" ..." if len(bare) > 5 else ""}) describe activity with no number of runs, '
                   f'models, measurements or outputs attached',
                   'give each item a countable target, so a reviewer can see when it is done')]

    # ---- [17] work-plan tasks with nobody named ------------------------
    def r_workplan_owner():
        heads = [m for m in _TASK_HEAD.finditer(src) if live(m.start())]
        if len(heads) < 3 or not _WORKPLAN_HINT.search(src):
            return []
        bare = []
        for i, m in enumerate(heads):
            stop = heads[i + 1].start() if i + 1 < len(heads) else min(len(src), m.end() + 3500)
            if not _OWNER.search(_plain(src[m.end():stop])):
                bare.append(m.group(1).strip())
        if len(bare) < max(3, (2 * len(heads)) // 3):
            return []

    for fn in (r_float_missing_caption, r_caption_outside_float, r_caption_not_standalone,
               r_result_without_float_ref, r_percent_vs_points,
               r_variability_population, r_pm_local_meaning, r_uncertainty_digits,
               r_p_zero, r_p_leading_zero_mixed, r_p_leading_zero_style, r_ns_without_p,
               r_p_odd_inequality, r_se_as_variability, r_significance_from_bars,
               r_no_variability, r_column_unit_missing, r_column_decimals, r_table_full_grid,
               r_table_no_head, r_table_empty_cell, r_caption_position, r_caption_length,
               r_float_source, r_colour_only, r_metric_implementation, r_hyperparameters,
               r_split_sizes, r_sota_search, r_abstract_outcome,
               r_float_never_referenced, r_figure_raster, r_figure_is_table_image,
               r_table_decimals_unaligned, r_test_unnamed, r_selection_rule,
               r_error_bar_tiny_n, r_plot_axis_name, r_plot_axis_unit, r_plot_grid_ornament,
               r_plot_rainbow, r_plot_depth, r_workplan_quantified, r_workplan_owner):
        add(fn)
    out.sort(key=lambda d: d['offset'])
    return out


# --------------------------------------------------------------------------- cli
def _lineof(src, off):
    return src.count('\n', 0, off) + 1


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    stage = 'submission' if '--submission' in sys.argv else 'draft'
    total = collections.Counter()
    for p in args:
        src = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        spans = ex.extract(src)
        found = checks(src, spans, {'stage': stage, 'path': p, 'style': {}})
        for d in found:
            total[d['rule']] += 1
            print(f"{pathlib.Path(p).name}:{_lineof(src, d['offset'])}  "
                  f"[{d['tier']}/{d['cost']}{'/BLOCKS' if d['blocks'] else ''}]  "
                  f"{d['rule']}: {d['text']}")
            if d['fix']:
                print(f"    -> {d['fix']}")
    print(f"\n--- {sum(total.values())} findings ---")
    for r, c in total.most_common():
        print(f'  {c:4d}  {r}')
