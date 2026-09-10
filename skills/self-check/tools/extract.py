#!/usr/bin/env python3
"""Source-mapped LaTeX extraction.

Yields rendered text units with byte offsets into the original source, so a finding
can be written back to an exact position. Math, floats, tables and verbatim are MASKED
rather than deleted, which keeps offsets aligned.

Round-trip contract: reassemble(extract(src)) == src, byte for byte, and every byte of
the source belongs to exactly one span.

Classification runs in layers, and the order is the whole point. An audit found five ways
a single stray character made real prose invisible to every check, all of them caused by
one pass matching inside material a later pass owns:

  1. Verbatim material is settled FIRST. Inside `\\verb|%|` the per-cent sign is not a
     comment and inside `\\verb|$|` the dollar is not math. Both used to swallow the rest
     of the sentence.
  2. Comments are settled SECOND, over verbatim-blanked source, so a `%` in a listing
     no longer hides the prose after the listing.
  3. Environments and math are matched over comment-blanked source, so a commented-out
     `\\begin{figure}` opens nothing and a commented-out `\\end{figure}` closes nothing.
     A commented `\\begin` used to make one comment span swallow a page of live prose.
  4. A verbatim-like environment with no `\\end` runs to end of file rather than not
     matching, so an unclosed `\\begin{comment}` hides its body instead of publishing it.
  5. Regions of different kinds are never merged into one another's kind. A region inside
     another is absorbed by it. A partial overlap is clipped so both survive.
"""
import re
from dataclasses import dataclass, field

# Environments whose body LaTeX does not tokenise. Nothing inside them is a comment, math
# or a macro, so they must be settled before the comment and math passes.
LITERAL_ENVS = ('verbatim', 'Verbatim', 'BVerbatim', 'lstlisting', 'listing', 'minted',
                'comment')

MASK_ENVS = ('equation', 'align', 'gather', 'multline', 'eqnarray', 'array',
             'tabular', 'table', 'figure', 'verbatim', 'Verbatim', 'BVerbatim',
             'lstlisting', 'listing', 'minted', 'algorithm', 'algorithmic', 'tikzpicture',
             'comment', 'wrapfigure', 'wraptable', 'sidewaystable', 'longtable')

# Review annotations are author-to-author traffic, not the paper's prose. Rendering their
# bodies as text makes every prose check read co-authors' notes as if they were the text —
# which produced twelve false positives on one real paper before this was masked.
ANNOT_MACROS = ('lc', 'ym', 'wzm', 'oa', 'sy', 'yp', 'ft', 'temp', 'todo', 'note',
                'comment', 'uriel', 'adam', 'bob', 'instruction', 'showinstructions',
                'ercscore', 'ReviewOld', 'biblegend', 'cready')

COMMENT_RE = re.compile(r'(?<!\\)%[^\n]*')

# \verb takes any non-letter as its delimiter and may not cross a line end. \lstinline
# accepts an option list and either a delimiter or a brace group.
_INLINE_VERB_RE = re.compile(r'\\(?:verb|lstinline)\*?[ \t]*(\[[^\]\n]*\])?([^A-Za-z\s*])')

# Rendered heading terminator. A heading carries no full stop of its own, so without this
# the title and the first sentence of the section become one fabricated sentence.
_HEADING_RE = re.compile(r'\\(?:sub){0,2}section\*?\s*(?:\[[^\]]*\])?\s*\{([^{}]*)\}')
_PARA_RE = re.compile(r'\n[ \t]*\n')
_WORDISH = re.compile(r'[A-Za-z0-9]')


@dataclass
class Span:
    start: int          # byte offset in source
    end: int
    kind: str           # 'text' | 'mask' | 'comment' | 'annot'
    text: str           # source slice, verbatim
    rendered: str = ''  # what a reader sees ('' for mask/comment/annot)

    @property
    def live(self) -> str:
        """`text` with line comments removed.

        A comment inside a float or math environment is swallowed by that environment's
        mask span, so a module reading `.text` sees commented-out content as live — two
        commented `\\includegraphics` read as real figures on a real paper. Read `.live`
        whenever you are asking what the document actually contains.
        """
        # The lookbehind must be for ONE backslash. Written as two it matched an escaped
        # `\%` and deleted the rest of the line. This has now been reverted twice by
        # rewrites of this file, so the assertion below pins it.
        return re.sub(r'(?<!\\)%[^\n]*', '', self.text)


def _match_brace(src: str, i: int) -> int:
    """Index just past the brace group opening at `i`, honouring nesting and escapes."""
    if i >= len(src) or src[i] != '{':
        return -1
    depth = 0
    j = i
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
                return j + 1
        j += 1
    return -1


def _blank(src: str, regions) -> str:
    """`src` with every region's characters replaced by spaces, newlines kept.

    Length and every line break are preserved, so an offset found in the blanked copy is
    the same offset in the original. This is how a later pass is stopped from matching
    inside material an earlier pass already owns.
    """
    if not regions:
        return src
    out, pos = [], 0
    for s, e in sorted((r[0], r[1]) for r in regions):
        s = max(s, pos)
        if e <= s:
            continue
        out.append(src[pos:s])
        out.append(re.sub(r'[^\n]', ' ', src[s:e]))
        pos = e
    out.append(src[pos:])
    return ''.join(out)


def _eol(src: str, i: int) -> int:
    j = src.find('\n', i)
    return len(src) if j == -1 else j


def _inline_verbatim(src: str):
    """`\\verb<c>…<c>` and `\\lstinline` spans, delimiter included."""
    regions = []
    for m in _INLINE_VERB_RE.finditer(src):
        d = m.group(2)
        if d == '{':
            end = _match_brace(src, m.end() - 1)
            if end == -1:
                end = _eol(src, m.end())
        else:
            j = src.find(d, m.end())
            # A \verb argument cannot span a line end. An unterminated one is a defect, and
            # masking to the line end keeps its stray % or $ from eating the next paragraph.
            end = (j + 1) if (j != -1 and '\n' not in src[m.end():j]) else _eol(src, m.end())
        regions.append((m.start(), end, 'mask'))
    return regions


def _literal_envs(src: str, provisional_comments):
    """Verbatim-like environment spans, matched without comment semantics inside.

    The body is not tokenised, so the FIRST `\\end{env}` closes it even on a line that
    starts with `%`. A `\\begin` that is itself commented out opens nothing, and an
    environment that is never closed runs to end of file — the body is hidden material,
    and publishing it as prose is the worse error.
    """
    regions = []
    for env in LITERAL_ENVS:
        for m in re.finditer(r'\\begin\{' + env + r'\*?\}', src):
            if any(a <= m.start() < b for a, b in provisional_comments):
                continue
            e = re.compile(r'\\end\{' + env + r'\*?\}').search(src, m.end())
            regions.append((m.start(), e.end() if e else len(src), 'mask'))
    return regions


def _mask_regions(src: str):
    """Offsets to mask: verbatim, comments, math, heavy environments and annotations."""
    verb = _inline_verbatim(src)
    b1 = _blank(src, verb)
    prov = [(m.start(), m.end()) for m in COMMENT_RE.finditer(b1)]
    lit = _literal_envs(b1, prov)
    b2 = _blank(src, verb + lit)
    comments = [(m.start(), m.end(), 'comment') for m in COMMENT_RE.finditer(b2)]
    # Everything below is matched over source with verbatim and comments blanked out, so no
    # commented-out delimiter can open or close anything.
    b3 = _blank(src, verb + lit + comments)

    regions = list(verb) + list(lit) + list(comments)
    for env in MASK_ENVS:
        if env in LITERAL_ENVS:
            continue
        for m in re.finditer(r'\\begin\{' + env + r'\*?\}', b3):
            e = re.compile(r'\\end\{' + env + r'\*?\}').search(b3, m.end())
            if e is None:
                # No live \end. A commented-out one still marks where the author meant the
                # float to stop, which is better than reading its body as prose.
                e = re.compile(r'\\end\{' + env + r'\*?\}').search(src, m.end())
                if e is None:
                    continue
            regions.append((m.start(), e.end(), 'mask'))
    for m in re.finditer(r'(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$[^$\n]*?(?<!\\)\$', b3, re.S):
        regions.append((m.start(), m.end(), 'mask'))
    for m in re.finditer(r'\\\[.*?\\\]', b3, re.S):
        regions.append((m.start(), m.end(), 'mask'))
    for name in ANNOT_MACROS:
        for m in re.finditer(r'\\' + name + r'\b\s*\{', b3, re.I):
            end = _match_brace(b3, m.end() - 1)
            if end <= m.start():
                # An unbalanced brace in a co-author's note is a defect in its own right —
                # `surviving-annotation` reports it. Dropping the region instead of masking
                # it republished the note body as prose, which is the twelve-false-positive
                # regression this masking exists to prevent. Mask the line.
                end = _eol(src, m.end())
            regions.append((m.start(), end, 'annot'))

    # Container first, so a region inside another is absorbed rather than merged.
    regions.sort(key=lambda r: (r[0], -r[1]))
    merged = []
    for s, e, k in regions:
        if not merged or s >= merged[-1][1]:
            merged.append((s, e, k))
        elif e <= merged[-1][1]:
            continue                                  # inside: the container owns it
        elif k == merged[-1][2]:
            merged[-1] = (merged[-1][0], e, k)        # same kind: one region
        else:
            merged.append((merged[-1][1], e, k))      # different kind: clip, keep both
    return merged


def extract(src: str) -> list:
    """Partition the source into spans covering every byte exactly once."""
    spans, pos = [], 0
    for s, e, kind in _mask_regions(src):
        if s > pos:
            chunk = src[pos:s]
            spans.append(Span(pos, s, 'text', chunk, _render(chunk)))
        spans.append(Span(s, e, kind, src[s:e]))
        pos = e
    if pos < len(src):
        chunk = src[pos:]
        spans.append(Span(pos, len(src), 'text', chunk, _render(chunk)))
    return spans


def _end_heading(m):
    title = m.group(1).strip()
    if not title:
        return ' '
    return title + ('' if title[-1] in '.!?:;' else '.') + ' '


def _render(chunk: str) -> str:
    """Best-effort reader-visible text. Offsets are NOT preserved inside a span."""
    t = re.sub(r'\\cite[a-zA-Z]*\s*(\[[^\]]*\])*\s*\{[^}]*\}', '\u2020', chunk)
    t = re.sub(r'\\(ref|autoref|cref|Cref|eqref|label)\s*\{[^}]*\}', '\u2021', t)
    for _ in range(3):  # unwrap nested single-arg macros
        # A heading closes a sentence. Run before the generic unwrap, and once per round so
        # that a title holding its own macro is terminated after that macro is flattened.
        t = _HEADING_RE.sub(_end_heading, t)
        t = re.sub(r'\\[a-zA-Z@]+\s*(\[[^\]]*\])?\s*\{([^{}]*)\}', r'\2', t)
    t = re.sub(r'\\[a-zA-Z@]+\s*', ' ', t)
    t = re.sub(r'[{}]', '', t)
    return t


def reassemble(spans: list) -> str:
    return ''.join(s.text for s in spans)


def sentences(spans: list):
    """(rendered_sentence, span_index, char_offset_within_span) triples.

    A blank line ends a sentence whatever punctuation precedes it. Splitting on `.!?`
    alone glued a heading to the first sentence of its section and ran sentence-pair rules
    across a paragraph break, so every rule reading two neighbours saw a join no reader
    sees.
    """
    out = []
    for i, sp in enumerate(spans):
        if sp.kind != 'text' or not sp.rendered.strip():
            continue
        r = sp.rendered
        start = 0
        bounds = []
        for m in _PARA_RE.finditer(r):
            bounds.append((start, m.start()))
            start = m.end()
        bounds.append((start, len(r)))
        for a, b in bounds:
            off = a
            for part in re.split(r'(?<=[.!?])\s+', r[a:b]):
                # A fragment with no letter or digit is not a sentence. Terminating a
                # heading leaves the `\label` that follows it alone on its own fragment,
                # and a lone reference marker is not prose any rule should read.
                if _WORDISH.search(part):
                    out.append((part.strip(), i, off))
                off += len(part) + 1
    return out


def _selftest():
    """Guard the two invariants that rewrites of this file have broken before.

    `Span.live` must keep an escaped `\\%` and must strip a real comment. Both regressed
    once each and were caught only by an adversarial audit.
    """
    a = Span(0, 0, 'text', 'We gained 4\\% overall. KEEPME')
    assert 'KEEPME' in a.live, 'Span.live deletes text after an escaped percent'
    b = Span(0, 0, 'text', 'body % DROPME')
    assert 'DROPME' not in b.live, 'Span.live fails to strip a real comment'


_selftest()
