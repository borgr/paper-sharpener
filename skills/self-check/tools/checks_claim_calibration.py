#!/usr/bin/env python3
"""Claim-calibration checks: the distance between what was measured and what is asserted.

Every rule in this module REPORTS. None of them proposes a rewrite that deletes or
weakens a hedge (may, might, appears, suggests, we argue), strips an approximator from a
graded absolute (almost all, fairly complete, largely universal), removes a tentative
modal, or drops a first-person stance marker. Such an edit is grammatical, survives every
mechanical meaning-preservation test, and silently lifts a claim past its evidence, so it
is never safe to apply without the author. Five separate rules in the ledger were flagged
unsafe for exactly that reason.

Published evidence makes this stricter rather than looser. Promotional wording is
positively associated with funding at odds ratios near 1.5 across two funders, measured on
real rejected applications, so confident prose is rewarded and the trade-off between
confidence and calibration belongs to the author. This module surfaces the trade-off and
declines to resolve it.

Consequently every finding here is tier 'query', and `fix` either names what the author
should verify or is empty. A postfilter (`_gate`) drops any finding that violates either
property, so a future edit to a rule cannot quietly ship a weakening fix.

Not implemented, from the 30-rule ledger, with the reason each was left out:

  * the hedge-deletion rule and the fact-versus-howler scoping rule are rules ABOUT rules,
    not document tests. They are honoured here as constraints, by `_gate` and by every
    `fix` string, rather than emitted as findings.
  * "the denominator is not stated within one sentence" (half of the percentage rule) fires
    on every accuracy and every per-language rate, where no denominator belongs in the
    sentence. Only the small-denominator half is decidable, and it is implemented.
  * "a paragraph adds a further strength while an obvious objection is unaddressed", the
    evaluative-adjective test on the why-it-matters sentence, and the vagueness test all
    need the reviewer's judgement about which sentence is the target and which objection is
    obvious. No pattern locates either.
  * the template-coverage test needs the funder's call and application form, which are not
    in the source.
  * the contribution-type trio (a claim about understanding versus a new capability, and
    the report of ambiguity between them) needs the proposal classified before the test can
    run, and the classification is exactly what is uncertain.
  * "flag the schedule-risk label only" produces a finding whose content is that a label
    exists, and the mitigation it asks after is not decidable from the text.
  * the direction-word test (improve, reduce, enhance with no magnitude) was measured
    before being dropped: 33 hits on the paper and 15 on the proposal work-plan part, well
    past the point where a reader stops reading findings. Most are objective sentences
    where the magnitude is exactly what the project will establish, so a number cannot be
    demanded there. The narrower question, not "where is the magnitude" but
    "what is the other side of the comparison", is decidable and is implemented as
    comparative-without-named-comparator over exactly three comparatives.
  * the deferral test ("will be determined", "subject to further work") is decidable as a
    phrase list but its condition, "sits under a scored criterion", is not readable from
    the source, and the phrase list belongs to the scaffolding family.
  * "no support anywhere in the document for the statement an intensifier introduces"
    requires deciding what supports a given claim, which is a semantic match no regex
    makes. The bare occurrence list (certainty-marker) is implemented instead.
  * "a claim of novelty whose own related-work section describes the same thing" is
    BLOCKED, not skipped. Locating the two sentences is easy; deciding that the cited work
    does the same thing rather than merely sharing the topic is the whole test, and the
    only mechanism available is n-gram overlap between the novelty sentence and a cited
    sentence in the related-work section. That mechanism is the one removed below for
    reporting a topic phrase as an overclaim. Measured on the four documents it also
    yields nothing to calibrate against: with level-aware section ranges the related-work
    sections hold 23, 27 and 14 sentences and share not one content bigram with any
    priority claim, so neither a positive nor a negative example exists here. It needs a
    claim-level match between the novelty predicate and the predicate attributed to the
    citation, plus, in a split document, the related-work file itself: in the ACL paper
    the priority claims sit in one \input file and the related work in another, and a
    check module is given one file at a time.
  * a strength mismatch between the abstract and the body was implemented, measured and
    removed. Pairing an abstract sentence with its body counterpart by shared n-grams
    matches shared terminology, not a shared claim: on the test corpus it reported "cross
    lingual knowledge generalization" as an overclaim because the phrase also occurs in a
    body sentence containing the word "might". Accusing an author of overclaiming on the
    strength of a topic phrase is exactly the finding that trains a reader to dismiss the
    tool, and no tightening of the n-gram fixed it.

Second pass, and what it changed beyond the four rules added. A concessive that pre-empts
a stated risk IS the conditioning, and the same shape recurs wherever a rule reads one
sentence and the discharging clause sits in its neighbour. Audited for it:
risk-kind-unstated-beside-flat-outcome had the identical trigger to the outcome-risk rule
and no `_risk_is_preempted` guard, and now has one. Four more read only their own sentence
for the evidence that discharges them, and now read the neighbour too: the multiplier for
orders-of-magnitude, the scope for unscoped-absolute, the intervention for
causal-verb-on-correlational-evidence, and the consequence for
novelty-as-its-own-justification. All five widenings were differentially tested against the
first-pass module over 25 real files and changed no finding. The rules with no such blind
spot are the lexical ones, where no neighbouring clause can repair grading an ungradable
term or writing "approached significance", and certainty-marker, which proposes nothing.

Interface: checks(src, spans, ctx) -> list[dict]   (see CHECKS_API.md)
"""
import os
import re
import sys
import pathlib
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex

FAMILY = 'claim-calibration'

# Per-rule ceiling. A calibration rule that fires more than a dozen times on one document
# is reading the author's register rather than a defect, and a reader who is accused of
# overclaiming twenty times stops reading the tool. Rules here are tightened to sit under
# this naturally; the cap only guards against a document shaped unlike the test corpus.
CAP = 12

# --------------------------------------------------------------------------- lexicons
# Hedges. Used only to decide whether a claim IS hedged. Never to propose removing one.
HEDGE = (r'\b(?:may|might|could|would|should|appears?|appeared|seems?|seemed|suggests?|'
         r'suggested|indicates?|indicated|implies|implied|possibly|perhaps|potentially|'
         r'presumably|arguably|apparently|plausibly|likely|unlikely|probably|somewhat|'
         r'largely|broadly|roughly|approximately|about|around|nearly|almost|virtually|'
         r'fairly|relatively|partly|partially|tends? to|tended to|we (?:argue|believe|'
         r'expect|anticipate|hypothesi[sz]e|conjecture|suspect)|in (?:our|my) view|'
         r'as far as we can tell|to (?:some|a large) extent|in some respects|'
         r'in principle|potential|possible)\b')

# Approximators that make an absolute into a scoped, hedged, correct claim.
# Their presence exempts the absolute. They are never removed.
APPROX = (r'\b(?:almost|nearly|virtually|practically|fairly|largely|broadly|mostly|'
          r'essentially|effectively|generally|typically|often|usually|not|no longer|'
          r'hardly|barely|rarely|seldom|some|many|most|several)\s*$')

# What may sit between the subject and its verb. A two-word wildcard gap matched
# "Every surface we add shows how much ...", reading a design sentence as a result claim,
# so only adverbs and connectives are allowed through.
_GAP = (r'(?:(?:also|then|therefore|thus|indeed|further|next|now|again|instead|however|'
        r'nevertheless|consistently|clearly|already|only|both|\w+ly)\s+){0,2}')

# Verbs that mark a sentence as reporting this document's own empirical work.
RESULT_VERB = (r'\b(?:we|our)\s+' + _GAP +
               r'(?:find|finds|found|show|shows|showed|observe|observed|measure|measured|'
               r'demonstrate|demonstrated|establish|established|confirm|confirmed|'
               r'report|reported|see|saw|obtain|obtained|achieve|achieved|verify|verified)\b'
               r'|\b(?:results?|experiments?|findings?|evidence|analysis|analyses|data|'
               r'ablations?)\s+' + _GAP +
               r'(?:show|shows|showed|demonstrate|demonstrates|reveal|reveals|confirm|'
               r'confirms|establish|establishes|indicate|indicates|suggest|suggests)\b')

# The narrower set: verbs that assert a finding rather than describe a procedure.
# "we measure", "we report" and "we see" describe what was done. Using the broad list
# reported "Language is where we measure decoupling" and "we report only that ..." as
# unsupported result claims, which are a roadmap sentence and a stated limitation.
CLAIM_VERB = (r'\b(?:we|our)\s+' + _GAP +
              r'(?:find|finds|found|show|shows|showed|observe|observed|demonstrate|'
              r'demonstrated|establish|established|confirm|confirmed|conclude|concluded|'
              r'prove|proved|reveal|revealed)\b'
              r'|\b(?:results?|experiments?|findings?|evidence|analysis|analyses|data|'
              r'ablations?)\s+' + _GAP +
              r'(?:show|shows|showed|demonstrate|demonstrates|reveal|reveals|confirm|'
              r'confirms|establish|establishes|indicate|indicates|suggest|suggests)\b')

# Priority / precedence markers. "first" is handled separately: the bare ordinal
# ("the first step", "First, we") is not a priority claim and must never be reported.
PRIORITY = (r'\bfirst-ever\b|\bfor the first time\b|\bunprecedented\b|\bno one has\b|'
            r'\bnobody has\b|\bhas never been (?:done|attempted|shown|studied)\b|'
            r'\bparadigm shift\b|\bthe only (?:work|study|approach|method|project|corpus|'
            r'dataset|framework|model)\b|\bnovel\b|\bpioneering\b|'
            r'\bfirst of its kind\b')
FIRST_PRIORITY = (r'\bthe first\s+(?:\w+\s+){0,2}'
                  r'(?:to|work|study|paper|project|corpus|dataset|benchmark|method|'
                  r'framework|model|system|demonstration|attempt|account|evidence|'
                  r'explanation|theory|proof|measurement|characteri[sz]ation|analysis|'
                  r'systematic|comprehensive|large-scale|end-to-end)\b')
# Ordinal "first" contexts. Any of these inside the match window vetoes a priority reading.
FIRST_ORDINAL = (r'\bfirst\s+(?:step|stage|phase|part|half|year|month|week|day|round|'
                 r'pass|token|layer|word|line|column|row|author|person|language|'
                 r'experiment|question|objective|work package|wp|two|three|four|set)\b|'
                 r'\bfirst[,;]|\bfirst-order\b|\bat first\b|\bfirst of all\b')

# Promotional superlatives about this document's own contribution.
SUPERLATIVE = (r'\bstate[- ]of[- ]the[- ]art\b|\bSOTA\b|\bbest[- ]performing\b|'
               r'\bunmatched\b|\bunrivalled\b|\bunrivaled\b|\bworld[- ]leading\b|'
               r'\bgroundbreaking\b|\bground[- ]breaking\b|\brevolutionary\b|'
               r'\boutperforms? all\b|\bsurpass(?:es)? all\b|\bbeats? all\b|'
               r'\bsuperior to all\b')
# Self-reference: without one of these a superlative is describing the field, not a claim.
SELF = (r'\b(?:we|our|ours|us)\b|\bthis (?:paper|work|project|proposal|study|method|'
        r'approach|framework)\b|\bthe proposed\b|\bthe present (?:paper|work|study)\b')
# A named comparison discharges the superlative: the reader can check it.
COMPARED = (r'\bthan\b|\bcompared (?:with|to)\b|\brelative to\b|\bover the\b|'
            r'\bagainst\b|\bbaselines?\b|\bprior (?:work|art|methods?)\b|†|‡')

# Causal verbs, and the correlational vocabulary that makes them unearned.
CAUSAL = (r'\bcauses?\b|\bcaused\b|\bcausing\b|\bleads? to\b|\bled to\b|'
          r'\bresults? in\b|\bresulted in\b|\bdrives?\b|\bdriven by\b|'
          r'\bproduces?\b|\binduces?\b|\bbrings? about\b|\bgives? rise to\b|'
          r'\bdemonstrates? that\b|\bproves? that\b|\bbecause of\b|\bdue to\b|'
          r'\bthe (?:root )?cause of\b|\bthe effect of\b')
# "predict" and "predictive" are deliberately absent: in a machine-learning document they
# name the task, not the evidence, and including them reported a work-package summary
# ("measure how much sharing a run produces ... and predict that extent") as a causal
# overclaim.
CORRELATIONAL = (r'\bcorrelat\w*\b|\bassociat(?:ion|ions|ed with|ive)\b|\bco-?occur\w*\b|'
                 r'\bcovar\w*\b|\bobservational\b|\bcross-sectional\b|\bR\^?2\b|'
                 r'\b(?:Pearson|Spearman|Kendall)\b|\bregress(?:ion|ions|ed)\b')

# Certainty markers. Halmos allows "obvious" as a signal that a step is standard, so
# these are listed and never deleted.
CERTAINTY = (r'\bobviously\b|\bclearly\b|\bof course\b|\bundoubtedly\b|'
             r'\bit is clear that\b|\bneedless to say\b|\btrivially\b|'
             r'\bit is evident that\b|\bself-evident\b')

# Comparatives on absolutes that have no gradations. An approximator on a QUANTIFIER
# ("almost all", "fairly complete", "largely universal") is a hedged true claim and is
# deliberately absent from this pattern.
UNGRADABLE = (r'\b(?:more|most|less|least|very|highly|extremely|somewhat|quite)\s+'
              r'(?:unique|optimal|optimum|exhaustive|universal|complete|impossible|'
              r'identical|equal|infinite|final|absolute|perfect)\b|'
              r'\b(?:an? )?(?:improved|increased|higher|greater|better)\s+'
              r'(?:level|degree|amount)\s+of\s+'
              r'(?:optimality|uniqueness|completeness|universality|exhaustiveness)\b')

# Commitment-level hedges only, for the abstract-against-body comparison. Deliberately
# excludes approximators (about, roughly, around, nearly), which qualify a number rather
# than a claim: pairing "about 13 seconds" with a flat abstract sentence reports a
# difference in numeric precision as a difference in confidence.
EPISTEMIC = (r'\b(?:may|might|could|appears?|seems?|suggests?|indicates?|implies|'
             r'possibly|perhaps|potentially|presumably|arguably|apparently|plausibly|'
             r'likely|probably|we (?:argue|believe|expect|anticipate|hypothesi[sz]e|'
             r'conjecture|suspect))\b')

# Ungraded absolutes, for the empirical-result test.
ABSOLUTE = r'\b(?:all|every|always|never|none|no)\b'
# Scope that makes an absolute checkable.
SCOPE = (r'\b(?:tested|examined|measured|evaluated|listed|reported|considered|'
         r'in (?:the|our) (?:sample|corpus|dataset|benchmark|suite|experiments?|setting)|'
         r'of the \d|of our \d|across the \d|in \d|for the \d|we (?:tested|examined|'
         r'evaluated|measured|considered|report|reported|present|ran|run|conducted|'
         r'describe|study|studied|control|controlled)|under (?:the|our)|'
         r'within (?:the|our))\b')

# Deferral of a decision to after the award, and outcome verbs asserted flat.
UNCONDITIONAL = (r'\bwill (?:show|establish|demonstrate|prove|reveal|confirm|'
                 r'determine|resolve|settle|deliver|yield|produce|identify)\b')
RISK_LABEL = (r'\bhigh[- ]risk\b|\bhigher[- ]risk\b|\bexploratory\b|\bspeculative\b|'
              r'\bhigh[- ]gain\b|\bambitious\b|\buncertain\b|\bblue[- ]sk(?:y|ies)\b')
# The risk is in what is learned.
RISK_OUTCOME = (r'\bmay not (?:hold|work|generali[sz]e|transfer|replicate|succeed|'
                r'carry|appear|emerge|be)\b|\bmight not\b|\bcould fail\b|'
                r'\bno (?:effect|signal)\b|\bnull result\b|\bfails? to (?:hold|'
                r'generali[sz]e|replicate)\b|\bthe (?:effect|signal|mechanism) '
                r'(?:may|might|could)\b|\bhypothes\w+ (?:may|might|could)\b')
# The risk is in when the step happens, or in access. Scope note only; see module report.
RISK_SCHEDULE = (r'\bdelivery date\b|\bdata access\b|\baccess agreement\b|\brecruit\w*\b|'
                 r'\bcompute allocation\b|\bdepend(?:s|ency|encies) on\b|\bdelay\w*\b|'
                 r'\bethics approval\b|\bprocurement\b|\bhiring\b|\bschedule\b|'
                 r'\btimeline\b|\bavailability of\b')

# Absence-as-argument phrasings.
ABSENCE = (r'\bhas never been (?:done|attempted|studied|tested|measured|explored)\b|'
           r'\bno one has (?:studied|examined|measured|tested|tried|asked)\b|'
           r'\bthere are no data on\b|\bno (?:study|work|prior work) has\b|'
           r'\bthis gap (?:has not|remains)\b|\bremains? (?:entirely )?unexplored\b|'
           r'\bhas received no attention\b|\bis (?:largely )?unstudied\b')
# What makes an absence claim into an argument.
CONSEQUENCE = (r'\benables?\b|\benabling\b|\bmakes? it possible\b|\bbecomes? possible\b|'
               r'\bwould allow\b|\ballows?\b|\bso that\b|\bwhich would\b|'
               r'\bunlocks?\b|\bopens? (?:up )?\b|\bmatters? because\b|'
               r'\bthe consequence\b|\bwithout (?:it|this|which)\b|\bblocks?\b|'
               r'\bcurrently cannot\b|\bcannot currently\b|\bdecidable\b')

# Change words that make a percentage a change rather than a level.
CHANGE = (r'\b(?:increase[ds]?|decrease[ds]?|reduc(?:e[ds]?|tion|ing)|improv(?:e[ds]?|'
          r'ement|ing)|gain(?:s|ed)?|drop(?:s|ped)?|fall(?:s|en)?|ris(?:e[ds]?|ing)|'
          r'speed-?up|faster|slower|higher|lower|more|less|fewer|growth|grew|'
          r'boost(?:s|ed)?|cut(?:s)?|saving[s]?)\b')
# Naming the base value discharges the percentage-change rule.
BASE_NAMED = (r'\brelative to\b|\bcompared (?:with|to)\b|\bover the\b|\bfrom\b.{0,40}\bto\b|'
              r'\bbaseline\b|\bof the\b|\bversus\b|\bvs\.?\b|\bagainst\b|\bpoints?\b|'
              r'\bthan\b')

TIME_UNIT = (r'(?:ms|milliseconds?|s|sec|secs|seconds?|min|mins|minutes?|h|hr|hrs|'
             r'hours?|days?)')

# ------------------------------------------------------------- second pass: lexicons
# The three comparatives the trial named, and their inflections. Nothing is extrapolated
# from them: a sibling module grew three evidenced heads into forty and reported 63
# findings on three documents, so "higher", "stronger", "improves" and the rest of the
# plausible class are deliberately absent. "higher" in particular is the most common word
# in a results section and carries its comparator in the table, not in the prose.
COMPARATIVE = r'\b(?:outperform|outperforms|outperformed|outperforming|better|faster)\b'

# What names the thing compared against. Checked in this sentence AND in either neighbour,
# because a comparator stated in a neighbouring clause IS the comparison, on the same
# principle as a concessive that pre-empts a stated risk.
COMPARATOR = (r'\bthan\b|\bcompared (?:with|to)\b|\brelative to\b|\bagainst\b|'
              r'\bversus\b|\bvs\.?\b|\bbaselines?\b|\bablations?\b|'
              r'\bprior (?:work|art|methods?|systems?|models?)\b|'
              r'\bover (?:the|our|its|his|her|their|a|an|previous|earlier|\w+ing)\b|'
              r'\bthe (?:previous|earlier|existing|monolingual|unmapped) \w+\b|†|‡')

# "better" and "faster" as adverbs modify a verb and rank nothing: "to better capture
# natural settings", "better understanding these discrepancies", "on toy data or better yet
# on natural data". All three occur in the test corpus and none is a claim.
COMPARATIVE_ADVERBIAL = (r'\b(?:better|faster)\s+(?:\w+ing|capture[sd]?|understand[s]?|'
                         r'reflect[s]?|represent[s]?|explain[s]?|model[s]?|approximate[sd]?|'
                         r'match(?:es)?|align[s]?|serve[sd]?|suit[s]?|predict[s]?|'
                         r'yet|still|late|soon|than)\b|'
                         r'\bthe better\b|\bfor the better\b|\ball the better\b|'
                         r'\bbetter (?:half|part)\b|\bknow better\b')
# The object of "outperform" IS the comparator: "outperformed models trained on trillions
# of words" names what was beaten, and only an objectless use claims a ranking with nothing
# behind it.
_OUTPERFORM_OBJECT = (r'^\s*(?:all |every |both |most |each )?'
                      r'(?:the |a |an |its |their |our |two |three |four |five |\d\S* )?'
                      r'[A-Za-z][\w-]*')

# A design the document itself describes as observational. Only explicit design vocabulary:
# "existing corpora" and "we analyse released models" are not here, because a controlled
# experiment routinely also analyses off-the-shelf models and saying so is not a confession
# that the causal claim rests on the observation.
OBSERVATIONAL = (r'\bobservational\b|\bcross-sectional\b|\bretrospective(?:ly)?\b|'
                 r'\bnaturally occurring\b|\bnatural(?:istic)?[- ]corpus\b|'
                 r'\bnatural corpora\b|\bfound data\b|\bin the wild\b|'
                 r'\bsurvey (?:data|responses|of respondents)\b|\bno intervention\b|'
                 r'\bwithout (?:any )?intervention\b|\bnon-?interventional\b|'
                 r'\bcorpus stud(?:y|ies)\b|\bcorrelational (?:design|study|analysis)\b|'
                 r'\bwe (?:do|did) not (?:vary|manipulate|control|intervene)\b')
# Mechanism verbs only. "demonstrates that" and "proves that" are in CAUSAL because they
# assert a conclusion, and with a document-level design gate they would reach every result
# sentence in an observational paper. Here the verb has to name a mechanism.
CAUSAL_MECHANISM = (r'\bcauses?\b|\bcaused\b|\bcausing\b|\bleads? to\b|\bled to\b|'
                    r'\bresults? in\b|\bresulted in\b|\bdrives?\b|\bdriven by\b|'
                    r'\bproduces?\b|\binduces?\b|\bbrings? about\b|\bgives? rise to\b|'
                    r'\bthe (?:root )?cause of\b|\bthe effect of\b|\bbecause of\b|'
                    r'\bdue to\b')

# An intervention anywhere in the neighbourhood earns the causal verb, so it vetoes.
INTERVENTION = (r'\bablat\w*|\bintervention\b|\bintervene\w*\b|\brandomi[sz]\w+\b|'
                r'\bwe (?:vary|varied|manipulat\w+|control(?:led)?|hold|held)\b|'
                r'\bcontrolled (?:experiment|setting|comparison|pretraining|bilingual)\b|'
                r'\bcausal (?:analysis|intervention)\b|\bcounterfactual\b|'
                r'\bidentical except\b|\bdiffer in one (?:trait|factor)\b')
# An investigative frame ahead of a causal verb makes it a question, not an assertion.
INVESTIGATIVE = (r'\b(?:whether|examines?|examined|examining|investigat\w+|tests?|tested|'
                 r'testing|asks?|asked|explores?|explored|question of|we ask|'
                 r'study whether|hypothesi[sz]\w+)\b')

# Populations a result can be generalised to.
POPULATION = (r'(?:models?|llms?|languages?|tasks?|datasets?|corpora|benchmarks?|domains?|'
              r'architectures?|tokeni[sz]ers?|speakers?|participants?|subjects?)')
# "all X" and "every X" only. "each X" and "any X" are distributive over the design ("for
# each model and game, we evaluate every language pair") and are not generalisations: with
# them included the corpus produced fifteen candidates, all of them design sentences.
UNIVERSAL_POP = r'\b(?:all|every)\s+(?:\w+[- ]){0,2}(' + POPULATION + r')\b'
POP_COUNT = (r'\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d{1,3})\s+'
             r'(?:\w+[- ]){0,2}(' + POPULATION + r')\b')
# First person plus a verb that reports what this document did, for the sentence that names
# the tested set.
TESTING_VERB = (r'\bwe\s+(?:\w+\s+){0,2}(?:test|tested|evaluate|evaluated|train|trained|'
                r'pretrain\w*|study|studied|examine|examined|measure|measured|report|'
                r'reported|ran|run|cover|covered|use|used|find|found|present)\b')

# Fixes must never do this. See _gate.
_WEAKENING = re.compile(
    # Verbs that weaken by themselves, with no object to name.
    r'\b(?:unhedg\w*|de-?hedg\w*|unqualif\w*|dequalif\w*)\b|'
    r'\b(?:delete|deleting|remove|removing|drop|dropping|cut|cutting|strip|stripping|'
    r'weaken|weakening|soften|softening|omit|omitting|excise|excising|replace|replacing|'
    r'downgrade|dilute|unhedge|tone down|do away with|get rid of|state (?:it |this )?'
    r'(?:plainly|flatly|without)|assert(?: it)? (?:flatly|plainly|directly))\b'
    r'[^.]{0,70}?\b(?:hedge|hedges|hedging|hedged|may|might|could|would|should|appears?|'
    r'seems?|suggests?|indicates?|possibly|perhaps|potentially|arguably|presumably|'
    r'plausibly|likely|probably|somewhat|we argue|we believe|we expect|modal|modals|'
    r'almost|nearly|virtually|fairly|largely|roughly|approximately|approximator|'
    r'qualifier|qualifiers|intensifier|caveat|stance|first-person|first person|'
    r'tentative|epistemic)\b', re.I)


# --------------------------------------------------------------------------- utils
def _F(rule, offset, cost, blocks, text, fix=''):
    """One finding. Tier is 'query' for every rule in this family, by construction."""
    return {'rule': rule, 'family': FAMILY, 'offset': int(offset), 'tier': 'query',
            'cost': cost, 'blocks': bool(blocks), 'text': text, 'fix': fix}


def _gate(findings):
    """Drop anything that breaks the family's two invariants.

    A rule edited later cannot ship a fix that deletes a hedge, and cannot escalate out of
    'query', because both are checked here rather than trusted at each call site.
    """
    out = []
    for f in findings:
        if f.get('tier') != 'query':
            continue
        if _WEAKENING.search(f.get('fix') or ''):
            continue
        out.append(f)
    return out


_ABBR = ('e.g.', 'i.e.', 'et al.', 'cf.', 'vs.', 'Fig.', 'Figs.', 'Tab.', 'Eq.', 'Eqs.',
         'Sec.', 'Secs.', 'App.', 'Ref.', 'Refs.', 'No.', 'approx.', 'resp.', 'w.r.t.',
         'Dr.', 'Prof.', 'Mr.', 'Ms.', 'St.', 'Inc.', 'ca.', 'al.')


_BREAK = '\x01'      # a heavy environment: never bridge a sentence across it
_INLINE = '\x02'     # inline math: bridge, because the sentence continues past it


def _sentences(spans):
    """Sentence records in document order.

    Each record is {'t': rendered sentence, 'sp': span, 'k': index}. Consecutive records
    are adjacent in the document, which is what the 'same or adjacent sentence' tests need.

    Two details matter and both were found by measuring false positives.

    Inline math is bridged. Masking splits every span at each $...$, so a naive per-span
    split cuts "raising the score to 12.6% --- a $14\\times$ improvement over the baseline"
    into two fragments, and the half holding the percentage then looks as though it names
    no base. Heavy environments break the sentence instead, because gluing a paragraph to
    whatever follows a figure invents adjacency that no reader sees.

    Abbreviations, initials and decimals are protected, or "et al." and "12.6" manufacture
    fragments that read as unsupported claims.
    """
    pieces, buf = [], []
    for sp in spans:
        if sp.kind == 'comment':
            continue                       # a reader never sees it
        if sp.kind == 'annot':
            buf.append((_INLINE, sp))      # a review note: bridged, so the prose either
            continue                       # side of it is not glued into one sentence
        if sp.kind == 'mask':
            head = sp.text.lstrip()[:8]
            buf.append((_INLINE if head.startswith(('$', '\\[', '\\(')) else _BREAK, sp))
            continue
        if sp.rendered.strip():
            buf.append((sp.rendered, sp))
    stream, index = [], []                 # index: (stream_start, stream_end, span)
    pos = 0
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
    prot = re.sub(r'\b([A-Z])\.', '\\1\x00', prot)          # initials
    prot = re.sub(r'(\d)\.(\d)', '\\1\x00\\2', prot)        # decimals
    out, start = [], 0
    for m in re.finditer(r'(?<=[.!?])\s+|' + _BREAK, prot):
        out.append((start, m.start()))
        start = m.end()
    out.append((start, len(prot)))
    recs = []
    for a, b in out:
        raw = prot[a:b]
        s = raw.replace('\x00', '.').replace(_INLINE, ' ').replace(_BREAK, ' ').strip()
        if len(s) < 3 or not re.search(r'[A-Za-z]', s):
            continue
        first = a + (len(raw) - len(raw.lstrip()))
        sp = span_at(first)
        s = re.sub(r'\s+', ' ', s)
        # \begin{abstract} renders as the bare word "abstract", so a sentence can open with
        # an environment name that no reader sees. Left in, it defeats a \b anchored word
        # match on the real first word and drags the reported offset to the \begin.
        if sp is not None:
            envs = set(re.findall(r'\\(?:begin|end)\s*\{(\w+)\*?\}', sp.text))
            while True:
                m2 = re.match(r'([A-Za-z]+)\s+', s)
                if m2 and m2.group(1) in envs:
                    s = s[m2.end():]
                    continue
                break
        if len(s) < 3:
            continue
        recs.append({'t': s, 'sp': sp, 'k': len(recs)})
    return recs


def _at(sp, phrase, fallback=None):
    """Offset into src for a rendered fragment, found by searching the span's own source.

    Rendering is not offset preserving inside a span, so the fragment is relocated by its
    leading tokens, longest run first. Numbers count as tokens: a finding about "12.6%"
    often has no words near it, and without the digits it would land on the span start,
    which puts the reported line number on an unrelated \\end{figure}.
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


def _support(src, off, radius=280):
    """True when the source near `off` carries a number, a citation or a cross-reference.

    Read from src rather than from rendered prose on purpose: a supporting figure is very
    often inside masked math ($14\\times$) or inside \\cite/\\ref, none of which survive
    into the rendered string. Judging support from prose alone would report a well
    evidenced sentence as bare.
    """
    w = src[max(0, off - radius): off + radius]
    if re.search(r'\\(?:cite|ref|autoref|cref|Cref|eqref)', w):
        return True
    if re.search(r'\$[^$]*\d', w):
        return True
    return _number_near(src, off, radius)


def _number_near(src, off, radius=120):
    """True when a numeral sits near `off`, ignoring citations and cross-references.

    The significance rule needs "is a magnitude given here", and a \\ref pointing at a
    section is not a magnitude. Using the full support test there vetoed both real
    candidates in the test corpus, because a results sentence almost always carries a
    cross-reference.
    """
    w = src[max(0, off - radius): off + radius]
    w = re.sub(r'\\(?:cite|ref|autoref|cref|Cref|eqref)[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*'
               r'\{[^}]*\}', ' ', w)
    w = re.sub(r'\\[a-zA-Z@]+', ' ', w)
    return bool(re.search(r'(?<![\w\\])\d', w))


def _pct_iter(text):
    """(match_start, match_end, value_string) for each percentage in rendered text.

    \\% survives rendering as a literal backslash-percent, so both forms are matched.
    A bare '%' never appears in a text span, because that is a comment.
    """
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(?:\\%|%|per ?cent\b|percent\b)', text):
        yield m.start(), m.end(), m.group(1)


def _is_definition_file(src, path):
    """A macro file has no prose to calibrate, and its rendered text is nonsense."""
    if re.search(r'\\begin\s*\{document\}', src) or re.search(r'\\section\s*\{', src):
        return False
    defs = len(re.findall(r'\\(?:new|renew|provide)command|\\def\b|\\DeclareMathOperator', src))
    return defs >= 5 or os.path.basename(path or '').lower().startswith(('macro', 'command',
                                                                        'lcommand', 'preamble'))


def _heading_ranges(src):
    """Argument ranges of sectioning commands and captions.

    "\\subsection{Sampling Variance and Significance}" is a topic label, and reporting it as
    an unsupported significance claim is the kind of finding that costs the tool its
    reader.
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


def _emph_ranges(src):
    """Argument ranges of \\emph and \\textit.

    A hand-written publication list writes each cited work's title in \\emph, and one of
    them in the test corpus is "Fusing finetuned models for better pretraining". Reading a
    comparative out of somebody else's title and calling it an unanchored claim is exactly
    the finding that costs the tool its reader.
    """
    out = []
    for m in re.finditer(r'\\(?:emph|textit|textsl)\s*\{', src):
        depth, j = 1, m.end()
        while j < len(src) and depth:
            if src[j] == '\\':
                j += 2
                continue
            depth += (src[j] == '{') - (src[j] == '}')
            j += 1
        out.append((m.end(), j))
    return out


def _inputs_a_body_file(src):
    """True when the file pulls its prose in from elsewhere with \\input or \\include.

    A macro file is not prose: this paper's preamble reads \\input{latex/Lcommands} and its
    body is right here, while the ACL paper reads \\input{section/0_abstract} and holds no
    prose at all. Only the second case makes an absence test meaningless, so the target name
    decides, not the presence of the command.
    """
    macroish = ('macro', 'command', 'preamble', 'package', 'style', 'def', 'header',
                'symbol', 'font', 'acronym', 'notation')
    for m in re.finditer(r'\\(?:input|include)\s*\{([^}]*)\}', src):
        name = m.group(1).strip().lower()
        base = os.path.basename(name)
        if not any(k in base for k in macroish):
            return True
    return False


def _comment_stripped(src):
    """`src` with line comments blanked and length preserved, so offsets still line up.

    A commented-out figure or table must not discharge a claim: the reader never sees it.
    """
    return re.sub(r'(?<!\\)%[^\n]*', lambda m: ' ' * len(m.group(0)), src)


def _stem(word):
    """Crude singular. Only ever used to ask whether two population nouns are the same."""
    w = word.lower()
    return w[:-1] if w.endswith('s') and not w.endswith('ss') else w


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
    """True when this sentence's opening content words sit inside one of the regions.

    Membership is decided by searching the region's own source rather than by comparing a
    reconstructed offset, because rendering is not offset preserving inside a span: a
    document with no math is a single text span, so every sentence in it would otherwise
    report the same offset and the abstract test would answer the same way for all of them.
    """
    if not regions:
        return False
    toks = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", sent)[:4]
    if not toks:
        return False
    pat = r'.{0,80}?'.join(re.escape(w) for w in toks)
    for a, bb in regions:
        if re.search(pat, src[a:bb], re.S | re.I):
            return True
    return False


def _content_words(t):
    STOP = {'the', 'a', 'an', 'and', 'or', 'but', 'of', 'in', 'on', 'to', 'for', 'with',
            'by', 'from', 'as', 'at', 'that', 'this', 'these', 'those', 'it', 'its',
            'we', 'our', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'not',
            'which', 'their', 'them', 'they', 'than', 'then', 'also', 'more', 'most',
            'can', 'may', 'will', 'would', 'such', 'both', 'into', 'only', 'while',
            'however', 'yet', 'across', 'between', 'when', 'where', 'what', 'how'}
    # Hyphens are normalised: the abstract writing "native-language efficiency" and the
    # body writing "native language efficiency" is one phrase, not two.
    t = re.sub(r'[-\u2010-\u2015]', ' ', t.lower())
    return [w for w in re.findall(r"[A-Za-z]{3,}", t) if w not in STOP]


# --------------------------------------------------------------------------- entry


# A concessive that pre-empts the stated risk IS the conditioning. "Thus, regardless of
# whether the outcome is one explanation or several, the project will establish ..." names
# the uncertainty and scopes the claim to hold under either branch, which is how a risk
# section is supposed to read. Flagging it reported correct writing as a defect.
_PREEMPTIVE = re.compile(
    r'\b(regardless of whether|whether or not|either way|in either case|'
    r'whichever|no matter (?:whether|which|how)|even if|whatever the)\b', re.I)


def _risk_is_preempted(sentence, window=''):
    return bool(_PREEMPTIVE.search(sentence or '') or _PREEMPTIVE.search(window or ''))


def checks(src, spans, ctx):
    """Return claim-calibration findings. Never raises: a broken check yields nothing."""
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
    prose = ' '.join(sp.rendered for sp in spans if sp.kind == 'text')
    abstract = _regions(src, 'abstract')
    out = []
    for fn in (_r_pct_small_denominator, _r_se_doubled_small_n,
               _r_significant_no_effect_size, _r_significance_threshold_language,
               _r_priority_unanchored, _r_superlative_no_comparison,
               _r_novelty_as_justification, _r_causal_on_correlational,
               _r_timing_precision, _r_number_measured_and_estimated,
               _r_pct_change_no_base, _r_orders_of_magnitude,
               _r_risk_outcome_unconditional, _r_risk_kind_unstated,
               _r_ungradable_comparative, _r_unscoped_absolute,
               _r_stacked_hedges, _r_unhedged_result_no_support,
               _r_certainty_marker, _r_abstract_claim_absent_from_body,
               _r_abstract_number_absent_from_body, _r_comparative_no_comparator,
               _r_causal_on_observational_design, _r_generalisation_beyond_tested):
        try:
            got = fn(src, spans, sents, prose, abstract, ctx) or []
        except Exception:
            continue                       # a broken check must return nothing, not raise
        out += got[:CAP]
    out.sort(key=lambda f: (f['offset'], f['rule']))
    return out


# ------------------------------------------------------------------- numbers and tests
def _r_pct_small_denominator(src, spans, sents, prose, abstract, ctx):
    """A percentage whose own sentence states a denominator under twenty.

    Zobel's objection is that two of five is not "40% of the time": the percentage throws
    away the sample size and borrows a large-sample authority. Only the decidable half of
    the ledger test is implemented. The other half, "the denominator is not stated within
    one sentence", fires on every accuracy and every per-language rate, where no
    denominator belongs in the sentence at all, so it is left out (see module report).
    """
    # The denominator has to be a count of something. "from 5.9%" is a base value, not a
    # denominator, and matching a bare number after "from" turned every percentage change
    # in the test corpus into a small-sample accusation.
    counted = (r'(?:cases?|examples?|instances?|trials?|runs?|seeds?|models?|languages?|'
               r'pairs?|datasets?|documents?|items?|subjects?|participants?|samples?|'
               r'tasks?|benchmarks?|questions?|facts?|entities|conditions?|settings?|'
               r'experiments?|attempts?|failures?|errors?)')
    out, seen = [], set()
    for s in sents:
        t = s['t']
        dens = [int(m.group(1)) for m in
                re.finditer(r'\b(?:of|out of|among|on|over|across|in|from)\s+(?:the\s+)?'
                            r'(\d{1,2})(?![.,]?\d)'
                            r'\s*(?!\\?%)(?:\w+\s+){0,2}' + counted + r'\b', t, re.I)]
        dens += [int(m.group(1)) for m in
                 re.finditer(r'\bn\s*=\s*(\d{1,2})(?![.,]?\d)\b', t)]
        small = [d for d in dens if 1 < d < 20]
        if not small:
            continue
        for a, b, val in _pct_iter(t):
            key = (s['k'], val)
            if key in seen:
                continue
            seen.add(key)
            out.append(_F('percentage-over-small-denominator', _at(s['sp'], t[a:b + 12], None),
                          'free', False,
                          f'"{val}%" is reported over {min(small)} observations, a '
                          f'denominator small enough that the percentage claims more '
                          f'stability than the count supports',
                          'Confirm the denominator, and consider giving the raw count '
                          'alongside the percentage so the reader can see how far one '
                          'observation moves it'))
    return out


def _r_se_doubled_small_n(src, spans, sents, prose, abstract, ctx):
    """A 95% interval built by doubling a standard error where n is under ten.

    At n below 10 the t multiplier is well above 2, so the interval is narrower than the
    data allows and every comparison read off it is overconfident. Fires only when the
    text states both the doubling and a small n, because inferring either is guesswork.
    """
    out = []
    doubling = (r'\b(?:two|2)\s+standard errors?\b|\btwice the standard error\b|'
                r'\b(?:±|\+/-)\s*2\s*(?:×|x|\*)?\s*(?:s\.?e\.?|standard error|sem)\b|'
                r'\b2\s*(?:×|x)\s*(?:s\.?e\.?|standard error)\b')
    for s in sents:
        t = s['t']
        if not re.search(doubling, t, re.I):
            continue
        ns = [int(m.group(1)) for m in
              re.finditer(r'\b(?:n|N)\s*=\s*(\d+)\b|\b(\d+)\s+(?:runs?|seeds?|trials?|'
                          r'replicates?|folds?)\b', t) if m.group(1)]
        ns += [int(m.group(1)) for m in
               re.finditer(r'\b(\d+)\s+(?:runs?|seeds?|trials?|replicates?|folds?)\b', t)]
        if any(n < 10 for n in ns):
            out.append(_F('standard-error-doubled-at-small-n', _at(s['sp'], t), 'lookup', True,
                          f'a 95% interval is obtained by doubling a standard error at '
                          f'n={min(ns)}, where the t multiplier is well above 2',
                          'Check the multiplier against the t distribution for these '
                          'degrees of freedom, and state the multiplier and n where the '
                          'interval is reported'))
    return out


def _r_significant_no_effect_size(src, spans, sents, prose, abstract, ctx):
    """"Significant" or "significantly" with no test, no p value and no effect size near it.

    The statistical reading and the plain-English reading are the same word, and a reader
    who supplies the statistical one takes a threshold crossing for a magnitude. Fires
    only when neither the sentence nor either neighbour carries any of a p value, a test
    name, a confidence interval or an effect-size statistic.
    """
    evidence = (r'\bordinary least squares\b|\bOLS\b|\bregress\w*\b|'
                r'\bp\s*[<=>≤≥]|\bp-?value|\bconfidence interval\b|\bCI\b|'
                r'\bt-?test\b|\bANOVA\b|\bchi-?squared?\b|\bχ2\b|\bWilcoxon\b|'
                r'\bMann-?Whitney\b|\bbootstrap\w*\b|\bpermutation test\b|'
                r"\bCohen'?s d\b|\beffect size\b|\bstandard (?:error|deviation)\b|"
                r'\bs\.?d\.?\b|\bstderr\b|\bsignificance test\b|\bcorrected\b|'
                r'\bBonferroni\b|\bHolm\b|\bFDR\b|\bpaired\b|\bunpaired\b|\bseeds?\b')
    headings = _heading_ranges(src)
    out = []
    for s in sents:
        t = s['t']
        for m in re.finditer(r'\bsignificantly\b|\bsignificant\b|\bsignificance\b', t, re.I):
            # "of great significance", "significant investment": not a test claim.
            tail = t[m.end():m.end() + 30]
            if re.match(r'\s+(?:investment|effort|resources|funding|portion|fraction|'
                        r'proportion|challenge|obstacle)', tail, re.I):
                continue
            # "significance measures", "significance testing", "the significance of script":
            # the word names a method or means plain importance, not a test result.
            if re.match(r'\s+(?:measures?|measurement|statistics?|testing|tests?|'
                        r'analys[ei]s|levels?|thresholds?|values?|of)\b', tail, re.I):
                continue
            window = ' '.join(x['t'] for x in sents[max(0, s['k'] - 2): s['k'] + 3])
            if re.search(evidence, window, re.I):
                continue
            off = _at(s['sp'], t[max(0, m.start() - 40):m.end() + 20])
            if any(a <= off < bb for a, bb in headings):
                continue
            if _number_near(src, off, 120):
                continue                   # a number sits right here: magnitude is given
            out.append(_F('significant-without-test-or-effect-size', off, 'lookup', False,
                          f'"{m.group(0)}" carries no test, p value, interval or effect '
                          f'size in this sentence or either neighbour, so a reader cannot '
                          f'tell whether a statistical claim is intended',
                          'Confirm whether the statistical sense is meant here, and if '
                          'so state the effect and its uncertainty in the units the '
                          'reader cares about'))
    return out


def _r_significance_threshold_language(src, spans, sents, prose, abstract, ctx):
    """Threshold-as-decision phrasing: "highly significant", "approached significance".

    A p value is a continuous quantity, so "approached significance" describes a number
    that failed a cut-off and "highly significant" reports a smaller p as a bigger effect.
    Separate rule from the effect-size one, because the repair differs: this one is about
    what the threshold can mean, not about a missing magnitude.
    """
    pat = (r'\bhighly significant\b|\bvery significant\b|\bstrongly significant\b|'
           r'\bapproach(?:ed|ing|es)? significance\b|\btrend(?:ed|ing|s)? toward'
           r'(?:s)? significance\b|\bmarginally significant\b|\bnearly significant\b|'
           r'\bborderline significant\b|\balmost significant\b|\bfailed to reach '
           r'significance\b')
    out = []
    for s in sents:
        for m in re.finditer(pat, s['t'], re.I):
            out.append(_F('significance-threshold-language', _at(s['sp'], s['t'][m.start():m.end() + 30]),
                          'lookup', False,
                          f'"{m.group(0)}" treats a significance threshold as a graded '
                          f'quantity or as a decision boundary the p value can approach',
                          'Report the p value and the effect with its interval, and say '
                          'plainly what the comparison supports'))
    return out


# --------------------------------------------------------------------- priority claims
def _r_priority_unanchored(src, spans, sents, prose, abstract, ctx):
    """A priority claim with nothing named that it exceeds.

    A genuine first should say so. The fault is the unanchored marker: the reviewer cannot
    check "the first study to" without the closest prior attempt and the respect in which
    it falls short. The bare ordinal ("the first step", "First, we") is vetoed, because
    that is not a priority claim at all.
    """
    out = []
    for s in sents:
        t = s['t']
        hits = [(m.start(), m.end(), m.group(0)) for m in re.finditer(PRIORITY, t, re.I)]
        for m in re.finditer(FIRST_PRIORITY, t, re.I):
            if not re.search(FIRST_ORDINAL, t[max(0, m.start() - 4):m.end() + 14], re.I):
                hits.append((m.start(), m.end(), m.group(0)))
        if not hits:
            continue
        window = ' '.join(x['t'] for x in sents[s['k']: s['k'] + 2])
        # A citation or cross-reference in this or the next sentence names the prior work.
        if '†' in window or '‡' in window:
            continue
        if re.search(COMPARED, window, re.I):
            continue
        a, b, word = sorted(hits)[0]
        out.append(_F('priority-claim-unanchored', _at(s['sp'], t[a:b + 30]), 'lookup', False,
                      f'the priority claim "{word.strip()}" names no prior work it '
                      f'exceeds, in this sentence or the next',
                      'Verify the claim against the closest prior attempt, and name that '
                      'attempt and the respect in which it falls short where the claim is '
                      'made'))
    return out


def _r_superlative_no_comparison(src, spans, sents, prose, abstract, ctx):
    """A promotional superlative about this work with no comparison set named.

    "Outperforms all prior methods on all twelve benchmarks" is a correct claim and is not
    reported, because it names its comparison set: the counter-case in the ledger is a
    paper that genuinely wins twelve of twelve and would be harmed by hedging. What is
    reported is the superlative with nothing behind it. A superlative describing the
    field rather than this work ("state-of-the-art models struggle with") is also skipped,
    which is why a self-reference is required.
    """
    out = []
    for s in sents:
        t = s['t']
        m = re.search(SUPERLATIVE, t, re.I)
        if not m:
            continue
        if not re.search(SELF, t, re.I):
            continue                       # describing others' systems, not a claim
        window = ' '.join(x['t'] for x in sents[max(0, s['k'] - 1): s['k'] + 2])
        if '†' in window or re.search(COMPARED, t, re.I):
            continue
        off = _at(s['sp'], t[m.start():m.end() + 30])
        out.append(_F('superlative-no-comparison-set', off, 'lookup', False,
                      f'"{m.group(0)}" claims a top position without naming the systems, '
                      f'benchmarks or metric it is measured against',
                      'Verify what the claim beats, and name the comparison set, the '
                      'metric and the regime where the claim is made'))
    return out


def _r_novelty_as_justification(src, spans, sents, prose, abstract, ctx):
    """An absence claim offered as the reason for doing the work, with no consequence.

    "No one has studied X" is a fact about the literature, not a reason. Reported only
    when neither this sentence nor the next says what becomes answerable once the gap is
    filled, since a gap that exists because a method was unavailable is a real argument.
    """
    out = []
    for s in sents:
        m = re.search(ABSENCE, s['t'], re.I)
        if not m:
            continue
        window = ' '.join(x['t'] for x in sents[max(0, s['k'] - 1): s['k'] + 2])
        if re.search(CONSEQUENCE, window, re.I):
            continue
        out.append(_F('novelty-as-its-own-justification',
                      _at(s['sp'], s['t'][m.start():m.end() + 30]), 'rework', False,
                      f'"{m.group(0).strip()}" states an absence in the literature and '
                      f'neither this sentence nor the next says what becomes answerable '
                      f'once it is filled',
                      'Verify what the result would settle, and say that here rather than '
                      'letting the absence stand as the reason'))
    return out


def _r_causal_on_correlational(src, spans, sents, prose, abstract, ctx):
    """A causal verb where the same or an adjacent sentence reports a correlation.

    Both halves have to be in the SAME sentence. A one-sentence window either side was
    tried first and reported "noise ... occasionally drives estimates into the negative
    regime" because the previous sentence happened to mention an OLS regression, which is
    the estimator rather than the evidence for that claim. A causal claim supported by an
    intervention is not reported, and neither is a causal verb inside a question the
    document is asking, since "this appendix examines whether overlap induces X" asserts
    nothing.
    """
    out = []
    for s in sents:
        t = s['t']
        m = re.search(CAUSAL, t, re.I)
        if not m:
            continue
        # An intervention or ablation earns the causal verb. Read the previous sentence
        # too: a design is described once and then claims are made against it.
        prev = sents[s['k'] - 1]['t'] if s['k'] else ''
        if re.search(r'\bablat\w*|\bintervention\b|\bwe (?:vary|varied|manipulat\w+|'
                     r'control(?:led)?|randomi[sz]\w+)\b|\brandomi[sz]ed\b|'
                     r'\bcontrolled (?:experiment|setting|comparison)\b|\bcausal '
                     r'(?:analysis|intervention)\b', t + ' ' + prev, re.I):
            continue
        # An investigative frame ahead of the verb makes it a question, not an assertion.
        if re.search(r'\b(?:whether|examines?|examined|examining|investigat\w+|tests?|'
                     r'tested|testing|asks?|asked|explores?|explored|question of|'
                     r'we ask|study whether|hypothesi[sz]\w+)\b',
                     t[max(0, m.start() - 90):m.start()], re.I):
            continue
        c = re.search(CORRELATIONAL, t, re.I)
        if not c:
            continue
        out.append(_F('causal-verb-on-correlational-evidence',
                      _at(s['sp'], t[m.start():m.end() + 30]), 'rework', True,
                      f'"{m.group(0)}" asserts a mechanism while the surrounding text '
                      f'reports "{c.group(0)}", which is an association',
                      'Check whether an intervention supports the causal reading here, '
                      'and if the evidence is associational say what was associated with '
                      'what'))
    return out


# ------------------------------------------------------------------ numbers as claims
def _r_timing_precision(src, spans, sents, prose, abstract, ctx):
    """A timing printed to more digits than any stated clock supports.

    Only timings, and only where the document never describes its timing method. Counts,
    seeds, byte and parameter sizes, hashes, identifiers and step indices are exact
    values, so they are outside the pattern by construction: this rule must never reach a
    number that rounding would destroy. Nothing is rounded here in any case.
    """
    if re.search(r'\bwall[- ]clock\b|\bperf_counter\b|\btime\.time\b|\bnanosecond\b|'
                 r'\bhigh-resolution\b|\btiming harness\b|\bclock resolution\b|'
                 r'\bCUDA events?\b|\btorch\.cuda\.synchronize\b', src, re.I):
        return []
    out = []
    for s in sents:
        t = s['t']
        for m in re.finditer(r'(?<![\w.])(\d+\.\d{2,})\s*(' + TIME_UNIT + r')\b', t):
            if re.search(r'[±]\s*$|\bplus or minus\s*$', t[:m.start()]):
                continue
            out.append(_F('timing-precision-beyond-stated-resolution',
                          _at(s['sp'], t[max(0, m.start() - 30):m.end()]), 'lookup', False,
                          f'"{m.group(1)} {m.group(2)}" prints '
                          f'{len(m.group(1).split(".")[1])} decimal places and the '
                          f'document never states the clock or apparatus that earns them',
                          'Name the timing method that supports these digits, or report '
                          'the number at the precision the measurement carries'))
    return out


def _r_number_measured_and_estimated(src, spans, sents, prose, abstract, ctx):
    """The same quantity written as an estimate in one place and bare in another.

    Decidable because it is a string comparison inside one document: the identical number
    and unit appears once behind an approximator and once without. The bare occurrence
    asserts a measurement the document elsewhere calls an estimate. Nothing is added or
    removed; the mismatch is reported and the author says which reading is right.
    """
    approx = r'(?:approximately|about|roughly|around|some|nearly|almost|up to|over|circa|~)'
    hedged, bare = {}, {}
    for s in sents:
        t = s['t']
        for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(' + TIME_UNIT +
                             r'|GB|MB|TB|KB|tokens?|words?|documents?|examples?|'
                             r'languages?|parameters?)\b', t):
            key = (m.group(1), m.group(2).lower().rstrip('s'))
            pre = t[max(0, m.start() - 22):m.start()]
            if re.search(approx + r'\s*$', pre, re.I):
                hedged.setdefault(key, (s, m))
            else:
                bare.setdefault(key, (s, m))
    out = []
    for key in sorted(set(hedged) & set(bare)):
        s, m = bare[key]
        out.append(_F('number-both-estimated-and-asserted',
                      _at(s['sp'], s['t'][max(0, m.start() - 30):m.end()]), 'lookup', False,
                      f'"{m.group(0)}" is stated bare here and as an estimate elsewhere '
                      f'in this document, so the two readings disagree on how it was '
                      f'obtained',
                      'Confirm whether this figure was measured or estimated, and mark '
                      'the two occurrences the same way'))
    return out


def _r_pct_change_no_base(src, spans, sents, prose, abstract, ctx):
    """A percentage change with no base value in this sentence or the one before.

    A 30% reduction is meaningless until the reader knows 30% of what. Levels ("accuracy
    of 82%") are outside the rule, and a change whose two absolute values are already
    given is not reported, since the base is recoverable. No number is supplied or
    inferred: the reader is told which sentence lacks the base.
    """
    out = []
    for s in sents:
        t = s['t']
        for a, b, val in _pct_iter(t):
            near = t[max(0, a - 60):b + 40]
            if not re.search(CHANGE, near, re.I):
                continue
            if re.search(r'\bpercentage points?\b|\bp\.?p\.?\b', t[b:b + 24], re.I):
                continue
            window = ' '.join(x['t'] for x in sents[max(0, s['k'] - 1): s['k'] + 1])
            if re.search(BASE_NAMED, window, re.I):
                continue
            if len(re.findall(r'(?<![\w.])\d+(?:\.\d+)?(?![\w])', window)) >= 3:
                continue                   # the two absolute values are on the page
            out.append(_F('percentage-change-without-base',
                          _at(s['sp'], t[max(0, a - 40):b + 10]), 'lookup', False,
                          f'"{val}%" reports a change and neither this sentence nor the '
                          f'one before names the value it is taken of',
                          'State which value is the base for this percentage, by '
                          'convention the starting value'))
    return out


def _r_orders_of_magnitude(src, spans, sents, prose, abstract, ctx):
    """"Orders of magnitude" standing in for a measured multiplier.

    Flagged in the abstract and in sentences reporting this document's own measurements,
    and deliberately not in related-work prose, where the looseness characterises a line
    of work rather than a result. No substitution is proposed, because the factor is not
    in the text and any figure chosen here would be invented.
    """
    out = []
    for s in sents:
        t = s['t']
        m = re.search(r'\b(?:an?\s+)?orders?\s+of\s+magnitude\b', t, re.I)
        if not m:
            continue
        off = _at(s['sp'], t[m.start():m.end() + 30])
        in_abs = _in_region(src, abstract, t)
        own = bool(re.search(RESULT_VERB, t, re.I)) or bool(re.search(SELF, t, re.I))
        if not (in_abs or own):
            continue                       # related-work characterisation: out of scope
        near = ' '.join(x['t'] for x in sents[max(0, s['k'] - 1): s['k'] + 2])
        if re.search(r'\b(?:\d+|ten|hundred|thousand|two|three|four|five)\b', near):
            continue                       # the multiplier is given here or next door
        out.append(_F('orders-of-magnitude-unquantified', off, 'lookup', False,
                      '"orders of magnitude" stands where a measured multiplier belongs, '
                      'in ' + ('the abstract' if in_abs else 'a sentence reporting this '
                                                             'work\'s own result'),
                      'Supply the measured factor in figures'))
    return out


# ------------------------------------------------------------------------ grant risk
def _r_risk_outcome_unconditional(src, spans, sents, prose, abstract, ctx):
    """A step labelled risky in its outcome whose outcome sentence is asserted flat.

    The risk label and the outcome verb then describe different uncertainties, and the
    reviewer scores the contradiction. Fires only where the risk is explicitly located in
    the outcome, so a step that is merely late is not touched. The repair adds
    conditioning, and only the author can say what is learned on the failing branch,
    which is why nothing is drafted here.
    """
    out = []
    for s in sents:
        t = s['t']
        if not re.search(RISK_LABEL, t, re.I):
            continue
        window = sents[max(0, s['k'] - 1): s['k'] + 3]
        wtext = ' '.join(x['t'] for x in window)
        if not re.search(RISK_OUTCOME, wtext, re.I):
            continue
        for x in window:
            v = re.search(UNCONDITIONAL, x['t'], re.I)
            if not v:
                continue
            if _risk_is_preempted(x['t'], wtext):
                continue  # a concessive already scopes the claim to hold under either branch
            out.append(_F('outcome-risk-with-unconditional-outcome',
                          _at(x['sp'], x['t'][max(0, v.start() - 40):v.end() + 20]),
                          'rework', True,
                          f'this step is labelled risky in its outcome yet its outcome '
                          f'sentence says "{v.group(0)}", which asserts the result the '
                          f'risk label says may not arrive',
                          'Verify what is learned on each branch, and make the outcome '
                          'sentence report the measurement rather than the result'))
            break
    return out


def _r_risk_kind_unstated(src, spans, sents, prose, abstract, ctx):
    """A risk label that says neither outcome nor schedule, beside a flat outcome verb.

    Reported as a pair with no rewrite proposed, because the two repairs are opposite:
    conditioning an outcome that is merely late corrupts a correct claim, and leaving a
    genuine outcome risk unconditioned leaves the contradiction standing. "High-risk,
    high-gain" alone is the funder's own call language and carries no risk claim, so it is
    named as such rather than reported here.
    """
    out = []
    for s in sents:
        t = s['t']
        m = re.search(RISK_LABEL, t, re.I)
        if not m:
            continue
        if re.search(r'high[- ]risk,?\s*(?:and\s*)?high[- ]gain', t, re.I):
            continue                       # call language, not a risk claim
        window = sents[max(0, s['k'] - 1): s['k'] + 3]
        wtext = ' '.join(x['t'] for x in window)
        if re.search(RISK_OUTCOME, wtext, re.I) or re.search(RISK_SCHEDULE, wtext, re.I):
            continue                       # the kind of risk is stated: other rules
        for x in window:
            v = re.search(UNCONDITIONAL, x['t'], re.I)
            if not v:
                continue
            if _risk_is_preempted(x['t'], wtext):
                continue  # a concessive already scopes the claim to hold under either branch
            out.append(_F('risk-kind-unstated-beside-flat-outcome',
                          _at(s['sp'], t[m.start():m.end() + 30]), 'lookup', False,
                          f'"{m.group(0)}" does not say whether the risk is in what the '
                          f'step shows or in when it happens, while a nearby outcome '
                          f'sentence says "{v.group(0)}"',
                          'Say which kind of risk this is, so the label and the outcome '
                          'sentence describe the same uncertainty'))
            break
    return out


# ----------------------------------------------------------------------- absolutes
def _r_ungradable_comparative(src, spans, sents, prose, abstract, ctx):
    """A comparative formed on an absolute that has no gradations.

    "More complete", "most optimal", "an improved level of optimality". An approximator on
    a quantifier is a different thing entirely and is absent from the pattern: "almost
    all", "nearly none", "fairly complete" and "virtually always" are hedged true claims.
    The fix names the bounded comparative to verify and never suggests dropping the
    comparative, because that would leave a bare absolute asserting more than the original.
    """
    out = []
    for s in sents:
        for m in re.finditer(UNGRADABLE, s['t'], re.I):
            out.append(_F('ungradable-comparative',
                          _at(s['sp'], s['t'][m.start():m.end() + 24]), 'lookup', False,
                          f'"{m.group(0)}" grades a term that has no gradations, so the '
                          f'phrase asserts a comparison the word cannot carry',
                          'Verify which bounded comparison the evidence supports, naming '
                          'the comparison set, the metric and the condition'))
    return out


def _r_unscoped_absolute(src, spans, sents, prose, abstract, ctx):
    """An ungraded absolute inside a sentence reporting this document's own result.

    Narrowed from the ledger test on purpose. The full test reaches every "all" and
    "never" in the document, including setup prose where the absolute is a fact about the
    design, and that produces far too many findings to be read. Restricted here to
    sentences that report a result, where the absolute is a claim about what was found.
    An approximated quantifier is exempt and is never altered: "almost all languages in
    the sample" is already a scoped claim and correct as written.
    """
    out = []
    for s in sents:
        t = s['t']
        if not re.search(CLAIM_VERB, t, re.I):
            continue
        for m in re.finditer(ABSOLUTE, t, re.I):
            pre = t[max(0, m.start() - 24):m.start()]
            if re.search(APPROX, pre, re.I):
                continue                   # 'almost all', 'not every': already scoped
            w = m.group(0).lower()
            after = t[m.end():m.end() + 90]
            if w == 'no' and not re.match(r'\s+\w+\s+(?:is|are|was|were|shows?|'
                                          r'improves?|transfers?|generali[sz]es?)\b',
                                          after):
                continue                   # 'no' as a plain negation, not a claim of none
            if re.search(SCOPE, after, re.I) or re.search(SCOPE, pre, re.I):
                continue
            # The scope is often stated once and then claims are made against it, so a
            # neighbouring sentence that names it has already done the scoping.
            if s['k'] and re.search(SCOPE, sents[s['k'] - 1]['t'], re.I):
                continue
            if re.search(r'^\s*(?:of|in|across|among|for)\s+(?:the\s+)?\d', after):
                continue
            out.append(_F('unscoped-absolute-in-result',
                          _at(s['sp'], t[max(0, m.start() - 30):m.end() + 30]),
                          'lookup', False,
                          f'"{w}" is an ungraded absolute in a sentence reporting a '
                          f'result, and the sentence does not say over what comparison '
                          f'set, metric or condition it holds',
                          'Confirm the scope over which this holds, and state that scope '
                          'here'))
            break                          # one finding per sentence
    return out


# -------------------------------------------------------------------------- hedging
def _r_stacked_hedges(src, spans, sents, prose, abstract, ctx):
    """Three or more hedges modifying one claim, so the level of commitment is unreadable.

    The window is tight, twelve words, because hedges spread across a sentence usually
    modify different claims, and a sentence saying one effect is established while a
    second may follow is not stacked. Every hedge found is listed and none is removed:
    each one that goes strengthens the claim, and only the author knows whether the
    evidence carries the stronger version.
    """
    out = []
    for s in sents:
        t = s['t']
        hits = [(m.start(), m.group(0)) for m in re.finditer(HEDGE, t, re.I)]
        if len(hits) < 3:
            continue
        words = [(m.start(), m.group(0)) for m in re.finditer(r'\S+', t)]
        for i in range(len(hits) - 2):
            a, c = hits[i][0], hits[i + 2][0]
            between = len([1 for p, _ in words if a < p < c])
            if between > 12:
                continue
            group = [h[1] for h in hits[i:i + 3]]
            out.append(_F('stacked-hedges-on-one-claim',
                          _at(s['sp'], t[a:c + 30]), 'rework', False,
                          'three hedges modify one claim here (' +
                          ', '.join(f'"{g}"' for g in group) +
                          '), so the level of commitment cannot be recovered',
                          'Decide which single level of commitment the evidence supports'))
            break                          # one report per sentence
    return out


def _r_unhedged_result_no_support(src, spans, sents, prose, abstract, ctx):
    """A result sentence with no hedge and no number, citation or reference beside it.

    A statement of procedure carries no hedge by design and is not a target, which is why
    a result verb is required. The abstract is excluded: an abstract reports results with
    no citation and no float reference by convention, and reporting that is a complaint
    about the genre. No hedge is added: adding one would assert a limit on the evidence
    that the document does not establish. The report exists so the author can point at the
    support that is elsewhere.
    """
    out = []
    for s in sents:
        t = s['t']
        m = re.search(CLAIM_VERB, t, re.I)
        if not m:
            continue
        if re.search(HEDGE, t, re.I):
            continue
        if '†' in t or '‡' in t:
            continue
        window = ' '.join(x['t'] for x in sents[max(0, s['k'] - 1): s['k'] + 2])
        if '†' in window or '‡' in window:
            continue
        off = _at(s['sp'], t)
        if _in_region(src, abstract, t):
            continue
        if _support(src, off, 300):
            continue
        out.append(_F('unhedged-result-without-support', off, 'lookup', False,
                      f'"{m.group(0)}" reports a result flat, with no number, citation or '
                      f'cross-reference in this sentence or either neighbour: '
                      f'"{t[:90]}"',
                      'Point the sentence at the evidence for it, or say where in the '
                      'document that evidence sits'))
    return out


def _r_certainty_marker(src, spans, sents, prose, abstract, ctx):
    """"Obviously", "clearly", "of course" and the rest, listed with what they introduce.

    No deletion is proposed and no judgement is made about whether the statement is
    supported. The same word does one of two opposite jobs: it tells a specialist a step
    is standard and can be skipped, or it marks the spot where an argument was declined.
    Halmos allows the first, and telling them apart needs the author's knowledge of the
    step, so the output is a list.
    """
    out = []
    for s in sents:
        t = s['t']
        for m in re.finditer(CERTAINTY, t, re.I):
            stmt = t[m.end():m.end() + 90].strip(' ,;:')
            out.append(_F('certainty-marker', _at(s['sp'], t[m.start():m.end() + 40]),
                          'free', False,
                          f'"{m.group(0)}" introduces "{stmt[:70]}"',
                          ''))
    return out


# ------------------------------------------------------- abstract against the body
def _r_abstract_claim_absent_from_body(src, spans, sents, prose, abstract, ctx):
    """An abstract phrase that occurs nowhere else in the document.

    Decidable because it is string absence inside one document, not a judgement about
    meaning. A content bigram the abstract asserts and the body never mentions again is
    either a claim the results do not reach or a term the body renamed, and both are worth
    the author's attention. Bigrams that appear anywhere outside the abstract are silent.
    """
    if not abstract:
        return []
    abs_sents = [s for s in sents if _in_region(src, abstract, s['t'])]
    if not abs_sents:
        return []
    body_words = _content_words(' '.join(
        s['t'] for s in sents if s not in abs_sents))
    body_bi = {(body_words[i], body_words[i + 1]) for i in range(len(body_words) - 1)}
    body_set = set(body_words)
    out, seen = [], set()
    for s in abs_sents:
        ws = _content_words(s['t'])
        # A proper noun the abstract names once is usually an illustration rather than a
        # promised result: "what is recorded only in Finnish or Portuguese becomes
        # reachable" is an example, and reporting it as a claim the body never delivers is
        # an accusation about a figure of speech. Capitalised mid-sentence tokens are
        # therefore excluded.
        proper = {w.lower() for w in re.findall(r'(?<=[a-z,;)] )([A-Z][a-z]{2,})', s['t'])}
        for i in range(len(ws) - 1):
            bi = (ws[i], ws[i + 1])
            if bi in body_bi or bi in seen:
                continue
            # Both halves absent from the body: a term the body never takes up at all.
            if ws[i] in body_set or ws[i + 1] in body_set:
                continue
            if ws[i] in proper or ws[i + 1] in proper:
                continue
            if len(ws[i]) < 5 or len(ws[i + 1]) < 5:
                continue
            seen.add(bi)
            out.append(_F('abstract-phrase-absent-from-body',
                          _at(s['sp'], ' '.join(bi)), 'rework', False,
                          f'the abstract says "{ws[i]} {ws[i + 1]}" and neither word '
                          f'appears anywhere else in this document',
                          'Check that the body reports the result this phrase promises, '
                          'or use the body\'s own term for it'))
    return out


# --------------------------------------------------- second pass: abstract numbers
def _r_abstract_number_absent_from_body(src, spans, sents, prose, abstract, ctx):
    """A figure the abstract asserts that appears nowhere else in the file.

    Decidable because it is string absence inside one document. The search reads `src`, not
    rendered prose, so a number living only in a table, in math or in a caption counts as
    present: those are where the body figure usually sits. Comments are blanked first,
    because a table commented out during drafting is not something a reader can check.

    The abstract is read from its own source range rather than through the sentence list.
    A preamble with no comment and no math is a single text span, so the abstract's first
    sentence can arrive carrying the document class and the title, and sentence-to-region
    matching then answers no for the whole abstract.

    Outside the pattern by construction: years, which label a work; values under ten with no
    unit, which count objectives and steps; digits glued to a name (L4M, GPT-4); and
    anything inside a citation key, a label or a cross-reference.
    """
    if not abstract:
        return []
    if _inputs_a_body_file(src):
        return []                          # the prose is in other files: nothing to search
    body = src
    for a, b in abstract:
        body = body[:a] + ' ' * (b - a) + body[b:]
    body = re.sub(r'(?<=\d),(?=\d)', '', _comment_stripped(body))
    unit = (r'(?:\\?%|per ?cent|percent|[KMBT]\b|×|GB|MB|TB|KB|' + TIME_UNIT + r')')
    out, seen = [], set()
    for a, b in abstract:
        window = _comment_stripped(src)[a:b]
        # A bib key, a label and a cross-reference all carry digits a reader never sees.
        window = re.sub(r'\\(?:cite|ref|autoref|cref|Cref|eqref|label|input|include)'
                        r'[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{[^}]*\}',
                        lambda m: ' ' * len(m.group(0)), window)
        for m in re.finditer(r'(?<![\w.,\\])(\d+(?:,\d{3})*(?:\.\d+)?)\s*(' + unit + r')?',
                             window):
            raw, u = m.group(1), (m.group(2) or '').replace('\\', '')
            val = raw.replace(',', '')
            if re.match(r'^(?:19|20)\d\d$', val):
                continue                   # a year names a work, not a measurement
            if '.' not in val and not u and float(val) < 10:
                continue                   # a bare small integer is a count or an ordinal
            if val in seen:
                continue
            if re.search(r'(?<![\d.])' + re.escape(val) + r'(?![\d])', body):
                continue
            seen.add(val)
            out.append(_F('abstract-number-absent-from-body', a + m.start(), 'lookup', True,
                          f'the abstract states "{raw}{u}" and that figure appears nowhere '
                          f'else in this file, in prose, table, caption or math',
                          'Point the sentence at the table or section that reports this '
                          'number, or quote the body\'s own figure in the abstract'))
    return out


# ------------------------------------------------------------ second pass: comparatives
def _r_comparative_no_comparator(src, spans, sents, prose, abstract, ctx):
    """"better", "outperforms" or "faster" with nothing named to compare against.

    Only the three comparatives the trial named. The ledger's direction-word test (improve,
    reduce, enhance with no magnitude) is a different and much wider rule that was measured
    at 33 hits on one paper and dropped; this one asks a narrower question, not for a
    magnitude but for the other side of the comparison, and it is discharged by a comparator
    anywhere in the sentence or either neighbour. A hedged comparative is not reported: it
    proposes a direction rather than asserting a ranking, and a hedge is never the defect.
    """
    heads = _heading_ranges(src)
    titles = _emph_ranges(src)
    out = []
    for s_ in sents:
        t = s_['t']
        for m in re.finditer(COMPARATIVE, t, re.I):
            word = m.group(0).lower()
            if re.search(COMPARATIVE_ADVERBIAL, t[max(0, m.start() - 12):m.end() + 26], re.I):
                continue                   # adverbial: ranks nothing
            if word.startswith('outperform') and re.match(_OUTPERFORM_OBJECT,
                                                          t[m.end():m.end() + 34]):
                continue                   # the verb's object IS the comparator
            window = ' '.join(x['t'] for x in sents[max(0, s_['k'] - 1): s_['k'] + 2])
            if re.search(COMPARATOR, window, re.I):
                continue                   # this sentence or a neighbour names it
            if re.search(HEDGE, t, re.I):
                continue
            if not (re.search(SELF, t, re.I) or re.search(CLAIM_VERB, t, re.I)):
                continue                   # a remark about the field, not a claim
            off = _at(s_['sp'], t[m.start():m.end() + 40])
            if any(a <= off < b for a, b in heads) or any(a <= off < b for a, b in titles):
                continue                   # a heading, a caption, or a cited work's title
            out.append(_F('comparative-without-named-comparator', off, 'lookup', False,
                          f'"{m.group(0)}" compares this work against nothing named, in '
                          f'this sentence or either neighbour',
                          'Name what the comparison is against, and the metric and '
                          'condition under which it holds'))
    return out


# ----------------------------------------------------- second pass: observational design
def _r_causal_on_observational_design(src, spans, sents, prose, abstract, ctx):
    """A causal verb in a result claim whose own design is described as observational.

    Companion to the correlational rule, not a widening of it: that one keys on the
    statistics reported (a correlation, an R^2, a regression) and this one on the design
    described (an observational or corpus study, naturally occurring data, no intervention).
    A sentence carrying correlational vocabulary is left to the other rule, so one site
    never produces two findings.

    The design statement may sit in the previous sentence, and an intervention named in the
    previous sentence vetoes: the design is described once and then claims are made against
    it, so reading either half in isolation gets the wrong answer.
    """
    # Document level: the design is stated once, in a setup section, and the claims come
    # chapters later, so a sentence window alone would find the two halves in one place
    # almost never. The gate is that the document describes an observational design and
    # describes no intervention anywhere, which is what makes it an observational study
    # rather than a controlled one that also looks at released models. Occurrences of the
    # observational phrases are removed before the intervention test, so "with no
    # intervention" does not read as an intervention.
    doc_design = re.search(OBSERVATIONAL, prose, re.I)
    stripped = re.sub(OBSERVATIONAL, ' ', prose, flags=re.I)
    doc_observational = bool(doc_design) and not re.search(INTERVENTION, stripped, re.I)
    out = []
    for s_ in sents:
        t = s_['t']
        m = re.search(CAUSAL_MECHANISM, t, re.I)
        if not m:
            continue
        prev = sents[s_['k'] - 1]['t'] if s_['k'] else ''
        nxt = sents[s_['k'] + 1]['t'] if s_['k'] + 1 < len(sents) else ''
        d = (re.search(OBSERVATIONAL, t, re.I) or re.search(OBSERVATIONAL, prev, re.I) or
             (doc_design if doc_observational else None))
        if not d:
            continue
        if re.search(CORRELATIONAL, t, re.I):
            continue                       # the correlational rule owns this site
        if re.search(INTERVENTION, t + ' ' + prev + ' ' + nxt, re.I):
            continue                       # an intervention earns the causal verb
        if re.search(INVESTIGATIVE, t[max(0, m.start() - 90):m.start()], re.I):
            continue                       # a question, not an assertion
        if re.search(HEDGE, t, re.I):
            continue
        if not (re.search(CLAIM_VERB, t, re.I) or re.search(RESULT_VERB, t, re.I)):
            continue                       # not this document reporting its own finding
        out.append(_F('causal-verb-on-observational-design',
                      _at(s_['sp'], t[m.start():m.end() + 30]), 'rework', True,
                      f'"{m.group(0)}" asserts a mechanism while the design here is '
                      f'described as "{d.group(0)}", which observes rather than intervenes',
                      'Check whether an intervention supports the causal reading, and if '
                      'the design only observes, say what was observed to go with what'))
    return out


# ------------------------------------------------- second pass: generalisation vs tested
def _r_generalisation_beyond_tested(src, spans, sents, prose, abstract, ctx):
    """A result claimed over all of a population whose tested count is named nearby.

    Both halves are required and they have to be in different sentences. A count in the
    claim's own sentence ("all eight languages we evaluate") is the scope, and the claim is
    correct as written. A count in a neighbouring sentence under a first-person testing verb
    is the tested set, and the claim then reaches past it.

    Restricted to "all" and "every": "each" and "any" distribute over the design ("for each
    model and game, we evaluate every language pair") and are not generalisations, and
    including them produced fifteen candidates on the corpus, every one a design sentence.
    A hedge or an approximator makes the quantifier a scoped claim, which is correct writing
    and is never reported or altered.
    """
    out = []
    for s_ in sents:
        t = s_['t']
        if not re.search(CLAIM_VERB, t, re.I):
            continue
        if re.search(HEDGE, t, re.I) or re.search(SCOPE, t, re.I):
            continue
        if re.search(POP_COUNT, t, re.I):
            continue                       # the tested set is right here: scoped
        for u in re.finditer(UNIVERSAL_POP, t, re.I):
            if re.search(APPROX, t[max(0, u.start() - 24):u.start()], re.I):
                continue                   # 'almost all models': already scoped
            head = _stem(u.group(1))
            hit = None
            for x in sents[max(0, s_['k'] - 3): s_['k'] + 4]:
                if x is s_ or not re.search(TESTING_VERB, x['t'], re.I):
                    continue
                for c in re.finditer(POP_COUNT, x['t'], re.I):
                    if _stem(c.group(1)) == head:
                        hit = c.group(0)
                        break
                if hit:
                    break
            if not hit:
                continue
            out.append(_F('generalisation-beyond-tested-population',
                          _at(s_['sp'], t[u.start():u.end() + 30]), 'rework', True,
                          f'the claim holds over "{u.group(0)}" while the tested set named '
                          f'in a neighbouring sentence is "{hit}"',
                          'Confirm what the result covers, and state the tested set in the '
                          'claim sentence when the claim is about that set'))
            break                          # one finding per sentence
    return out


# ------------------------------------------------------------------------- runner
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    stage = 'draft' if '--draft' in sys.argv else 'submission'
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
                print(f"{os.path.basename(p)}:{line}  [{f['cost']}"
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
