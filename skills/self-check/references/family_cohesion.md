# Cohesion

## What this family governs

Cohesion is the property that lets a reader move from one sentence to the next, and from one paragraph to the next, without going back. A passage can fail on cohesion while every sentence in it is true, grammatical and well chosen, which is why the failure is nearly invisible in your own draft. The reader experiences it as fatigue rather than as an error, so they blame their own attention, slow down, and stop trusting the argument. In a paper that surfaces as a reviewer naming the writing itself as a weakness, or saying the method cannot be reconstructed from the main text — the ICLR rows in this family record both as complaints that arrive separately from any technical objection. In a proposal it surfaces as a panel member who has to speak for your work from notes and cannot restate what it claims.

## The mechanism

Two ideas generate most of these 42 rules. The first is that structural position carries interpretive meaning on its own, independently of the words filling it. Gopen and Swan's argument is that readers arrive at every sentence with fixed expectations about where certain kinds of material will sit, and they read the sentence through those expectations whether or not the author cooperated. Two slots do nearly all the work. The opening of a sentence, the topic position, tells the reader what the sentence is about and links backward to what they already hold in mind. The closing of the sentence, the stress position, is where the reader spends their greatest interpretive weight, so whatever lands there is taken as the point.

The second idea is that every unit of discourse — clause, sentence, paragraph, section, document — is expected to serve a single function and make a single point. A unit that serves two produces no locatable error, so again the reader blames themselves.

Those two ideas are enough to derive a large fraction of the family, and deriving them is a better use of an hour than memorising the rules. Given that the opening slot is the backward link, old information must precede new information, because a new term arriving in the opening slot has nothing to attach to and must be held uninterpreted until its anchor appears. Given that the opening slot names the topic, the openings of consecutive sentences in one paragraph must form a small related set, or the reader rebuilds the frame every sentence and never accumulates a through-line. Given both, the seam between one sentence's end and the next sentence's beginning is where cohesion is actually judged, so a join sharing no word, synonym, pronoun or connective is a gap the reader must fill by guessing. Given that the closing slot is where emphasis lands, filling it with a citation, a hedge or a restated given wastes the strongest structural cue you have, and a sentence offering three candidate points but only one closing slot forces the reader to pick. Given that readers look for the action of a clause in its verb, a paragraph whose verbs are mostly copulas has hidden its actions inside abstract nouns, where each reader will recover a slightly different reading. Given one point per unit, a paragraph covering two claims should be split and each half should open with the claim it now owns.

Position also scales up. A section, a summary and a whole document each have an opening slot, and the same logic says the claim belongs in it. The reason this matters more in a proposal than in a paper is the reading budget. Gallo measured actual panel discussion at 19 to 29 minutes per application, NIH's own guidance says many reviewers scan the document while listening to the discussion, and NIAID states that every panel member scores every application including the ones they did not read. Under that budget the opening slot of each unit is often the only part that is read at all, so a claim placed late is not merely de-emphasised. It is not delivered.

## The rules, grouped by the mechanism they instantiate

### Position inside the sentence (9 rules)

This is the engine. Every rule here is a way of asking whether the material in a slot is the material that slot signals.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| Sentence opens with unmet information, splits subject from verb, or buries its point mid-sentence | Known material first, verb close behind the subject, new point last | The authors' own hedge is that no fixed algorithm exists and any expectation can be violated productively | Gopen & Swan, American Scientist 78, 1990 |
| Underline each sentence from its start to its main verb, read those strings in order, flag if they are not a small related set or a third are new | Pick the one concept the paragraph is about and move it into the opening slot of most sentences | A related-work paragraph surveying four unrelated systems, or a limitations list, where the shifting topic is the content | Gopen & Swan, 'The Topic Position'; Williams (rev. Bizup) 11th ed., Lesson 5 |
| Take the last eight words of a sentence and the first eight of the next, flag if nothing recurs and no connective bridges | Open the second sentence with the term the first ended on, or add the connective that names the intended relation | A deliberate hard break or a pivot after a digression, where a bridge falsely implies continuation | Gopen & Swan, 'Perceiving Logical Gaps' |
| Familiar material at the end and new material at the start | Invert so the familiar term opens and the new term lands last, changing voice if the inversion needs it | A genuinely new term that is the paragraph's topic and subject of the next several sentences | Williams, Ten Principles 4 and 6, Lesson 5, pp. 68-70, 80-83 |
| Locate syntactic closure and ask whether an aside, citation, hedge or restated given is sitting there | Move the emphasis-worthy phrase to the end and demote the displaced material to a modifier | A sentence whose whole job is to restate a given before a pivot has nothing emphasis-worthy in it | Gopen & Swan, 'The Stress Position' |
| Count plausible points in the sentence against available closing positions, flag when points exceed slots | Add a medial closure or split, rather than cutting words to hit a length target | A summary sentence listing parallel items of equal weight is meant to read as one undifferentiated set | Gopen & Swan, 'The Stress Position' |
| List the main verbs, flag if more than half are copulas or light verbs | Name the actions and promote each to a main verb, then make the acting character the subject | Definitions and identity statements are genuinely copular, and forcing an action verb damages them | Gopen & Swan, 'Locating the Action' |
| Scan for -tion, -ment, -ance, -ity, -sis, -ing nouns sitting as subject of an empty verb | Turn the noun back into a verb and give it its performer as subject, and if the performer is absent report that | A nominalisation referring back to an action already described is doing cohesive work in the opening slot | Williams, Lesson 3, 'Characters', patterns 1-5 |
| Paragraph or sentence opens with a bare demonstrative whose referent is the whole previous paragraph | Name the referent at the opening, keep bare demonstratives inside sentences whose subject is fixed | After a display equation with no short name, the bare demonstrative is the natural resumption | corpus, Multilingual-Knowledge-Transfer 5f9dd4b0d |

### One unit, one point (5 rules)

Same principle at paragraph and section scale. The test is always to ask how many points the unit makes and where its one point sits.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| Read the paragraph and ask what single point its sentences jointly make, flag if two are needed | Split at the seam and open the new paragraph with a sentence naming its point | A short paragraph deliberately staging a contrast holds two propositions on purpose | Gopen & Swan, second set of reader expectations |
| Read only the first sentence of every paragraph in order, flag if that sequence is not the argument | Move the paragraph's claim to its first sentence and let evidence follow | A paragraph whose point needs a definition first should put the claim in sentence two | NIH General Grant Writing Tips, Tip 3; NIH First Level Peer Review |
| One paragraph carries two claims the document assigns to different sections | Name the cut point sentence by sentence, then move each half under the heading that owns it | A paragraph whose content is the relation between the two claims is destroyed by the split | corpus, erc-proposal ff4896a |
| Interpretation is interleaved with the results themselves | Collect interpretation into a discussion section and leave results to the measurements | A chained multi-experiment section must interleave when experiment 2 is motivated by experiment 1 | corpus, Multilingual-Knowledge-Transfer 738df3bd8 |
| A summarising paragraph sits mid-results rather than at a section boundary | Move the summary to the discussion or the section close | In a long results section a mid-section recap is the waypoint that lets the reader follow the fourth subsection | corpus, Multilingual-Knowledge-Transfer c6138ef91 |

### Promises the reader is tracking (6 rules)

An announced count, a forward reference or an early topic sets an expectation the reader actively holds. Broken promises are the one class of prose fault readers catch almost every time.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| For each promised count, check the text delivers that many, in that order, with the same labels | Correct the count and order, or delete the enumeration and let items stand as paragraphs | None. A miscounted enumeration is always an error | Gopen & Swan, 'Perceiving Logical Gaps'; Van Buren & Buehler, The Levels of Edit, JPL 80-1 |
| List topics given a paragraph or more in the first third, search the rest for a return | Connect the topic to a downstream objective in one sentence, or cut it to the clause the argument uses | A topic introduced to be explicitly ruled out of scope belongs early and does not return | Cronan & Deckard, New Faculty Guide, 'Avoid Irritating Your Reviewer' |
| Follow each aim through the Approach and check it is addressed under its own label, in order | Head each Approach block with the aim identifier it delivers and cross-reference where treatment moves | Two aims sharing one platform should describe it once and reference it twice | NIH, Writing Effective Critiques; NIH Reviewer Discussion Cheat Sheet |
| A forward reference points at a section without saying what the reader will find | Say what the target supplies, or cut the reference | A descriptive section title is its own gloss, and a compact deferral list needs no glosses | corpus, Helix-Agent-Eval-ICML2026 b5cc5586e |
| A cross-reference resolves to the section it sits inside | After any section move, resolve every ref in the moved text and delete self-pointers | A float naming its own section is locating work, since floats drift pages from home | corpus, erc-proposal e33c79f |
| A paragraph became redundant after a reordering but stayed in place | Reread the paragraphs that bridged the reordered sections and cut what the new order already does | The redundant paragraph is often the only full statement of a term, the earlier one being an instance | corpus, Helix-Agent-Eval-ICML2026 43e83b1bd |

### Order of introduction across the document (7 rules)

Old before new, applied above the sentence. Every unit should introduce its objects before its operations, and its claim before its background.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| Per section, count sentences of general background before the central claim, flag more than two | Move the claim sentence verbatim with all its qualifiers to the section opening, background after | A claim misread without a prior definition needs the definition first | Przeworski & Salomon, SSRC; Cronan & Deckard |
| A metrics or evaluation section precedes the benchmarks and systems it measures | Order sections so each one's objects are introduced before its operations | When the metric is the contribution, or the metrics are standard, they belong first | corpus, Helix-Agent-Eval-ICML2026 b5cc5586e |
| Section order, paragraph order or emphasis does not match the reading path | Draft a one-line purpose per section and check each depends only on lines above it | A mandated template, or two genuinely parallel contributions forced into false subordination | reviewers, ICLR 2024, ICLR 2025 |
| Read the summary with the rest removed and list every unexplained term, number, acronym or claim | Resolve every dependency inside the summary, cutting scope rather than leaving a pointer | Under a hard summary cap, drop the claim rather than compress it into an unreadable clause | NIH Application Guide FORMS-I, section 7 |
| Read the narrative in five separated sittings stopping at arbitrary points, flag every page-back | Add a re-entry cue at each transition and restate load-bearing numbers rather than pointing back | Restating every number is noise in a short document read in one sitting | Kraicer, The Art of Grantsmanship, HFSP; Reid, IUFRO-SPDC handbook |
| Content needed to judge the paper lives only in the appendix | Every introduction claim needs its support in the main text, appendix holds proofs and extras | At a hard page limit, promoting a forty-row settings table evicts the method description | reviewers, ICLR 2024, ICLR 2025 |
| A float sits pages from its discussion or arrives after the reader first needs it | Place the float on the page of first discussion, or restate the one number inline | A full-page float discussed in three sections, or a conventional page-one teaser figure | reviewers, ICLR 2024, ICLR 2025 |

### The same thing under the same name (4 rules)

A reader links two passages by recognising a repeated term. Renaming the same object breaks the link even when both names are good.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| Compare the argument-carrying noun phrases of the summary against those of the aims | Make the summary's vocabulary a strict subset of the body's, keeping every field-identifying term | A cross-disciplinary proposal may need terms from two fields, so name both and say which panel leads | NSF 04-016, Project Summary; NIAID, Know Your Audience |
| For each published assessment question, find the answering passage and check it uses the question's wording | Head each passage with the funder's own noun phrases, in the order the form asks them | Parroting criteria without answering them is the failure mode this rule invites | UKRI Funding Service guidance; Horizon Europe General Annexes A, D, E |
| The last sentence of a section and the first of the next share no term or consequence | Read consecutive boundaries as pairs and name the step in the opening clause | A section opening a genuinely independent question should start cold | corpus, Multilingual-Knowledge-Transfer 39a9d0688 |
| The same claim is stated in two sections in two voices | Cut the duplicate, after checking whether a qualifying clause survives only in the copy being cut | In an ERC B2 each work package is read separately, so restating the objective is by design | corpus, erc-proposal e33c79f |

### The reader's actual budget (7 rules)

These rules do not add a new principle. They set the stakes for the ones above by pinning down who reads how much.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| A load-bearing claim first appears after page one, or only where a non-assigned panellist would skip | Put problem, central idea and expected outcome on page one in that order, repeat once where developed | Schemes with a scored structured summary, or two-stage schemes, already force this | Gallo et al., PLoS ONE 2013;8(8):e71693; NIAID, Know Your Audience |
| No two or three self-contained sentences exist that the lead reviewer could quote | Write one sentence naming the question and what changes if it is answered, at the head of summary and objectives | Where the whole panel reads the proposal, the quotable line spends space argument could use | NIAID, Target Your Assigned Reviewers; ERC Guide for Peer Reviewers v6.0 |
| Wider relevance exists only as an implication spread across a section | Write two or three standalone relevance sentences where a skimming reader will meet them | An entirely specialist panel, such as ERC Step 2 remote reviewers, does not need the portable statement | Wellcome, How to write an application; EPSRC New Investigator Award |
| Font, size, justification, heading and list style differ across the document and its attachments | Set layout once from the call's requirements, apply to every attachment, check the rendered PDF | Portal-generated attachments carry their own house style, and Horizon Europe permits legible alternatives | EPSRC New Investigator Award; Horizon Europe Annex A; Wellcome (Dr Alex Mold) |
| A passage is in the dense traditional register where a direct version carries the same content | Rewrite toward the accessible end, expecting a real but modest gain | Readers tested were undergraduates, and NSF abstracts with fewer common words drew larger awards | Ryba et al., Frontiers in Psychology 2021;12:714321 |
| A reviewer names the writing, presentation, clarity or readability itself as a weakness | Do a dedicated presentation pass and fix the worst three sections rather than polishing everywhere | none recorded | reviewers, ICLR 2024, ICLR 2025 |
| A core mechanism cannot be reconstructed from the main text alone | Write the method as inputs, each transformation with its symbols, outputs, then a worked pass over one input | A dual-use method where the recipe is the artifact to withhold, or an already-standard pipeline | reviewers, ICLR 2024, ICLR 2025 |

### Report rather than repair (4 rules)

Four rules in this family forbid the fix. Each names a defect visible from the page whose correct resolution needs knowledge only the author holds, so acting on it means inventing content.

| Test | Fix | Counter-case | Source |
| --- | --- | --- | --- |
| Check the passage against eight query triggers, from missing material to internal contradiction | Raise a query when one fires and name which one | The editor's own failure to understand is not always the text's fault, so look the term up first | CIEP, Tomlinson, 'What are queries', 19 January 2024 |
| Look for factual inconsistency, faulty logic, an unclear passage, an incomplete comparison, a vague time reference | Point them out. Do not repair them at this level | At a substantive level the same findings are in scope to fix, so the level sets the routing | World Bank Editorial Style Guide 2020, Appendix A.1, Level C |
| Track every first-person and second-person pronoun and every demonstrative for an ambiguous referent | Point out the ambiguity and let the author name the referent | Where the antecedent is unique and adjacent, spelling it out needs no query | World Bank 2020, Level C, pronoun and demonstrative items |
| Find every qualifier preceding its claim and classify it as a scope restriction or a hedge | Report both classes with the classification and propose nothing | 'For the 40 languages with dumps above 100MB, coverage is complete' cannot have its opening clause moved | Przeworski & Salomon, SSRC; Cronan & Deckard |

## What the corpus adds

Fifteen of the 42 rules come from practice rather than from a guide. Ten were mined from real revisions of this researcher's own repositories, and five from defects ICLR reviewers complained about. They know one thing Gopen and Williams do not, and it is structural. Gopen and Swan describe cohesion faults as drafting faults, arising while a sentence is being written. The corpus rows show that most cohesion faults in a real paper or proposal are produced by an *editing operation* — moving a block between work packages, reordering two subsections, splitting one source paragraph across two headings. That relocates the whole pass. Nine of these ten rules fire at the moment of a move rather than during a read-through, which is why the self-pointing cross-reference rule says the check belongs to the move.

The corpus also carries defects no writing guide has vocabulary for, because they are artifacts of the medium. A `\ref` that resolves to its own containing section, a float pages from its discussion, a settings table stranded in an appendix — none of these exist in the prose Gopen analysed. And the reviewer rows supply the price, which the guides never state. Cohesion appears in ICLR reviews as a named weakness standing on its own, separate from any technical objection.

The smallest and most instructive real edit in the file is a topic-position repair. Before, the sentence opened with `this`. After, it opened with `code-switching`. The note attached to that row observes that edits run in both directions in the corpus, so the rule is about position rather than about avoiding demonstratives. Two other rows are worth reading verbatim for the reasoning they preserve. One reads `this parag. should be removed based on the order of the sec 5.3 and 5.4`, a redundancy created purely by reordering. Another, on a duplicated claim, warns the reviser to check first whether the "keeping the rest as natural as possible" clause survives anywhere else, because it is the design constraint rather than decoration.

## How to run the pass by hand

Start with the reverse outline, because it is cheap and it finds the expensive problems. Read only the first sentence of every paragraph, in sequence, skipping everything else. That sequence should be your argument. Where it is not, you have found either a paragraph whose claim is buried at its end or a paragraph that does not belong. Do this before any sentence-level work, since fixing seams inside a paragraph you are about to delete is wasted effort.

Second, walk the boundaries. Read the last sentence of each section against the first sentence of the next as a pair, and do the same for the seam between consecutive sentences inside any paragraph that felt slow. A seam with no shared term, synonym, pronoun or connective is the finding. Add the term or add the connective that names the relation you actually intend.

Third, run the two mechanical scans, which need no judgement and can be done while tired. Underline each sentence from its start to its main verb and read the underlined strings in order, looking for a topic string that wanders. Then list the main verbs of each paragraph and flag any paragraph where more than half are copulas or light verbs.

Fourth, check the promises. Every announced count, every forward reference, every topic given a paragraph in the opening third. If you have moved any block since the last pass, resolve its cross-references now.

Fifth, simulate the real read. For a proposal, read it in five separated sittings, stopping at arbitrary points rather than at section boundaries, and mark every place you had to page back. For a paper, read the method as though implementing it from the main text alone.

Last, collect the queries. Ambiguous pronouns, leading qualifiers you cannot classify, incomplete comparisons and internal contradictions go into a list for the author. Do not repair them, because their correct resolution depends on what the author meant to assert.

## Where this family is weak

Five rules rest entirely on one source, and that source is a tally of reviewer complaints from ICLR 2024 and 2025 with no mechanism recorded and, in one case, no counter-case either. They tell you what reviewers said. They do not tell you why the defect causes the complaint, so you cannot derive anything from them or predict where they misfire. Seven of the ten corpus rules likewise carry no mechanism field, only a test, a fix and a commit hash, and none of the ten records whether it is decidable. Treat those as observations awaiting an explanation.

The grant rules are the best evidenced in the family, since ten of them cite published funder guidance and two cite measured panel behaviour. That evidence does not transfer. Exactly one rule in this family is scoped to papers, the enumeration-count rule, and it comes from Gopen and Swan by way of a 1980 NASA edit-levels document. Everything specific to ML papers in this family comes from the ICLR complaint tally and from four of this researcher's own repositories. No writing authority addresses cohesion in ML papers directly, so the eight-page limit, the appendix convention, the two-column float, the equation-heavy method section and the rebuttal cycle are all places where the family is running on local extension rather than on evidence. The single-source ICLR rules are where that gap is most visible, and they are the rules most worth checking against your own experience before you trust them with a student's draft.
