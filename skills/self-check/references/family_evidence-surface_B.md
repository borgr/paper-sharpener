# Evidence surface, part B

## What this half covers

This half continues `family_evidence-surface_A.md` and does not restate it. Read that page first for the family definition and the tier vocabulary. The 50 rules here cover the surfaces on which a claim becomes checkable — tables, figures, reported numbers, uncertainty, p values, the reproduction surface, and the track-record entries in a grant. More than half of them exist because an earlier, wider rule was judged unsafe and cut into pieces, so the page spends its first section on that repair pattern rather than on the rules themselves.

## The lesson of the repairs

Twenty-eight of these fifty rules carry the `repaired` provenance. Each was once part of a broader rule whose single stated fix was correct for some of the cases its test matched and wrong for the rest. The audit that split them was not tightening prose. It was removing rules that would have made a paper worse when applied as written.

Take the axis and label rule from Gopen & Swan, which survives in this half as the one entry still flagged unsafe. Its test asks whether a table runs the condition down the left and the outcome to the right, and whether every graph axis carries a label and a unit. Its recorded unsafe reason is that it bundles transposing a reversed table with supplying missing units, two findings whose correct fixes differ. Transposition is a rearrangement of material already on the page, so an editor can do it and check it. A unit is a fact about the measurement setup, and it is either recorded elsewhere in the paper or held only by the author. The repaired pieces respect that difference. Rule 29 recovers an axis unit from the methods section, the caption or the released code and reports the axis to the author where no part of the paper states it. Rule 30 refuses to touch a scale multiplier at all, because a label reading `CPU time (seconds x 10^2)` is genuinely ambiguous about whether the scaling has already been applied, and only the plotting code settles it.

The p-value cluster shows the same split running between two adjacent defects. A p value printed as `0.000` is repairable from the printed string alone — no test returns exactly zero, the venue defines a floor form, and the replacement needs no access to the analysis. A result reported as `NS` looks like the same kind of defect and is not. The value the reader needs was never in the document, so that rule can find the label automatically and can never supply the replacement. Its suggestion goes further and forbids substituting `p > 0.05`, since the bound is not what the analysis produced and carries no more information than the label it replaced. One test, two situations, and a shared fix would have written a bound into the paper that the author never computed.

The lie-factor pair shows a fix that is destructive rather than merely unavailable. Both rules compute Tufte's ratio of drawn effect to effect in the data against the published 0.95 to 1.05 band. Where the cause is dimensional inflation — a one-dimensional quantity drawn as circle area, so a 2x difference is drawn as 4x — there is exactly one correct repair, and re-encoding on a single length dimension changes no number and no axis. Where the cause is a truncated value axis, the same arithmetic returns a large ratio on loss curves, near-ceiling accuracy panels and calibration plots that are correctly drawn that way, and widening the axis would compress the entire result into a row of pixels. So the second rule computes the ratio, reports it with the axis range and the convention used, and proposes no change.

The general principle is short. A rule whose single stated fix does not repair every case its test matches must be split before use. The two failure shapes to look for are a test that spans a mechanically repairable defect and one needing a number absent from the document, and a test whose fix is right in one situation and destroys the evidence in another. Splitting is cheap. Applying an unsplit rule costs a real paper.

## What reviewers actually complain about

Eight rules came from defects ICLR 2024 and ICLR 2025 reviewers named in writing. A defect a reviewer names is a defect that already cost someone a score, so these deserve a first pass of their own. The frequency column is the number of distinct reviews in which the complaint appeared.

| Freq | Test, as recorded |
|---|---|
| 9 | Hyperparameters, training setup, or implementation details needed to reproduce a reported number are absent or only partly given. |
| 8 | A mechanism, format, or abstract concept is described only in prose where the reviewer asks for a concrete example, worked instance, diagram, or pseudocode. |
| 6 | A table or figure is legible but its content is ambiguous — the reviewer cannot tell what rows, columns, bolding, or plotted elements mean. |
| 4 | Figure text, axis labels, tick labels, legends, or line widths are too small or too crowded to read at normal viewing size. |
| 4 | The released code or supplement cannot be run as given — no README, no environment or run instructions, or the reviewer concludes reproduction is not possible. |
| 3 | The caption does not carry the information needed to read the panel without hunting through the text, or asserts something the panel does not show. |
| 3 | Results are reported as point estimates with no error bars, standard deviations, seed count, or significance test, or with too few seeds. |
| 2 | A figure, table, or algorithm block is never referenced or explained in the running text. |

Two of these carry counter-cases that turn the fix into a different complaint. Rule-based bolding of the best mean in every column, applied where the gaps sit inside the reported spread, converts an ambiguity complaint into an overclaiming one. Adding the one factual takeaway a self-contained caption wants, to an exploratory panel with a null result, manufactures a claim the panel does not support — which is the failure the second quoted reviewer had already caught.

## The rules, grouped by mechanism

### Table construction and its blanks — 5 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A rule separates every pair of adjacent rows or columns. | Report the density with what the venue style file says. Where the file is silent and the table is read down, keep only top, header and bottom rules. | A wide appendix table read across is easier to track with a rule per row. Some journal classes mandate full ruling. | Zobel p.106 |
| Empty cells, excluding grouping labels continued from above. | Report each blank with row and column and ask which of not measured, not applicable, or zero it means. Propose no filler. | A blank continuing a grouping label is a legitimate ditto. | Zobel p.106 |
| A single-quantity decimal column not aligned on the decimal point. | Align it, for instance with a siunitx S column. Add no digit and change none. | Identifier and integer columns are excluded. Padding with trailing zeros would be a precision change. | Zobel p.106 |
| A column of measured physical or resource values whose head names no unit. | Recover the unit from the methods, caption or released code. Where the paper never states it, report the column. | Normalised, probability, percent-marked and count columns have no unit to add. | Zobel p.106, ch.8 checklist |
| Table columns no sentence refers to. | Report the list and ask which are load-bearing for readers. Relocate agreed ones to an appendix at full width. Never delete. | A full per-language or per-benchmark table whose completeness is the contribution. | Higham p.91, Zobel p.106 |

### Figure axes, units, and drawn observations — 6 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A reversed table, or a graph axis with no label or unit. | Put the condition on the left in natural order and the outcome on the right. Label every axis with quantity and unit. | A leaderboard sorted on score is right to put the score first, since ranking is the content. | Gopen & Swan 1990, Levels of Edit VI-D |
| One axis carries a set quantity and one a measured response, and the set quantity is on the vertical axis. | Redraw with the set parameter horizontal, then update the caption and every sentence naming an axis. Report where the methods leave the setting open. | ROC, precision-recall and other two-outcome curves have no input axis and are excluded. | Zobel p.84 |
| A discrete series of 30 or fewer observations drawn as a bare connected line. | Add one distinct marker per measured point, reusing the paper's existing marker set. Change no value. | A per-step training curve becomes an ink band once marked. A scatter is already marked. | Zobel p.84 |
| An axis label naming a measured quantity without its unit. | Write the unit in parentheses, taken from methods, caption or code. Report the axis where nothing states it. | Normalised, probability and ratio axes have none. A caption may already carry it. | Zobel p.113 |
| A scale multiplier such as `x 10^3` in an axis label. | Report the ambiguity and ask whether the ticks were already divided. Rescale no tick and no value. | Compute at `10^18` FLOPs and memory in `2^30` bytes are read correctly by the field. | Zobel p.113 |
| A numeric or comparative claim resting on a figure with no absolute value quoted in the referencing sentence. | Ask the author for one or two representative values. Read nothing off the plotted curve. | Schematics have no value to quote. Figures duplicating an adjacent table need none. | Zobel p.113 |

### Colour as an encoding channel — 3 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A continuous quantity encoded with a rainbow or jet map. | Swap in a perceptually monotonic sequential map, or a diverging map for deviation from a meaningful midpoint. Values untouched. | Field-fixed maps stated in the caption, and tasks that locate a boundary rather than order values. | Rougier Rule 6, Nguyen M1 |
| Category identity carried by hue alone. | Add a redundant channel to every series — marker shape, dash pattern or end-of-line label — in a colourblind-safe palette. Remove no series. | A single series, or position already identifying each mark. Dashes are poor on dense scatter marks. | Nature colour guidance, Wong 2011 |
| More than about seven colours encoding categories, or more than five on a qualitative scale. | Report the count and de-emphasise. Colour the focal few, draw the rest as labelled thin grey lines. Never merge into "other" and never drop a series. | A figure whose point is diversity rather than per-category comparison. | Nguyen M1, Krzywinski 2010 |

### Graphical integrity and the table-graphic crossover — 4 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A one-dimensional quantity drawn with a two- or three-dimensional mark, lie factor outside 0.95 to 1.05. | Re-encode on one length or position dimension, then recompute the ratio. Leave the axis range exactly as set. | Area encoding of a quantity that is itself an area, and bubble size carrying a third variable. | Tufte p.57 |
| A magnitude claim over a value axis that neither starts at zero nor spans the scale, ratio above 1.05. | Report the ratio, the axis range and the convention used. Propose no axis change. Offer widening or a caption number. | Loss curves, near-ceiling accuracy panels and calibration plots are correctly narrow. | Tufte p.57 |
| Twenty or fewer plotted numbers as unconnected categorical bars with no numerals in the panel. | Print the exact values as bar labels, or move the same numbers into a table. Add no mark. | Bars read from a projected slide, and panels where error-bar overlap is the message. | Tufte p.56 |
| Twenty or fewer plotted numbers over more than a third of a column. | Report the count and the area, and ask whether the shape of the marks or their values is the claim. Propose no replacement. | Four points asserting linearity, a five-size scaling curve, a block-structure heatmap. | Tufte p.56 |

### Precision as a claim about measurement — 3 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Within one measured quantity, members differ in digits after the decimal point. Exact values excluded. | Report the group and ask whether measurement error is the same across members. Round nothing and pad nothing. | A millisecond clock beside a nanosecond counter keeps its own precision, with the difference stated. | Zobel p.79 |
| A reported uncertainty carrying more than two significant digits. | Round the uncertainty alone to two significant digits. | Seeds, parameter sizes, step indices and point estimates are enumerated as must-not-match. | Higham p.91 |
| Both leading-zero forms appear for p values in one document. | Add or remove the single character before the decimal point to match the recorded convention. Change no digit. | APA conditions the zero on whether the statistic can exceed 1, so `.03` for p beside `0.98` for t is consistent. | SAMPL, JAMA, APA 6.36 |

### Naming the uncertainty — 4 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Point estimates with no error bars, seed count or significance test. | Report mean and spread over at least three to five seeds, state the count in the caption, say what the interval is. | Pretraining-scale runs where one seed costs thousands of GPU-hours. Deterministic methods have zero spread. | ICLR 2024, ICLR 2025 |
| Intervals present but the text never names the variability source, estimator or multiplier. | State source, run count, estimator and multiplier in the caption, with one convention throughout. | A single deterministic expensive run honestly has no error bar and should say so. | NeurIPS checklist 7, ARR R5 |
| A plus-minus or `mean (value)` form whose second term is named nowhere. | Ask which quantity it is, then name it at first use and in every caption and header. Do not infer it from magnitude. | A venue template or shared results macro may define the convention at one site. | SAMPL |
| A standard error quoted in support of a claim about spread, consistency or stability. | Ask for n and the standard deviation and add the spread, or reword the claim to be about precision of the mean. Never relabel the printed number. | The plus-minus form over seeds is entrenched, and adding n lets a reader convert. | SAMPL |

### p values — 3 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A p value printed as `0`, `0.000`, `.000` or any all-zero string. | Replace with the venue floor form, keeping the document's leading-zero convention. Use exponent form for exponentially small values. | A genuine `3e-17` belongs in exponent form. A literal `0` in a counts column is not a p value. | SAMPL, JAMA |
| `NS` or "not significant" with no p value in the same sentence, cell, row or caption. | Ask the author for the value and report it as an equality. Do not substitute a bound such as `p > 0.05`. | A caption or adjacent column already giving the values, with cells carrying NS as a reading aid. | SAMPL |
| An inequality other than a bound the venue's scheme defines. | Ask for the exact value and report it as an equality, keeping the floor form below it. Where unrecoverable, keep the inequality and say so. | Genetic-association studies are exempt from the floor, JAMA defines `P>.99`, and quoted inequalities were never this author's to fix. | SAMPL, JAMA |

### Comparability of the comparison — 3 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A number whose selection rule is unstated, or a table mixing single-run, mean, median and best-of. | State the aggregation for every column and use the same one for the method and its baselines. | Best-configuration reporting is right when tuning reach is the claim and the search budget is reported for baselines too. | ARR R1, ARR C3 |
| A change introduced with no ablation row removing it while holding the rest fixed. | Add the missing rows, or state which contributions are not separately attributed and why. | Ablation is genuinely impractical at scale, and a robustness check or error analysis meets the obligation. | Lipton & Steinhardt 3.2 |
| A baseline whose tuning budget is unstated or smaller than the method's, prompt baselines especially. | Report the budget per system, or match budgets and rerun, or say plainly the numbers are quoted under an unknown budget. | An unrerunnable published state-of-the-art result, quoted with a note about the unmatched budget. | ARR R1 |

### The reproduction surface — 6 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Hyperparameters, training setup or implementation details absent or partial. | A settings table per experiment covering optimizer, rate, batch size, epochs, seeds and hardware, plus which were tuned over what grid. | Closed-API experiments have no optimizer or epochs, and a licence may forbid publishing a production configuration. | ICLR 2024, ICLR 2025 |
| Released code cannot be run as given. | A README with exact environment, one command per reported table and the seeds used, run by someone outside the project from a clean checkout. | Pipelines welded to internal infrastructure or licensed data. Exact paths leak identity under double-blind review. | ICLR 2024, ICLR 2025 |
| A dataset, model or language selection with no stated rationale. | State the criterion, and where the criterion was availability, say so. | A field-standard benchmark suite needs the suite motivated, and per-task rationale for forty tasks is noise. | ARR M4 |
| Splits, hyperparameter values and the selection procedure appear nowhere. | Put what a reader needs to appreciate the result in the main text and the exhaustive list in an appendix with a pointer. | A theoretical paper with no experiments has nothing to report and should say so. | NeurIPS checklist 6, ARR C2 |
| Example counts or per-split sizes missing, or the split procedure unstated. | Add a dataset table with per-split counts and say whether the splits are standard or newly drawn. | A fixed public benchmark with universally known splits can be cited instead. | ARR B6 |
| A bare third-party metric or tool name behind a reported number. | Name the package, its version and the non-default settings at the first reported use. | A metric with one canonical implementation the field uses without variation. | ARR C4 |

### Floats and the text that carries them — 6 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Figure text or line widths too small or crowded at normal viewing size. | Size at final print width with the smallest text no smaller than the caption font. Drop panels rather than shrink them. | A panel grid whose message is the aggregate pattern, repaired with a zoomed inset beside the full grid. | ICLR 2024, ICLR 2025 |
| Legible but ambiguous rows, columns, bolding or plotted elements. | State in the caption what each column reports, what bold marks and over what the aggregate runs. Make bolding rule-based. | Rule-based bolding of gaps inside the reported spread asserts a winner the error bars do not support. | ICLR 2024, ICLR 2025 |
| A caption that cannot be read alone, or asserts what the panel does not show. | Give plotted quantities, axes, series, what varies across panels, and the one factual takeaway the panel supports. | An exploratory panel with a null result has no takeaway to add. Fifteen tables sharing a legend want one prose paragraph. | ICLR 2024, ICLR 2025 |
| A float never referenced or explained in the running text. | One sentence per float naming it and stating what it shows. Grep each label and confirm a reference exists. | An appendix gallery of dozens of qualitative samples, where a sentence per float is boilerplate. | ICLR 2024, ICLR 2025 |
| An abstract construct described only in prose. | Pair it with one small worked example or a pseudocode block at the point of first definition. | A two-hundred-token template belongs in an appendix with a pointer. Pseudocode for [name] is filler. | ICLR 2024, ICLR 2025 |
| A bare cross-reference such as "Results are shown in Table 3." | Replace the pointer with a sentence stating the finding and citing the figure as its support. | A reference artefact for lookup, such as a full hyperparameter table, needs only a pointer. | NeurIPS checklist 7, Levels of Edit VI-C |

### Citations and shown instances — 4 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A category the paper coins is used in a claim and no instance of it appears anywhere, appendix and artefact included. | Insert one concrete instance at the point the claim is made rather than promising it in an appendix. | (none recorded) | corpus, do-llms-benefit-own-words |
| A results claim is qualified in the text and the qualifying comparison is never cited. | Add the citation reporting the contrasting finding in the same sentence. | The qualification may come from the paper's own experiment, so the fix is a pointer to its own section. | corpus, Multilingual-Knowledge-Transfer |
| A citation is malformed, inconsistent with the rest of the text, or missing where the claim plainly needs one. | Query it to draw attention. Correct nothing and never supply an absent citation. | PES D4.2 still expects the editor to flag where citations are needed, so silence is not the alternative. | Editors Canada, Ethical Editing 2024 |
| An unattributed quotation, an unsupported generalization, or a table with no source. | Flag the site and leave the supply to the author. | In heavily cited text one batched note beats a query per instance. | Editors Canada, PES 2024 D4.2 |

### Grant track-record outputs — 3 rules

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| An ERC selected output with no statement of the applicant's role and of the capacity it demonstrates. | Add one clause of role and one naming the part of the work plan the output makes deliverable. Leave every entry listed. | Sole authorship, or alphabetical ordering with the norm stated, needs one sentence for the whole list. | ERC Information for Applicants V11.0, s2.2 |
| A Wellcome research-outputs section not saying which outputs are most relevant and what the role was. | State relevance and role in first person, the register Wellcome's guidance uses, added to existing entries. | NIH's third-person Project Summary convention breaks here, and the inversion holds too. | Wellcome, How to write an application |
| A UKRI past contribution with no statement of what it evidences about delivering this work. | Report those entries and propose a delivery clause for each. Leave the selection to the applicant and never propose deleting. | A narrative CV wants a small set while the same list under ERC or Wellcome must appear in full. | UKRI/EPSRC New Investigator Award |

## Running the pass by hand

Work the surfaces in this order, because each step supplies information the next one needs.

1. Legibility first. Print at final width and check the smallest text in every float. An illegible panel makes every later check on it pointless.
2. Sweep the numbers mechanically. Grep for all-zero p values, `NS`, threshold inequalities, mixed leading-zero forms, and uncertainties longer than two significant digits. These are the repairs entailed by the printed string alone, so do them and move on.
3. Sweep the tables. List blanks, ragged decimal columns, unit-less measured columns, rule density and unreferenced columns. Fix alignment and ruling. Batch the blanks and the missing units into one query.
4. Sweep the figures. Check which axis carries the set quantity, whether discrete series are marked, whether labels carry units, whether a scale multiplier appears, and whether the colour encoding survives greyscale. Compute the lie factor only where a magnitude claim rests on the panel, and separate dimensional inflation from a truncated axis before proposing anything.
5. Read every float against its caption and its text reference. Mark bare pointers, captions that cannot stand alone, and floats the text never names.
6. Check the comparison. Aggregation rule per column, baseline budgets, ablation rows per introduced change, seed counts and named intervals.
7. Check the reproduction surface. Settings, splits, counts, metric versions, selection rationale, runnable release.
8. Collect everything that needs a number absent from the document into one batched query. Rules 26, 30, 31, 32, 37, 39, 42, 43, 45 and 46 all end in a question rather than an edit, and delivering them together saves the author a round.
9. For a grant, close on the track-record entries, one role clause and one delivery clause per output, with the selection left to the applicant.

## Where this half is weak

The repairs inherited their parents' citations, so the source column is much less independent than its length suggests. Four table rules cite one page of Zobel, three axis rules cite another, six p-value and uncertainty rules cite one SAMPL document, two rules each rest on a single Tufte page, and the three grant rules share one merged ERC-Wellcome-UKRI source block. The shared inheritance also left the three grant rules with an identical `cost` field that describes all three funders at once, which is wrong for each of them individually. Treat a citation repeated across a group as one piece of evidence for the group, and do not read agreement between siblings as corroboration.

The `reviewers` sources are weaker still. All eight cite "ICLR 2024, ICLR 2025" with no review identifier, so the frequency counts cannot be audited and nothing distinguishes a complaint from four reviewers of one paper from four separate papers.

Several checks are marked decidable and are not settleable from inside the document. Rule 26 finds the blank but the three meanings are only in the author's head. Rule 28 needs the unit to have been recorded somewhere else in the paper. Rule 32 asks whether measurement error is the same across a group, which the text does not state. Rule 39 needs a rendered measurement, a convention choice that Tufte's own example is contested on, and a field judgement about the smallest material difference. Rule 47 needs a style sheet that may not exist. The rules already flagged undecidable — the ambiguous-table check, the worked-example check, the baseline-budget check, the selection-rationale check, the scale-multiplier check, the figure-number check and the unreferenced-column check — are honest about it. Run all of these as queries and never as edits.
