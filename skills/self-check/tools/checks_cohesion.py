#!/usr/bin/env python3
"""Cohesion checks: whether a reader can follow the prose without going back.

The spine is Gopen & Swan's reader-expectation mechanics (American Scientist 78(6),
1990). Their own caveat governs this whole module, verbatim: "None of these
reader-expectation principles should be considered 'rules'." Every one of them can be
violated to good effect, and only the author knows whether a given violation is the
content. Consequently:

  * every finding here is tier 'query',
  * no finding proposes a rewrite of a sentence, and
  * `fix` never contains an edit instruction. It names what to confirm, or is empty.

`_gate` enforces all three as a postfilter, so a later edit to a rule cannot quietly ship
a rewrite. That matters more here than in any other family: the ledger's own suggestions
for these rules ("move it into the opening slot", "open the second sentence with the term
the first ended on") are exactly the edits Gopen & Swan say cannot be made mechanically.

Every counter-case that can be decided mechanically is executed as a veto rather than
printed as advice, because a printed counter-case is advice the reader pays to apply and
an executed one is a check. Nine of them are in force:

  * a related-work paragraph surveying several unrelated systems legitimately shifts
    topic -> `_enumerative` vetoes survey sections, citation-dense paragraphs and
    paragraphs whose sentences carry an ordinal enumeration.
  * a limitations list legitimately shifts topic per item -> the same veto covers
    Limitations, Future Work, Broader Impact and Risk sections, and every paragraph
    inside an itemize/enumerate/description.
  * a deliberate hard pivot after a digression should not be bridged, since a bridge
    would falsely imply continuation -> `_PIVOT` vetoes both join rules whenever the
    second sentence announces the break itself. The sentence-level join is tested only
    inside one paragraph, because a paragraph break is itself a signalled discontinuity;
    the section boundary is a separate rule that treats the heading as a bridge.
  * a heading is not a sentence and owes no lexical bridge to the prose under it ->
    `_is_headingish`, and `_is_runin_heading` for the bold run-in kind that renders as
    ordinary text.
  * "shared" and "Sharing" are the same term -> `_stem`/`_shared_stems`.
  * a paragraph that announces its own list is enumerating by design -> `_announces_list`.
  * a unique adjacent antecedent needs no query (the ledger's counter-case for rule 7) ->
    the reference rule fires only where the reference is a paragraph's first word, so
    there is provably nothing adjacent for it to point at.
  * expletive "it" points forward at its own clause and back at nothing ->
    `_EXPLETIVE_IT`.
  * a section whose opening sentence develops the heading's terms is not restating them ->
    the restatement rule requires the opening to add at most two content terms of its own.
    Measured: the two openings in the corpus that do repeat every heading term add 5 and
    17, so the test separates development from restatement rather than guessing at it.

The last four of those were added after a live trial on a real proposal, where each had
produced a class of false positive.

Implemented, nine rules:

  sentence-join-unbridged               ledger 11 / "Perceiving Logical Gaps"
  section-boundary-unbridged            ledger 11 at the widest gap a reader crosses
  paragraph-topic-drift                 ledger 10 / "The Topic Position"
  paragraph-topic-sentence-not-first    ledger 15, narrowed to what can be counted
  paragraph-opens-on-procedure          the topic position of a paragraph's first sentence
  section-opens-restating-heading       the same slot at the opening of a section
  pronoun-antecedent-crosses-paragraph  ledger 7, gated structurally rather than lexically
  forward-promise-unfulfilled           an announced delivery, checked against the delivery
  enumeration-count-mismatch            ledger 14 / the flag-word count

The 16-rule ledger, rule by rule. Six are covered above (7, 10, 11 twice, 14, and 15 in
part). For each of the rest, the decision and the specific missing thing:

  0  a load-bearing claim first appears after the first page -- BLOCKED. Needs pagination.
     Source order is not page order, and nothing in a .tex file says where page one ends.
  1  summary vocabulary against body vocabulary -- BLOCKED. Needs "the noun phrases that
     carry the argument" ranked by importance. Measured on the paper, which does mark its
     summary as an abstract environment: 20 abstract stems, 7 of them absent from the body,
     and all 7 are generic modifiers (build, important, impressive, little, modern, truly).
     A raw set difference finds the register, not the argument, so the missing thing is a
     term-importance judgement and not a parser.
  2  each aim addressed under its own label and in the same order -- BLOCKED. Needs the aim
     identifiers to appear in the Approach. Measured on the ERC B1, which is as
     well-labelled as this corpus gets: the Objectives section carries "Objective 1/2/3" as
     run-in headings, and the Approach names its blocks "The first step", "In the second
     step", "In the third step". Deciding that the second step delivers Objective 2 is the
     judgement the rule is asking for, so a mechanical version can only check the labels
     the author already wrote, which is a different and weaker test.
  3  font, size, justification and list style identical throughout -- BLOCKED. Needs the
     rendered PDF and the call's stated requirements. Neither is an input here.
  4  a topic discussed at length in the first third and never returned to -- BLOCKED. Needs
     a topic's identity tracked across a whole document. The topic-string machinery here is
     paragraph-scoped by construction, and nothing in the source says that a topic named in
     one section is the topic named in another, which is the judgement the rule asks for.
  5  the eight CIEP query triggers -- NOT A DOCUMENT TEST. A rule about the review. It is
     honoured as this module's constraint (report, never repair), not emitted as a finding.
  6  routing a defect by editing level -- NOT A DOCUMENT TEST, same as 5.
  8  content the reviewer needs to judge the paper lives only in the appendix -- BLOCKED.
     Needs a claim matched to its support across two documents, and nothing in the source
     marks which detail a reviewer requires.
  9  a float sits pages away from the text discussing it -- BLOCKED. LaTeX defers floats,
     so distance in .tex is not distance in the PDF; in this corpus every appendix figure
     would report as far from its body reference.
  12 more than half a paragraph's main verbs are copulas or light verbs -- IMPLEMENTABLE
     only with a parser. Built and measured first: 3 paragraphs on the paper, 6 on the B1,
     3 on the B2, so the cap is not what killed it. The count is wrong at the source. The
     rule needs main verbs and `_first_verb` returns first finite verbs, so a passive
     reports its auxiliary: of the 272 sentences in the three documents whose first finite
     verb is a copula or a light verb, 87 are an auxiliary in front of a real action verb
     ("all models are optimised with AdamW"). A third of the evidence is the opposite of
     what the rule claims to have found, and the ledger's counter-case (definitions and
     identity statements are genuinely copular) is not separable from the defect by a count.
  13 an abstract noun as the subject of an empty verb -- IMPLEMENTABLE, and excluded by this
     family rather than by detection. Its only output is a rewrite, which is forbidden here.
     Measured anyway before dropping it: 50 occurrences on the paper, 20 on the ERC B2, 8 on
     the B1, so it is also far past the cap below.
  15 the sentences of background before a section's central claim -- COVERED IN PART. Naming
     "the sentence carrying the central claim" is the judgement itself, so the rule as
     written is BLOCKED. Two decidable slices of it are implemented instead:
     `paragraph-topic-sentence-not-first` at paragraph scope, where the claim's proxy is a
     term three later sentences take as their subject, and `section-opens-restating-heading`
     for the case where the opening sentence carries no information at all.

Built, measured, then removed:

  * `subject-verb-separation` (Gopen & Swan's first principle, at a word-count threshold).
    CUT as taste, not for its count -- it reported 0 on the paper, 1 on the B1, 0 on the B2.
    Gopen & Swan state that none of their principles should be treated as a rule, and a
    word-count threshold is precisely the arbitrary line they warn against: the finding
    "nine words separate the subject from its verb" asserts that eight would have been
    fine. Do not reinstate it, or anything else that fires on a count of words.
  * `bare-demonstrative-subject` (ledger 7, first attempt). The three documents hold 55
    sentences opening on a demonstrative, 9 of them with a verb directly after it, and 0
    survive the antecedent gate. The gate was the problem: counting commas and semicolons
    in the previous sentence counts clauses, not antecedents. Without it the rule reports 9
    occurrences whose antecedent is, in the ledger's own counter-case, usually unique and
    adjacent. Ledger 7 is now covered by the structural gate described above, which needs no
    estimate of how many antecedents the previous sentence offered.

One deliberate non-change. `_stem` was defined twice in this file, and the crude
definition shadowed a careful one that maps "ization" to "ize". The trial notes recommend
deleting the crude one and letting the careful one apply. Only the dead definition was
deleted here, so the crude one stays in force: swapping them changes what bridges what, and
therefore changes the counts of the two join rules, which is a deliberate decision to take
against measurements rather than a side effect of a coverage pass. `_same_term`, which the
rules added in this pass use, closes the same gap locally by treating a shared
five-character prefix as one term.

One test judged wrong as written: ledger 11 says to compare "the last eight words" with
"the first eight". Applied to raw words that window is mostly function words, and it
reported joins that share a topic term nine words back. The implementation compares the
last and first eight CONTENT words, and treats a demonstrative or pronoun opening as a
bridge in its own right, which is what the paper's "Perceiving Logical Gaps" section
actually argues.

One bug fixed in this pass. `enumeration-count-mismatch` counted a list's items from the
offset of the list's first paragraph, which lands on the text of the first item, past its
\item. Every itemize therefore counted one short, and a correct three-item list announced
as "three reasons" reported as a mismatch -- a false positive on the one rule in this
family whose ledger entry records no counter-case. `_count_items` now counts over the
enclosing environment and excludes the items of any nested list.

Measured, submission stage (paper / ERC B1 / ERC B2):

  sentence-join-unbridged                8 / 3 / 5
  section-boundary-unbridged             1 / 1 / 0
  pronoun-antecedent-crosses-paragraph   2 / 0 / 0
  paragraph-opens-on-procedure           2 / 0 / 0
  paragraph-topic-drift                  0 / 0 / 0
  paragraph-topic-sentence-not-first     0 / 0 / 0
  section-opens-restating-heading        0 / 0 / 0
  forward-promise-unfulfilled            0 / 0 / 0
  enumeration-count-mismatch             0 / 0 / 0

22 findings over 236KB of source, no rule past 8 on any one document. The fourth test
document, main_acl.tex, is a shell whose sections are \input, so it holds no prose and
reports nothing; its seven section files were measured separately and report 6 findings,
never more than 2 of one rule in one file. Five further ERC drafts (plan, scratchfile,
old_main, Rstat, b2.review) were measured as a precision check on documents the rules were
not tuned against: 26 sentence-join findings, 11 of them in one loose planning file, and 1
reference finding each in old_main and scratchfile, both of them true.

Five rules fire on nothing in this corpus, which is the correct answer for it and not
evidence that they work. Each was therefore verified against a constructed document,
positive and negative:

  * forward-promise-unfulfilled fires on a promise resolved through \label whose target
    section carries none of the promised terms, and on an unaddressed "we return to X
    below"; it stays silent when the later section delivers the terms.
  * enumeration-count-mismatch fires on "three contributions" followed by two ordinals and
    on "four reasons" followed by three \items, stays silent when the counts agree, and
    ignores the items of a nested list.
  * paragraph-topic-sentence-not-first fires on a paragraph whose opening sentence is
    general background and whose next three sentences all take one term as their subject;
    it stays silent when that term appears in the opening sentence.
  * section-opens-restating-heading fires on "Cross-lingual knowledge transfer" followed by
    "Cross-lingual knowledge transfer is the topic of this section", and stays silent on a
    heading whose opening sentence develops it.
  * pronoun-antecedent-crosses-paragraph, which does fire twice on the paper, was also run
    against a constructed set: a bare "This shows" after a paragraph break fires, "This
    sample shows" does not, expletive "It is likely that ..." does not, and the same
    sentence without a paragraph break does not.

Two rules depend on a claim the paragraph model cannot make on its own -- that a sentence
is the FIRST of its paragraph. The model drops any sentence that renders as markup residue,
and a dropped sentence promotes the next one into the opening slot: the first version of
the reference rule reported a paragraph's third sentence as its opening, because "Our
\ceq\ definition ..." renders with a stray backslash. `_starts_paragraph` asks the source
instead, and both rules go through it.

Interface: checks(src, spans, ctx) -> list[dict]   (see CHECKS_API.md)
"""
import os
import re
import sys
import bisect
import pathlib
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex

FAMILY = 'cohesion'

# Per-rule ceiling on one document. The audit bar is tighter than this number -- a new
# cohesion rule past about 12 findings on one document is reading the author's style -- and
# every rule here was tightened until it sat far under the bar on the test corpus, the
# highest being 8. The cap only guards a document shaped unlike any of them.
# A cohesion rule that fires more often than this is
# reading the author's style rather than a break in the argument, and a reader who is
# handed twenty "the reader must supply the link" notes stops reading all of them. Every
# rule below is tightened to sit under the cap on the test corpus; the cap only guards a
# document shaped unlike it.
CAP = 15

# ------------------------------------------------------------------- structure lexicons
_HEAD_CMD = (r'(chapter|section|subsection|subsubsection|paragraph|subparagraph|'
             r'cvsection|cvsubsection)')
_LEVEL = {'chapter': 0, 'section': 1, 'cvsection': 1, 'subsection': 2, 'cvsubsection': 2,
          'subsubsection': 3, 'paragraph': 4, 'subparagraph': 5}

# Macro arguments that are not authored prose. Draft notes and template boilerplate render
# into the prose stream and would otherwise be joined to the sentences around them, which
# manufactures both a topic shift and a missing bridge at every note.
_ANNOT_CMD = (r'(?:todo|todonotes|note|bob|ym|adam|lc|wzm|temp|cready|instruction|ercscore|'
              r'taglegend|marginpar|'
              r'footnote|thanks|caption|captionof|reviewer|highlight|comment)')

# Sections whose content is a list of unrelated things. Every topic rule is silent here:
# the shift IS the content, which is the ledger's counter-case for rule 10.
_ENUM_SECTION = re.compile(
    r'related work|prior work|previous work|background|literature|limitation|'
    r'future work|broader impact|ethic|acknowledg|reference|appendix|'
    r'risk|contingenc|gantt|deliverable|milestone|curriculum|track record|'
    r'funding|grant|team|publication|award|bibliograph|recognition|expertise|'
    r'supervis|teaching|invited|talks|service|career|mentor|membership|patent|'
    r'prize|honour|honor|fellowship|host institution|environment|feasibility|'
    r'resources|budget|profile', re.I)

# ------------------------------------------------------------------- cohesion lexicons
# An explicit connective bridges a join on its own: the author has named the relation.
_CONNECTIVE = re.compile(
    r'^(?:and|but|or|yet|so|nor)\b|'
    r'^(?:however|therefore|thus|hence|consequently|accordingly|moreover|furthermore|'
    r'additionally|also|besides|meanwhile|similarly|likewise|conversely|instead|'
    r'nevertheless|nonetheless|still|indeed|overall|together|finally|lastly|next|then|'
    r'first|firstly|second|secondly|third|thirdly|fourth|again|rather|equally|'
    r'specifically|notably|importantly|crucially|concretely|formally|briefly|'
    r'otherwise|alternatively|elsewhere|already|thereby|whereas|while|because|since|'
    r'although|though|when|if|unless|until|once|despite|given|assuming|whether|'
    r'even|only|both|neither|either)\b|'
    # "in contrast", "as a side effect", "for the same reason": a named relation, with up
    # to three words of slack, because "as a side effect" and "as an effect" are one thing.
    r'^(?:in|by|as|for|on|at|to|with|of|from|after|before|beyond|under|through)\s+'
    r'(?:\w+\s+){0,3}?'
    r'(?:contrast|addition|particular|short|turn|fact|words|case|cases|way|ways|'
    r'comparison|consequence|consequences|practice|principle|sum|summary|end|result|'
    r'results|hand|effect|effects|general|respect|respects|following|response|return|'
    r'exchange|reason|reasons|example|instance|light|absence|presence|place|stead|'
    r'contrary|same|latter|former|above|earlier|previous|outset|first)\b|'
    r'^(?:as long as|so long as|as far as|as soon as|insofar as|provided that|'
    r'in order to|in order that|only if|only when|only once)\b|'
    r'^(?:that is|for example|for instance|e\.g\.|i\.e\.|to this end|to that end|'
    r'as such|more precisely|more generally|put differently|said differently|'
    r'taken together|put together|either way|in any case)\b', re.I)


# A back-reference anywhere in the opening window bridges, not only in first position:
# "Using this combined framework we pretrain ..." reaches back with its third word.
# "that" is excluded because a complementizer ("we show that") is not a back-reference.
_ANAPHOR_IN = re.compile(
    r'\b(?:this|these|those|it|its|they|them|their|such|here|both|either|neither|'
    r'the same|the former|the latter|the above|the resulting|the rest|the others|'
    r'the two|the three|the other|all of|each of|one of)\b', re.I)
# "that" only in the first two words: "Attributing that failure ..." reaches back, while
# "we show that ..." is a complementizer and reaches nowhere.
_THAT_BACK = re.compile(r'^(?:\w+\s+)?(?:that|those)\s+[a-z]', re.I)
# A connective adverb anywhere in the opening window has named the relation, even when it
# is not the first word: "The research design therefore seeks ..." is bridged by
# "therefore" sitting in fourth position.
_CONN_IN = re.compile(
    r'\b(?:however|therefore|thus|hence|consequently|accordingly|moreover|furthermore|'
    r'also|instead|nevertheless|nonetheless|conversely|similarly|likewise|then|again|'
    r'further|additionally|besides|equally|'
    r'rather|too|still|already|indeed|meanwhile|otherwise|thereby|because|since|'
    r'while|whereas|although|though|despite|unlike|yet)\b', re.I)

# For a topic string the test is more generous than for a sentence opening: "Each stopped
# where ...", "Another route ...", "The latter ..." are all pointing back at the previous
# topic rather than naming a new one, and a bare "each" or "another" in first position is
# not the ambiguous case that a mid-sentence one would be.
_ANAPHOR_TOPIC = re.compile(
    r'^(?:this|these|those|that|it|its|they|them|their|such|here|both|either|neither|'
    r'each|another|others|one|all|the same|the former|the latter|the above|the rest|'
    r'the others|the two|the three|the other|the first|the second|the third|the next|'
    r'the last|the remaining|the resulting|the final)\b', re.I)

# The second sentence announces the break itself. Bridging a declared pivot would falsely
# imply continuation, which is the ledger's counter-case for rule 11.
_PIVOT = re.compile(
    r'^(?:however|but|yet|instead|conversely|in contrast|by contrast|on the other hand|'
    r'nevertheless|nonetheless|that said|even so|unrelated|separately|independently|'
    r'aside from|apart from|setting aside|leaving aside|returning|to return|we now|'
    r'we next|we then|before|first|finally|lastly|meanwhile|elsewhere|a different|'
    r'another|the remaining|two further|one further|note that|recall that|'
    r'as an aside|in passing|orthogonal)\b', re.I)

# A paragraph opening on the document's own machinery rather than on its subject.
_PROCEDURE_OPEN = re.compile(
    r'^(?:in|for)\s+this\s+(?:section|subsection|paper|work|study|chapter|part|'
    r'appendix|proposal|paragraph)\b|'
    r'^this\s+(?:section|subsection|paper|work|study|chapter|part|appendix|proposal)\s+'
    r'(?:\w+ly\s+)?(?:describ|present|discuss|introduc|review|cover|explain|report|'
    r'summari|outlin|detail|examin|address|turn|proceed|begin|is\s+organi|'
    r'is\s+structur|contain)\w*\b|'
    r'^(?:we|i)\s+(?:now|next|first|then|also|finally|briefly)?\s*'
    r'(?:turn|move|proceed|begin|start|continue|conclude|close)\b|'
    r'^(?:we|i)\s+(?:now|next|first|then|also|finally|briefly)?\s*'
    r'(?:describe|present|discuss|introduce|review|outline|summari[sz]e|report|detail|'
    r'explain)\s+(?:here|below|next|now|first|in\s+(?:this|the)\s+'
    r'(?:section|subsection|paper|work|appendix|remainder|rest|following))\b|'
    r'^(?:the\s+)?(?:remainder|rest|structure|organi[sz]ation|outline)\s+of\s+'
    r'(?:this|the)\s+(?:paper|section|proposal|work|document|chapter)\b|'
    r'^in\s+(?:what\s+follows|the\s+following|the\s+remainder|the\s+rest)\b|'
    r'^(?:before|having)\s+(?:we\s+)?(?:proceed|turn|describ|present|introduc|'
    r'establish|show|discuss|explain)\w*\b|'
    r'^(?:as|so\s+far)\s+(?:we\s+)?(?:noted|mentioned|described|discussed|saw|'
    r'explained|argued)\s+(?:above|earlier|previously)\b', re.I)

# A promise that something arrives later in the document.
_PROMISE = re.compile(
    r'\b(?:we|i)\s+(?:will|shall)\s+(?:\w+ly\s+|also\s+|then\s+|later\s+|first\s+|'
    r'next\s+|now\s+)*'
    r'(show|prove|demonstrate|describe|present|discuss|introduce|analy[sz]e|report|'
    r'return|revisit|explain|argue|address|cover|detail|examine|quantify|establish|'
    r'evaluate|compare|derive|verify|see)\b|'
    r'\bwe\s+(?:return|come\s+back|turn\s+back)\s+to\b|'
    r'\b(?:is|are)\s+(?:described|discussed|presented|analy[sz]ed|reported|addressed|'
    r'deferred|taken\s+up|treated|given|shown|proved|established)\s+'
    r'(?:in\s+(?:section|sec\.|appendix|app\.|‡)|below|later|'
    r'in\s+(?:what\s+follows|the\s+following))', re.I)
# A promise pointing forward without naming where.
_VAGUE_FORWARD = re.compile(r'\b(?:below|later|in\s+what\s+follows|in\s+the\s+following|'
                            r'subsequently|in\s+due\s+course|shortly)\b', re.I)

_ENUM_HEAD = re.compile(
    r'\b(two|three|four|five|six|2|3|4|5|6)\s+'
    r'(?:\w+(?:ly)?\s+){0,2}'
    r'(contributions?|reasons?|factors?|steps?|stages?|phases?|components?|properties|'
    r'questions?|objectives?|challenges?|aims?|goals?|criteria|ways?|respects?|kinds?|'
    r'types?|sources?|limitations?|observations?|findings?|assumptions?|conditions?|'
    r'requirements?|hypotheses|axes|dimensions?|claims?|effects?|mechanisms?|'
    r'strategies|variants?|settings?|regimes?|difficulties)\b', re.I)
_NUMW = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
         '2': 2, '3': 3, '4': 4, '5': 5, '6': 6}
_ORDINALS = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth')

# Finite verb forms. Detection is deliberately incomplete: a sentence whose main verb is
# not recognised yields no finding at all, which costs a miss and never a false positive.
# The -s forms of bases whose plural noun is common in this register ("results", "uses",
# "changes", "shares", "means", "sets") are left out on purpose: "The results show" must
# read "results" as the subject head, not as the verb.
_VERBS = set("""
is are was were be been being am isn't aren't wasn't weren't
has have had having hasn't haven't hadn't do does did done doesn't didn't don't
will would can could may might shall should must cannot can't won't wouldn't couldn't
shows showed shown show finds found find reports reported report measured measure
trains trained train evaluates evaluated evaluate tested testing compares compared compare
observes observed observe demonstrates demonstrated demonstrate suggests suggested suggest
indicates indicated indicate implies implied imply explains explained explain
describes described describe presents presented present introduces introduced introduce
proposes proposed propose argues argued argue claimed assumes assumed assume
requires required require allows allowed allow enables enabled enable
prevents prevented prevent caused affects affected affect influenced
increased decreased reduces reduced reduce improves improved improve changed
depends depended depend relies relied rely consists consisted consist
contains contained contain includes included include follows followed follow
precedes preceded precede appears appeared appear seems seemed seem
remains remained remain becomes became become occurs occurred occur
exists existed exist emerges emerged emerge persists persisted persist arises arose arise
holds held hold applies applied apply yields yielded yield produces produced produce
generates generated generate predicts predicted predict estimates estimated estimate
computes computed compute calculates calculated calculate derives derived derive
obtains obtained obtain achieves achieved achieve reaches reached reach
exceeds exceeded exceed outperforms outperformed outperform matched
shared transferred generalizes generalized generalize generalises generalised generalise
learns learned learnt learn mapped tokenizes tokenized tokenize injects injected inject
mixed sampled selects selected select chooses chose choose defines defined define
denotes denoted denote calls called call considers considered consider addressed
answered asks asked ask raises raised raise noted recalls recalled recall reviewed
summarizes summarized summarize concludes concluded conclude
establishes established establish confirms confirmed confirm verifies verified verify
validates validated validate replicates replicated replicate fails failed fail
lacks lacked lack loses lost lose gained benefited helped supported
provides provided provide gives gave give takes took take makes made make
builds built build creates created create develops developed develop designed
implements implemented implement performs performed perform carries carried carry
conducts conducted conduct analyzes analyzed analyze analysed analyse
identifies identified identify detects detected detect reveals revealed reveal
captures captured capture represents represented represent encodes encoded encode
aligns aligned align merges merged merge separates separated separate
combines combined combine adds added add removes removed remove keeps kept keep
leaves left leave turned begins began begin started ended
continues continued continue extends extended extend expands expanded expand scaled
grows grew grow dropped rises rose rise falls fell fall varies varied vary
differs differed differ corresponds corresponded correspond relates related relate
linked connects connected connect bridged meant mattered counted worked
serves served serve aimed planned expects expected expect
anticipates anticipated anticipate hypothesizes hypothesized believes believed believe
knows knew know sees saw see looked treats treated treat named labelled labeled
stored releases released release publishes published publish writes wrote write
says said say stated tells told tell lets let
""".split())

_STOP = set("""
the a an and or but of in on to for with by from as at that this these those it its
we our us they them their he she his her is are was were be been being am not no
which who whom whose there here then than thus so such both each either neither
can could may might will would shall should must do does did done have has had
if unless until while whereas when where how what why any some more most other others
one two three also only very much many few own same able across over under between
into through during after before about above below within without against upon
i my me you your he'd it's don't
""".split())


# A paragraph-opening reference has nothing before it inside its own paragraph, so its
# antecedent is necessarily across the break. "This" with a noun after it ("This mapping")
# carries its own antecedent and is excluded; only the bare forms are collected.
_OPEN_REF = ('this', 'these', 'those', 'such', 'it', 'they', 'them', 'its', 'their')
# Expletive "it" points forward at a clause, not back at anything: "It is likely that ...".
_EXPLETIVE_IT = re.compile(
    r'^it\s+(?:is|was|are|were|has|had|will|would|can|could|may|might|should|must|'
    r'does|did|remains|follows|turns|appears|seems|becomes|proves|helps|takes|makes|'
    r'matters|suffices|holds)\b[^.]{0,90}?'
    r'\b(?:that|to|whether|how|why|when|if|for|because)\b', re.I)


# ------------------------------------------------------------------------------ output
def _F(rule, offset, cost, blocks, text, fix=''):
    """One finding. Tier is 'query' for every rule in this family, by construction."""
    return {'rule': rule, 'family': FAMILY, 'offset': int(offset), 'tier': 'query',
            'cost': cost, 'blocks': bool(blocks), 'text': text, 'fix': fix}


# An edit instruction. Gopen & Swan's principles are not rules, so none of them licenses
# one, and `_gate` drops any finding that carries one.
_EDIT = re.compile(
    r'\b(?:rewrite|rewritten|recast|rephrase|reword|rearrange|reorder|restructure|'
    r'move|shift|relocate|promote|demote|open\s+(?:the|this|it|with)|start\s+with|'
    r'add|insert|append|prepend|replace|substitute|delete|remove|drop|cut|strip|'
    r'split|merge|join|bridge|shorten|tighten|change|turn\s+\w+\s+into|make\s+the)\b',
    re.I)


def _gate(findings):
    """Enforce the family's three invariants, whatever a rule tried to emit.

    Tier must be 'query', `fix` must not read as an edit instruction, and no finding may
    carry a suggested replacement sentence. Checked here rather than trusted at each call
    site, because the ledger's suggestions for these rules ARE rewrites and the next
    person to edit this file will be tempted to paste one in.
    """
    out = []
    for f in findings:
        if f.get('tier') != 'query':
            continue
        if _EDIT.search(f.get('fix') or ''):
            continue
        if re.search(r'\bwrite\b.*"', f.get('fix') or ''):
            continue
        out.append(f)
    return out


# ------------------------------------------------------------------------------ source
def _brace_end(src, i):
    """Index just past the '}' closing the group whose '{' sits at i-1."""
    depth, j = 1, i
    while j < len(src) and depth:
        if src[j] == '\\':
            j += 2
            continue
        depth += (src[j] == '{') - (src[j] == '}')
        j += 1
    return j


def _headings(src):
    """Sectioning commands in source order: offset, level, rendered title, arg range."""
    out = []
    for m in re.finditer(r'\\' + _HEAD_CMD + r'\*?\s*(?:\[[^\]]*\])?\s*\{', src):
        end = _brace_end(src, m.end())
        title = re.sub(r'\s+', ' ', ex._render(src[m.end():max(m.end(), end - 1)])).strip()
        out.append({'off': m.start(), 'level': _LEVEL[m.group(1)], 'title': title,
                    'arg': (m.end(), end)})
    return out


def _annot_ranges(src):
    """Argument ranges of note, todo and template-boilerplate macros, plus captions.

    Up to four consecutive brace groups are consumed, because the paper's note macro is
    \\note[opt]{author}{colour}{text} and only the last group holds the prose.
    """
    out = []
    for m in re.finditer(r'\\' + _ANNOT_CMD + r'\b\s*(?:\[[^\]]*\])*\s*(?=\{)', src):
        j = m.end()
        for _ in range(4):
            if j >= len(src) or src[j] != '{':
                break
            j = _brace_end(src, j + 1)
        out.append((m.start(), j))
    return out


def _inside(off, ranges):
    return any(a <= off < b for a, b in ranges)


def _at(sp, phrase, fallback=None):
    """Offset into src for a rendered fragment, relocated by its own leading tokens.

    Rendering is not offset preserving inside a span, so the fragment is found by matching
    its first tokens against the span's source, longest run first.
    """
    base = sp.start if fallback is None else fallback
    toks = re.findall(r"[A-Za-z][A-Za-z'-]{2,}|\d+(?:\.\d+)?", phrase)[:5]
    for n in (5, 4, 3, 2, 1):
        if len(toks) < n:
            continue
        pat = r'.{0,60}?'.join(re.escape(w) for w in toks[:n])
        m = re.search(pat, sp.text, re.S)
        if m:
            return sp.start + m.start()
    return base


def _regions(src, name):
    """(body_start, body_end) for each \\begin{name}...\\end{name}, nesting aware."""
    op = re.compile(r'\\begin\s*\{' + name + r'\*?\}')
    cl = re.compile(r'\\end\s*\{' + name + r'\*?\}')
    marks = sorted([(m.start(), m.end(), 1) for m in op.finditer(src)] +
                   [(m.start(), m.end(), -1) for m in cl.finditer(src)])
    out, stack = [], []
    for s, e, kind in marks:
        if kind == 1:
            stack.append(e)
        elif stack:
            out.append((stack.pop(), s))
    return sorted(out)


def _starts_paragraph(src, off, sent=''):
    """True when `off` is the first authored word after a paragraph break.

    The paragraph model drops any sentence that renders as markup residue, and a dropped
    sentence promotes the one after it to the head of the paragraph. That is how the first
    version of the reference rule reported a paragraph's THIRD sentence as its opening:
    "Our \\ceq\\ definition ..." renders with a stray backslash, `_is_prose` rejected it,
    and the sentence two positions later inherited the slot. Any rule whose claim is "this
    is the paragraph's first sentence" must ask the source, not the model.

    A paragraph also starts after a heading, after an environment edge and after an
    \\item, so those count as breaks; the heading's own argument is stripped from the lead
    rather than read as prose. Indentation control, a label and vertical space may sit in
    front of the first word. So
    may the first word itself: `_at` locates a sentence by its first token of three letters
    or more, so a two-letter opening ("It also has ...") is left behind in the lead, and a
    lead that is a prefix of the sentence is still the paragraph's opening.
    """
    off = int(off)
    m = None
    for m in re.finditer(r'\n[ \t]*\n|\\par\b|\\item\b|'
                         r'\\(?:begin|end)\s*\{[a-zA-Z*]+\}', src[:off]):
        pass
    if m is None:
        return False
    lead = re.sub(r'(?<!\\)%[^\n]*', '', src[m.end():off])
    lead = re.sub(r'\\(?:label|vspace|hspace|setlength|phantomsection|' + _HEAD_CMD +
                  r')\*?\s*(?:\[[^\]]*\])?\s*(?:\{[^{}]*\})+', ' ', lead)
    lead = re.sub(r'\\[A-Za-z@]+\*?|\\\\', ' ', lead)
    res = re.sub(r'[^A-Za-z]', '', lead).lower()
    if not res:
        return True
    return len(res) <= 12 and re.sub(r'[^A-Za-z]', '', sent or '').lower().startswith(res)


def _list_regions(src):
    """Body ranges of every itemize, enumerate and description, innermost last."""
    return sorted(_regions(src, 'itemize') + _regions(src, 'enumerate') +
                  _regions(src, 'description'))


def _count_items(src, off):
    """Top-level \\item count of the list containing `off`, or 0 when there is none.

    Counted over the enclosing environment rather than from `off` forward. A list
    paragraph's own offset lands on the text of the FIRST item, past its \\item, so
    counting from there reported every list one item short -- which turned a correct
    three-item enumeration announced as "three reasons" into a mismatch. Items of a
    nested list are not items of this one, so they are excluded.
    """
    regs = _list_regions(src)
    here = [(a, b) for a, b in regs if a <= off < b]
    if not here:
        return 0
    a, b = min(here, key=lambda r: r[1] - r[0])
    inner = [(x, y) for x, y in regs if a < x and y <= b]
    n = sum(1 for m in re.finditer(r'\\item\b', src[a:b])
            if not _inside(a + m.start(), inner))
    return n if n >= 2 else 0


def _is_definition_file(src, path):
    """A macro file has no prose to check, and its rendered text is nonsense."""
    if re.search(r'\\begin\s*\{document\}', src):
        return False
    defs = len(re.findall(r'\\(?:new|renew|provide)command|\\def\b|\\DeclareMathOperator|'
                         r'\\usepackage', src))
    return defs >= 5 or os.path.basename(path or '').lower().startswith(
        ('macro', 'command', 'lcommand', 'preamble', 'style'))


# ------------------------------------------------------------------------------ words
def _tok(s):
    """Words, numbers and the punctuation that interrupts a clause, in order."""
    return re.findall(r"[A-Za-z][A-Za-z'\u2019-]*|\d+(?:[.,]\d+)*|--|[,;:]", s)


def _stem(w):
    """Crude suffix stripping, enough that "shared" and "Sharing" bridge to each other."""
    w = w.lower()
    for suf in ('ations', 'ation', 'ing', 'edly', 'ed', 'es', 'ly', 's'):
        if len(w) - len(suf) >= 4 and w.endswith(suf):
            return w[:-len(suf)]
    return w


def _shared_stems(a, b):
    return bool({_stem(x) for x in a} & {_stem(y) for y in b})


def _same_term(term, stems):
    """True when `stems` holds the same term as `term`, allowing for morphology.

    Stemming is crude by design, so "tokenizer" and "tokenization" reduce to different
    stems and a strict test would call a paragraph topicless while it repeats one word.
    A shared five-character prefix is therefore treated as the same term. It over-merges
    ("transfer" with "translation"), which costs findings and never invents one.
    """
    st = _stem(term)
    for w in stems:
        if w == term or _stem(w) == st:
            return True
        if len(term) >= 5 and len(w) >= 5 and (w[:5] == term[:5]):
            return True
    return False


def _content(s):
    """Content-word stems in order, hyphens treated as spaces."""
    t = re.sub(r'[-\u2010-\u2015]', ' ', s.lower())
    out = []
    for w in re.findall(r"[a-z][a-z']{1,}", t):
        if w in _STOP or len(w) < 3:
            continue
        out.append(_stem(w))
    return out


def _first_verb(toks):
    """Index of the sentence's first finite verb, or None.

    Conservative on purpose. An infinitive ("to show"), a verb inside a relative clause
    that opens the sentence, and anything not in the closed form list are all passed over,
    which loses findings rather than inventing them.
    """
    for i, w in enumerate(toks):
        if w.lower() not in _VERBS:
            continue
        if i and toks[i - 1].lower() == 'to':
            continue                                # infinitive, not the main verb
        return i
    return None


# ----------------------------------------------------------------- document structure
_PB = '\x01'        # paragraph break: a blank line, a heavy environment, an env name
_GLUE = ' \u2022 '  # inline math: the sentence continues past it

_ABBR = ('e.g.', 'i.e.', 'et al.', 'cf.', 'vs.', 'Fig.', 'Figs.', 'Tab.', 'Eq.', 'Eqs.',
         'Sec.', 'Secs.', 'App.', 'Ref.', 'Refs.', 'No.', 'approx.', 'resp.', 'w.r.t.',
         'Dr.', 'Prof.', 'Mr.', 'Ms.', 'St.', 'Inc.', 'ca.', 'al.', 'Alg.', 'Thm.')


def _split_sentences(text):
    """(sentence, offset_in_text) with abbreviations, initials and decimals protected."""
    prot = text
    for a in _ABBR:
        prot = prot.replace(a, a.replace('.', '\x00'))
    prot = re.sub(r'\b([A-Z])\.', '\\1\x00', prot)
    prot = re.sub(r'(\d)\.(\d)', '\\1\x00\\2', prot)
    out, start = [], 0
    for m in re.finditer(r'(?<=[.!?])["\')\]]?\s+', prot):
        out.append((start, m.start()))
        start = m.end()
    out.append((start, len(prot)))
    res = []
    for a, b in out:
        s = prot[a:b].replace('\x00', '.').strip()
        if not s:
            continue
        # A piece opening in lower case is a split artefact, not a sentence: the period
        # before it belonged to an abbreviation or a citation marker. Merged back, because
        # every rule here reads the opening words of a sentence and a fragment has none.
        if res and s[0].islower():
            res[-1] = (res[-1][0] + ' ' + s, res[-1][1])
            continue
        res.append((s, a))
    return res


def _is_prose(s):
    """Reject rendered markup residue: gantt bars, tikz options, key=value debris."""
    if '=' in s or '\\' in s or '{' in s or '}' in s:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", s)
    if len(words) < 4:
        return False
    letters = sum(ch.isalpha() or ch.isspace() for ch in s)
    return letters / max(1, len(s)) > 0.82


def _split_at_titles(text, titles):
    """Cut a paragraph wherever a heading title appears, not only at its start.

    A heading renders as its own title text, and a source that puts no blank line after
    \\section glues the title to the prose that follows it. Left joined, a section-opening
    sentence appears to share its terms with the heading and the section model is off by
    one paragraph. Returns (text, opens_a_section) pairs in order.
    """
    out, opened = [], False
    while True:
        best = None
        for t in titles:
            if len(t) < 5:
                continue
            q = text.find(t)
            while q > 0 and text[q - 1].isalnum():
                q = text.find(t, q + 1)
            if q >= 0 and (best is None or q < best[0]):
                best = (q, t)
        if best is None:
            break
        q, t = best
        head = text[:q].strip(' .,;:\u2020\u2021')
        if head:
            out.append((head, opened))
        text, opened = text[q + len(t):].lstrip(' .,;:\u2020\u2021'), True
    out.append((text, opened))
    return out


def _paragraphs(src, spans, heads):
    """Paragraphs of authored prose, in document order, each with its sentences.

    Built from `.rendered` on text spans only. Three source facts are handled, and each was
    found by looking at what the extractor actually produced on the test corpus:

      * inline math is glue and a heavy environment is a break. Gluing a paragraph to
        whatever follows a figure invents an adjacency no reader sees, which is the one
        thing a join rule must never do.
      * an environment name renders as a bare word on its own line (\\begin{itemize}
        becomes "itemize", \\begin{abstract} becomes "abstract"), so those lines are
        breaks, not sentences.
      * a heading renders as its own title text, so the title is stripped from the head of
        the paragraph that follows it. Left in, every section-opening sentence would
        appear to share its terms with the heading.
    """
    titles = sorted({h['title'] for h in heads if h['title']}, key=len, reverse=True)
    frags = []
    for sp in spans:
        if sp.kind not in ('text', 'mask'):
            # A line comment, a comment environment or an annotation body. None of them is
            # the document's prose, and an annotation sits INSIDE a sentence, so it
            # contributes nothing and does not break the paragraph either.
            continue
        if sp.kind == 'mask':
            head = sp.text.lstrip()[:8]
            frags.append((_GLUE if head.startswith(('$', '\\[', '\\(')) else _PB, sp))
            continue
        txt = sp.rendered
        if not txt.strip():
            if re.search(r'\n[ \t]*\n', txt):
                frags.append((_PB, sp))
            continue
        envs = {e for e in re.findall(r'\\(?:begin|end)\s*\{(\w+)\*?\}', sp.text)}
        if envs:
            txt = re.sub(r'(?m)^[ \t]*(?:' + '|'.join(re.escape(e) for e in envs) +
                         r')[ \t]*$', _PB, txt)
        txt = re.sub(r'\n[ \t]*\n', _PB, txt)
        frags.append((txt, sp))

    bufs, cur = [], []
    for txt, sp in frags:
        if txt == _PB:
            if cur:
                bufs.append(cur)
                cur = []
            continue
        if txt == _GLUE:
            if cur:
                cur.append((_GLUE, sp))
            continue
        parts = txt.split(_PB)
        for k, part in enumerate(parts):
            if k and cur:
                bufs.append(cur)
                cur = []
            if part.strip():
                cur.append((part, sp))
    if cur:
        bufs.append(cur)

    hoff = [h['off'] for h in heads]
    m = re.search(r'\\appendix\b|\\begin\s*\{appendices\}', src)
    app_from = m.start() if m else len(src)
    annot = _annot_ranges(src)
    hidden = annot + [h['arg'] for h in heads]
    lists = (_regions(src, 'itemize') + _regions(src, 'enumerate') +
             _regions(src, 'description'))
    paras = []
    for buf in bufs:
        raw = re.sub(r'[ \t]*\n[ \t]*', ' ', ''.join(p for p, _ in buf))
        raw = re.sub(r'\s+', ' ', raw).strip()
        sp = buf[0][1]
        for text, opened in _split_at_titles(raw, titles):
            while True:                              # a short title, stacked or leading
                for t in titles:
                    if 2 < len(t) < 5 and text.lower().startswith(t.lower()):
                        text, opened = text[len(t):].lstrip(' .,;:\u2020\u2021'), True
                        break
                else:
                    break
            if not text:
                continue
            sents = []
            for snt, _ in _split_sentences(text):
                if not _is_prose(snt):
                    continue
                off = _at(sp, snt)
                if _inside(off, hidden):
                    continue
                sents.append({'t': snt, 'sp': sp, 'off': off})
            if not sents:
                continue
            off = sents[0]['off']
            si = bisect.bisect_right(hoff, off) - 1
            for j, rec in enumerate(sents):
                rec['i'] = j
                rec['p'] = len(paras)
            paras.append({'sents': sents, 'off': off, 'sec': si, 'k': len(paras),
                          'opens_section': opened, 'appendix': off >= app_from,
                          'title': heads[si]['title'] if si >= 0 else '',
                          'in_list': _inside(off, lists)})
    return paras


def _listish(para, heads):
    """True when the paragraph sits in a list or in a section that is one.

    Structural only. Used by the sentence-level rules, which must not be silenced by the
    survey heuristics below: a citation-dense paragraph is a bad place to judge a topic
    string and a perfectly good place to judge a held-open subject.
    """
    if para['in_list']:
        return True
    if para['title'] and _ENUM_SECTION.search(para['title']):
        return True
    if para['sec'] >= 0:
        for h in heads[:para['sec'] + 1][::-1]:      # inherit from the enclosing section
            if h['level'] <= 1:
                if _ENUM_SECTION.search(h['title'] or ''):
                    return True
                break
    return False


def _enumerative(src, para, heads):
    """True when a shifting topic is the content rather than a defect.

    All three of the ledger's counter-cases for the topic rules land here: a survey
    paragraph, a limitations or risk list, and any paragraph inside an itemize.
    """
    if _listish(para, heads):
        return True
    sents = para['sents']
    # A survey: several distinct works cited across several sentences.
    cited = sum(1 for s in sents if '\u2020' in s['t'])
    if cited >= 3 or (cited >= 2 and cited >= len(sents) - 1):
        return True
    # An explicit enumeration: two or more sentences opening with an ordinal.
    ords_ = sum(1 for s in sents
                if re.match(r'(?:' + '|'.join(_ORDINALS) + r'|finally|lastly)\b',
                            s['t'], re.I))
    return ords_ >= 2


# A sentence-initial adverbial closed by a comma is not the subject. "However, when we
# train on X, the model shows ..." has its subject after the second comma, and reading
# "However" as the subject head reported a nonsense separation.
_SUBORD = set("""
however therefore thus hence consequently accordingly moreover furthermore additionally
also besides meanwhile similarly likewise conversely instead nevertheless nonetheless
still indeed overall together finally lastly next then first firstly second secondly
third thirdly again rather specifically notably importantly crucially concretely
when if while whereas because since although though after before once unless until as
given assuming despite whether following using having in for on at by with from to
during under over through across within among without unlike beyond regarding
concerning toward towards amid via besides outside inside above below behind
unfortunately strikingly
surprisingly interestingly critically ultimately here there
""".split())


def _subject_start(toks):
    """Index where the grammatical subject starts, past any leading adverbial."""
    if not toks:
        return 0
    if toks[0] == ',':
        return 1
    if toks[0].lower() in _SUBORD:
        c = next((i for i, w in enumerate(toks[:16]) if w == ','), None)
        if c is not None:
            return c + 1
    return 0


def _topic(sent):
    """The sentence's opening string up to its main verb, and its content stems.

    This is Gopen & Swan's topic position, and Williams's diagnostic procedure verbatim:
    underline from the start of the sentence to the main verb. Returns None when the verb
    cannot be located, because a guessed topic string is worse than none.
    """
    toks = _tok(sent)
    st = _subject_start(toks)
    v = _first_verb(toks[st:])
    if v is None:
        return None
    v += st
    if v == st:
        return None
    words = [w for w in toks[st:v] if re.match(r"[A-Za-z]", w)]
    stems = _content(' '.join(words))
    return {'v': v, 'toks': toks, 'words': words, 'stems': stems,
            'verb': toks[v].lower()}


# ------------------------------------------------------------------------------- entry


# A heading is not a sentence. Requiring a lexical bridge from a heading to the paragraph
# beneath it flags normal structure, and it fired on a CV section ("Current position(s)"
# against a dated entry) on a real proposal.
_HEADINGISH = re.compile(
    r'^\s*(?:[A-Z][^.!?]{0,70}|.{0,70}\s---\s.{0,70})$')
_DATED = re.compile(r'^\s*(?:19|20)\d\d\s*(?:--|-|\u2013)')


def _is_headingish(sent):
    t = (sent or '').strip()
    if not t:
        return True
    if _DATED.match(t):
        return True
    # No sentence-final punctuation and short enough to be a title.
    if len(t) <= 80 and not re.search(r'[.!?]\s*$', t):
        return True
    return bool(_HEADINGISH.match(t)) and not re.search(r'[.!?]', t)




# --- three vetoes added after the first real trial ---------------------------------
# Each removed a class of false positive on a live proposal.

_CATAPHORIC = re.compile(
    r'\b(two|three|four|five|six|seven|several|the following|these)\s+'
    r'(things|ways|steps|reasons|objectives|claims|outcomes|components|items|points|parts)\b',
    re.I)
_INLINE_ENUM = re.compile(r'\(\s*(?:[1-9]|i{1,3}|iv|v)\s*\)')


_ENUM_VERBS = frozenset(
    'establish show demonstrate prove measure build develop design create release '
    'identify isolate determine quantify evaluate compare test validate'.split())


def _announces_list(text):
    """A paragraph that announces its own list is enumerating by design."""
    t = text or ''
    if _CATAPHORIC.search(t):
        return True
    if len(_INLINE_ENUM.findall(t)) >= 2:
        return True
    # A repeated opening word only signals an enumeration when it is an IMPERATIVE and it
    # repeats at least three times. As written — any repeated first word, twice — this
    # vetoed ordinary prose with two sentences beginning "The", which silenced the rule
    # across all 2140 files of a corpus sweep.
    opens = re.findall(r'(?:^|\.\s+)([A-Z][a-z]+)\b', t)
    if len(opens) >= 3:
        first = opens[0].lower()
        imperative = first in _ENUM_VERBS
        if imperative and sum(1 for o in opens if o.lower() == first) >= 3:
            return True
    return False


_RUNIN = re.compile(r'\\noindent\s*\\(?:textbf|textsc|emph)\s*\{')


def _is_runin_heading(src, off):
    """A run-in bold heading is a heading, whatever it renders as."""
    ls = src.rfind('\n', 0, max(0, int(off) - 1)) + 1
    return bool(_RUNIN.match(src[ls:ls + 60]))


def checks(src, spans, ctx):
    """Return cohesion findings. Never raises: a broken check yields nothing."""
    try:
        return _gate(_checks(src, spans, ctx or {}))
    except Exception:
        return []


def _checks(src, spans, ctx):
    if _is_definition_file(src, ctx.get('path', '')):
        return []
    heads = _headings(src)
    paras = _paragraphs(src, spans, heads)
    if not paras:
        return []
    sents = [s for p in paras for s in p['sents']]
    out = []
    for fn in (_r_sentence_join_unbridged, _r_section_boundary_unbridged,
               _r_paragraph_topic_drift, _r_paragraph_topic_sentence_not_first,
               _r_paragraph_opens_on_procedure, _r_section_opens_restating_heading,
               _r_pronoun_antecedent_crosses_paragraph,
               _r_forward_promise_unfulfilled, _r_enumeration_count_mismatch):
        try:
            got = fn(src, spans, paras, sents, heads, ctx) or []
        except Exception:
            continue                                  # a broken check reports nothing
        out += got[:CAP]
    out.sort(key=lambda f: (f['offset'], f['rule']))
    return out


# ------------------------------------------------------------------ between sentences
def _shared(a_stems, b_stems):
    return set(a_stems) & set(b_stems)


def _r_sentence_join_unbridged(src, spans, paras, sents, heads, ctx):
    """Consecutive sentences sharing no term, with no connective between them.

    Gopen & Swan, "Perceiving Logical Gaps": when the closing words of one sentence and the
    opening words of the next have nothing in common and no connective names the relation,
    the reader supplies the link, and different readers supply different ones.

    Three vetoes. A connective opening has already named the relation. An anaphor opening
    ("this", "these", "they") IS the bridge. A declared pivot must not be bridged, because
    a bridge there would falsely imply the new material continues the old. Joins are tested
    only inside a paragraph: a paragraph break is itself a signalled discontinuity, and the
    section boundary is a separate rule with its own tolerance.
    """
    out = []
    for p in paras:
        if p['in_list'] or p['appendix'] or _enumerative(src, p, heads):
            continue
        ss = p['sents']
        for i in range(len(ss) - 1):
            a, b = ss[i], ss[i + 1]
            if _CONNECTIVE.match(b['t']):
                continue
            if _PIVOT.match(b['t']):
                continue
            head = ' '.join(re.findall(r"[A-Za-z][A-Za-z'-]*", b['t'])[:10])
            if _ANAPHOR_IN.search(head) or _ANAPHOR_TOPIC.match(head) or \
               _THAT_BACK.match(head) or _CONN_IN.search(head):
                continue
            # The closing words the reader actually sees are a formula: the terms that
            # would bridge the join are inside masked math, so no judgement is possible.
            if '\u2022' in ' '.join(a['t'].split()[-6:]):
                continue
            ca, cb = _content(a['t']), _content(b['t'])
            if len(ca) < 6 or len(cb) < 6:
                continue                              # window covers the whole sentence
            if _shared(ca[-8:], cb[:8]):
                continue
            # Tightening, measured: the opening window must share nothing with ANY earlier
            # sentence in the paragraph, not merely with the closing window of the one
            # before it. On the ledger's literal pairwise test this rule reported 22, 16
            # and 29 findings on the three test documents, and most of the surplus was a
            # sentence returning to a term from two sentences back, which a reader carries
            # without effort. The claim reported here is the stronger one: nothing in the
            # paragraph so far anchors the sentence.
            earlier = set()
            for x in ss[:i + 1]:
                earlier |= set(_content(x['t']))
            if earlier & set(cb[:8]) or _shared_stems(earlier, cb[:8]):
                continue
            if _is_headingish(a['t']) or _is_headingish(b['t']):
                continue  # a heading needs no lexical bridge to the prose beneath it
            if _is_runin_heading(src, b['off']) or _is_runin_heading(src, a['off']):
                continue  # a run-in bold heading is a heading, whatever it renders as
            first = ' '.join(re.findall(r"[A-Za-z][A-Za-z'-]*", b['t'])[:6])
            last = ' '.join(re.findall(r"[A-Za-z][A-Za-z'-]*", a['t'])[-6:])
            out.append(_F('sentence-join-unbridged', b['off'], 'rework', False,
                          f'"... {last}" is followed by "{first} ...", which shares no '
                          f'term with it and carries no connective',
                          'Confirm the relation between the two sentences is the one a '
                          'reader will supply'))
    return out


def _r_section_boundary_unbridged(src, spans, paras, sents, heads, ctx):
    """A section's closing sentence and the next section's opening sentence share no term.

    The widest join in the document, and the one where a reader who loses the thread has
    the furthest to go back. The new section's own heading counts as a bridge, since the
    reader has just read it, so the test is against the opening sentence AND its title. A
    section that opens by declaring a pivot, and one that opens on the document's own
    structure, are both left alone: they have announced the break.
    """
    out = []
    by_sec = collections.defaultdict(list)
    for p in paras:
        if p['sec'] >= 0:
            by_sec[p['sec']].append(p)
    for si in sorted(by_sec):
        nxt = si + 1
        if nxt not in by_sec or si < 0:
            continue
        if heads[si]['level'] != heads[nxt]['level'] or heads[nxt]['level'] > 2:
            continue                                  # a nested detail block is not a join
        if by_sec[si][-1]['appendix'] or by_sec[nxt][0]['appendix']:
            continue
        prev_ss = by_sec[si][-1]['sents']
        open_p = by_sec[nxt][0]
        first = open_p['sents'][0]
        if _CONNECTIVE.match(first['t']) or _PIVOT.match(first['t']) or \
           _PROCEDURE_OPEN.match(first['t']) or _ANAPHOR_TOPIC.match(first['t']):
            continue                                  # it points at the heading above it
        if _ENUM_SECTION.search(heads[nxt]['title'] or '') or \
           _ENUM_SECTION.search(heads[si]['title'] or ''):
            continue
        if by_sec[si][-1]['in_list'] or open_p['in_list']:
            continue
        closing = _content(prev_ss[-1]['t'])
        opening = _content(first['t']) + _content(heads[nxt]['title'] or '')
        if len(closing) < 5 or len(opening) < 5:
            continue
        if _shared(closing, opening) or _shared_stems(closing, opening):
            continue
        if _is_headingish(prev_ss[-1]['t']) or _is_headingish(first['t']):
            continue  # a heading is not a sentence, so no bridge is owed across it
        if (heads[nxt].get('level') or 1) <= 1:
            continue  # top-level sections are discrete by design in a funder template
        out.append(_F('section-boundary-unbridged', first['off'], 'rework', False,
                      f'"{heads[nxt]["title"][:48]}" opens on "'
                      f'{first["t"][:56]}...", which shares no term with the sentence '
                      f'that closed the previous section',
                      'Confirm the reader is expected to carry nothing across this '
                      'boundary'))
    return out


# ------------------------------------------------------------------ within a paragraph
def _r_paragraph_topic_drift(src, spans, paras, sents, heads, ctx):
    """A paragraph whose sentences do not share a topic.

    The procedure is Gopen & Swan's topic position read through Williams's diagnostic: take
    each sentence's opening string up to its main verb, read those strings in order, and
    ask whether they form a small set of related ideas. Here "related" is decided by a
    shared stem: the paragraph is reported only when NO stem appears in two or more topic
    strings, which is the strongest form of the finding and the only one that needs no
    judgement about degree.

    Silent wherever a shifting topic is the content -- survey paragraphs, limitations and
    risk lists, anything inside an itemize -- see `_enumerative`. A topic string that opens
    on a back-reference is not counted as a topic at all, which is the measured difference
    between a usable rule and a noisy one: 15 findings on the three documents without that
    exclusion, 6 with it.
    """
    out = []
    for p in paras:
        if p['appendix'] or _enumerative(src, p, heads):
            continue
        tps = [(_topic(s['t']), s) for s in p['sents']]
        # A topic string that opens on a back-reference ("This range", "These questions",
        # "Such a model") carries no new topic: the demonstrative is doing the linking, so
        # counting it as an unrelated topic reports cohesion as its opposite.
        tps = [(t, s) for t, s in tps
               if t and t['stems'] and not _ANAPHOR_TOPIC.match(' '.join(t['words']))]
        if len(tps) < 3:
            continue
        counts = collections.Counter()
        for t, _ in tps:
            counts.update(set(t['stems']))
        if any(c >= 2 for c in counts.values()):
            continue
        para_text = ' '.join(t2['t'] for t2, _ in tps) if tps else ''
        if _announces_list(para_text) or _announces_list(p.get('t') or ''):
            continue  # the paragraph announces its own list, so shifting subject is the form
        strings = ' | '.join(' '.join(t['words'])[:26] for t, _ in tps[:4])
        out.append(_F('paragraph-topic-drift', p['off'], 'rework', False,
                      f'{len(tps)} sentences open on unrelated subjects: {strings}',
                      'Confirm the paragraph is meant to be read as a list rather than '
                      'as one topic'))
    return out


def _r_paragraph_opens_on_procedure(src, spans, paras, sents, heads, ctx):
    """A paragraph whose first sentence is about the document rather than its subject.

    The topic position of a paragraph's first sentence sets what the paragraph is about, so
    spending it on the paper's own machinery ("In this section we describe", "We now turn
    to") tells the reader where they are and nothing about what is true. Reported, never
    repaired: a roadmap is a convention many venues expect, so the paragraph that ends the
    first section is exempt, as is anything in an abstract.
    """
    abstract = _regions(src, 'abstract')
    first_sec = min((p['sec'] for p in paras if p['sec'] >= 0), default=-1)
    last_of_first = None
    for p in paras:
        if p['sec'] == first_sec:
            last_of_first = p['k']
    out = []
    for p in paras:
        if p['in_list'] or p['appendix'] or _inside(p['off'], abstract) or \
           p['k'] == last_of_first:
            continue
        s = p['sents'][0]
        m = _PROCEDURE_OPEN.match(s['t'])
        if not m:
            continue
        out.append(_F('paragraph-opens-on-procedure', s['off'], 'rework', False,
                      f'the paragraph opens on the paper\'s own procedure: '
                      f'"{m.group(0)[:60]}"',
                      'Confirm the reader needs the roadmap here more than the content'))
    return out


# ------------------------------------------------------------------- across a document
def _r_forward_promise_unfulfilled(src, spans, paras, sents, heads, ctx):
    """A promise that something comes later, with no later text that delivers it.

    Two shapes, one defect. A promise naming a target ("we show in Section 5 that X") is
    resolved through \\label: if the label sits later in the source, the promised terms are
    looked for in the section that holds it. A promise naming no target ("we return to this
    below") is checked against everything after it. In both cases the promise must have at
    least three content stems of its own, and delivery means at least half of them, minimum
    two, co-occur in one later paragraph. A promise whose target label does not exist is
    NOT reported here: that is a broken cross-reference and belongs to another family.
    """
    hoff = [h['off'] for h in heads]
    labels = {}
    for m in re.finditer(r'\\label\s*\{([^}]*)\}', src):
        labels.setdefault(m.group(1).strip(), m.start())
    out = []
    for s in sents:
        m = _PROMISE.search(s['t'])
        if not m:
            continue
        after = s['t'][m.end():]
        stems = [w for w in _content(after)
                 if w not in ('section', 'sec', 'appendix', 'app', 'figur', 'tabl',
                              'paper', 'work', 'follow', 'below', 'later')]
        stems = list(dict.fromkeys(stems))
        if len(stems) < 3:
            continue                                  # nothing specific enough promised
        need = max(2, (len(stems) + 1) // 2)
        # Where does the promise point?
        win = src[s['off']:s['off'] + 400]
        refs = [r.strip() for mm in re.finditer(
            r'\\(?:ref|autoref|cref|Cref)\s*\{([^}]*)\}', win) for r in mm.group(1).split(',')]
        target = None
        for r in refs:
            if r in labels and labels[r] > s['off']:
                target = bisect.bisect_right(hoff, labels[r]) - 1
                break
        if target is not None:
            pool = [p for p in paras if p['sec'] == target]
        elif not refs and _VAGUE_FORWARD.search(s['t']):
            pool = [p for p in paras if p['off'] > s['off']]
        else:
            continue                                  # points somewhere unresolvable
        if not pool:
            continue
        best = 0
        for p in pool:
            got = len(set(stems) & set(_content(' '.join(x['t'] for x in p['sents']))))
            best = max(best, got)
        if best >= need:
            continue
        where = (f'Section "{heads[target]["title"][:38]}"' if target is not None
                 else 'anywhere later in this file')
        out.append(_F('forward-promise-unfulfilled', s['off'], 'rework', False,
                      f'"{m.group(0)[:44]}" promises {", ".join(stems[:4])}; '
                      f'{where} carries {best} of those {len(stems)} terms',
                      'Confirm the promise is kept somewhere the reader will reach'))
    return out


def _r_enumeration_count_mismatch(src, spans, paras, sents, heads, ctx):
    """An announced count of items that the following enumeration does not deliver.

    The one rule in this family whose ledger entry records no counter-case, and the reason
    is that a reader who is counting along always loses. Reported only when an enumeration
    was actually attempted -- two or more ordinal markers, or an itemize immediately after
    -- so an announced count followed by running prose is never reported.
    """
    out = []
    for p in paras:
        for s in p['sents']:
            m = _ENUM_HEAD.search(s['t'])
            if not m:
                continue
            n = _NUMW[m.group(1).lower()]
            tail = [x['t'] for x in p['sents'][s['i'] + 1:]]
            nxt = [q for q in paras if p['k'] < q['k'] <= p['k'] + 3]
            body = ' '.join(tail) + ' ' + ' '.join(
                x['t'] for q in nxt if q['in_list'] or q['k'] == p['k'] + 1
                for x in q['sents'])
            seen = [k for k, w in enumerate(_ORDINALS)
                    if re.search(r'(?:^|[.;:]\s*|\band\b\s+)' + w + r'\b[,\s]',
                                 body, re.I)]
            items = 0
            if len(seen) >= 2 and seen == list(range(len(seen))):
                items = len(seen)
                # The window is three paragraphs wide, so an enumeration that runs past it
                # would report as short. If the ordinal the announcement asks for appears
                # anywhere in the next few thousand characters of source, say nothing.
                if items < n and n <= len(_ORDINALS) and re.search(
                        r'\b' + _ORDINALS[n - 1] + r'\b',
                        src[p['off']:p['off'] + 4000], re.I):
                    items = 0
            else:
                nl = [q for q in nxt if q['in_list']]
                if nl:
                    items = _count_items(src, min(q['off'] for q in nl))
            if not items or items == n:
                continue
            out.append(_F('enumeration-count-mismatch', s['off'], 'rework', True,
                          f'"{m.group(0)}" announces {n}, and {items} follow',
                          'Confirm which count is right'))
    return out



# ------------------------------------------------------- the paragraph's topic sentence
def _r_paragraph_topic_sentence_not_first(src, spans, paras, sents, heads, ctx):
    """A paragraph whose one repeated term is absent from its opening sentence.

    Gopen & Swan put the reader's expectation for the paragraph's point in its first
    sentence; the ledger's grant-scope version of the same test (rule 15) counts the
    sentences of background that arrive before the claim. Both need "the sentence carrying
    the central claim" identified, which is the judgement itself, so neither is decidable
    as written. The decidable slice is narrower and reported instead: the paragraph repeats
    exactly ONE content term across three or more of its sentences, that term is the only
    candidate for what the paragraph is about, the opening sentence does not contain it,
    and a later sentence carries it in its own topic position. Nothing here is inferred --
    the repetition count, the absence and the topic position are all counted.

    Vetoes, each of which is a paragraph with no topic sentence by design: a list, a survey
    or limitations paragraph (`_enumerative`), a paragraph announcing its own enumeration, a
    paragraph opening on a back-reference (its topic was set in the paragraph before), one
    opening on procedure (already reported by its own rule), and a paragraph whose heading
    names the repeated term, since the reader was handed it one line earlier and the
    opening sentence owes no restatement.
    """
    out = []
    for p in paras:
        if p['appendix'] or p['in_list'] or _enumerative(src, p, heads):
            continue
        ss = p['sents']
        if len(ss) < 4:
            continue                                  # too short for a term to repeat
        first = ss[0]
        if not _starts_paragraph(src, first['off'], first['t']):
            continue                   # a dropped sentence, not the paragraph's opening
        if _is_headingish(first['t']) or _is_runin_heading(src, first['off']):
            continue
        if _PROCEDURE_OPEN.match(first['t']):
            continue
        head = ' '.join(re.findall(r"[A-Za-z][A-Za-z'-]*", first['t'])[:10])
        if _ANAPHOR_TOPIC.match(head) or _ANAPHOR_IN.search(head) or _THAT_BACK.match(head):
            continue
        if _announces_list(' '.join(x['t'] for x in ss)):
            continue
        sets = [set(_content(x['t'])) for x in ss]
        if len(sets[0]) < 4:
            continue                                  # nothing much in the opening either
        counts = collections.Counter()
        for st in sets:
            counts.update(st)
        rep = [w for w, c in counts.items() if c >= 3]
        # A topic is usually a phrase, so "the paired tokenizer" repeats two stems, not
        # one. Requiring exactly one repeated stem made the rule unable to fire on its own
        # constructed positive. The bound is on the size of the repeated SET instead: one
        # to three stems is a term or a short phrase, and a paragraph repeating more than
        # that has no single candidate topic to be missing from its opening.
        if not 1 <= len(rep) <= 3:
            continue
        if any(_same_term(w, sets[0]) for w in rep):
            continue                                  # the opening sentence has the term
        title = set(_content(p['title'] or ''))
        if any(_same_term(w, title) for w in rep):
            continue                                  # the heading handed it to the reader
        subj = []
        for i in range(1, len(ss)):
            t = _topic(ss[i]['t'])
            if t and any(_same_term(w, set(t['stems'])) for w in rep):
                subj.append(i)
        if len(subj) < 3:
            continue                     # a repeated term that is never a subject is not
        hold = subj[0]                   # what the paragraph is about, only what it uses
        out.append(_F('paragraph-topic-sentence-not-first', first['off'], 'rework', False,
                      f'no term this paragraph repeats ({", ".join(rep)}) appears in its '
                      f'opening sentence, and {len(subj)} later sentences take one as '
                      f'their subject, from sentence {hold + 1} of {len(ss)}',
                      f'Confirm the reader is meant to reach sentence {hold + 1} before '
                      f'the paragraph names what it is about'))
    return out


# ------------------------------------------------------------------- reference distance
def _r_pronoun_antecedent_crosses_paragraph(src, spans, paras, sents, heads, ctx):
    """A paragraph opening on a bare pronoun or demonstrative.

    Ledger rule 7 asks whether a pronoun's referent and a demonstrative's antecedent are
    unambiguous. Its counter-case is that a unique adjacent antecedent needs no query, and
    an earlier attempt at this rule died on exactly that: counting commas in the previous
    sentence counts clauses, not antecedents, so there was no way to tell a unique
    antecedent from a field of them.

    The gate here is structural instead of lexical, and it is certain rather than
    estimated. When the reference is the FIRST word of a paragraph's FIRST sentence there
    is nothing inside the paragraph for it to point at, so the antecedent is across a
    paragraph break by construction, and the candidate set is a whole paragraph rather
    than a noun. Only the bare forms count: "This mapping shows" carries its own
    antecedent and is not collected, "This shows" is.

    This does not contradict `sentence-join-unbridged`, which counts a demonstrative
    opening as a bridge. That rule runs between adjacent sentences inside one paragraph,
    where the candidate set is one sentence long and the demonstrative does link. Here the
    candidate set is a whole paragraph on the far side of a break, and the two rules can
    never fire on the same sentence: this one requires the sentence to be the paragraph's
    first, which is where the join rule stops looking.

    Four vetoes. Expletive "it" points forward at its own clause and back at nothing. A
    paragraph that opens a section is skipped, both because the heading between them is a
    signalled break and because the paragraph model splits on a heading title, so a
    section-opening paragraph is the one place its boundaries are not certain. A blank line
    must actually separate the two paragraphs in the source, so a paragraph the extractor
    split at a float or an equation is never reported. Lists are skipped: an item opening
    "These are ..." points at the stem the list hangs from.
    """
    out = []
    for k, p in enumerate(paras):
        if k == 0 or p['in_list'] or p['opens_section']:
            continue
        if _listish(p, heads):
            continue
        prev = paras[k - 1]
        if prev['sec'] != p['sec'] or prev['in_list']:
            continue                                  # a heading or a list sits between
        first = p['sents'][0]
        if not _starts_paragraph(src, first['off'], first['t']):
            continue                   # a dropped sentence, not the paragraph's opening
        if _is_headingish(first['t']) or _is_runin_heading(src, first['off']):
            continue
        toks = _tok(first['t'])
        if not toks or toks[0].lower() not in _OPEN_REF:
            continue
        w0 = toks[0].lower()
        if w0 == 'it' and _EXPLETIVE_IT.match(first['t']):
            continue
        if w0 in ('this', 'these', 'those', 'such'):
            if _first_verb(toks) != 1:
                continue                              # a noun follows, so it is not bare
        out.append(_F('pronoun-antecedent-crosses-paragraph', first['off'], 'rework', False,
                      f'the paragraph opens on "{" ".join(toks[:4])}", whose antecedent is '
                      f'in the previous paragraph',
                      'Confirm the antecedent is the only one a reader could pick from '
                      'across the paragraph break'))
    return out


def _heading_opening(src, spans, h):
    """The first prose sentence after a heading, before any title stripping.

    Read from the source rather than from `paras`, because `_paragraphs` deletes the title
    string wherever it appears -- including inside a sentence that restates it, which is
    exactly the sentence this rule is looking for. Returns '' unless the whole opening
    passage is authored prose: if a float, an equation, a table or an annotation macro
    overlaps it, there is no sentence here to judge.
    """
    a = h['arg'][1]
    # A heading is normally followed by a blank line, so the opening passage starts past
    # any run of whitespace, labels and spacing macros. Cutting at the FIRST blank line
    # instead returned an empty string for three headings out of four.
    lead = re.match(r'(?:\s|\\label\s*\{[^{}]*\}|\\(?:noindent|indent|par)\b|'
                    r'\\(?:vspace|hspace)\*?\s*\{[^{}]*\})*', src[a:a + 400])
    a += lead.end() if lead else 0
    tail = src[a:a + 900]
    m = re.search(r'\n[ \t]*\n', tail)
    if m:
        tail = tail[:m.start()]
    b = a + len(tail)
    if b <= a:
        return ''
    for sp in spans:
        if sp.start < b and sp.end > a and sp.kind not in ('text', 'comment'):
            return ''
    tail = re.sub(r'(?<!\\)%[^\n]*', '', tail)
    txt = re.sub(r'\s+', ' ', ex._render(tail)).strip()
    sent = next((q for q, _ in _split_sentences(txt)), '')
    return sent if _is_prose(sent) else ''


def _r_section_opens_restating_heading(src, spans, paras, sents, heads, ctx):
    """A section whose first sentence adds nothing to the heading above it.

    The topic position of a section's first sentence is the most expensive slot in the
    section, and a restatement of the title spends it on the one thing the reader already
    has. Decided by counting, not by judging similarity: every content term of the heading
    reappears in the opening sentence, and the sentence contributes at most two content
    terms the heading did not already carry. A sentence that develops the title's terms
    fails that second test and is never reported.

    Vetoed where a roadmap opening is already reported by `paragraph-opens-on-procedure`,
    so one sentence never produces two findings, and where the heading carries fewer than
    two content terms, since "Method" is restated by any sentence about the method.
    """
    out = []
    for h in heads:
        if not h['title'] or h['level'] > 3:
            continue
        tstems = list(dict.fromkeys(_content(h['title'])))
        if len(tstems) < 2:
            continue
        snt = _heading_opening(src, spans, h)
        if not snt or _is_headingish(snt) or _PROCEDURE_OPEN.match(snt):
            continue
        sstems = set(_content(snt))
        if not sstems or not all(_same_term(w, sstems) for w in tstems):
            continue
        fresh = [w for w in sstems if not _same_term(w, tstems)]
        if len(fresh) > 2:
            continue
        out.append(_F('section-opens-restating-heading', h['off'], 'rework', False,
                      f'"{h["title"][:40]}" is followed by "{snt[:60]}", which repeats '
                      f'every term of the heading and adds {len(fresh)}',
                      'Confirm the reader needs the heading restated before the section '
                      'begins'))
    return out

# ------------------------------------------------------------------------------ runner
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    stage = 'draft' if '--draft' in sys.argv else 'submission'
    quiet = '--quiet' in sys.argv
    tot = collections.Counter()
    per_file = collections.Counter()
    for path in args:
        src = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
        spans = ex.extract(src)
        found = checks(src, spans, {'stage': stage, 'path': path, 'style': {}})
        for f in found:
            tot[f['rule']] += 1
            per_file[(os.path.basename(path), f['rule'])] += 1
            if not quiet:
                line = src.count('\n', 0, f['offset']) + 1
                print(f"{os.path.basename(path)}:{line}  [{f['cost']}"
                      f"{'/BLOCKS' if f['blocks'] else ''}]  {f['rule']}: {f['text']}")
                if f['fix']:
                    print(f"        -> {f['fix']}")
    print(f'\n--- {sum(tot.values())} findings, stage={stage} ---')
    for r, c in tot.most_common():
        print(f'  {c:4d}  {r}')
    if len({k[0] for k in per_file}) > 1:
        print('\nby file:')
        for (fn, r), c in sorted(per_file.items()):
            print(f'  {fn:18s} {c:4d}  {r}')
