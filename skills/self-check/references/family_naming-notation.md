# Naming and Notation

## 1. What this family governs

Fifty-six rules enforce three promises to the reader. One concept carries exactly one name across the title, the body, the figures, the captions and the appendix. One symbol denotes exactly one object. Every acronym, abbreviation and non-standard symbol is expanded before the reader meets it, in every place a reader can enter the document independently. The damage from a failure here is silent rather than loud — the reader "silently merges two things or splits one, and any error that follows is untraceable because the notation hid it" (rule 39), apparent contradictions appear between passages that agree (rule 36), and a reviewer who cannot tell which object an equation refers to has to guess, "which makes checking the math impossible" (rule 33). At grant scale the cost lands on the score. A drifted objective label between Part I and Part II makes the mapping from method to goal the reviewer's own work (rule 8), and a project acronym that appears as POLYVOC, PolyVoc and Poly-Voc costs recognition at the moment the Lead Reviewer is arguing for you (rule 7).

## 2. The mechanism

Everywhere else in written English, repeating a word is a fault and varying it is a courtesy. That habit has a name — elegant variation — and it is the single most dangerous instinct a competent line editor brings to a scientific manuscript. The reason is that a scientific reader is doing a different job from a literary one. They are building a map from surface forms to referents, and they build it on the assumption that the map is one-to-one. Under that assumption a new word is evidence of a new thing. So when an author writes "shared-subword fraction" in the aims, "vocabulary overlap ratio" in the approach and "token sharing index" on a figure axis, the reader does not experience pleasant variety. They acquire three concepts and then spend the rest of the paper trying to work out how the three relate (rule 10).

The inversion is worth stating flatly. Elegant variation is a virtue in general prose and a defect here, so a general-purpose editor improving your repeated term is not polishing the paper. It is inserting an ambiguity that neither of you can see afterwards, because the edit reads better locally at every site it touches. The same inversion runs the other way for symbols. Prose editors do not touch notation at all, which is why symbol collisions survive to submission — "ad hoc symbol choices made mid-sentence produce collisions that can only be fixed by renaming across the whole paper, so they usually are not fixed" (rule 40).

Three further rules fall out of the same premise, and it is worth deriving them rather than memorising them. First, if every name charges the reader a lookup, then a name used once charges the lookup and returns nothing, so it should be deleted and the sentence written in words (rule 41). Second, if the reader's map is built as they read, then any surface a reader can arrive at without having read what precedes it is its own scope and needs its own first-use expansion. That is exactly why the expansion rule is positional rather than global — per major section (rule 3), per figure caption and table header (rule 51), per narrative attachment where the funder's reviewers open attachments in any order (rule 9), and per separately built PDF (rule 5). Third, if a name is evidence about its referent, then a coined name is an assertion. Calling a component a curiosity module claims the agent wants things, and the claim travels past the reader without ever being argued (rule 47).

The asymmetry between detection and repair is the last piece, and it is what keeps this pass safe. Finding two names for one thing is mechanical. Deciding which name survives is not, because the same evidence is produced by a real distinction the author is drawing badly. "Latency" in one figure and "CPU time" in another may be wall-clock and processor cost, and unifying them erases a genuine difference (rule 53). LM-judge and LLM-judge are distinct established abbreviations, so expanding every LM-judge asserts a scale property the experiments may not have (rule 23). Mb and MB may both be right in a paper that reports bandwidth in megabits and storage in megabytes (rule 54). A global replace to the canonical name also rewrites strings that must not move — cited paper titles, dataset and model identifiers, code symbols and quoted prior-work phrasing (rules 36 and 10, both flagged unsafe for exactly this). Detect mechanically and repair by query. That is the whole discipline, and Chicago supplies the branch rule for the ambiguous case — leave a consistent author's choice alone, and impose your preference throughout only once the author is already inconsistent, because a partial sweep is worse than either uniform state (rule 31).

## 3. The rules, grouped by mechanism

### 3.1 One concept, one name (11 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 36 | Same concept named two or more ways, or two concepts sharing a name, including variants between title, text and figures | Canonical name per concept in a glossary, then replace variants | ICLR 2024, 2025 |
| 10 | Every concept named more than once, with every surface form used for it | One term per concept, identical in aims, approach, figures, captions | NIH grant-writing tips |
| 8 | Objective identifiers and names differ in order, spelling or membership between Part I and Part II | One canonical list, generate both parts' headings from it | ERC IfA V11.0 §2.2 |
| 7 | Project acronym not byte-identical across cover, headers, abstract, body | Bind to one macro, grep for near-variants | ERC IfA V11.0 §2.2 |
| 18 | One referent carries an abbreviation in one section and the spelled form in another | Spelled form in body prose, replaced in one commit | corpus, erc-proposal |
| 23 | Abbreviation drops a letter of the thing it abbreviates | Make every mention identical to the expansion's initials | corpus, supervisor |
| 24 | Section heading names a mechanism the section does not describe | Rename heading and the body noun in the same edit | corpus, supervisor |
| 13 | "Proposal" used where the referent is the research | "Proposal" for the document, "project" for the work | Cronan & Deckard |
| 53 | Two labels for one quantity across figures, tables and axes | Report the pair, ask the author. Do not unify | Zobel ch. 8 (repaired) |
| 30 | A name, date, place or figure reference is internally inconsistent | Raise a query. Do not pick a winner | CIEP 5.4.5 |
| 31 | Author chose between two acceptable variants | Consistent, leave alone. Inconsistent, sweep | Chicago |

Counter-case to hold in mind. A mechanical sweep is the failure mode here. It is not the fix. Rules 36 and 10 both carry an unsafe flag because variant replacement rewrites quoted titles, reference entries and figure labels where the alternate form is correct. Rule 18's counter-case is narrower and easy to get wrong. Table headers and axis labels where column width binds are correctly abbreviated to O1, O2, O3 with the expansion given once in the caption, and spelling out "Objective 2" in every cell of a ten-column table makes the table worse.

### 3.2 Terms that carry a claim, or carry nothing (6 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 47 | A coined name imports a claim about cognition, understanding, intent or emotion | Rename after what it computes, keep the metaphor as a labelled analogy | Lipton & Steinhardt §3.4.1 |
| 48 | A technical term is used against or beyond its established sense | Use the correct term, or coin a distinct one and state the relation | Lipton & Steinhardt §3.4.2 |
| 49 | A suitcase word (interpretability, generalisation, bias, robustness, alignment) with no sense named nearby | Replace the first occurrence in each section with the specific sense | Lipton & Steinhardt §3.4.3 |
| 50 | A key term the argument depends on is undefined, or shifts between sections | Define at first use, twice — the formal condition and what it amounts to | ARR G4, Knuth pt. 11 |
| 20 | A term is borrowed from a neighbouring field where it already means something else | Rename, or define the local sense at first use throughout | corpus, supervisor |
| 22 | A load-bearing term is used repeatedly with no definition anywhere | Define in one sentence, or drop it for a narrower defined word | corpus, supervisor |

None of these six is machine-decidable. Rule 49's counter-case draws the line better than any test does — as an organising label the suitcase word is right, so naming a research programme artificial intelligence is fine and putting intelligence into an equation as a scalar is not. Rule 20 has the sharpest trap. Where the borrowed term is the venue's own established name for the technique (attention, kernel, regret, distillation), renaming to a private coinage cuts the paper out of its own citation graph.

### 3.3 One symbol, one object (7 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 39 | Table of every symbol against every meaning it carries. Flag two meanings for one symbol, two symbols for one concept | Assign one symbol per concept before revising the mathematics | Knuth pt. 14, Halmos §6 |
| 40 | Symbol assignment designed up front over spaces, functions, indices, parameters, sets | Reserve frozen letters, one letter family per kind of object, no case-or-font-only pairs | Halmos §6 |
| 33 | One symbol denotes two objects, or changes meaning between sections | Rename the second use, add a symbol-to-object table with type and shape | ICLR 2024, 2025 |
| 32 | A symbol or term is used before its definition, or defined only many lines later | Introduce at first use in the same sentence, keep a notation table | ICLR 2024, 2025 |
| 37 | Figure symbols do not match the text's symbols for the same objects | Generate figure labels from the same symbol list as the text | ICLR 2024 |
| 21 | A symbol's letters collide with a standard mathematical reading | Rename to something with no standard reading nearby | corpus, supervisor |
| 34 | Reviewer calls the notation system as a whole confusing or heavy | Cut the inventory, fix case and decoration conventions, re-derive the key result | ICLR 2024, 2025 |

Rules 33 and 39 both allow deliberate collisions and this is where enforcement does damage. Notation abuse the theory relies on — p(x) for a density and a mass function, a loss L applied to one example and to a batch — is intended identification, and renaming the second use splits objects the derivation means to join and forces a duplicate statement of every lemma. Rule 39's own exemption is a reuse scoped inside one proof, declared at its start. Rule 32's exemption is field-universal notation, where defining the gradient operator or d for dimension at first use adds a page of noise. Two rules here are only usable in narrowed form. Rule 34 is a global verdict that names no symbol, and its narrower test is to count distinct symbols in display math, flag those used fewer than three times, then check case and decoration conventions for collisions. Rule 21's narrower test is fully mechanical — a multi-letter sub- or superscript set in math italics rather than `\mathrm` renders as a product of single-letter variables.

### 3.4 Fewer symbols, and symbols that behave in prose (8 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 41 | A symbol is used exactly once, or introduced only to be referenced in the following proof | Delete it and say the sentence in words | Halmos §16 |
| 52 | Two levels of subscript, or an indexed family whose subsets need a second index | Name the set without enumerating elements, refer to elements by bare letters | Knuth pt. 15 |
| 44 | A sentence begins with a symbol, or two symbols from different formulas are separated only by punctuation | Noun in apposition before the symbol, a word between the two symbols | Knuth pts. 1-2, Halmos §17 |
| 45 | A relational symbol translates into different words in different clauses | Fix one reading, spell out the symbol where the other reading was wanted | Halmos §17 |
| 46 | Logical symbols for implication, quantification, "such that", or dots for "therefore", in running prose | Replace with the word, keep the symbols for displays | Knuth pt. 3 |
| 43 | "X also satisfies (n)" where display (n) is written in a different symbol | Name the property and use the name | Halmos §16 |
| 42 | Numbered displays nothing ever refers to, or references to a number on a later page | Unnumber the uncited displays, place the display at or before first reference | Halmos §16, Knuth pt. 16 |
| 38 | Equations unnumbered, or one equation packing several steps into one line | Number every display, split any equation needing more than one substitution | ICLR 2024, 2025 |

Rules 38 and 42 point in opposite directions and the conflict is real rather than an error in the set. Rule 38 comes from reviewers who could not cite the step they were questioning. Rule 42's counter-case concedes exactly that — uniform numbering is right while co-authors and reviewers need to cite lines, and the rule is about the reader of the final text. Rule 42 also carries an unsafe flag, because moving a display to precede its first reference can invert a derivation's dependency order and stripping a number can break references elsewhere in the source. Rule 52 is likewise flagged, since legitimate nested indices exist and blanket de-nesting damages correct mathematics. Rule 44's counter-case is the only one in the family that is honestly empty — nothing substantive, beyond table cells and displays where the layout supplies the boundary that punctuation would.

### 3.5 Abbreviation discipline (12 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 35 | An acronym is used unexpanded at first use in the main text | Expand in the main text and again in the abstract, then grep for all-caps tokens | ICLR 2024, 2025 |
| 51 | An abbreviation or non-standard symbol is unexpanded in the abstract, a caption or a table header | Expand again on first use in any artifact a reader can reach independently | Van Buren & Buehler VI-H.10 |
| 3 | An acronym appears unexpanded at first use in the section where it first appears | Expand at first use in every major section | Shulman et al. 2020 |
| 9 | An acronym relies on an expansion in a different narrative attachment | Re-expand at first use in every attachment | NIH tip 3 |
| 5 | An acronym's first occurrence in the part being read lacks the expansion with the acronym in parentheses | Expand once per part, then use the acronym only | NSF 04-016 |
| 14 | An acronym's next use is more than about two pages after its definition, or it recurs fewer than three times | Re-expand at each major section head, or delete the acronym | Cronan & Deckard |
| 2 | An acronym is coined for a term used fewer than about ten times, or one not standard for the readership | Spell the term out every time | Barnett & Doubleday 2020 |
| 1 | A specialised term or acronym appears in the title, abstract, lay summary or first page | Restrict specialised terms to sections where they are unavoidable | Martinez & Mammola 2021 |
| 4 | A technical noun phrase absent from the panel descriptor and unglossed in the same or previous sentence | Gloss in five to ten words, or use the descriptor's own phrase | ERC IfA §1.6, NSF PAPPG II.D.2.b |
| 11 | A title over the character limit, or carrying an unexpanded acronym, a coinage or a formula | Rewrite as the question or the outcome in the descriptor's words | Horizon Europe form, NIH, UKRI |
| 12 | Formulas, notation, subscripts or special characters in the abstract | Verbal statement for each formula, ASCII for each special character | Horizon Europe form |
| 6 | Clipped informal forms in narrative prose (lab, math, temp, prep, config, stats, spec, demo, info) | Expand each, keeping only clippings that are the field's term of art | NSF 04-016 |

Rules 5 and 9 contradict each other head-on, and rule 5 is flagged unsafe for it. NSF's guide says expand once and never re-expand. NIH says re-expand in every narrative section, because attachments are read separately and in different orders. Follow the funder in front of you. Six rules in this group are marked funder-conditional for the same reason (4, 5, 7, 9, 11, 12). The general counter-case across the whole group is the field-standard acronym. Writing out Bidirectional Encoder Representations from Transformers costs a line and tells the reader nothing the token did not (rule 35), and expanding DNA or GPU spends characters against a hard limit (rule 9). Rule 1 has the strongest counter-evidence of any rule in the family, discussed in section 6.

### 3.6 Citation keys and source plumbing (9 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 15 | A cite key names the work by description (all-caps, OUR, OWED, KEY) | Replace with the real author-year key as soon as the bib entry exists, then grep for all-caps keys | corpus, erc-proposal |
| 16 | A citation key's author segment does not match the paper's actual first author | Derive the key from the first author's surname at creation, rename repo-wide in one pass | corpus, erc-proposal |
| 17 | An ad-hoc short key where the venue publishes a canonical one | Take the key from the publisher's export | corpus, erc-proposal |
| 28 | Two tables or figures share a label because one was copied from the other | Give the copy a distinct label at the moment of copying | corpus, supervisor |
| 26 | A sectioning command has no label while the text cross-references that section | Add the label on the same line as the heading, when the heading is written | corpus, erc-proposal |
| 27 | Composite-figure panels referenced by digit while the figure itself is numbered | Letter the panels and reference by letter | corpus, ICML submission |
| 29 | A coloured placeholder stands where a count belongs | Fill the count and delete the colouring macro in the same edit | corpus, supervisor |
| 19 | Multi-token notation typed inline in several places instead of bound to a macro | Define one macro, replace every occurrence | corpus, MKT repo |
| 25 | Headings mix Title Case and sentence case within one document | Choose one convention, apply in a single pass | corpus, erc-proposal |

Three counter-cases here matter more than the rules. Under double-blind review a concurrently-submitted paper by the same authors must be cited descriptively, so replacing that stand-in with the true key breaks the venue's anonymity rule rather than fixing a placeholder (rule 15). Large-consortium reports are keyed by organisation or model by convention, and renaming `openai2023gpt4` to `achiam2023gpt4` makes the entry unrecognisable to every reader who knows it by the organisation (rule 16). Rule 25's mixture is mandated by several venue style files, where Title Case for sections and sentence case for subsections is required, and unifying fights the class file. Rule 19's macro also has a build cost — in a proposal whose parts compile standalone, a macro defined only in the main preamble renders as an undefined control sequence for a co-author.

### 3.7 Units and cross-artifact consistency (3 rules)

| # | Test | Fix | Source |
|---|---|---|---|
| 54 | One quantity's unit spelled two ways across figures, tables and text (Mb and Mbyte, sec and s, MiB and MB) | Report the variants and ask which unit is meant, then fix one spelling including inside figure images | Zobel ch. 8 (repaired) |
| 55 | A figure axis or table column reporting a dimensioned quantity with no unit anywhere in label, header, caption or note | Report and ask the author. Do not infer from siblings or magnitudes | Zobel ch. 8 (repaired) |
| 56 | Two tables of comparable size presenting the same comparison in opposite orientations | Report the pair and propose one orientation, noting the width must still fit | Zobel ch. 8 (repaired) |

All three are report-only by construction. Mb against Mbyte can be a factor of eight, and the labels do not settle which was meant (rule 54). Inferring MB because a sibling table uses MB would silently rescale every number in the column (rule 55). Rule 56 excludes lopsided pairs from the test itself rather than arguing them away afterwards.

## 4. What the corpus adds

Fifteen of these fifty-six rules were mined from real revisions of this researcher's own repositories, which is the largest corpus share of any family. Six of the fifteen came in as a supervisor's or co-author's margin note, and that is the signal Knuth and Halmos cannot supply. Knuth and Halmos wrote about the mathematics on the page. The corpus is about the source file, the build, and the moment a name drifts.

Three things the corpus knows that the literature does not.

The first is that the plumbing is where naming actually fails. Nothing in Halmos covers a duplicated LaTeX label, and rule 28 is a table copied from another table with its label carried along — `\label{tab:kuhnpoker_card_conditioned_behavior}` became `\label{tab:kuhnpoker_card_conditioned_behavior_full}` only after the copy sent readers to the wrong table. Rule 29 is a coloured stand-in where a number belongs, `\textcolor{orange}{XYZ}` becoming `63`, and its cost line is blunt about why it matters — the marker can survive to submission. Rule 27 is a panel reference, `Figure~\ref{...}(2)` corrected to `(B)`, because Figure 3(2) is ambiguous between panel two and figure two.

The second is that drift is invisible from inside one section. Rule 18's mechanism records that the author's own review comment caught the drift before the prose did, and the comment itself is the before-text, `% CHECK  section 4 writes "Objective~1" and "Objective~2"; this section writes O1--O3. Unify one way.` A writer working in one file cannot see a two-name problem. Only a two-section read finds it, which is why the pass below is ordered the way it is. Rule 19 is the same fact about rendering. A reviewer objected to `$\text{English}_1$--$\text{English}_2$` on rendering grounds, since the inline form renders the hyphen as a minus sign, and the macro conversion then fixed six sites at once.

The third is the citation key naming the wrong first author, and it deserves its own paragraph because it is the defect nobody rechecks. Rule 16 is `\citep{[name]2026compartmentalization}` corrected to `\citep{[name]2026pretraining}`. A wrong key is not a broken key. It compiles, it renders a plausible name, it reads as deliberate, and so no human and no compiler ever looks at it again. The rule's own mechanism notes that this same key was renamed twice in the history, first to a wrong surname and then to the right one, so the cost of a late rename scales with the number of mentions. Rule 15 is the same failure with a different mask — `\citep{[OUR SKILLS PAPER]}` became `\citep{skillissue2026}`, and the reason it survived is that "a descriptive stand-in reads as prose to a human and as a valid key to LaTeX, so neither the author nor the compiler flags it." Rule 17 completes the set, with `\citep{moroni2025sava}` replaced by the venue's canonical `\citep{moroni-etal-2025-optimizing}`, because two keys for one work make the bibliography silently duplicate the entry. Derive the key from the first author's surname and the venue's export at the moment the entry is created. Checking it afterwards does not happen.

Two corpus rules are supervisor questions rather than fixes, and they read as such. Rule 22's before-text is `nitpick: I'd be careful what we call 'semantics' here, and define it precisely.` Rule 21's is `maybe bad symbol? reminds me of exponents or experiments what about xpos or something`. Neither has an after-text in the ledger, which is honest. The supervisor raised the naming problem and the author had to choose.

## 5. How to run the pass by hand

Work in one pass over the whole document rather than section by section, because the defects in this family only exist between two places. Read section 4 above before starting.

1. **Build the term list.** Go through the document and write down every concept the text names more than once, with every surface form used for it (rule 10). Include the title, the abstract, every section heading, every figure caption, every axis label and every table header, since those are exactly the surfaces a single-section read never compares (rules 36, 18, 53).
2. **Check one name per concept, and one concept per name.** Any concept with two or more forms is a hit. Any form used for two concepts is also a hit, and it is the worse of the two. Do not unify yet.
3. **Build the symbol table.** Every symbol against every meaning it carries, including index letters, subscript conventions and case conventions (rule 39). Flag any symbol with two meanings, any concept written with two symbols, any symbol used exactly once, and any symbol whose letters read as something else in the surrounding notation (rules 33, 41, 21).
4. **Walk the abbreviations positionally.** For each acronym, find its first use in the main text, in the abstract, in each caption, in each table header and in each separately-read part or attachment. A bare acronym at any of those entry points is a hit (rules 35, 51, 3, 9). Then measure the distance from each definition to its next use, and count total uses. Under about three uses or over about two pages, the acronym is not earning itself (rules 14, 2).
5. **Grep the source.** All-caps cite keys and coloured placeholder macros (rules 15, 29). Duplicate labels, and sectioning commands with no label where the text cross-references them (rules 28, 26). Multi-letter sub- and superscripts not wrapped in `\mathrm` (rule 21, narrowed). Clipped forms from the list in rule 6. Then check each cite key's author segment against the paper's actual first author (rule 16).
6. **Resolve each hit as a query.** Never as a sweep. For every pair of names, ask one question — one quantity or two. If one, the author picks the survivor and you replace variants in a single commit. If two, the repair is to sharpen the distinction instead. Exclude quoted titles, reference entries, dataset and model identifiers, and code symbols from any replacement (rules 53, 36, 10). Where a variant is the author's own consistent choice and no house style overrides it, leave it (rule 31).

## 6. Where this family is weak

Ten of the fifty-six rules are marked not machine-decidable, and they cluster in the sections that matter most. All four Lipton and Steinhardt rules on suggestive names, overloaded terms and suitcase words are undecidable (47, 48, 49, plus 50 on undefined key terms), as is Halmos on designing the alphabet up front (40) and the two grant rules about reader-facing plain language (10, 11). Rule 34 is worse than undecidable as written, since a reviewer's verdict that the notation "seems to vary" names no symbol to change. Its narrowed form is usable. The unnarrowed form is not.

The whole one-name family runs on judgement no script has. A script can find two labels for what looks like one quantity. Nothing in the source distinguishes an author naming one thing twice from an author drawing a real distinction badly, and that is why rules 53, 54, 55 and 30 all say report and ask. Rules 4, 5, 10, 42 and 52 carry explicit unsafe flags, meaning the stated fix will damage correct text if applied without a human.

Single-source rules are the thinnest part. Each of the three Lipton and Steinhardt rules rests on one section of one position paper. Rule 13, on "proposal" against "project", rests on Cronan and Deckard alone. Rules 11 and 12 restate the text of one funder's form field and are marked funder-conditional, so they transfer to another funder only by assumption. Rule 6's list of clipped forms is one line of NSF guidance elevated to a nine-item grep.

Rule 1 is the one to distrust most, and its own counter-case says why. Martinez and Mammola found across 21,486 articles that jargon in the title and abstract predicts fewer citations. Vincent-Lamarre found the opposite for expert gatekeepers — across 12,364 AI conference submissions, higher jargon ratios went with higher acceptance, and accepted papers scored lower on Flesch Reading Ease. Markowitz found NSF abstracts with fewer common words drew larger awards. The effect may simply reverse where the reader is an assigned specialist, so treat rule 1 as a rule about lay and generalist readers and drop it for a specialist venue.

The fifteen corpus rules carry no decidability label at all, which is a gap in the ledger rather than a claim about them. Two of them (21, 22) have no after-text and no counter-case, because what was recorded was a supervisor asking a question. Rule 26 and rules 28, 29 also lack counter-cases, and for those three that is probably correct — a missing label, a duplicated label and an unfilled placeholder have no legitimate version.
