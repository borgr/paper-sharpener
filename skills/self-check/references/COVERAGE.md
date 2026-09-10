# What has evidence, and what does not

Measured over **2,140 real `.tex` files** from the Overleaf corpus at submission stage, plus
four documents judged finding by finding.

## Firing

125 rule ids exist in the code. **115 fired somewhere** in the sweep. `probe` is a selftest
fixture and correctly never fires in production.

## Nine rules with no evidence, and why

Tested against constructed positives and, where possible, against text that provably
triggered them before.

| rule | status |
|---|---|
| `uncited-bibitem` | fires on a constructed positive — rare, not broken |
| `paragraph-topic-drift` | correct but strict; requires no stem shared by any two topics, which academic prose rarely violates. Diagnosed in full, veto tightened, still silent. |
| `outcome-risk-with-unconditional-outcome` | fired on b2 before a concessive guard was added; the guard is right and the text was correct writing |
| `risk-kind-unstated-beside-flat-outcome` | same family, same guard |
| `project-acronym-variant` | grant-gated; the corpus is papers |
| `generalisation-beyond-tested-population` | untriggered by a constructed positive — needs a faithful fixture before it can be trusted |
| `percentage-arithmetic-mismatch` | as above |
| `approximate-figure-inconsistent` | as above |
| `standard-error-doubled-at-small-n` | as above |

The last four are the honest gap. A rule whose trigger cannot be reproduced from its own
description is not validated, and four of them are in that state.

## Rules that were far too loose, found only by scale

The four-document sample could not reveal these. At submission stage over the corpus:

| rule | max in one file | total |
|---|---|---|
| `missing-graphic-file` | 285 | 1239 |
| `doubled-word` | 124 | 231 |
| `repeated-sentence` | 101 | 337 |
| `float-missing-label` | 82 | 388 |
| `unnumbered-display-equation` | 62 | 1226 |
| `undefined-citation-project` | 58 | 400 |
| `duplicated-paragraph` | 45 | 68 |
| `adjacent-symbols-one-punctuation` | 43 | 291 |
| `hardcoded-cross-reference` | 43 | 203 |
| `dangling-reference-project` | 31 | 2240 |

The precision bar for a single document is twelve. Ten rules exceed it, one by more than
twentyfold.

**Two mitigations are in place.** A saturation guard collapses any rule firing more than
twelve times in one file to a single line stating the count and that a rule firing that often
is usually detecting a configuration fact rather than that many defects — it never blocks. And
graphics specifically get a fraction test, so a project whose figure directory is absent
yields one `graphics-tree-absent` finding rather than several hundred.

**Neither is a real fix for the other eight.** They are contained, not corrected.

## What this means for the precision figures

`TRIAL2` measured 0.64 and 0.39 on two papers. `TRIAL3` measured 0.75 on the newest layer,
over 24 findings. Both were sampled from four documents, before the sweep showed ten rules
saturating on real material. Treat those numbers as upper bounds.
