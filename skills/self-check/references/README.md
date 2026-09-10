# self-check

Checks a LaTeX paper or grant proposal against itself and leaves sited queries. Reports
rather than rewrites, because of a measured finding rather than caution — of 541 gathered
rules, five have exactly one correct output.

See `SKILL.md` for how to use it. This file records what is here and how it was built.

## Layout

```
SKILL.md            how to run it, the pass order, the guards, the budget
CHECKS_API.md       the contract every check module implements
extract.py          source-mapped LaTeX extraction; masks math/floats/comments/annotations
docset.py           resolves which .tex files a document actually builds from
check.py            built-in checks; stage-gates scaffolding rules
checks_*.py         one module per family, 7 modules
run.py              loads every module, project-scope checks, cost normalisation
teach.py            attaches the mechanism once per family, then fades
annotate.py         writes findings into the .tex as addressed notes; sweeps them back out
accuracy.py         measures rules against real revision history (read the docstring first)
mine_fixtures.py    finds commits where a human repaired a flagged defect
fixtures/           mined fix events, 34 across two histories
../ledger/          541 rules with sources, SUMMARY.md, and nine family pages
```

## Design decisions and what forced them

**Reports, does not rewrite.** Six independent audits found the silent tier nearly empty. The
repair for almost every real defect lives outside the manuscript — in the analysis output,
the figure source, the bibliography, or the author's intent.

**Stage-gated.** The same paper yields 52 findings mid-draft and 176 at submission. Review
markers and TODOs are supposed to be present while writing. Two rules looked like noise
because their density grew during drafting, until it was clear they were being measured at
the wrong moment in the document's life.

**Scoped to the built document.** Globbing swept in scratch files and abandoned variants,
which is where most remaining noise lived.

**Annotation bodies are masked.** Rendering `\lc{...}` as prose made every check in every
module audit co-authors' notes as if they were the paper. One check produced twelve false
positives before this was fixed centrally.

**Costs are normalised.** A finding whose fix begins "Confirm…" is free by construction. Two
cohesion rules were labelled `rework` because their importance was mistaken for their cost,
which is exactly what defeats a triage.

**Counter-cases execute where they can.** A counter-case that only gets printed is advice the
reader pays to apply. The hyphenation check tests grammatical position and the clipping check
consults a term-of-art list, which removed two false positives on a real proposal.

## Rules cut, and why

`space-before-cite` — 34 instances per 10k words, flat across 824 commits of two documents,
and plainly visible in every line the author touched. High visibility plus sustained
indifference is the one case where inaction is informative.

`undefined-acronym` on established forms — fired on MIT, IBM, ACL, ICML, EUR, USD. A 43%
false-positive rate on one document, fixed with a stoplist.

`relational-head-without-complement`, first version — generalised a pattern seen five times
into a class of forty heads and produced 63 findings on three documents. Cut back to the
heads the corpus actually evidenced, which leaves one true finding.

## The validation method, and its limit

`accuracy.py` measures finding density at an old commit against HEAD. **It is asymmetric.** A
rule whose density drops sharply is confirmed. A rule whose density holds proves nothing,
because the corpus records what authors managed under deadline rather than what should have
been fixed. A tool built to catch what humans miss cannot be validated by asking whether
humans already caught it.

`mine_fixtures.py` supplies the missing positive evidence. A commit where a finding count
drops is a commit where someone repaired that defect class unprompted. That is how the four
cohesion rules were kept after their density came back flat.

23 of the implemented rules have at least one documented repair event.

## What is not done

The 419 ledger rows carrying verbatim text from private co-authored projects must be scrubbed
before anything goes public.

`blocks_submission` and the `lookup`/`rework` boundary are not reliable labels — three
independent raters disagreed by 7 and 8 of 55. Treat them as hints.

No end-to-end trial has been run on a document by its author, which is the only test that
separates a rule finding nothing worth fixing from a rule finding an unmet need.
