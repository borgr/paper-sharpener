# Sentence mechanics

*44 rules. Provenance mix — literature 7, grant-funders 8, corpus 8, repaired 13, reviewers 4, query-discipline 2, empirical 2.*

## 1. The remit of this family

Every sentence hands the reader a small processing job, and this family is about the size of that job rather than about whether the sentence is correct. The load comes from a short list of structural moves — an action buried inside a noun, a subject held away from its verb by a dozen words of qualification, an opening that spends ten words on preamble before the main clause starts. ML writing adds its own version, the stacked pre-modifier, as in "a transformer-based multi-task contrastive pretraining objective", where four modifiers queue in front of a nominalised head with nothing marking how they group. The family also covers the surface layer that structural trouble hides in, so numerals and units, emphasis markup, LaTeX ties and proofreading defects sit here too. Nothing in this family changes what a sentence claims. It changes how much work the claim costs to extract.

## 2. The mechanism

Williams's explanation is the spine. A reader judges prose clear when two alignments hold at once — the main characters of the story appear as the grammatical subjects, and the crucial actions those characters perform appear as the verbs. Prose becomes hard when the second alignment breaks. Take a verb and freeze it into a noun, and "we ablate the vocabulary" becomes "the ablation of the vocabulary". That single move is a nominalisation, and it sets off a cascade the writer never chooses deliberately.

The cascade runs as follows. Once the action has moved into a noun, the verb slot is empty, and it gets filled by a verb that carries no action of its own — is, has, provides, exhibits, performs, is observed. The nominalised action now needs somewhere to sit, so it becomes the subject, and abstract nouns come with prepositional trains that specify them, so the subject grows to eight or twelve words before the verb arrives. Sometimes there is no character left to promote at all, and the sentence needs a placeholder to open on, which is where expletive openings come from. Meanwhile the agent who actually did the work has nowhere to go except a by-phrase, and dropping that phrase is free, so it gets dropped.

Everything expensive about the resulting sentence follows from one fact about reading. Parsing runs left to right and incrementally, and the reader cannot resolve the syntax or assign importance to anything until the main verb arrives. Whatever sits in the gap between the subject head and the verb is structurally branded as parenthetical, whatever its content, so a writer who puts something load-bearing there has already told the reader to discount it. A long preamble before the main clause and a long abstract subject cost the same thing for the same reason. Both spend working memory on unresolved structure, and that memory is then unavailable for the claim.

Two further consequences follow from the same source. First, a nominalised head noun attracts modifiers that sit in front of it, and English marks nothing about how a chain of nouns brackets internally, so a specialist resolves the stack from prior knowledge and nobody else can. The chain is transparent only to a reader who already knows the answer. Second, each new subordinate clause hung on the end of a sentence reopens the question of what it attaches to, and after two links the answer stops being recoverable from position.

A reader who has this much can derive several of the rules unaided. Measure the gap between subject head and verb. Measure the preamble. Cap the chain of trailing subordinate clauses. Flag runs of three or more stacked nouns. Require a recoverable agent in any clause describing work someone will do. Require that the first verb of a stated aim be an outcome verb, since an outcome verb is what you get when the action is in the verb slot where it belongs.

## 3. An important caveat, stated plainly

This family is well founded in the writing literature and it is not where experienced reviewers of ML papers actually intervene. A separate corpus analysis of 13,139 real changes made by 382 researchers found expert reviewers spending almost no effort here. One shard of 50 changes yielded no sentence-mechanics rules at all. The reviewers' own complaints that did land in this family are surface defects — unparseable sentences quoted back for clarification appear 5 times, broken cross-references 5 times, citation-command misuse 7 times, and typo density 21 times. Nobody rewrote a nominalisation.

That has one practical consequence, and it is a scheduling decision rather than a reason to discard the family. Run this pass late, once the argument and the claims are settled, and run it cheaply. Most of it is countable, so a script or a single focused read gets it. Spending your first editing hour on subject-verb distance buys less than spending it on whether the claims are supported, and it also risks polishing sentences that a later structural edit will delete.

## 4. The rules, grouped by mechanism

### 4.1 Verb delay and unresolved syntax (7 rules)

The reader is holding an incomplete parse. Every rule here shortens the hold.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Words between subject head and main verb exceed about seven, or a quarter of the sentence | Promote the interrupting material to its own clause, or delete it as an aside | A short qualifier that must bind to the subject belongs there — "Models trained on the paired corpus outperform ..." | Gopen & Swan 1990; Williams 11th ed., Principle 5 |
| More than about ten words of introductory phrase before the main clause, or a subject over about eight words | Move the preamble after the main clause, or promote the subject's buried action to the verb | A preamble stating the condition the whole claim holds under goes first — "Under the assumptions of Theorem 2, ..." | Williams 11th ed., Principle 5 (pp. 145-147) |
| A chain of more than one subordinate clause at the sentence end, especially "which ... that ... because ..." | Replace later links with a resumptive modifier repeating the key noun, a summative modifier, or a participial free modifier | Nested conditions in specification prose may need one sentence so their scope stays unambiguous | Williams 11th ed., Principle 9 (pp. 151-157) |
| Sentences over 20 words, reported as a share of the document | Split at the first coordinating conjunction or relative pronoun, claim in the first half | An enumeration of a matched set reads long and is still one parse | NIH General Grant Writing Tips, Tip 3; NIH study section chair cheat sheet, Step 9 |
| An abstract or lay-summary sentence is long or multiply embedded although its words are ordinary | Split at the embedding boundaries, one or two subordinate clauses maximum. Do not attack the vocabulary first | Uniformly short sentences read as choppy, and Markowitz found longer NSF abstracts drew larger awards | Huang et al., Scientometrics 2025;130(11):6305-6321 |
| Reading left to right, two parses are open and only later words disambiguate | Reorder so the disambiguator arrives first, or insert the "that" after assume, suppose, show, find | Drop "that" when another "that" sits nearby in the clause | Knuth, Larrabee & Roberts, Mathematical Writing, points 8 and 17 |
| A reviewer quotes a sentence back and asks what it means | One proposition per sentence, name the subject, define any term doing unusual work | A statement precise in a formalism the reviewer lacks — add a gloss beside the formal sentence instead of splitting it | ICLR 2024, ICLR 2025 (frequency 5) |

### 4.2 Compression with nothing marking the structure (3 rules)

Material has been packed in without the grammatical signal that says how it groups.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Runs of three or more nouns used as one modifier chain | Unpack with a preposition or of-phrase, head noun first — "the protocol problem for packet-switched data communication networks" | An established compound that is one name, such as support vector machine or byte pair encoding | Knuth, Larrabee & Roberts, point 26 |
| A comma joins two spans that each have their own subject and finite verb, with no conjunction and no subordinator | Split into two sentences and let the second open on its own subject | Real subordination — the mined example "necessary, since even" is correct and the split would drop the causal link | erc-proposal d8af5c31f (26 instances, all in the length-capped proposal) |
| A field capped by sentence or character count meets its cap by splicing two claims into one sentence | Treat the cap as a budget of separate claims. Cut a claim rather than splice | Where the cap cannot hold the content, say less | NIH FORMS-I, Project Narrative; NIAID title limit |

### 4.3 Agents in subjects, actions in verbs (2 rules)

The two Williams alignments, stated as checks.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A passive clause describing project work where the agent is not recoverable | Name the agent as subject — we, the WP2 postdoc, the named collaborator | A standard service or external process ("samples will be sequenced at the core facility"). Naming a person there invents a staffing commitment | NIH Tip 3; NIH Simplified Review Framework, Factor 3 |
| An aim longer than three sentences, or whose first verb is not an outcome verb (identify, define, quantify, establish, determine, measure) | One outcome verb plus its object, then at most two sentences of method | An exploratory aim whose point is that the outcome is unpredictable should name what is learned either way | NIAID Write Your Research Plan; NIH advice on application sections |

### 4.4 Mathematics doing the grammar's work (3 rules)

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Replace every display and long inline expression with "blah" and read aloud. Flag sentences that stop being grammatical or stop carrying a claim | Restate in words what each display asserts | A proof written for verification may be a chain of displays if the prose says what the chain establishes | Knuth, Larrabee & Roberts, point 13 |
| A colon before a display whose lead-in is not a complete sentence on its own | Delete the colon, leave lead-in and display untouched | A complete lead-in that enumerates keeps its colon, as does one ending "as follows" | Knuth et al. point 23; Halmos, How to Write Mathematics, section 17 |
| Displays punctuated inconsistently across the document where the sentence ends at the display | Report the count and the document's current pattern. Propose no inserted character | A document that consistently omits terminal punctuation is internally correct | Knuth et al. point 23; Halmos section 17 |

### 4.5 Numbers, units and figures (8 rules)

Cheapest group to run and the one most often broken by an over-broad fix, which is why each test carries its exclusions.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Decimal below one with no leading zero (.3 Kb), excluding bounded statistics under AMA style, math mode, code, filenames, versions | Insert the leading zero | "P = .04" and "r = .61" are correct AMA and must not change | Zobel, Writing for Computer Science 2nd ed., ch. 5 |
| Value hard against a spelled unit (11.2Kbytes, 50ms), excluding closed-up symbols, code, math mode | Insert a space, non-breaking where possible, changing no digits | "95%" and closed-up degree symbols are correct as written | Zobel ch. 5 |
| Two adjacent numerals where the first is a count below twenty-one and the second starts a compound (14 512-Kb sets) | Spell the first number out, leave the second in figures | "2048 512-Kb sets" is out of scope by the twenty-one boundary and is reported only | Zobel ch. 5 |
| A sentence whose first word is a numeral | Report only. Ask the author to spell out or recast | Spelling out is wrong for a large exact value, and recasting can bury a number placed first on purpose | Zobel ch. 5 |
| A range or coordinated pair mixing a spelled number with a figure (between four and 32 processors) | One mode per construction — figures unless the venue spells numbers to ten, then words | "four of the 32 processors" is a different construction and is left alone | Zobel ch. 5 |
| A slashed fraction as an abbreviation in prose, excluding math mode, ratios, dates, unit expressions | Spell it out hyphenated (1/3 becomes one-third) | "a 4/3 aspect ratio" and "the 1/s in the denominator" stay in figures | Zobel ch. 5 |
| Number plus spelled-out unit as an unhyphenated pre-noun modifier (a 10 millisecond delay) | Hyphenate the spelled compound | "a 10 ms delay" keeps its space and takes no hyphen. Predicative uses take none either | Zobel ch. 5, with SI practice on symbols |
| Small numbers as adjectives in digits, or values named as values spelled out | Spell out adjectival small numbers, keep digits for values, apply uniformly | Venue style overrides, and measurement-dense text reads better in uniform numerals | Knuth, Larrabee & Roberts, point 18 |

### 4.6 Emphasis and page landmarks (3 rules)

A scanning reader navigates by visual landmarks. These rules protect the scarcity that makes a landmark work.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Bold exceeds a few per cent of body text. List rhetorical bold spans, excluding bold notation, labels, headings, form fields | Report density and the list, ask which one or two items the argument turns on, unbold only confirmed spans | Sparse bold on the hypothesis is the intended use. Bold lower-case letters are vectors and bold capitals matrices | NIH Tip 2; NIAID Add Emphasis |
| Classify every italic span as notation or emphasis, then report the rhetorical count and its share | Report both counts and propose nothing | *Escherichia coli*, gene *TP53*, variable *n*, *in vivo* are notation and none is emphasis | NIH Tip 2; NIAID Add Emphasis |
| Paragraphs over about 150 words, or a page with no heading, list or break in its upper half | Split at the second claim, add the heading that names the block's argument, convert in-prose enumerations to lists | A chain of inference where each step depends on the last stays whole. Give it a heading | NIH Tip 2; NIH First Level Peer Review; chair cheat sheet Step 9 |

### 4.7 Parallel form (2 rules)

Form signals status, so a break in form signals a difference in kind that may not exist.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Within one list, heading level or table stub, an item whose construction differs from its siblings | Recast into the shared construction, or report it as a possible structural mismatch if it will not recast | Genuinely non-parallel items, where forcing the wording hides a real problem. A deliberate one-word closing row is not an error | Van Buren & Buehler, The Levels of Edit 2nd ed., VI-H item 6 |
| An orphan enumerator — an (a) with no (b), an (i) with no (ii) | Report the orphan and its sentence. Propose nothing, since the two repairs are opposite in effect | A lone label deliberately set up for a later cross-reference | Van Buren & Buehler, VI-H item 6 |

### 4.8 Surface errors and the query discipline (8 rules)

The reviewer cannot audit your laboratory, so they use the artefact in front of them as the sample. The second half of this group is about which of these to fix silently.

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Any non-zero spelling or grammar finding in the rendered PDF | Proofread the render, read the narrative aloud, re-run after the final reformat | Domain terms and non-English names get flagged correctly. The rule is zero unresolved findings | NIH Tip 5 ("zero tolerance ... reviewers may think your research could be conducted in the same manner") |
| Surface errors dense enough that a reviewer lists them or asks for proofreading | Fix the whole class of error rather than only the instances found | A blanket pass corrupts gene symbols, dataset names and code tokens. A fluency rewrite can flip "we do not assume X" into "we assume not X" | ICLR 2024, ICLR 2025 (frequency 21) |
| A misspelling surviving many commits in body prose | Spellcheck the source before every circulation, since rereading does not surface these | Misspellings inside quoted material, verbatim model outputs, annotator comments and typo-robustness strings are data | Open-human-feedback d7d349d45 (6 instances) |
| A word split or run together by a typing slip | Spellcheck, and expect a cluster in late-edited text | "occursin" is a real Julia function, as are argmax and camel-cased model names | Helix-Agent-Eval-ICML2026 3fe78e4d4 |
| A negated modal written open where the closed form is standard | Use the closed form | "can not only detect but also localise" and contrastive "can act or can not act" reverse if closed | Instructions-shape-Production a272a3c9c |
| A verb disagreeing with a subject that was edited | Recheck the verb whenever a subject changes | Notional and collective agreement are correct — "a number of annotations were discarded" | erc-proposal 505e5a859 (3 instances, all after a subject edit) |
| Wording wrong under grammar or fixed idiom, with a unique recoverable reading | Correct silently as mechanical copy editing, no query | On assessed student work, flag rather than fix | Editors Canada, Ethical Editing of Graduate Student Texts, rev. 2024-08-14, Part 2 p.5 |
| A dangling participle, subject-verb disagreement, or wrong preposition | Fix at the mechanical level, no query, to keep the query list short enough to be read | Editors Canada routes agreement to a flag on assessed student work | World Bank Publications Editorial Style Guide 2020, App. A.1 Level C |

### 4.9 LaTeX plumbing and cross-references (5 rules)

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| A space before \footnote, \cite or \ref | Two different fixes. Delete the space before \footnote. Replace it with a tie before \cite and \ref | Binding "directly" to \citep yields "Argilla(Smith, 2020)" with no space | Open-human-feedback c4bbfcd87 |
| A plain space where the convention is a tie | Tilde before every \ref, \cref and \cite | (none recorded) | Multilingual-Knowledge-Transfer 621180bfb |
| A footnote duplicated at each reuse instead of labelled once | Label once and reference the label later | Uses pages apart in two columns cost a flip back, some venue styles disallow \ref into a footnote, and a second access date needs its own note | Helix-Agent-Eval-ICML2026 e2106cf5e |
| Parenthetical citation where textual is needed or the reverse, missing brackets, nonstandard style | Textual when the authors are the sentence subject, parenthetical otherwise. Grep every citation command and reparse the sentence | Under a numeric style the textual command already renders "Smith et al. [1]", so adding brackets breaks the format | ICLR 2024, ICLR 2025 (frequency 7) |
| Raw label text in the output, a reference pointing at the wrong float, unresolved numbering | Compile twice, then read the final PDF for stray labels and check every number | (none recorded) | ICLR 2024, ICLR 2025 (frequency 5) |

### 4.10 Register for a distant reader (3 rules)

| Test | Fix | Counter-case | Source |
|---|---|---|---|
| Idioms, phrasal verbs, sporting and military metaphors, humour (low-hanging fruit, silver bullet, game changer, tackle head-on) | Replace each with its literal statement | A metaphor that is the field's technical term — pipeline, bottleneck, pruning | Kraicer, The Art of Grantsmanship (HFSP), 3.1 |
| Read once as a specialist checking feasibility detail, once as an outside researcher listing unparseable sentences. Flag both kinds of failure | Plain statement first, technical precision in the following clause. Do not pick one audience | Where the funder splits by audience, as ERC does with B1 and B2, write each part for its own reader | Wellcome, How to write an application; UKRI/EPSRC New Investigator Award |
| Abstract scores near or below Flesch Reading Ease zero, or general scientific jargon in orienting sentences | Reduce general scientific jargon first, then sentence length | A formula cannot tell a necessary technical term from an avoidable one, and no study links a readability score to funding outcome | Plaven-Sigray et al., eLife 2017;6:e27725 |

## 5. Running the pass by hand

Do this after the argument is settled, on the rendered PDF, in one sitting. Steps 1 to 3 are the structural core and the rest are cheap sweeps.

1. **Verb-delay sweep.** For each sentence in the abstract, the aims and the first page, find the head noun of the grammatical subject and count the words to the main verb. Flag anything over seven, or over a quarter of the sentence length. Then count the words before the main clause begins and flag over ten, and count the subject and flag over eight.
2. **Buried-action check on the flagged set.** For each flagged sentence, name the character who acts and the action performed. If the action is sitting in a noun, move it to the verb and put the character in the subject. That one move usually clears the verb delay, the long subject and the missing agent together.
3. **Tail-chain and stack count.** Count consecutive subordinate clauses at each sentence end and flag any chain past one. Scan for runs of three or more nouns acting as one modifier and flag each run.
4. **Word counts.** Sentences over 20 words, with the share of the document reported. Paragraphs over 150 words. Pages with no heading, list or break in the upper half.
5. **Blah test.** Replace every display and every long inline expression with "blah", read the section aloud, and flag any sentence that stops being grammatical or stops carrying a claim.
6. **Density counts.** Bold as a share of body text, with rhetorical spans separated from notation. Italic spans classified the same way. Report both and change nothing without the author's answer.
7. **Scripted sweeps.** Numbers and units against the eight tests in 4.5. Enumerators for orphan labels. List items for construction mismatch. Idiom list. Citation commands and cross-references, read in the render rather than the source.
8. **Proofread last, on the render, after the final reformat**, since typos concentrate in whatever was edited last and the source and the render differ.

The countable diagnostics are steps 1, 3 and 4. If you only have twenty minutes, run those three on the abstract and the aims and stop.

## 6. Where this family is weak

Thirteen of the 44 rules carry provenance "repaired", meaning they were split out of bundled originals that would have damaged correct text. This family had the highest defect rate before repair, and the reason is visible in the repaired tests. Every one of them now carries an exclusion list — math mode, code, filenames, bounded statistics, bold vectors, species binomials — because the parent rule matched on markup or on a character pattern and could not see the function the pattern was serving. A rule in this family that has no exclusion list is more likely to be under-tested than to be genuinely universal.

Single-source dependence is the second weakness. Four rules rest on Williams and Gopen & Swan alone, five on the Stanford Mathematical Writing notes alone, seven on one chapter of Zobel, and two on one item of the JPL Levels of Edit. Eight rules come from mined revisions of one researcher's own papers, several from a single commit, and the comma-splice count of twenty-six comes entirely from one length-capped proposal, so the frequency measures that proposal's compression rather than a general tendency. The thresholds inherit this. Seven words of subject-verb gap, ten words of preamble, twenty words per sentence and 150 words per paragraph are all round numbers from prose guidance rather than measured breakpoints.

Four rules carry no counter-case at all, which for this family is a warning rather than a reassurance. Two of the mined corpus rules were marked too vague and needed a narrower test written for them, and the LaTeX-spacing rule needed splitting into two fixes because "bind directly" applied to \citep deletes a space that has to be there. Set against all of this is section 3. The reviewer corpus says this family is not where the marginal edit pays, so the honest reading is that the structural core in 4.1 through 4.3 earns its place on the strength of the reading-process mechanism, and the rest earns its place by being cheap.
