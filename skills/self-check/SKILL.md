---
name: self-check
description: Check a LaTeX paper or grant proposal against itself and leave sited queries — cross-references, numbers that disagree, claims that outrun their evidence, terminology drift, scaffolding that must not ship. Runs passes weighted by where expert reviewers actually spend effort, reports rather than rewrites, and can write findings into the .tex as notes addressed to whoever owns the answer. Use when asked to check, proofread, or review a paper or proposal below the structural level, or before a submission.
---

# Checking a document against itself

This finds what a reader will stumble on, and it does not rewrite your prose. That is a
measured decision rather than caution. Of 512 rules gathered from the writing literature,
funder guidance, professional editing standards, ICLR reviewer complaints and 19,315 real
expert edits, **five** have exactly one correct output. Every other repair needs something
the document does not contain — which number is right, what the sentence meant to claim,
what the figure would look like regenerated.

So the output is queries, and the reader decides.

## Before anything, establish two things

**The stage.** Pass `--draft` while writing and nothing while preparing to submit. Review
markers, TODOs and placeholders are supposed to be present in a draft and are defects only
when they ship. The same paper gives 52 findings at draft stage and 176 at submission, and
almost all of the difference is scaffolding.

**The document.** Globbing `*.tex` sweeps in scratch files, notes and abandoned variants,
and every finding in those is noise. `run.py` resolves the input graph from each
`\documentclass` file and reports which document it picked, newest first. Check that it
picked the one you meant.

```bash
cd build/sharp
python3 run.py --draft path/to/*.tex          # while writing
python3 run.py path/to/*.tex                  # before submitting
```

## Run the passes in this order, and say why

The order is not the literature's. A corpus of 19,315 attributed edits by 383 researchers
says where expert attention actually goes, and it differs sharply from where the writing
guides put their rules.

| pass | expert attention | rules asserted |
|---|---|---|
| integrity | 40% | 16% |
| cohesion | 15% | 10% |
| claim-calibration | 14% | 15% |
| evidence-surface | 16% | 23% |
| register-redundancy | 8% | 11% |
| naming-notation | 5% | 14% |
| sentence-mechanics | **1.4%** | **10%** |

Integrity first, because it is where reviewers spend two fifths of their effort and it needs
no knowledge outside the document. Sentence-mechanics last and cheaply — the literature has
44 rules there and the corpus supports one, which is one no guide contains.

The deterministic passes may always run, since they cost nothing and conflict with nothing.
Stop reporting judgement findings below the highest failing level, because fixing a higher
one rewrites everything under it.

## Rank by what it costs the author, never by severity

A finding that costs thirty seconds and one that costs a day must not sit in the same list,
because review time competes with running experiments.

- **free** — resolved from what is on the page, in seconds. A yes-or-no about intent, a
  stale marker, a wording choice.
- **lookup** — needs a value that already exists somewhere. A number from a log, a citation,
  a hyperparameter from a config.
- **rework** — needs something that does not exist yet. Regenerate a figure, run the
  ablation, obtain the measurement.

Judge by the fix, never by how much the defect matters. An overclaim fixed by softening one
sentence is free even though it matters enormously.

Two intersections organise the work. **Blocking and free** should be cleared immediately and
continuously. **Blocking and rework** should surface weeks before a deadline, because those
change what experiments still need running.

Cost `free` and `batchable` are the reliable labels — three independent raters agreed within
3 and 4 of 55. `lookup` against `rework` and `blocks_submission` are not reliable, so treat
them as hints rather than gates.

## Three guards that override every rule

These exist because 50 gathered rules would have damaged correct text, and the audits caught
them before anything ran.

**Never weaken a claim marker automatically.** Deleting a hedge, dropping the intensifier
from "almost all", or stripping a tentative modal is grammatical, preserves meaning by every
mechanical test, and silently raises the claim past its evidence. Five rules across three
sources were flagged unsafe for exactly this, and no professional standard states the
protection. `checks_claim_calibration.py` and `checks_register_redundancy.py` enforce it in
code with a gate that has survived bypass attempts.

The evidence makes this sharper. Promotional language is positively associated with funding
at odds ratios near 1.5 across two funders on real rejected applications. Confident prose is
rewarded, which is precisely why the trade-off belongs to the author.

**Never bundle.** A rule whose single fix does not repair every case its test matches must be
split first. That caused most of the 50 unsafe rules — "bind footnotes, citations and
references directly to the preceding word" is right for a footnote and wrong for a citation.

**Never let a precision rule touch an exact value.** Rounding exists because excess digits
mislead about measurement error. An exact integer has none, so a count, a seed, a parameter
size, a hash or a step index must be excluded.

## Report, or write notes at the site

The corpus settles the default. Across five independent samples, roughly a quarter of every
cross-author edit is not an edit — it is an addressed question left at the exact site of a
problem the editor could not resolve, deleted by whoever answers it. Nobody in that corpus
had read a professional standard, and SENSE and Editors Canada prescribe the same thing.

```bash
python3 -c "import run, annotate, teach; ..."   # see annotate.write / annotate.sweep
```

> **Write mode has survived three adversarial audits but has never been used on a document
> anyone depends on.** The defects the third audit named are fixed and verified — a `}` in a
> line comment no longer shifts the brace map into an `\emph{}` argument, every file
> receiving a note now carries its own `\providecommand`, and the guard is enforced inside
> `write()` as well as in `run.scan` so no call path bypasses it. Round trips are
> byte-identical on single and multi-file projects. Even so, run it on a branch the first
> time, and read the diff.

`annotate.write()` inserts `\scnote{...}` at each finding, addressed to whoever last touched
the line by git blame. It validates every offset against brace depth and span kind, refuses
the preamble, refuses a file that is untracked or has uncommitted changes, refuses a file it
cannot decode as UTF-8, escapes the note body, and carries a content-and-position digest so a
rerun replaces rather than duplicates. `annotate.sweep()` removes every note it wrote and
restores the file byte-identically — verified end to end on a real document.

Prefer notes over a report when the author is mid-draft, since they meet each question while
writing. Prefer a report before submission, when the list is being cleared in one sitting.

## Budget

**At most five judgement findings per report.** More than that is a rewrite the author
cannot review back. If a level has more, report the five with the largest consequence and
say what was deferred. Mechanical findings are exempt, since they are cleared in a batch.

## Teach once, then fade

`teach.py` attaches the mechanism to the first finding of each family and a page citation
afterwards, per project and then per user. Your second paper is quieter than your first. The
family pages in `../ledger/` derive each family's rules from its mechanism, so a reader can
regenerate the rules instead of memorising them.

## What this does not do

It does not judge whether the research is sound, and it does not check structure — whether
the argument exists and in what order is a different and more expensive pass.

It cannot tell a rule that finds nothing worth fixing from a rule that finds a real defect
nobody has had time for. Finding density measured across 824 commits of real revision
confirms a rule when it drops sharply and proves nothing when it holds flat, because the
corpus records what authors managed under deadline rather than what should have been fixed.

Sentence-mechanics coverage is deliberately thin. Cohesion rests on Gopen and Swan, whose own
caveat is that none of their principles should be treated as rules, so those findings report
only.

Grant rules are funder-conditional in 39 cases. Whether references count against the page
limit is inverted between Horizon Europe, ERC and UKRI, so a rule either names its funder or
drops to a query.


## Packaging

There is deliberately no built `dist/` tree. One existed and had drifted badly — it carried
none of three rounds of fixes, still used a macro name that collides with the LaTeX kernel,
and still wrote notes into `\documentclass{...}` while reporting success. A snapshot that
looks installable is worse than no snapshot.

Packaging must therefore be a build step run at publish time, from the live tree, with the
scrubbed ledger copied from `../ledger/public/` and never from `../ledger/private/`.
