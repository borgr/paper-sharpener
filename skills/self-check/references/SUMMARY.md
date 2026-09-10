# The sub-structural layer

Everything here sits below structural revision and above typo-hunting. Structural work asks
whether the argument exists and in what order. This layer asks whether a reader who accepts
the structure can follow the prose, trust the numbers, and tell what is claimed from what is
shown. It is the layer that consumes most manual review time, and it is the layer no single
source covers.

Read this page and you can run the passes by hand. The family pages give the mechanisms. The
ledger gives the rules with their sources.

## The governing test

One question decides how any rule may be applied. **How many correct outputs exist?**

SENSE, the Dutch society of language professionals, states it as the boundary of the whole
profession — direct fixing is for cases where "only one correct answer possible", flagging is
for cases "where more than one solution is possible". Harnby reaches the same place from the
other side, that when several repairs would each work, "the query trumps the amendment every
time".

That test produces three tiers, and the distribution it produces is the central finding of
this whole exercise.

| tier | meaning | count |
|---|---|---|
| silent | exactly one correct output, meaning cannot move | 6 |
| batch | meaning preserved, taste involved, one accept/reject per class | 68 |
| query | the fix needs knowledge absent from the text | 298 |

**The silent tier is nearly empty, and that is not timidity.** The repair for almost every
real defect lives outside the manuscript, in the analysis output, the figure source, the
bibliography, or the author's intent. A script can detect these reliably and cannot fix them.
So the honest product is a reviewer that explains itself. An auto-editor is the wrong shape for this work. The six silent
rules are grammar and idiom errors with one possible form, minor typos inside quotations,
and mechanical agreement.

## The seven families

| family | rules | what it governs |
|---|---|---|
| evidence-surface | 99 | tables, figures, numbers, error terms, captions |
| integrity | 68 | cross-references, citations, internal consistency, completeness |
| claim-calibration | 63 | hedging, overclaiming, evidence matching the assertion |
| naming-notation | 56 | one concept one name, symbols, acronyms, citation keys |
| sentence-mechanics | 44 | nominalisation, subject-verb distance, modifier stacks |
| cohesion | 42 | old before new, topic and stress position, paragraph joins |
| register-redundancy | 39 | hype, filler, restatement across sections |

A further 28 rules govern the editor's procedure rather than the text, so they carry no tier.

## Three guards that override every other rule

These exist because the audits found rules that would have damaged correct text.

**Never automatically weaken a claim marker.** Deleting a hedge, dropping the intensifier
from a graded absolute such as "almost all", or removing a tentative modal is grammatical,
passes every mechanical meaning-preservation test, and silently raises a claim past its
evidence. Five separate rules across three sources were flagged unsafe for exactly this. No
professional standard states the guard, so it is written here as a local extension.

The evidence makes this sharper rather than softer. Promotional language is positively
associated with funding, replicated across two funders at odds ratios near 1.5 on real
rejected applications. Confident prose is rewarded. That is precisely why the trade-off
between claim strength and defensibility must be the author's decision and never a silent
edit.

**Never bundle situations whose correct fixes differ.** This caused most of the 50 unsafe
rules. A rule saying "bind footnotes, citations and references directly to the preceding
word" is right for a footnote, where the space must go, and wrong for a citation, which
needs a non-breaking space kept. One rule had to become two. Before using any rule, ask
whether its single stated fix repairs every case its test matches.

**Never let a precision rule touch an exact value.** Rounding exists because reporting more
digits than the measurement error supports misleads. An exact integer has no measurement
error. A rounding rule reaching a count, a random seed, a parameter size, a hash, an
identifier or a step index destroys the value rather than tidying it.

## Two conditional layers

Eight rules have no fixed correct answer because standards disagree. The leading zero on a
*P* value is the sharpest case, where APA and AMA are opposed. Those are style-sheet
switches, never hardcoded rules.

Thirty-nine grant rules are funder-conditional. Whether references count against the page
limit is inverted between Horizon Europe (counted), ERC (excluded) and UKRI (counted inside
the word count). NIH's third-person summary convention breaks UKRI and Wellcome first-person
summaries. Each such rule names its funder or drops to query.

## What the evidence actually supports

Three limits belong on this page rather than buried.

**Effect sizes are small.** The promotional-language gap is 0.93 percent of words against
0.89 percent. Readability experiments move understanding by an odds ratio near 1.08 per unit
of style. Language rules are real and marginal, and a tool implying prose swings outcomes is
lying.

**Most stance and hype studies analyse funded proposals only**, because archives publish
awards. They establish that grant prose has grown more confident. They cannot establish that
confidence causes funding.

**Reviewers barely agree with each other.** Across 43 reviewers scoring the same 25 NIH
applications, agreement was zero. Inside that null result sits the finding that justifies a
defect-hunting tool at all — a good score reflected "an absence of weaknesses" rather than a
count of strengths. Removing defects is the lever. Adding strengths is not.

## The passes, in order

Run them top-down, one topic at a time, and stop reporting judgement findings below the
highest failing level, because fixing a higher one rewrites everything under it.

1. **Claim** — the title and abstract against what the results support.
2. **Structure** — reverse outline, first sentence of every paragraph read in sequence.
3. **Figures** — captions standing alone, floats called out, axes carrying what varied.
4. **Consistency** — numbers, terms, units, acronyms, cross-references.
5. **Citations** — does each support the sentence attached to it.
6. **Hedging** — claim strength against evidence strength.
7. **Sentences** — old before new, characters as subjects, modifier stacks unpacked.
8. **Mechanics** — the small silent set, and nothing more.

The deterministic passes may always run, since they cost nothing and conflict with nothing.
The stop rule governs judgement findings only.
