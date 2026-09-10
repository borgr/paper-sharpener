# Check module interface

Every check module lives in this directory as `checks_<family>.py` and exports one function.

```python
def checks(src: str, spans: list, ctx: dict) -> list[dict]:
    """Return a list of findings. Never raise — a broken check must return []."""
```

## Inputs

- `src` — the raw `.tex` source, exactly as on disk. Offsets you report index into this.
- `spans` — output of `extract.extract(src)`. Each span has `.start`, `.end` (byte offsets
  into `src`), `.kind` in `text|mask|comment`, `.text` (verbatim source slice) and
  `.rendered` (reader-visible text, empty for mask and comment).
  Every byte of `src` belongs to exactly one span. Math, floats, tables and verbatim are
  `mask`. Comments are `comment`. Only `text` spans hold prose.
- `ctx` — `{'stage': 'draft'|'submission', 'path': str, 'style': dict}`.
  `stage` matters. Scaffolding rules (TODOs, placeholders, review markers) must only fire
  when `stage == 'submission'`, because a draft is supposed to contain them.
  `style` holds house-style decisions, for example `{'serial_comma': True, 'p_leading_zero': False}`.
  A rule whose correct output depends on house style must read `style` and return [] if the
  needed key is absent.

## Output — one dict per finding

```python
{
  'rule':   'kebab-case-id',      # stable, unique across all modules
  'family': 'integrity',          # one of the seven families
  'offset':  12345,               # byte offset into src, or 0 if not localisable
  'tier':   'query',              # silent | batch | query
  'cost':   'free',               # free | lookup | rework
  'blocks':  True,                # would a reviewer require this fixed before acceptance
  'text':   'what is wrong, one line, name the actual thing found',
  'fix':    'what to do, one line — or "" when the rule only reports',
}
```

## Hard rules, from the audits

1. **Only report what you can detect with certainty.** A false positive costs more than a
   miss, because it trains the reader to ignore findings.
2. **Never emit a rule that deletes or weakens a hedge**, an intensifier on a graded
   absolute ("almost all"), a tentative modal, or a first-person stance marker. Those raise
   claim strength past the evidence. Report them, propose nothing, tier `query`.
3. **Never emit a rounding or precision rule that can reach an exact value** — a count, a
   seed, a byte or parameter size, a hash, an identifier, a step index.
4. **Never bundle.** If your test matches two situations whose correct fixes differ, that is
   two checks with two rule ids.
5. **`tier: 'silent'` requires exactly one correct output.** Almost nothing qualifies. If
   detecting the problem does not tell you its unique repair, the tier is `query`.
6. **Read prose from `.rendered` on `text` spans only.** Never regex prose out of raw `src`,
   or you will match inside math, comments and macro arguments.
7. Report offsets into `src`. To locate a finding from rendered text, use the span's
   `.start` plus your own search within `span.text`.

8. **Read `span.live`, never `span.text`, when asking what the document contains.** A comment
   nested inside a float or math environment is swallowed by that environment's mask span, so
   `.text` shows commented-out content as if it were live. Two commented-out
   `\includegraphics` read as real figures on a real paper before this existed. `.live` is
   `.text` with line comments stripped. Use `.text` only when you genuinely want the bytes,
   for instance to locate an offset.

9. **Verify adjacent-word matches against the source, not only `.rendered`.** Macro unwrapping
   turns `\end{minipage}\begin{minipage}` into the text "minipage minipage", so a
   doubled-word check that trusts `.rendered` manufactures its own hits.

10. **A rule that reads one sentence in isolation can miss that a neighbour did the work.** A
    concessive such as "regardless of whether the outcome is one explanation or several" is
    itself the conditioning, so an unconditional verb after it is correct. Check the window,
    not the sentence.

11. **Examples in a rule are not a licence to generalise.** A rule evidenced by three
    relational heads was extended to forty and produced 63 findings on three documents.
    Implement the examples given.

