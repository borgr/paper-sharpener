#!/usr/bin/env python3
"""Register-redundancy checks: hype, self-praise, empty filler, and the same point twice.

THE DANGEROUS FAMILY. Published filler-word lists mix genuinely empty words with hedges,
approximators, near-quantifiers and intensifiers: "virtually", "generally", "practically",
"certain", "almost", "largely", "fairly", "quite", "various", "individual", "basically",
"really", "exactly". Deleting one of those looks like tidying and passes every mechanical
meaning-preservation test, but it converts a hedged statement into an absolute one and an
honest uncertainty into an unkeepable promise. Several rules in the source ledger were
repaired for exactly this, and the repair is honoured here structurally rather than by
remembering it at each call site:

  * HEDGE_VOCAB lists every word that could carry claim strength.
  * A check that finds a filler candidate whose word is in HEDGE_VOCAB must emit
    fix == '' and tier == 'query'. `_safe_delete` is the single place that decides.
  * `_gate` runs over every finding on the way out and DROPS any finding whose `fix`
    proposes deleting, removing, trimming, weakening or replacing a HEDGE_VOCAB word,
    any finding that names a HEDGE_VOCAB word as its target while carrying a non-empty
    fix, and any finding tiered 'silent'. A future edit to a rule therefore cannot ship
    a hedge-deleting fix even if the rule author forgets.

The empirical trade-off, which this module reports and refuses to resolve. Promotional
language is positively associated with funding, replicated across two funders at odds
ratios near 1.5 on real funded-and-rejected applications, and the raw density gap is small
(0.93% of words against 0.89%). Hype is therefore not simply a defect to remove: it is a
choice with evidence on both sides. Every promotional rule here (self-praise-adjective,
self-praise-craft-adverb, emotive-word-in-technical-part) reports the occurrence, names the
trade-off in the finding text, proposes nothing, and leaves the decision with the author.
`blocks` is False for every rule in the family, because no reviewer requires a register
change before acceptance.

Not implemented, from the 24-row ledger, with the reason for each:

  * the reviewer-praise-mirroring row is a category error the ledger itself names: the
    measured association is between REVIEWER wording and reviewer scoring, so there is no
    applicant-side text to test. Its advice is already carried by self-praise-adjective.
  * the three query-discipline rows (query a possible diction error rather than fixing it;
    justify an aesthetic query; do not cut redundancy unless the substantive level was
    agreed) are rules ABOUT rules, not document tests. They are honoured as constraints:
    every ambiguous-word finding here is a query with an empty fix, which is what those
    rows ask for.
  * the two NIH Project Summary rows (third-person convention, past accomplishments plus
    first person) need the funder identity and the attachment identity. `ctx` carries
    stage, path and house style, none of which says "this file is an NIH Project Summary",
    and the counter-cases are explicit that firing on a UKRI or Wellcome summary
    manufactures a violation. The funder-neutral half is implemented as
    summary-reports-completed-work, which reports and proposes nothing.
  * the methodology-as-task-list row and the capability-section-as-CV row need the funder's
    template to know which attachment is being read (Horizon Europe Excellence versus
    Implementation, the UKRI capability attachment). Neither could be exercised: the whole
    test corpus contains zero \\item, so the bullet-to-prose ratio they turn on is
    undefined and any threshold would be invented rather than measured.

Built, measured, then removed:

  * "given" was dropped from the ambiguous-filler scan after measuring 8 hits on the paper.
    Every one was the "arbitrary member of a set" sense -- "any given word", "a given
    replicate", "given the fact" -- which is load-bearing and not filler, so the word
    produced eight findings and no defects.
  * "kind of" was narrowed to the hedge position (before an evaluative adjective, plus
    "kinda"/"sorta") after measuring 8 hits across the two proposals, every one the noun
    "the kind of capability" or "one kind of computation". The unnarrowed pattern was pure
    noise on the corpus.
  * "in particular" was excluded from the ambiguous-filler scan: it is a discourse
    connective, not a quantifier over a set the text may or may not specify.
  * "virtually" and "practically" now require a following quantifier, absolute or
    adjective, i.e. the hedge position. Bare "Practically," and "efficiently and
    practically?" were both matched before and neither is a hedge or a filler.
  * the emotive-word list deliberately omits "revolutionary", "groundbreaking" and
    "unprecedented", and the praise list omits "state-of-the-art", "novel" and
    "pioneering", because checks_claim_calibration already reports those under
    superlative-no-comparison-set and priority-claim-unanchored. Two findings on one word
    is how a reader learns to ignore the tool.
  * the significance half of the emotive row ("flag the significance part if emotive words
    outnumber the concrete consequences it names") was dropped: counting "concrete
    consequences" is not a string test, and the ledger's own counter-case says a few such
    words belong there. The rule fires only in the technical part, where the ledger says
    the ban is absolute.
  * the multiple-negation rule originally counted two negations anywhere in one clause. Its
    single hit on the corpus was "if sharing is not introduced immediately it does not arise
    later", two juxtaposed predicates whose parity no reader loses, so the two negations must
    now sit within 25 characters of each other (NEG_GAP). The parity-confusing cases are
    adjacent by nature: "not uncommon", "no ... without", "not ... nor". The rule now fires
    nowhere on the corpus and once on the fixture, which is the right ratio for a rule whose
    false positive is an accusation of incoherence.
  * findings inside author annotations and template boilerplate are dropped wholesale
    (`_note_ranges`). Three of the four filler findings on the paper came from inside
    \lc{...} and \adam{...} review notes, and the one negation finding on the proposal came
    from the ERC template's own \instruction{Do NOT include any description of resources}.
    Review markers and leftover template text belong to the integrity family, which reports
    them: running the register rules over them charges the author twice for one defect.
  * "basically" and "really" are treated as HEDGE_VOCAB even though the repaired ledger row
    permits deleting them. "basically the same" and "really large" grade a claim, and the
    gate cannot tell that position from the empty one reliably enough to propose a
    deletion. They are reported instead.

The gate has already earned itself twice during development, which is the argument for
having it rather than trusting the call sites. It ate the unlinked-paragraph rule's own fix,
because "do not delete it, a generalist reviewer may need it" reads to the pattern as a
deletion aimed at "may"; the fix was reworded. And it ate the redundant-modifier fix on
"various different", which said Write "various" and so quoted a HEDGE_VOCAB word as its
target; the fix now names the word being deleted instead. Both were caught by --selftest
asserting that every rule still fires, not by inspection.

No rule here reads `ctx['stage']` or `ctx['style']`, and that is deliberate rather than an
omission. The family contains no scaffolding rule -- a TODO, a placeholder and a review
marker are the integrity family's findings, and a draft is supposed to contain them -- and
no rule whose correct output depends on a house-style decision. Annotations are excluded
structurally at both stages instead of being reported at one of them.

Interface: checks(src, spans, ctx) -> list[dict]   (see CHECKS_API.md)
"""
import os
import re
import sys
import pathlib
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex

FAMILY = 'register-redundancy'

# Per-rule ceiling on one document. A register rule past this is reading the author's
# voice rather than a defect. No rule reaches it on the test corpus; the cap only guards
# a document shaped unlike it.
CAP = 15

# --------------------------------------------------------------------------- the gate
# Every word that could carry claim strength: hedges, approximators, near-quantifiers,
# tentative modals, intensifiers, and the graded-absolute modifiers. Deleting any of them
# changes what the sentence claims. This set is consulted by `_safe_delete` before a fix is
# written and again by `_gate` before a finding leaves the module.
HEDGE_VOCAB = {
    # hedges and tentative modals
    'may', 'might', 'could', 'would', 'should', 'appear', 'appears', 'appeared', 'seem',
    'seems', 'seemed', 'suggest', 'suggests', 'suggested', 'indicate', 'indicates',
    'imply', 'implies', 'tend', 'tends', 'tended', 'perhaps', 'maybe', 'possibly',
    'potentially', 'presumably', 'arguably', 'apparently', 'seemingly', 'plausibly',
    'likely', 'unlikely', 'probably', 'reportedly', 'putatively', 'ostensibly',
    # approximators and near-quantifiers
    'almost', 'nearly', 'virtually', 'practically', 'essentially', 'effectively',
    'basically', 'largely', 'mostly', 'broadly', 'generally', 'typically', 'usually',
    'often', 'frequently', 'occasionally', 'rarely', 'seldom', 'hardly', 'barely',
    'scarcely', 'roughly', 'approximately', 'about', 'around', 'circa', 'fairly',
    'relatively', 'somewhat', 'partly', 'partially', 'moderately', 'marginally',
    'some', 'several', 'many', 'most', 'few', 'much', 'various', 'certain', 'particular',
    'particularly', 'individual', 'given', 'specific', 'respective', 'kind', 'sort',
    # intensifiers and graded-absolute modifiers
    'very', 'really', 'quite', 'rather', 'highly', 'extremely', 'strongly', 'greatly',
    'considerably', 'substantially', 'significantly', 'markedly', 'notably', 'vastly',
    'completely', 'entirely', 'totally', 'wholly', 'fully', 'absolutely', 'perfectly',
    'purely', 'strictly', 'exactly', 'exact', 'precisely', 'truly', 'utterly', 'only',
    'just', 'at least', 'at most', 'up to', 'no more than', 'no fewer than',
}

# A fix that reads like this is a hedge-deleting fix, whatever rule wrote it.
_DEL_VERB = (r'\b(?:delete|deletes|deleting|remove|removes|removing|drop|drops|dropping|'
             r'cut|cuts|cutting|strip|strips|stripping|trim|trims|trimming|omit|omits|'
             r'omitting|excise|weaken|soften|replace|replaces|replacing|shorten)\b')
_WEAKENING = re.compile(
    _DEL_VERB + r'[^.]{0,80}?\b(?:hedge|hedges|hedging|hedged|qualifier|approximator|'
    r'intensifier|modal|modals|stance|first-person|tentative|' +
    '|'.join(sorted(re.escape(w) for w in HEDGE_VOCAB if ' ' not in w)) + r')\b', re.I)
_TIERS = ('batch', 'query')          # 'silent' needs one correct output; nothing here has


def _F(rule, offset, cost, text, fix='', tier='query'):
    """One finding. `blocks` is False for the whole family: register is never a blocker."""
    return {'rule': rule, 'family': FAMILY, 'offset': int(offset), 'tier': tier,
            'cost': cost, 'blocks': False, 'text': text, 'fix': fix}


def _targets(f):
    """The words a finding proposes to act on: everything it quotes, split into words."""
    quoted = re.findall(r'"([^"]{1,60})"', (f.get('fix') or '') + ' ' + (f.get('text') or ''))
    out = set()
    for q in quoted:
        out.add(q.strip().lower())
        out |= {w for w in re.findall(r"[a-z']+", q.lower())}
    return out


def _gate(findings):
    """The postfilter. Drops anything that could strip claim strength.

    Four invariants, none of them trusted to the call sites:
      1. tier is 'batch' or 'query' -- 'silent' would apply an edit with no author in the
         loop, and no register rule has exactly one correct output.
      2. a non-empty fix must not read as deleting or weakening a hedge, approximator,
         intensifier or modal (`_WEAKENING`, which is generated FROM HEDGE_VOCAB, so
         adding a word to the set tightens the gate automatically).
      3. a non-empty fix must not name a HEDGE_VOCAB word among the strings it quotes.
         This is the one that catches `Delete "virtually" from this sentence`, where the
         verb and the target are far apart or the phrasing is novel.
      4. a finding with an empty fix must be a query, so a report never arrives tiered as
         a batch edit.

    Invariant 3 is deliberately blunt: it also drops a legitimate finding whose quoted
    context happens to contain a hedge word, and it looks at the `text` as well as the
    `fix`. That is the right direction of error here. A dropped finding is a miss, while a
    fix that deletes a hedge is a silent overclaim shipped under the appearance of tidying,
    and the second costs more than the first. Where a rule was losing findings to this, the
    rule's wording was changed to name the word it deletes rather than the context around it.
    """
    out = []
    for f in findings:
        fix = (f.get('fix') or '').strip()
        if f.get('tier') not in _TIERS:
            continue
        if not fix and f.get('tier') != 'query':
            continue
        if fix:
            if _WEAKENING.search(fix):
                continue
            if _targets(f) & HEDGE_VOCAB:
                continue
        out.append(f)
    return out


def _safe_delete(word):
    """(fix_is_allowed, tier) for a proposal to delete `word`.

    The single decision point. A word that could carry claim strength is reported with an
    empty fix at tier 'query'; anything else may be proposed as a batch deletion.
    """
    w = word.strip().lower()
    if w in HEDGE_VOCAB or any(t in HEDGE_VOCAB for t in re.findall(r"[a-z']+", w)):
        return False, 'query'
    return True, 'batch'


# ------------------------------------------------------------------------- lexicons
# Frames whose removal cannot change what the sentence claims. The frame asserts nothing:
# it announces that an assertion is coming. Deleting it leaves the claim untouched, which
# is why this is the one deletion rule in the family with an unconditional fix.
EMPTY_FRAME = (r'\bit is important to note that\b|\bit is important to (?:point out|'
               r'mention|emphasi[sz]e) that\b|\bit should be (?:noted|mentioned|'
               r'pointed out|remarked|stressed|emphasi[sz]ed) that\b|'
               r'\bit (?:is|may be) (?:worth|worthwhile) (?:noting|mentioning|'
               r'pointing out) that\b|\bit must be (?:noted|emphasi[sz]ed|stressed) '
               r'that\b|\bas a matter of fact\b|\bneedless to say\b|'
               r'\bit is interesting to note that\b|\bthe fact of the matter is that\b|'
               r'\bwe would like to (?:note|point out|mention|emphasi[sz]e) that\b|'
               r'\bit goes without saying that\b|\bwhat is more important is that\b|'
               r'\bit bears (?:noting|mentioning|repeating) that\b')

# Doubled pairs. Each member means what the pair means.
DOUBLED = (r'\bfull and complete\b|\bcomplete and full\b|\beach and every\b|'
           r'\bbasic and fundamental\b|\bfundamental and basic\b|\bfirst and foremost\b|'
           r'\btrue and accurate\b|\bany and all\b|\ball and any\b|\bhopes and desires\b|'
           r'\bnew and novel\b|\bnovel and new\b|\bone and the same\b|'
           r'\bvarious and sundry\b|\bnull and void\b|\bfirst and initial\b|'
           r'\bcomponents and parts\b|\bgoals and objectives\b|\baims and objectives\b|'
           r'\bmethods and methodology\b')

# Pleonasm: the modifier's meaning is already inside the noun. Value is the word to delete.
REDUNDANT_MODIFIER = {
    'final outcome': 'final', 'final outcomes': 'final', 'final conclusion': 'final',
    'final conclusions': 'final', 'end result': 'end', 'end results': 'end',
    'past history': 'past', 'future plans': 'future', 'future plan': 'future',
    'true facts': 'true', 'true fact': 'true', 'basic fundamentals': 'basic',
    'new innovation': 'new', 'new innovations': 'new', 'unexpected surprise': 'unexpected',
    'advance planning': 'advance', 'advance warning': 'advance', 'free gift': 'free',
    'various different': 'different', 'each individual': 'individual',
    'joint collaboration': 'joint', 'added bonus': 'added', 'close proximity': 'close',
    'general consensus': 'general', 'past experience': 'past',
}
# A live contrast makes the modifier load-bearing: "past performance" against "projected".
CONTRAST_PARTNER = (r'\bfuture\b|\bprojected\b|\bexpected\b|\bcurrent\b|\bpresent\b|'
                    r'\bprior\b|\bearlier\b|\blater\b|\bplanned\b|\bforecast\w*\b|'
                    r'\bas opposed to\b|\brather than\b|\bversus\b|\bvs\.?\b')

# An intensifier on an ungradable absolute. Reported, never deleted: the intensifier
# grades the claim, and CHECKS_API forbids a rule that can reach it.
INTENSIFIER_ABSOLUTE = (r'\b(?:completely|totally|entirely|absolutely|utterly|wholly|'
                        r'perfectly|fully|exact|exactly|precisely|literally|truly|'
                        r'quite|very|really)\s+'
                        r'(?:same|identical|equal|unique|complete|impossible|essential|'
                        r'universal|optimal|final|absolute|eliminate|eliminates|'
                        r'eliminated|revolutioni[sz]e[ds]?|destroy(?:s|ed)?|'
                        r'unanimous|certain|sufficient|necessary)\b')

# Category nouns after an adjective. Value is a template for the rewrite.
CATEGORY_NOUN = [
    (r'\b(\w+)\s+in\s+colo(?:u)?r\b', 'drop "in colour" and keep the adjective'),
    (r'\b(\w+)\s+in\s+size\b', 'drop "in size" and keep the adjective'),
    (r'\b(\w+)\s+in\s+shape\b', 'drop "in shape" and keep the adjective'),
    (r'\b(\w+)\s+in\s+appearance\b', 'drop "in appearance" and keep the adjective'),
    (r'\bperiod of time\b', 'write "period"'),
    (r'\bin\s+a[n]?\s+(\w+)\s+manner\b(?!\s+(?:that|which|of))',
     'turn the adjective into an adverb'),
    (r'\bof\s+a[n]?\s+(\w+)\s+nature\b', 'turn the adjective into the predicate'),
]

# The four words the repaired ledger row scopes this to. Deletion is proposed for none of
# them without `_safe_delete` agreeing, and 'basically'/'really' are in HEDGE_VOCAB.
FILLER_ADVERB = (r'\bactually\b|\bbasically\b|\breally\b|\bkinda\b|\bsorta\b|'
                 r'\b(?:kind|sort) of\s+(?:a\s+)?(?:big|small|large|hard|difficult|easy|'
                 r'odd|strange|surprising|similar|different|obvious|clear|weird|good|bad|'
                 r'unclear|tricky|nice)\b')
# A contrast the text has just raised makes "actually" and "really" contrastive, which is
# the counter-case: deleting it loses the contradiction the sentence exists to state.
CONTRAST_CUE = (r'\bbut\b|\byet\b|\bhowever\b|\bwhereas\b|\bthough\b|\bin fact\b|'
                r'\bmerely\b|\brather\b|\binstead\b|\bnot only\b|\bor\b|\bsurprising\w*\b|'
                r'\bcontrary\b|\bwhile\b|\bexpect\w*\b|\bappear\w*\b|\bseem\w*\b')
# A graded position: the word is modifying a quantifier or an absolute, so it is an
# approximator rather than filler even before HEDGE_VOCAB is consulted.
GRADED_AFTER = (r'^\s*(?:all|every|no|none|any|the same|identical|complete|equal|'
                r'always|never|zero|nothing|everything|universal|impossible)\b')

# The ambiguous set: hedge, approximate quantifier, forward pointer, or empty filler, and
# a scan cannot tell which. Reported with the sentence, never deleted. See the docstring
# for the words removed from this pattern and why.
AMBIGUOUS = (r'\b(?:virtually|practically)\s+(?=all\b|every\b|none\b|no\b|identical\b|'
             r'the same\b|complete\b|impossible\b|always\b|never\b|any\b|zero\b|\w+ly\b|'
             r'[a-z]+ed\b)'
             r'|(?<!\bin )\bparticular\s+(?=[a-z]+\b)'
             r'|\bcertain\s+(?=[a-z]+s?\b)'
             r'|\bvarious\s+(?=[a-z]+\b)'
             r'|\bindividual\s+(?=[a-z]+s\b)'
             r'|\bgenerally\b|\bquite\b')
AMBIGUOUS_ROLE = {
    'virtually': 'hedge on a quantifier', 'practically': 'hedge on a quantifier',
    'generally': 'hedge on the scope of the claim', 'quite': 'grades the following word',
    'particular': 'either a pointer to a case the text specifies, or filler',
    'certain': 'either a pointer to conditions the text specifies, or filler',
    'various': 'either an approximate quantifier, or filler',
    'individual': 'either a distributive quantifier, or filler',
}

# Praise applied to the authors' own work or team. Deliberately excludes the superlatives
# checks_claim_calibration already reports.
SELF_PRAISE = (r'\boutstanding\b|\bexcellent\b|\bexceptional(?:ly)?\b|\bhighly successful\b|'
               r'\binternationally (?:recogni[sz]ed|renowned|leading)\b|\bworld[- ]class\b|'
               r'\bprestigious\b|\bunparalleled\b|\bimpressive\b|\bimmense\b|'
               r'\b(?:unique|ideal|perfect)(?:ly)? (?:placed|positioned|suited|qualified)\b|'
               r'\bunrivall?ed\b|\bfirst[- ]rate\b|\bpremier\b|\btop[- ]tier\b|'
               r'\bhighly (?:regarded|cited|influential)\b|\bstellar\b')
# Craft praise: the authors admiring their own design. The claim may well be supported,
# so this reports and stops.
CRAFT_PRAISE = (r'\bcleverly\b|\belegantly\b|\bingeniously\b|\bmeticulously\b|'
                r'\bskil?lfully\b|\bthoughtfully\b|\bcarefully (?:designed|crafted|'
                r'constructed|chosen|engineered)\b|\b(?:elegant|clever|ingenious|'
                r'sophisticated|beautiful)\s+(?:design|solution|method|approach|'
                r'formulation|construction|trick|framework|architecture)\b')
# Emotive and evaluative words, banned in the technical part.
EMOTIVE = (r'\bexciting\b|\bremarkabl[ey]\b|\bdramatic(?:ally)?\b|\bstunning\b|'
           r'\btremendous(?:ly)?\b|\bastonishing\b|\bspectacular\b|\bbreathtaking\b|'
           r'\bstriking(?:ly)?\b|\bfascinating\b|\bincredibl[ey]\b|\bamazing\b|'
           r'\bextraordinar(?:y|ily)\b|\bthrilling\b|\bcompelling\b|\btransformative\b|'
           r'\bgame[- ]changing\b|\bmind[- ]boggling\b|\bbeautiful(?:ly)?\b')
SELF = (r'\b(?:we|our|ours|us|i|my|me)\b|\bthis (?:paper|work|project|proposal|study|'
        r'method|approach|framework|team|group|laborator\w+|lab)\b|\bthe (?:PI|applicant|'
        r'proposed|present (?:paper|work|study|proposal))\b|\bthe host (?:institution|'
        r'group)\b')
# A named honour is a fact, not praise. ERC asks applicants to explain listed recognition.
AWARD_CONTEXT = (r'\bAward\b|\bPrize\b|\bMedal\b|\bFellowship\b|\bFellow\b|\bHonou?r\b|'
                 r'\bChair\b|\bLaureate\b|\bScholar\b|\bGrant\b|\bDistinguished\b')

# Criticism aimed at the people rather than the design.
DISMISSIVE = (r'\bna[iï]ve(?:ly)?\b|\bflawed\b|\bsimplistic\b|\bmisguided\b|\bcrude(?:ly)?\b|'
              r'\bfails? to appreciate\b|\bfailed to appreciate\b|\bmisunderstand\w*\b|'
              r'\bmisunderstood\b|\bill[- ]conceived\b|\bsloppy\b|\bcareless(?:ly)?\b|'
              r'\bunsophisticated\b|\bwrong[- ]?headed\b|\bsuperficial(?:ly)?\b|'
              r'\bmerely anecdotal\b|\bhand[- ]wav(?:y|ing)\b|\bconfused\b')
# Prior work has to be in the sentence, or the adjective is about the authors' own method.
PRIOR_WORK = (r'†|\bet al\b|\bprior work\b|\bprevious work\b|\bearlier work\b|'
              r'\bprior (?:approaches|methods|studies|attempts)\b|'
              r'\bprevious (?:approaches|methods|studies|attempts|authors)\b|'
              r'\bexisting (?:work|approaches|methods|literature)\b|'
              r'\bthe literature\b|\bearlier (?:attempts|studies|authors)\b')

# Complaints about the applicant's own circumstances.
COMPLAINT = (r'\binadequate(?:ly)? (?:funding|funded|resourc\w+|support\w*)\b|'
             r'\binsufficient(?:ly)? (?:funding|funded|resourc\w+|support\w*|equipment)\b|'
             r'\black of (?:equipment|resources|funding|support|infrastructure)\b|'
             r'\blacked (?:equipment|resources|funding|support)\b|'
             r'\breviewed unfairly\b|\bunfair(?:ly)? (?:review\w*|assess\w*|treat\w*)\b|'
             r'\blimited institutional support\b|\bhas never provided\b|'
             r'\bnever been (?:properly )?funded\b|\bpreviously low funding\b|'
             r'\bdifficult department\b|\bwithout adequate (?:funding|resources|support)\b')

# Proof duplication.
PROOF_DUP = (r'\bby the same (?:technique|argument|method|reasoning|steps?) as\b|'
             r'\bsee the proof of\b|\bidentical to the proof of\b|'
             r'\banalogous to (?:the proof of|that of)\b|\bmutatis mutandis\b|'
             r'\bfollows (?:exactly )?as (?:in|for) (?:the proof of|Theorem|Lemma)\b|'
             r'\bthe (?:same|identical) argument (?:as|applies)\b')

# Sentence-level negations, for the parity rule. Negative prefixes (unaffected, unified,
# unrestricted) are deliberately absent: they were measured and every hit was a false
# positive, because the prefix is lexical rather than a second negation of the predicate.
NEGATION = (r"\bnot\b|\bn't\b|\bno\b|\bnone\b|\bnever\b|\bnothing\b|\bnobody\b|"
            r"\bwithout\b|\bcannot\b|\bfails? to\b|\bfailed to\b|\blacks?\b|\blacked\b|"
            r"\bnor\b|\bneither\b|\bno longer\b|\babsent\b")
# Coordinated and focus negations that are one negation, not two.
NEG_SINGLE = r'\bneither\b[^.]{0,60}?\bnor\b|\bnot only\b|\bnot just\b|\bnot merely\b'
# Two negations further apart than this are in different predicates. See the rule.
NEG_GAP = 25
CLAUSE_SPLIT = (r'[,;:()]|\band\b|\bbut\b|\bor\b|\bthat\b|\bwhich\b|\bwho\b|\bif\b|'
                r'\bwhen\b|\bunless\b|\bbecause\b|\bwhile\b|\bsince\b|\bwhere\b|'
                r'\bwhether\b|\bso\b|\bthen\b|\bwhereas\b|\bthough\b')

# Negated predicates with an established one-word affirmative. Quantity bounds, negated
# hedges, statistical negatives and gradable adjectives are absent by construction: the
# counter-cases are explicit that "not significant", "not yet demonstrated" and "no fewer
# than three sites" must keep their negation.
AFFIRMATIVE = {
    'does not include': 'excludes', 'do not include': 'exclude',
    'did not include': 'excluded', 'does not contain': 'lacks',
    'do not contain': 'lack', 'does not have': 'lacks', 'do not have': 'lack',
    'did not have': 'lacked', 'did not continue': 'stopped',
    'does not continue': 'stops', 'is not present': 'is absent',
    'are not present': 'are absent', 'not before': 'after',
    'does not agree with': 'contradicts', 'do not agree with': 'contradict',
}
# Anything in the sentence from this list vetoes the substitution.
AFFIRM_VETO = (r'\bsignifican\w*\b|\bp\s*[<>=]|\beffect size\b|\bconfidence interval\b|'
               r'\bpower\b|\byet\b|\bstill\b|\bmay\b|\bmight\b|\bcould\b|\bshould\b|'
               r'\bwould\b|\bexpect\w*\b|\bhedge\b|\bat least\b|\bat most\b|\bfewer\b|'
               r'\bmore than\b|\bno fewer\b|\bno more\b|\bonly\b|\bnecessarily\b')

# Announcing frames: the sentence says what the document will do rather than what is true.
ANNOUNCE = (r'^(?:in|throughout)\s+this\s+(?:paper|study|work|article|proposal|report)'
            r'\s*,?\s+(?=\w)'
            r'|^this\s+(?:paper|study|work|proposal|article)\s+(?:examines|investigates|'
            r'explores|presents|describes|discusses|considers|addresses|reports on|'
            r'sets out to|aims to|seeks to|will)\s+'
            r'|^(?:here|herein)\s*,\s*we\s+(?:examine|investigate|explore|discuss|'
            r'consider|study|present|describe)\s+'
            r'|^we\s+(?:now\s+)?(?:examine|investigate|explore|discuss|consider|study|'
            r'turn to|look at|set out)\s+(?:the|how|whether|what|this|these|our)\b')
# What makes the remainder a claim rather than a topic.
CLAIMISH = (r'\d|†|‡|\bbecause\b|\bthan\b|\bwhereas\b|\bshows?\b|\bshowed\b|\bis\b|'
            r'\bare\b|\bwas\b|\bwere\b|\bcannot\b|\bdoes not\b|\bdo not\b|\bmust\b|'
            r'\bfollows\b|\bimplies\b|\bexplains?\b|\baccounts for\b|\bpredicts?\b')

# Work already completed, for the summary rule.
COMPLETED = (r'\b(?:we|i)\s+(?:have|had)\s+\w+(?:ed|n)\b|'
             r'\b(?:we|i)\s+(?:developed|built|showed|released|published|established|'
             r'demonstrated|created|ran|collected|trained|designed|validated|introduced)\b|'
             r'\bover the (?:past|last)\s+(?:\w+\s+)?(?:years?|decade|months?)\b|'
             r'\bin (?:earlier|previous|prior|our earlier|our previous) work\b|'
             r'\bour (?:earlier|previous|prior|recent) work (?:showed|established|'
             r'demonstrated|developed)\b')

# Section titles that are subjective by design. The emotive ban does not reach them.
SUBJECTIVE_SECTION = (r'impact|significance|broader|vision|motivation|why now|'
                      r'discussion|conclu|outlook|summary|abstract|synopsis|'
                      r'introduction|related work|state of the art|background|'
                      r'acknowledg|limitation')
# Sections that orient rather than argue, for the unlinked-paragraph rule.
BACKGROUND_SECTION = r'related work|state of the art|background|prior work|literature'


# --------------------------------------------------------------------------- utils
_ABBR = ('e.g.', 'i.e.', 'et al.', 'cf.', 'vs.', 'Fig.', 'Figs.', 'Tab.', 'Eq.', 'Eqs.',
         'Sec.', 'Secs.', 'App.', 'Ref.', 'Refs.', 'No.', 'approx.', 'resp.', 'w.r.t.',
         'Dr.', 'Prof.', 'Mr.', 'Ms.', 'St.', 'Inc.', 'ca.', 'al.')
_BREAK = '\x01'      # a heavy environment: never bridge a sentence across it
_INLINE = '\x02'     # inline math: bridge, because the sentence continues past it


def _sentences(spans):
    """Sentence records in document order: {'t', 'sp', 'k'}.

    Inline math is bridged and heavy environments break the sentence, so a claim split by
    a $...$ is not read as two fragments while a paragraph is never glued to whatever
    follows a figure. Abbreviations, initials and decimals are protected, or "et al." and
    "12.6" manufacture fragments. Environment names that render as a bare word
    ("\\begin{abstract}" -> "abstract") are stripped from the head of a sentence, because a
    rule anchored on the first word would otherwise match the environment name.
    """
    buf = []
    for sp in spans:
        if sp.kind == 'comment':
            continue                       # a reader never sees it
        if sp.kind == 'mask':
            head = sp.text.lstrip()[:8]
            buf.append((_INLINE if head.startswith(('$', '\\[', '\\(')) else _BREAK, sp))
            continue
        if sp.rendered.strip():
            buf.append((sp.rendered, sp))
    stream, index, pos = [], [], 0
    for txt, sp in buf:
        stream.append(txt)
        index.append((pos, pos + len(txt), sp))
        pos += len(txt)
    t = ''.join(stream)

    def span_at(i):
        for a, b, sp in index:
            if a <= i < b:
                return sp
        return index[0][2] if index else None

    prot = t
    for a in _ABBR:
        prot = prot.replace(a, a.replace('.', '\x00'))
    prot = re.sub(r'\b([A-Z])\.', '\\1\x00', prot)
    prot = re.sub(r'(\d)\.(\d)', '\\1\x00\\2', prot)
    cuts, start = [], 0
    for m in re.finditer(r'(?<=[.!?])\s+|' + _BREAK, prot):
        cuts.append((start, m.start()))
        start = m.end()
    cuts.append((start, len(prot)))
    recs = []
    for a, b in cuts:
        raw = prot[a:b]
        s = raw.replace('\x00', '.').replace(_INLINE, ' ').replace(_BREAK, ' ').strip()
        if len(s) < 3 or not re.search(r'[A-Za-z]', s):
            continue
        sp = span_at(a + (len(raw) - len(raw.lstrip())))
        s = re.sub(r'\s+', ' ', s)
        if sp is not None:
            # Structural macro arguments render as bare words and glue themselves to the
            # front of the following sentence: "\\section{Related Work}" makes the next
            # sentence begin "Related Work Earlier attempts ...", which drags its reported
            # offset back onto the \\section command, hides it behind the heading filter and
            # empties _section_at. "\\documentclass{article}" does the same to the first
            # sentence of the document. Only structural macros are stripped, and only from
            # the head of a sentence, so emphasised prose is left alone.
            heads = re.findall(r'\\(?:begin|end|(?:sub)*section|paragraph|subparagraph|'
                               r'chapter|title|documentclass|usepackage|input|include|'
                               r'author|date|bibliographystyle|pagestyle)\*?\s*'
                               r'(?:\[[^\]]*\])?\s*\{([^{}]{1,60})\}', sp.text)
            heads = sorted({re.sub(r'\s+', ' ', h).strip() for h in heads},
                           key=len, reverse=True)
            changed = True
            while changed:
                changed = False
                for h in heads:
                    if h and s.startswith(h) and len(s) > len(h) + 2:
                        s = s[len(h):].lstrip(' .,:;')
                        changed = True
                        break
        if len(s) < 3:
            continue
        recs.append({'t': s, 'sp': sp, 'k': len(recs)})
    for r in recs:
        r['off'] = _at(r['sp'], r['t']) if r['sp'] is not None else 0
    return recs


def _at(sp, phrase, fallback=None):
    """Offset into src for a rendered fragment, relocated by searching the span's source.

    Rendering is not offset preserving inside a span, so the fragment is found by its
    leading tokens, longest run first. Numerals count as tokens: without them a finding
    whose neighbourhood is all digits lands on the span start.
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


def _in_region(src, regions, sent):
    """True when a sentence's opening content words are found inside one of the regions.

    Membership is decided by searching the region's own source rather than by comparing a
    reconstructed offset: a document with no math is one text span, so every sentence in it
    would otherwise report the same offset and every membership test would answer alike.
    """
    if not regions:
        return False
    toks = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", sent)[:4]
    if not toks:
        return False
    pat = r'.{0,80}?'.join(re.escape(w) for w in toks)
    for a, b in regions:
        if re.search(pat, src[a:b], re.S | re.I):
            return True
    return False


def _sections(src):
    """[(body_start, body_end, title)] for every sectioning command, title rendered flat."""
    heads = [(m.start(), m.end(), m.group(1)) for m in
             re.finditer(r'\\(?:sub)*section\*?\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}', src)]
    out = []
    for i, (s, e, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(src)
        flat = re.sub(r'\\[a-zA-Z@]+\s*', ' ', title)
        out.append((e, end, re.sub(r'\s+', ' ', flat).strip(' -{}')))
    return out


def _section_at(secs, off):
    """Title of the section containing `off`, or '' before the first heading."""
    for a, b, t in secs:
        if a <= off < b:
            return t
    return ''


def _heading_ranges(src):
    """Argument ranges of sectioning commands and captions.

    A title is a label, not prose: reporting "Semantics matter for token space merging" as
    an announcing sentence is the finding that costs the tool its reader.
    """
    out = []
    for m in re.finditer(r'\\(?:chapter|section|subsection|subsubsection|paragraph|'
                         r'subparagraph|caption|captionof|title)\*?\s*(?:\[[^\]]*\])?\s*\{',
                         src):
        depth, j = 1, m.end()
        while j < len(src) and depth:
            if src[j] == '\\':
                j += 2
                continue
            depth += (src[j] == '{') - (src[j] == '}')
            j += 1
        out.append((m.end(), j))
    return out


def _in_heading(hrs, off):
    return any(a <= off < b for a, b in hrs)


# Macros whose argument a reader sees as prose. Anything else wrapping a long run of words
# is an annotation, not the document.
KNOWN_MACRO = set(
    'textbf textit emph texttt textsc textrm textsf textmd textup textnormal underline '
    'uline sout footnote footnotetext section subsection subsubsection paragraph '
    'subparagraph chapter title author caption captionof text mbox hbox fbox centering '
    'item textcolor colorbox highlight href url texorpdfstring MakeUppercase '
    'MakeLowercase thanks date abstract keywords quote cite citep citet citealp citealt '
    'citeauthor citeyear ref autoref cref Cref eqref label'.split())


def _note_ranges(src):
    """Offset ranges of author annotations and template boilerplate.

    Not a style preference -- a precision fix, measured. The test corpus defines \\lc,
    \\adam and \\uriel as coloured review-note macros in an INCLUDED preamble, so a
    per-file check cannot read their definitions, while `extract` unwraps a single-argument
    macro straight into rendered prose. Left in, three of the four filler findings on the
    paper came from inside review notes ("btw this is kinda in tension to us"), and the one
    negation finding on the proposal came from the ERC template's own \\instruction{Do NOT
    include any description of resources...}. Neither is the author's prose, and neither is
    this family's business: scaffolding and review markers belong to the integrity family.

    The test is structural rather than a name list: an unknown macro name wrapping at least
    40 characters and six words is an annotation. \\textbf and \\footnote are prose and are
    listed as such, and short-argument macros such as \\ceq never reach the threshold.
    """
    out = []
    for m in re.finditer(r'\\([a-zA-Z@]+)\s*\{', src):
        if m.group(1) in KNOWN_MACRO:
            continue
        depth, j = 1, m.end()
        while j < len(src) and depth:
            if src[j] == '\\':
                j += 2
                continue
            depth += (src[j] == '{') - (src[j] == '}')
            j += 1
        arg = src[m.end():j - 1]
        if len(arg) >= 40 and len(re.findall(r'[A-Za-z]{3,}', arg)) >= 6:
            out.append((m.start(), j))
    out.sort()
    merged = []
    for a, b in out:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def _content_words(t):
    STOP = {'the', 'a', 'an', 'and', 'or', 'but', 'of', 'in', 'on', 'to', 'for', 'with',
            'by', 'from', 'as', 'at', 'that', 'this', 'these', 'those', 'it', 'its',
            'we', 'our', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'not',
            'which', 'their', 'them', 'they', 'than', 'then', 'also', 'more', 'most',
            'can', 'may', 'will', 'would', 'such', 'both', 'into', 'only', 'while',
            'however', 'yet', 'across', 'between', 'when', 'where', 'what', 'how',
            'have', 'has', 'had', 'does', 'do', 'did', 'one', 'two', 'each', 'any',
            'all', 'no', 'its', 'us', 'i', 'my', 'me', 'if', 'so', 'there', 'here'}
    t = re.sub(r'[-\u2010-\u2015]', ' ', t.lower())
    return [w for w in re.findall(r"[A-Za-z]{3,}", t) if w not in STOP]


def _is_definition_file(src, path):
    """A macro file has no prose to judge, and its rendered text is nonsense."""
    if re.search(r'\\begin\s*\{document\}', src) or re.search(r'\\section\s*\{', src):
        return False
    defs = len(re.findall(r'\\(?:new|renew|provide)command|\\def\b|\\DeclareMathOperator',
                          src))
    return defs >= 5 or os.path.basename(path or '').lower().startswith(
        ('macro', 'command', 'lcommand', 'preamble', 'style'))


def _openers(sents, secs):
    """Sentence indices that open a section. Signposting there is legitimate.

    The ledger's counter-case is explicit: an announcing sentence is necessary at a section
    opening and in a contributions list, so the announcing rule must not reach them.
    """
    out = set()
    for a, b, _ in secs:
        inside = [s for s in sents if a <= s['off'] < b]
        for s in inside[:2]:
            out.add(s['k'])
    return out


# --------------------------------------------------------------------------- entry
def checks(src, spans, ctx):
    """Return register-redundancy findings. Never raises: a broken check yields nothing."""
    try:
        return _gate(_checks(src, spans, ctx or {}))
    except Exception:
        return []


def _checks(src, spans, ctx):
    if _is_definition_file(src, ctx.get('path', '')):
        return []
    sents = _sentences(spans)
    if not sents:
        return []
    d = {'src': src, 'spans': spans, 'sents': sents, 'ctx': ctx,
         'secs': _sections(src), 'heads': _heading_ranges(src),
         'abstract': _regions(src, 'abstract'),
         'notes': _note_ranges(src),
         'prose': ' '.join(sp.rendered for sp in spans if sp.kind == 'text')}
    d['openers'] = _openers(sents, d['secs'])
    out = []
    for fn in (_r_empty_frame, _r_doubled_pair, _r_redundant_modifier,
               _r_category_noun, _r_intensifier_absolute, _r_filler_adverb,
               _r_ambiguous_filler, _r_acronym_barely_used,
               _r_self_praise, _r_craft_praise, _r_emotive_technical,
               _r_dismissive, _r_complaint,
               _r_announcing_frame, _r_multiple_negations, _r_negation_affirmative,
               _r_restated_claim, _r_summary_completed_work,
               _r_proof_duplicated, _r_background_unlinked):
        try:
            got = fn(d) or []
        except Exception:
            continue                       # a broken check must return nothing, not raise
        out += got[:CAP]
    # Filter on the offset the finding actually reports. A review note sits mid-sentence
    # more often than not, so the sentence straddles prose and annotation: the paper's
    # "btw this is kinda in tension to us" survived a sentence-level filter because the
    # sentence it interrupts begins in real prose.
    out = [f for f in out
           if not any(a <= f['offset'] < b for a, b in d['notes'])
           and not _in_heading(d['heads'], f['offset'])]
    out.sort(key=lambda f: (f['offset'], f['rule']))
    return out


def _prose_sents(d):
    """Sentences a reader sees as prose: not a heading, caption, note or template block."""
    return [s for s in d['sents']
            if not _in_heading(d['heads'], s['off'])
            and not any(a <= s['off'] < b for a, b in d['notes'])]


# ------------------------------------------------------------------ safe deletions
def _r_empty_frame(d):
    """A frame that announces an assertion instead of making one.

    The only unconditional deletion in the family. "It is important to note that X" and X
    assert exactly the same thing with the same strength, so removing the frame cannot
    change the claim -- unlike every other candidate here, where the word might be grading
    it. "Needless to say" is also reported by checks_claim_calibration as a certainty
    marker; the overlap is deliberate, because there the finding is that the author
    declined an argument and here it is that the words can go.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(EMPTY_FRAME, s['t'], re.I):
            phrase = m.group(0)
            ok, tier = _safe_delete(phrase)
            out.append(_F('empty-frame-phrase', _at(s['sp'], s['t'][m.start():m.end() + 30]),
                          'free',
                          f'"{phrase}" announces an assertion instead of making one, and '
                          f'the sentence says the same thing without it',
                          'Delete the frame; the sentence carries the same claim '
                          'without it' if ok else '',
                          tier))
    return out


def _r_doubled_pair(d):
    """A doubled pair whose members mean the same thing.

    The reader looks for the distinction the pair implies and finds none. A pair containing
    a word that could grade a claim is reported rather than repaired, and a legal or
    specification context where the members are separable ("complete and correct") is not
    in the list.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(DOUBLED, s['t'], re.I):
            pair = m.group(0)
            ok, tier = _safe_delete(pair)
            out.append(_F('doubled-synonym-pair', _at(s['sp'], s['t'][m.start():m.end() + 20]),
                          'free',
                          f'"{pair}" pairs two words for one meaning, so the reader looks '
                          f'for a distinction that is not there',
                          'Keep whichever member matches the register of the surrounding '
                          'prose and cut the pairing' if ok else '',
                          tier))
    return out


def _r_redundant_modifier(d):
    """A modifier whose meaning is already inside the noun.

    Two guards. A live contrast in the sentence ("past performance" beside "projected")
    makes the modifier load-bearing and vetoes the finding entirely. And the word to be
    deleted goes through `_safe_delete`, which is why "each individual" is reported with an
    empty fix -- "individual" is a distributive quantifier as often as it is padding, and a
    scan cannot tell.
    """
    out = []
    for s in _prose_sents(d):
        low = s['t'].lower()
        for phrase, word in REDUNDANT_MODIFIER.items():
            for m in re.finditer(r'\b' + re.escape(phrase) + r'\b', low):
                window = low[max(0, m.start() - 120): m.end() + 120]
                if re.search(CONTRAST_PARTNER, window.replace(phrase, ' '), re.I):
                    continue               # the modifier is carrying a contrast
                ok, tier = _safe_delete(word)
                out.append(_F('redundant-modifier',
                              _at(s['sp'], s['t'][m.start():m.end() + 20]), 'free',
                              f'"{phrase}" says the modifier twice: the meaning of '
                              f'"{word}" is already in the noun',
                              f'Delete "{word}"' if ok else '',
                              tier))
    return out


def _r_category_noun(d):
    """A category noun after an adjective: "pink in colour", "in an accurate manner".

    The rewrite converts the adjective rather than deleting a word, so it cannot reach a
    hedge. "in a manner that ..." is excluded by the pattern, because there the manner
    phrase carries a restriction.
    """
    out = []
    for s in _prose_sents(d):
        for pat, how in CATEGORY_NOUN:
            for m in re.finditer(pat, s['t'], re.I):
                phrase = m.group(0)
                out.append(_F('redundant-category-noun',
                              _at(s['sp'], s['t'][m.start():m.end() + 20]), 'free',
                              f'"{phrase}" names the category the adjective already '
                              f'implies',
                              f'Rewrite as one word: {how}', 'batch'))
    return out


def _r_intensifier_absolute(d):
    """An intensifier on an ungradable absolute: "exact same", "completely eliminate".

    Reported and never repaired. The intensifier grades the claim, and CHECKS_API forbids a
    rule that can reach one -- deleting "exact" from "the exact same world" is a change in
    what is being asserted, not tidying, even though every mechanical test calls it
    redundant.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(INTENSIFIER_ABSOLUTE, s['t'], re.I):
            out.append(_F('intensifier-on-absolute',
                          _at(s['sp'], s['t'][m.start():m.end() + 20]), 'free',
                          f'"{m.group(0)}" intensifies a word that has no gradations, so '
                          f'the intensifier is either emphasis or a claim -- reported, not '
                          f'cut, because deleting it changes the assertion',
                          '', 'query'))
    return out


def _r_filler_adverb(d):
    """"actually", "basically", "really", hedge-position "kind of".

    Scoped to exactly the words the repaired ledger row names, and no wider. Deletion is
    proposed only for a word `_safe_delete` clears, outside a contrast context and outside
    a graded position. In practice that leaves "actually" alone: "basically" and "really"
    are in HEDGE_VOCAB because "basically the same" and "really large" grade a claim, so
    both are reported instead. The contrast guard exists for the counter-case, where
    "actually" marks a contradiction the sentence exists to state and deleting it loses the
    point.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(FILLER_ADVERB, s['t'], re.I):
            word = m.group(0)
            after = s['t'][m.end():m.end() + 24]
            contrast = bool(re.search(CONTRAST_CUE, s['t'], re.I))
            graded = bool(re.search(GRADED_AFTER, after, re.I))
            ok, tier = _safe_delete(word)
            if contrast or graded:
                ok, tier = False, 'query'
            why = ('it is contrastive here' if contrast else
                   'it grades what follows' if graded else
                   'it could be grading the claim')
            out.append(_F('empty-filler-adverb',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'free',
                          f'"{word}" adds no proposition to this sentence'
                          + ('' if ok else f', but {why}, so no deletion is proposed'),
                          f'Delete "{word}"' if ok else '', tier))
    return out


def _r_ambiguous_filler(d):
    """The words that are a hedge, a pointer or padding, and a scan cannot tell which.

    The heart of the family, and the reason the gate exists. Every occurrence is reported
    with its sentence and the role it might be playing. No deletion is ever proposed:
    removing "virtually" from "virtually all" upgrades a hedged claim to an absolute one,
    and removing "certain" from "certain conditions" drops a restriction the argument may
    depend on. Which of those is in front of you is decided by the surrounding argument,
    which is the author's knowledge and not the scan's.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(AMBIGUOUS, s['t'], re.I):
            word = m.group(0).strip().lower()
            role = AMBIGUOUS_ROLE.get(word, 'hedge, pointer or filler')
            sent = s['t'] if len(s['t']) <= 110 else s['t'][:107] + '...'
            out.append(_F('hedge-or-filler-ambiguous',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'free',
                          f'"{word}" here is {role} -- in "{sent}"', '', 'query'))
    return out


def _r_acronym_barely_used(d):
    """An acronym defined in the narrative and then barely used.

    Decidable: the definition is a parenthesised initialism whose letters are the initials
    of the words before it, and the uses are counted in the prose after it. Fewer than
    three later uses and the abbreviation costs the reader more than it saves. Deleting an
    abbreviation cannot change a claim, so this one carries a fix.
    """
    prose = d['prose']
    out, seen = [], set()
    for m in re.finditer(r'((?:[A-Za-z][A-Za-z-]*\s+){1,6})\(([A-Z][A-Za-z]{1,6})s?\)',
                         prose):
        ac = m.group(2)
        if ac in seen or len(ac) < 2:
            continue
        words = [w for w in re.split(r'[\s-]+', m.group(1).strip()) if w]
        if len(words) < len(ac):
            continue
        initials = ''.join(w[0].upper() for w in words[-len(ac):])
        if initials != ac.upper():
            continue
        seen.add(ac)
        uses = len(re.findall(r'\b' + re.escape(ac) + r's?\b', prose[m.end():]))
        if uses >= 3:
            continue
        expansion = ' '.join(words[-len(ac):])
        sp = next((x for x in d['spans'] if x.kind == 'text' and ac in x.text), None)
        off = _at(sp, ac) if sp is not None else 0
        out.append(_F('acronym-barely-used', off, 'free',
                      f'"{ac}" is defined for "{expansion}" and used {uses} more '
                      f'time{"" if uses == 1 else "s"} after that',
                      f'Delete the abbreviation and write "{expansion}" at each use',
                      'batch'))
    return out


# ------------------------------------------------------------------- promotional register
def _r_self_praise(d):
    """Praise applied to the authors' own work or team, with the funding trade-off named.

    Report only. The claim may be entirely supported, and the evidence cuts both ways:
    promotional wording is positively associated with funding at odds ratios near 1.5
    across two funders, so a reviewer's dislike of an adjective and a funder's measured
    preference for it point in opposite directions. Two guards keep this honest. A
    self-reference must be in the sentence, or the adjective is describing the field --
    "modern LLMs exhibit impressive multilingual capabilities" is not self-praise. And a
    named honour is a fact rather than praise, so an award context vetoes the finding,
    which is what keeps "IBM Outstanding Technical Achievement Award" out of the report.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(SELF_PRAISE, s['t'], re.I):
            word = m.group(0)
            window = s['t'][max(0, m.start() - 60): m.end() + 60]
            if re.search(AWARD_CONTEXT, window):
                continue                   # a named honour is evidence, not praise
            if word[0].isupper() and m.start() > 0:
                continue                   # part of a proper name
            if not re.search(SELF, s['t'], re.I):
                continue                   # praising the field, not this work
            out.append(_F('self-praise-adjective',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'lookup',
                          f'"{word}" praises your own work; a reviewer cannot check an '
                          f'adjective, though promotional wording does track funding '
                          f'(OR about 1.5, two funders) -- your call, not the tool\'s',
                          '', 'query'))
    return out


def _r_craft_praise(d):
    """The authors admiring the design of their own method.

    "Carefully designed", "cleverly", "elegantly": the reader is told the work is good
    instead of being shown the property that makes it good. Reported and not repaired,
    because the judgement may be supported by the very next sentence and the tool cannot
    read that.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(CRAFT_PRAISE, s['t'], re.I):
            if not re.search(SELF, s['t'], re.I):
                continue
            out.append(_F('self-praise-craft-adverb',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'lookup',
                          f'"{m.group(0)}" praises the craft of your own design rather '
                          f'than naming the property that makes it work', '', 'query'))
    return out


def _r_emotive_technical(d):
    """An emotive or evaluative word in the objective part of the document.

    Scoped by section, as the source scopes it: the ban is absolute in the technical part
    and a few such words legitimately belong in significance, impact, vision, discussion
    and the introduction, which are excluded. Report only, for the same funding trade-off
    as the praise rules.
    """
    out = []
    for s in _prose_sents(d):
        title = _section_at(d['secs'], s['off'])
        if not title or re.search(SUBJECTIVE_SECTION, title, re.I):
            continue
        if d['abstract'] and _in_region(d['src'], d['abstract'], s['t']):
            continue
        for m in re.finditer(EMOTIVE, s['t'], re.I):
            out.append(_F('emotive-word-in-technical-part',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'rework',
                          f'"{m.group(0)}" is an evaluative word in the technical section '
                          f'"{title[:40]}", where the property that made it feel that way '
                          f'is what the reader needs', '', 'query'))
    return out


def _r_dismissive(d):
    """Criticism that lands on the people rather than on the design.

    Prior work has to be named in the sentence, or the adjective is about the authors' own
    method: both hits on the test corpus were self-critical ("our naive conflict-resolving
    policy", "a naive baseline"), and reporting those as attacks on a reviewer's work would
    be a false positive of the worst kind. A fix is offered because restating a limitation
    impersonally does not weaken it -- it makes it checkable.
    """
    out = []
    for s in _prose_sents(d):
        if not re.search(PRIOR_WORK, s['t'], re.I):
            continue
        ms = [m for m in re.finditer(DISMISSIVE, s['t'], re.I)
              if not re.search(SELF, s['t'][:m.start()], re.I)]
        if ms:
            m = ms[0]
            words = ', '.join(f'"{x.group(0)}"' for x in ms[:4])
            out.append(_F('dismissive-criticism-of-prior-work',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'rework',
                          f'{words} judges the authors of prior work rather than its '
                          f'design, and a reviewer may be one of them',
                          'State the limitation as a property of the study design, and '
                          'name what the study did establish before what it did not',
                          'query'))
    return out


def _r_complaint(d):
    """A complaint about the applicant's own circumstances.

    A funder assesses resources as a criterion, so a complaint reads as evidence against
    that criterion. Career breaks and caring responsibilities are a different thing and
    belong in the section the funder provides for them, which is why the pattern names
    funding, equipment and review grievances only.
    """
    out = []
    for s in _prose_sents(d):
        ms = list(re.finditer(COMPLAINT, s['t'], re.I))
        if ms:
            m = ms[0]
            words = ', '.join(f'"{x.group(0)}"' for x in ms[:3])
            out.append(_F('circumstance-complaint',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'rework',
                          f'{words} complains about your circumstances, which a panel '
                          f'reads against the resources criterion',
                          'Convert it into what is committed now and what this grant '
                          'supplies, and put career context in the section provided for it',
                          'query'))
    return out


# ------------------------------------------------------------------ shape of the claim
def _r_announcing_frame(d):
    """A sentence that announces what the document will do instead of stating what is true.

    The frame is deleted mentally and what remains is inspected: if the remainder carries
    no number, no citation, no comparison and no assertion, the paragraph was a topic
    announcement and not an argument. Section openings and the first two sentences of a
    section are exempt, because the ledger's counter-case is explicit that signposting is
    necessary there and in a contributions list.
    """
    out = []
    for s in _prose_sents(d):
        if s['k'] in d['openers']:
            continue                       # signposting belongs at a section opening
        m = re.search(ANNOUNCE, s['t'], re.I)
        if not m:
            continue
        rest = s['t'][m.end():]
        if len(rest) < 12 or re.search(CLAIMISH, rest, re.I):
            continue                       # the remainder is a claim already
        out.append(_F('announcing-frame-no-claim', _at(s['sp'], s['t'][:80]), 'rework',
                      f'"{m.group(0).strip()}" announces a topic and what follows it '
                      f'("{rest[:60].strip()}") is not something a reader can agree or '
                      f'disagree with',
                      'Promote the remainder to a claim; if it is self-evident once the '
                      'frame is gone, the paragraph needs a claim rather than a rewrite',
                      'query'))
    return out


def _r_multiple_negations(d):
    """More than one negation in one clause, with the parity spelled out.

    Reports and stops, as the repaired row requires. Litotes and statistical negatives are
    correct as written and are double-negative in form -- "not uncommon in low-resource
    settings", "the difference was not non-significant" -- so the correct repair depends on
    which negation carries the point and only the author knows. Negative prefixes are not
    counted: "unaffected", "unified" and "unrestricted" each produced a false second
    negation when they were. "Neither ... nor" and "not only" are one negation, not two.
    """
    out = []
    for s in _prose_sents(d):
        t = re.sub(NEG_SINGLE, ' ', s['t'], flags=re.I)
        for cl in re.split(CLAUSE_SPLIT, t, flags=re.I):
            ms = list(re.finditer(NEGATION, cl, re.I))
            hits = [m.group(0).strip() for m in ms]
            if len(hits) < 2:
                continue
            # The two negations must sit on the same predicate, not merely in the same
            # clause. Measured: the only hit on the corpus without this was "if sharing is
            # not introduced immediately it does not arise later", two juxtaposed clauses
            # whose parity no reader loses. The parity-confusing cases are adjacent by
            # nature ("not uncommon", "no ... without", "not ... nor").
            if min(b.start() - a.end() for a, b in zip(ms, ms[1:])) > NEG_GAP:
                continue
            frag = ' '.join(cl.split())[:100]
            out.append(_F('multiple-negations-one-clause', _at(s['sp'], frag or s['t']),
                          'rework',
                          f'{len(hits)} negations in one clause ({", ".join(hits[:4])}) in '
                          f'"{frag}" -- confirm the polarity you intend',
                          '', 'query'))
    return out


def _r_negation_affirmative(d):
    """A negated predicate that has a one-word affirmative in the same register.

    The candidate is offered for approval and never applied. Every exclusion the repaired
    row demands is in place: significance terms, effect sizes, probabilities, gradable
    adjectives, modals, hedges, quantity floors and "yet"/"still" all veto the sentence, and
    a sentence-initial imperative is skipped because "Do NOT include a budget table here" is
    template text rather than a claim.
    """
    out = []
    for s in _prose_sents(d):
        low = s['t'].lower()
        if re.search(AFFIRM_VETO, low, re.I):
            continue
        for phrase, aff in AFFIRMATIVE.items():
            for m in re.finditer(r'\b' + re.escape(phrase) + r'\b', low):
                raw = s['t'][m.start():m.end()]
                if m.start() < 3 or raw != raw.lower():
                    continue               # an imperative or a shouted template line
                out.append(_F('negation-with-affirmative-equivalent',
                              _at(s['sp'], s['t'][m.start():m.end() + 30]), 'free',
                              f'"{phrase}" spends two words where "{aff}" says the same '
                              f'thing',
                              f'Candidate: "{aff}". Confirm, or keep the negation if the '
                              f'absence is the point being made', 'query'))
    return out


def _r_restated_claim(d):
    """The same claim in two or three landmark places, with the wording drifting.

    Landmarks are the abstract or synopsis, the contributions/objectives/aims section, and
    the conclusion/discussion/impact section: the three places a claim is conventionally
    stated, which is why the same sentence turns up in all three with small differences.
    Reported as a SET, with every variant quoted, so the author picks one phrasing rather
    than being told which to keep.

    Kept tight on purpose. checks_claim_calibration removed an abstract-versus-body pairing
    rule because shared n-grams match shared terminology rather than a shared claim. The
    difference here is the threshold and the target: a pair needs at least five shared
    content words AND a Jaccard overlap of 0.42 over content words, which is near-identical
    wording rather than a shared topic, and the finding says "you wrote this twice" rather
    than accusing anyone of overclaiming. On the test corpus it reports three sets on the
    proposal, each a genuine restatement ("the effort of adding a surface" against "adding a
    new surface"), and nothing at all on the paper.
    """
    src, sents = d['src'], d['sents']
    buckets = {}
    if d['abstract']:
        buckets['abstract'] = [s for s in sents if _in_region(src, d['abstract'], s['t'])]
    for a, b, title in d['secs']:
        if re.search(r'contribut|objectiv|\baims?\b|\bgoals?\b', title, re.I):
            buckets.setdefault('contributions', []).extend(
                [s for s in sents if a <= s['off'] < b])
        elif re.search(r'conclu|discuss|impact|summary|outlook', title, re.I):
            buckets.setdefault('conclusion', []).extend(
                [s for s in sents if a <= s['off'] < b])
    if len(buckets) < 2:
        return []
    words = {s['k']: set(_content_words(s['t'])) for s in sents}
    where, parent = {}, {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    keys = list(buckets)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            for s1 in buckets[keys[i]]:
                for s2 in buckets[keys[j]]:
                    if s1['k'] == s2['k'] or abs(s1['k'] - s2['k']) < 3:
                        continue
                    A, B = words[s1['k']], words[s2['k']]
                    if len(A) < 5 or len(B) < 5:
                        continue
                    shared = A & B
                    if len(shared) < 5 or len(shared) / len(A | B) < 0.42:
                        continue
                    if s1['t'] == s2['t']:
                        continue           # identical wording is a different fault
                    parent.setdefault(s1['k'], s1['k'])
                    parent.setdefault(s2['k'], s2['k'])
                    where[s1['k']] = keys[i]
                    where[s2['k']] = keys[j]
                    union(s1['k'], s2['k'])
    groups = collections.defaultdict(list)
    for k in parent:
        groups[find(k)].append(k)
    by_k = {s['k']: s for s in sents}
    out = []
    for members in groups.values():
        members = sorted(set(members))
        if len(members) < 2:
            continue
        places = sorted({where.get(k, '?') for k in members})
        quotes = ' | '.join(f'{where.get(k, "?")}: "{by_k[k]["t"][:70]}"'
                            for k in members[:3])
        out.append(_F('claim-restated-across-sections', by_k[members[0]]['off'], 'rework',
                      f'the same claim is stated {len(members)} times across '
                      f'{len(places)} landmark section{"" if len(places) == 1 else "s"} '
                      f'({", ".join(places)}) with the wording drifting -- {quotes}',
                      '', 'query'))
    return out


def _r_summary_completed_work(d):
    """A summary or abstract sentence whose main clause reports work already finished.

    Report only, and deliberately funder-neutral. Several funders invite a track-record
    sentence in the summary and only the instructions printed against that field decide: an
    ERC B1 synopsis can legitimately open on completed pilot work that establishes
    feasibility, and cutting it removes the evidence the panel needs at step one. The NIH
    Project Summary is the one place where this is an instruction violation, and that
    variant is not implemented because nothing in `ctx` identifies the attachment.
    """
    if not d['abstract']:
        return []
    box = [s for s in d['sents'] if _in_region(d['src'], d['abstract'], s['t'])]
    if not box:
        return []
    total = sum(len(s['t'].split()) for s in box) or 1
    out = []
    for s in box:
        m = re.search(COMPLETED, s['t'], re.I)
        if not m:
            continue
        share = round(100 * len(s['t'].split()) / total)
        out.append(_F('summary-reports-completed-work', s['off'], 'lookup',
                      f'the summary reports completed work ("{m.group(0).strip()}") and '
                      f'that sentence uses about {share}% of the box',
                      '', 'query'))
    return out


def _r_proof_duplicated(d):
    """A proof that defers to an earlier proof instead of sharing a lemma.

    The reader verifies the same reasoning twice and still never learns what the shared
    structure was. A short symmetric case is genuinely faster to restate than to abstract,
    which is why the fix is offered as a query rather than applied.
    """
    out = []
    for s in _prose_sents(d):
        for m in re.finditer(PROOF_DUP, s['t'], re.I):
            out.append(_F('proof-duplicated-reasoning',
                          _at(s['sp'], s['t'][m.start():m.end() + 30]), 'rework',
                          f'"{m.group(0)}" sends the reader through the same reasoning a '
                          f'second time without naming what the two results share',
                          'Extract the shared reasoning as a lemma, state it once, and '
                          'derive both results from it', 'query'))
    return out


def _r_background_unlinked(d):
    """A background paragraph no later sentence uses.

    Every non-load-bearing paragraph adds surface for an objection and removes space from
    the argument. But the counter-case is decisive and shapes the fix: the further a
    reviewer is from your field, the more orientation they need, so a paragraph a specialist
    would skip can be exactly what the generalist reviewer needs. The paragraph is therefore
    never proposed for deletion -- the fix adds the missing link clause. Deliberately strict:
    a paragraph is only reported when EVERY one of its own repeated content words is absent
    from the whole document after that section. It fires nowhere on the test corpus, which
    is the right behaviour for three well-linked documents rather than evidence that it
    works.
    """
    src = d['src']
    out = []
    for a, b, title in d['secs']:
        if not re.search(BACKGROUND_SECTION, title, re.I):
            continue
        after = set(_content_words(' '.join(
            sp.rendered for sp in ex.extract(src[b:]) if sp.kind == 'text')))
        for m in re.finditer(r'(?:\A|\n\s*\n)(.+?)(?=\n\s*\n|\Z)', src[a:b], re.S):
            para = m.group(1)
            if len(para.split()) < 40:
                continue
            text = ' '.join(sp.rendered for sp in ex.extract(para) if sp.kind == 'text')
            ws = [w for w in _content_words(text) if len(w) >= 6]
            key = [w for w, c in collections.Counter(ws).items() if c >= 2]
            if len(key) < 2:
                continue
            if any(w in after for w in key):
                continue
            out.append(_F('background-paragraph-unlinked', a + m.start(1), 'rework',
                          f'this paragraph in "{title[:40]}" turns on '
                          f'{", ".join(sorted(key)[:4])}, and no sentence after the '
                          f'section mentions any of them',
                          'Add one clause naming the aim, method choice or gap this '
                          'paragraph orients, and move it beside that claim. Keep the '
                          'paragraph: a generalist reviewer needs the orientation a '
                          'specialist skips', 'query'))
    return out


# --------------------------------------------------------------------------- self-test
# Prose carrying one instance of each rule, most of it the ledger's own before-examples.
# Used by --selftest, because fourteen of the twenty rules fire nowhere on the test corpus
# and a rule that has never fired is a rule that has never been checked.
_FIXTURE = r"""\documentclass{article}
\begin{document}
\begin{abstract}
Over the past five years we have developed a matched-vocabulary protocol and we now
propose to extend it to forty languages.
Vocabulary sharing accounts for much of the variation in cross-lingual transfer.
\end{abstract}
\section{Introduction}
Our laboratory has an outstanding record in multilingual modelling, and we are ideally
placed to deliver this.
It is important to note that the matched-vocabulary ablation (MVA) removes the confound.
The MVA is reported once more later on in the appendix.
This provides a full and complete description of each and every configuration.
During that period of time the membrane became pink in colour, and the holes must be
aligned in an accurate manner.
The final outcome rests on true facts.
Productivity actually depends on factors that basically involve psychology.
The method generally recovers virtually all of the signal under certain conditions.
Progress has been slow because our department has never provided adequate computing
resources and our previous proposal was reviewed unfairly.
\section{Related Work}
Subword tokenisation arrived in 2016, and tokenisation has framed every comparison
published since. The lineage runs from byte-pair encoding through unigram inventories to
the byte-level inventories most systems ship today, and each redesign reshuffles those
inventories again without changing anything the rest of this document depends on.

Earlier attempts \citep{rust2021} were naive about the confound and simplistic in their
treatment of prior work, and they failed to appreciate that corpus size varies with
vocabulary.
\section{Method}
We cleverly designed the estimator, and the elegant solution we present here is an
exciting and dramatic departure.
The two token spaces are the exact same size and the procedure completely eliminates
drift.
The consortium does not include any industrial partner in the first period.
It is not uncommon that no model without shared tokens transfers at all.
Padding so that the section has a body, with a sentence that carries no frame at all.
We examine the effect of vocabulary size on cross-lingual transfer.
The proof of Theorem 2 follows by the same technique as the proof of Theorem 1.
\section{Conclusion}
Vocabulary sharing accounts for most of the variation in cross-lingual transfer.
\end{document}
"""

# (tier, fix) pairs a rule must never be able to ship, and why each is caught.
_BYPASS = [
    ('batch', 'Delete "virtually" from this sentence'),        # quoted hedge target
    ('batch', 'Remove the word largely.'),                     # verb + hedge, unquoted
    ('query', 'Strip the hedge and tighten the claim'),         # verb + the word "hedge"
    ('silent', ''),                                             # tier not in the family
    ('batch', ''),                                              # empty fix must be a query
    ('query', 'delete "certain" here'),                         # quoted hedge target
    ('query', 'Replace "generally" with nothing'),              # replace + quoted hedge
    ('query', 'The word "quite" is surplus; take it out'),      # NO deletion verb at all
    ('batch', 'Trim "almost" and "fairly" from the claim'),     # two quoted hedges
    ('query', 'Soften the modal so it reads as tentative'),      # weakening the other way
]
# Findings that must survive, or the gate is simply eating the family.
_SURVIVE = [
    ('batch', 'Delete "it is important to note that"'),
    ('batch', 'Keep whichever member matches the register and cut the pairing'),
    ('query', ''),
    ('query', 'Candidate: "excludes". Confirm, or keep the negation if the absence is '
              'the point being made'),
]


def _selftest():
    """Assert the rules fire, and that the gate cannot be talked out of its invariants."""
    import tempfile
    ok = True
    with tempfile.NamedTemporaryFile('w', suffix='.tex', delete=False) as fh:
        fh.write(_FIXTURE)
        path = fh.name
    spans = ex.extract(_FIXTURE)
    got = checks(_FIXTURE, spans, {'stage': 'submission', 'path': path, 'style': {}})
    fired = collections.Counter(f['rule'] for f in got)
    expected = ['empty-frame-phrase', 'doubled-synonym-pair', 'redundant-modifier',
                'redundant-category-noun', 'intensifier-on-absolute',
                'empty-filler-adverb', 'hedge-or-filler-ambiguous',
                'acronym-barely-used', 'self-praise-adjective',
                'self-praise-craft-adverb', 'emotive-word-in-technical-part',
                'dismissive-criticism-of-prior-work', 'circumstance-complaint',
                'announcing-frame-no-claim', 'multiple-negations-one-clause',
                'negation-with-affirmative-equivalent',
                'summary-reports-completed-work', 'proof-duplicated-reasoning',
                'claim-restated-across-sections', 'background-paragraph-unlinked']
    for r in expected:
        if not fired[r]:
            print(f'  FAIL  {r} did not fire on the fixture')
            ok = False
    # Every finding must satisfy the family's invariants after the gate.
    for f in got:
        if f['tier'] not in _TIERS or f['family'] != FAMILY:
            print(f'  FAIL  {f["rule"]} left the module tiered {f["tier"]!r}')
            ok = False
        if f['fix'] and _targets(f) & HEDGE_VOCAB:
            print(f'  FAIL  {f["rule"]} proposes acting on a hedge: {f["fix"]!r}')
            ok = False
    # The gate itself, attacked directly. This is the test that matters: a rule author who
    # writes the fix a different way, or forgets the tier, must still not get through.
    for tier, fix in _BYPASS:
        probe = {'rule': 'probe', 'family': FAMILY, 'offset': 0, 'tier': tier,
                 'cost': 'free', 'blocks': False, 'text': 'probe', 'fix': fix}
        if _gate([probe]):
            print(f'  FAIL  gate passed a bypass: tier={tier!r} fix={fix!r}')
            ok = False
    for tier, fix in _SURVIVE:
        probe = {'rule': 'probe', 'family': FAMILY, 'offset': 0, 'tier': tier,
                 'cost': 'free', 'blocks': False, 'text': 'probe', 'fix': fix}
        if not _gate([probe]):
            print(f'  FAIL  gate ate a legitimate finding: tier={tier!r} fix={fix!r}')
            ok = False
    # Adding a word to HEDGE_VOCAB must tighten the gate without any other edit.
    for w in ('virtually', 'largely', 'certain', 'various', 'quite', 'basically'):
        if not _WEAKENING.search('delete ' + w):
            print(f'  FAIL  {w} is in HEDGE_VOCAB but not in the generated gate pattern')
            ok = False
    # A broken rule must yield nothing rather than raise.
    if checks('', [], {}) != [] or checks(None, None, None) != []:
        print('  FAIL  checks() did not degrade to []')
        ok = False
    print(f'selftest: {"PASS" if ok else "FAIL"}  '
          f'({sum(fired.values())} findings, {len(fired)} rules on the fixture, '
          f'{len(_BYPASS)} bypasses blocked, {len(_SURVIVE)} legitimate fixes kept)')
    return ok


# ------------------------------------------------------------------------- runner
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    stage = 'draft' if '--draft' in sys.argv else 'submission'
    if '--selftest' in sys.argv:
        sys.exit(0 if _selftest() else 1)
    quiet = '--quiet' in sys.argv
    tot = collections.Counter()
    per_file = collections.Counter()
    for p in args:
        src = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        spans = ex.extract(src)
        found = checks(src, spans, {'stage': stage, 'path': p, 'style': {}})
        for f in found:
            tot[f['rule']] += 1
            per_file[(os.path.basename(p), f['rule'])] += 1
            if not quiet:
                line = src.count('\n', 0, f['offset']) + 1
                print(f"{os.path.basename(p)}:{line}  [{f['tier']}/{f['cost']}]  "
                      f"{f['rule']}: {f['text']}")
                if f['fix']:
                    print(f"        -> {f['fix']}")
    print(f'\n--- {sum(tot.values())} findings, stage={stage} ---')
    for r, c in tot.most_common():
        print(f'  {c:4d}  {r}')
    if len({k[0] for k in per_file}) > 1:
        print('\nby file:')
        for (fn, r), c in sorted(per_file.items()):
            print(f'  {fn:18s} {c:4d}  {r}')
