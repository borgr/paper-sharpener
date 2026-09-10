#!/usr/bin/env python3
"""Sentence-mechanics checks.

The corpus said this family gets ~1.4% of expert attention against 10% of the asserted
rules, an eightfold over-weighting, and across 400 sampled real changes it produced exactly
one discovered rule. So the default here is NOT to implement, and the declines below are the
substantive output. Three rules were added to the discovered one, each because it has a
unique mechanical trigger and a single correct repair.

DISCOVERED RULE — missing complement on a relational head.
Five editors across five separate projects each inserted a short prepositional phrase
supplying the argument of a relational noun or verb that had none: "subset of evaluations",
"Throughput of serving compressed LoRAs", "generalizes to variants of the training problem".
The defect survives self-revision because the author's memory supplies the missing slot, so
only a reader who does not already know the answer notices. No writing guide states it.

MEASURED AND CUT BACK. A first version generalised the discovered rule to 40 relational
heads and produced 63 findings on three documents, far past the precision bar. Nearly all
were idioms ("for example"), established compounds ("knowledge transfer") or table headers.
The list is now restricted to heads the corpus actually evidenced, with idiom and compound
vetoes, because a rule seen five times does not license a class of forty.

IMPLEMENTED, and why each earned it
-----------------------------------
[4 partial] doubled-word. A word typed twice in a row is almost always a slip, and there
    the repair is unique: delete the second one. Reviewers list this class explicitly. Vetoed
    against the correct English doubles ("had had", "that that"), against repeated proper
    names, and against the one construction where a doubled word is the grammar rather than
    a slip: the pseudo-cleft copula. "What it is is a calibration problem" is correct, and
    applying the fix to it yields "What it is a calibration problem", so a cleft head within
    40 characters before an is/was/are/were pair vetoes the finding. Critically it requires the pair to appear LITERALLY IN THE SOURCE SLICE, because
    the extractor's macro unwrapping manufactures phantom doubles: `\\end{minipage}
    \\begin{minipage}` renders as "minipage minipage" and was the only hit the first version
    found on two of the three test documents.
[20] value-closed-up-to-unit. "11.2Kbytes", "50ms" run a value into its unit. Mechanical,
    single repair (insert the space), no digit is touched, and the unit list is closed so
    the conventionally closed-up forms are out of reach by construction: 95%, 37degC, $5,
    a 7B model, a 4x speedup, GPT-4o, A100 all fail the match rather than needing a veto.
[31] colon-before-display-completing-grammar. Narrowed from the ledger's "lead-in is not a
    complete sentence", which needs a parser, to the subset where the word before the colon
    is a preposition or a copula, so the display certainly supplies the complement. The
    repair is unique (delete the colon, touch nothing else) and the ledger's counter-cases
    fall outside the trigger: "as follows:", "the following:" and "has two terms:" all end
    on a word that is not in the list. The narrowing costs the ledger's own before-example,
    "define the set of nonincreasing vectors:", which is missed because knowing that
    "define" is still waiting for its object needs a parser. A deliberate false negative:
    "vectors" is a noun, and a noun before the colon is also how the legitimate case looks.

All three fire zero times on the three test documents, which are clean of them rather than
immune to them. Each is verified against the ledger's before-example and against every
counter-case the ledger names: 95%, 37degC, a 7B model, a 4x speedup, an A100, GPT-4o,
"11.2 Kbytes" already spaced, "50ms" inside math, a 10-ms hyphenated compound, "had had",
a repeated proper name, "as follows:", "has two terms:" and a complete lead-in.

DECLINED — 29 of 32, with the reason for each
---------------------------------------------
A threshold nobody stated. Each of these names a number its source does not support, and a
word-count line is the arbitrary boundary Gopen & Swan warn against. Same ground on which
`subject-verb-separation` was cut from this module.
  [2]  sentence over 20 words — a maximum sentence length.
  [3]  aim longer than three sentences — and the outcome-verb half is grant structure, not
       sentence mechanics; which verb an aim takes is the author's claim to make.
  [5]  paragraph over about 150 words — and see "needs the rendered document" below.
  [13] more than about seven words between subject head and main verb — a maximum
       words-before-verb, and a duplicate (see below).
  [14] more than about ten words of introductory phrase, subjects over about eight words.
  [15] a chain of more than one trailing subordinate clause — a maximum clause count, and
       see "needs a parser".
  [1]  Flesch Reading Ease near or below zero — the paper reports a 134-year trend, and its
       own counter-case says a score is a trigger to look rather than a target, with no link
       measured to any outcome. There is no stated defect line to test against.

Needs a parser, so it cannot be decided with certainty from the source.
  [9]  dangling participle, subject-verb disagreement, wrong preposition — all three need
       syntax, and the middle one needs to know which noun is the head.
  [15] subordinate-clause chains — "that" and "which" are not clause boundaries on their own.
  [16] a run of three or more nouns as one modifier — needs a POS tagger to tell noun from
       adjective, and its own counter-case (support vector machine, byte pair encoding) is
       the majority case in a technical paper, so the volume would blow the precision bar.
  [29] list parallelism — needs the construction of each sibling item, and where the items
       genuinely are not parallel the counter-case says forcing the wording hides the real
       problem, which makes the output taste.
  [17] the "blah" test on formulas — requires reading the result aloud and judging whether a
       claim survives. Its one mechanical corner is implemented as [31].
  [18] small numbers as adjectives versus as values — the adjective/value distinction is
       syntactic, and venue style overrides the rule with no key in ctx['style'].

Taste, or a house style with no key in ctx['style'] to read.
  [7]  idioms and metaphors — its own counter-case is that pipeline, bottleneck and pruning
       are the field's correct technical names, so a word list cannot separate a cultural
       idiom from a term of art. Register-redundancy's ground in any case.
  [23] a range with one end spelt and the other in figures — reads correctly either way, and
       which direction is right is set by the venue, with no key defined.
  [24] a slashed fraction in prose ("1/3 of the data") — reads correctly; spelling it out is
       a copy-editing preference, and many venues prefer the figures.
  [25] an unhyphenated spelt-out unit compound ("a 10 millisecond delay") — reads correctly;
       and keeping it safe needed a determiner-plus-unit whitelist, which means the trigger
       was mine rather than the rule's.
  [28] italics as notation versus emphasis — whether a given italic span is a gene symbol, a
       variable, a loanword or emphasis is settled by the field's convention, which is not
       in the document. The output is a count, not a defect.
  [8]  "wrong under grammar or fixed idiom, so fix it silently" — a rule about how to route
       an edit, not a test a document can fail. It has no trigger to implement.

Needs the rendered document, or a resource outside the source.
  [4 rest] a spelling and grammar pass over the final PDF — needs an external dictionary,
       and its own counter-case says a blanket pass corrupts gene symbols, dataset names and
       code tokens. Only the doubled-word half is source-decidable, and that half is in.
  [5 rest] the longest unbroken block on each page, a page with no break in its upper half —
       page geometry does not exist until the document is typeset.
  [6]  funder caps counted in sentences or characters — the cap lives in the call text, and
       nothing in ctx carries it.
  [10 rest] the reviewer's proofreading complaint — a spellchecker again.
  [12] broken cross-references — the "??" half needs the compiled PDF.
  [26] passive clause whose agent IS in the work-package table — needs the table, needs
       passive detection, and the proposed repair promotes a table row into a staffing
       commitment that only the applicant can make.
  [27] passive clause whose agent is in NO work-package table — proving that no row anywhere
       owns the work is not decidable from one .tex source, and a wrong finding here accuses
       the applicant of an unfunded promise.
  [21] a count in figures against a figure-led compound ("14 512-Kb sets") — keeping it off
       "Table 2 3-shot", "top 5 32-bit" and version strings took a veto list that kept
       growing, which is the sign that the trigger is not unique.

Duplicates a rule that already exists in another module.
  [19] decimal below one without its leading zero — evidence-surface already has
       `p-leading-zero-style` and `p-leading-zero-mixed`, and they read the style key.
  [13] words between subject and verb — cohesion already has `subject-verb-separation`, under
       Gopen & Swan's own caveat that none of their principles is a rule.
  [12] cross-reference faults — integrity has `hardcoded-cross-reference`,
       `reference-to-commented-out-label`, `reference-type-mismatch` and `duplicate-label`;
       naming-notation has `reference-to-unnumbered-equation`.
  [30] an orphan enumerator, an (a) with no (b) — cohesion has `enumeration-count-mismatch`
       and integrity has `stated-count-vs-list`. Implemented and measured anyway: 0 findings
       on all three documents, so it adds nothing the two existing rules do not cover.
  [32] terminal punctuation on displays — a document-wide house style with no key, the rule
       itself forbids inserting the character, and evidence-surface already owns display and
       float conventions.
  [11] parenthetical versus textual citation — needs the venue's .bst to know whether the
       style is numeric, and under a numeric style the reviewer's own fix double-brackets
       the citation. Naming-notation owns citation-command correctness.

DROPPED ON MEASUREMENT — implemented, run, and removed
------------------------------------------------------
[22] sentence-opens-on-numeral. The brief named this a good candidate and the data refused
     it: 16 findings, 14 of them on b1.tex, past the ~10 bar on one document. The hits were
     CV date ranges ("2017 -- 2023PhD, ..."), numbered aim labels ("1. Identifying the
     causes ..."), footnote markers ("7.8This why-me half ...") and, on the paper, a run-in
     \\paragraph heading followed by a settings fragment ("SmolLM2-360M. 4,600 steps, batch
     size 768"). None is a sentence that a reader sees opening on a figure. The rule needs
     to know where sentences actually begin, and the rendered stream is not a reliable
     sentence stream: a heading, a table stub and a list label all look like one.
[10 narrow] citation-breakable-space, a plain space where the venue requires ~ before
     \\cite. Mechanical and style-gated, so it was silent by default, but forcing the key on
     gave 59 findings on the paper, 38 on b1 and 21 on b2. At that volume it is a
     document-wide reformat rather than a defect list, which is exactly what trains a reader
     to ignore findings. If a venue wants it, it belongs in a one-pass fixer, not here.
     Removed rather than capped, because a capped count hides the real size of the change.

Not implemented and never to be: nothing here may delete or weaken a hedge, an intensifier
on a graded absolute, a tentative modal or a first-person stance marker. `_gate` enforces it
as a postfilter, and also refuses tier 'silent' from any rule but a uniquely repairable one.
"""
import re

FAMILY = 'sentence-mechanics'

# Heads that are relational: they denote a relation and are incomplete without its other
# term. Each maps to the prepositions that can license its complement.
RELATIONAL = {
    # Only heads the corpus actually showed an editor completing.
    'subset': ('of',), 'throughput': ('of', 'for', 'on'),
}
RELATIONAL_VERBS = {
    'generalizes': ('to', 'across', 'beyond'), 'generalize': ('to', 'across', 'beyond'),
    'generalises': ('to', 'across', 'beyond'), 'generalise': ('to', 'across', 'beyond'),
}
# A determiner or possessive before the head means the relation is already anchored by
# earlier text ("its accuracy", "the ratio we reported"), so absence proves nothing.
ANCHORED = re.compile(r'\b(its|their|our|your|his|her|this|that|these|those|such|same)\s*$', re.I)
# "for example", "for instance" and the like are idioms, not relational heads.
IDIOM = re.compile(r'\b(for|an|another|one|some|as|by|e\.g\.?|i\.e\.?)\s*$', re.I)
# A preceding noun or adjective makes it a compound ("knowledge transfer"), already anchored.
COMPOUND = re.compile(r'\b[a-z]{4,}(?:-[a-z]+)?\s*$')
TERMINAL = re.compile(r'^\s*[.;:,)\]}]|^\s*$')


def _F(rule, off, tier, cost, blocks, text, fix):
    return {'rule': rule, 'family': FAMILY, 'offset': int(off), 'tier': tier, 'cost': cost,
            'blocks': blocks, 'text': text, 'fix': fix}


def _loc(sp, needle):
    """Source offset for a finding first seen in rendered text (CHECKS_API.md rule 7)."""
    i = sp.text.find(needle)
    return sp.start + (i if i >= 0 else 0)


def _findings_for(text, base_off, out):
    for m in re.finditer(r'\b([A-Za-z]+)\b', text):
        w = m.group(1)
        low = w.lower()
        preps = RELATIONAL.get(low) or RELATIONAL_VERBS.get(low)
        if not preps:
            continue
        before = text[max(0, m.start() - 30):m.start()]
        if ANCHORED.search(before) or IDIOM.search(before):
            continue
        if low in RELATIONAL and COMPOUND.search(before):
            continue  # an established compound is anchored by its modifier
        after = text[m.end():m.end() + 60]
        # A complement must start within the next couple of words.
        nxt = after.split()[:3]
        if any(t.strip('.,;:()[]').lower() in preps for t in nxt):
            continue
        # A hyphenated or compound use is a modifier, not a relational head.
        if after[:1] == '-' or before[-1:] == '-':
            continue
        # Sentence-final or clause-final with no complement is the defect.
        if TERMINAL.match(after) or (nxt and nxt[0].lower() in
                                     ('is', 'are', 'was', 'were', 'and', 'but', 'which', 'that')):
            out.append(_F('relational-head-without-complement', base_off + m.start(), 'query',
                          'free', False,
                          f'"{w}" denotes a relation but its other term is missing '
                          f'("{(w + after[:34]).strip()}")',
                          f'name what it is a relation to, with {" or ".join(preps)}, '
                          'or confirm the reader can supply it from the previous sentence'))


# ------------------------------------------------------- [4] a word typed twice in a row
_DOUBLE = re.compile(r'\b([A-Za-z]{2,})([ \t]+|\n(?!\s*\n))\1\b')
# Correct doubled English, and words a repetition of which is deliberate.
_DOUBLE_OK = {'had', 'that', 'very', 'blah', 'long', 'ha', 'no'}
# The pseudo-cleft doubles the copula and is correct: "What it is is a calibration
# problem" loses its main verb if the second "is" goes. Guarded by the cleft head rather
# than by blanket-exempting the copulas, so a plain "the results were were reported" typo
# is still caught.
_CLEFT_HEAD = re.compile(r'\b(?:what|whatever|all|the (?:point|problem|question|issue|'
                         r'reason|thing|difficulty|answer|upshot))\b[^.!?;:]{0,40}$', re.I)
_CLEFT_COPULA = {'is', 'was', 'are', 'were'}


def _c_doubled_word(spans, out):
    for sp in spans:
        for m in _DOUBLE.finditer(sp.rendered):
            w = m.group(1)
            if w.lower() in _DOUBLE_OK:
                continue
            if w.lower() in _CLEFT_COPULA and _CLEFT_HEAD.search(sp.rendered[:m.start()]):
                continue  # pseudo-cleft: deleting the second copula breaks the sentence
            if w[0].isupper():
                continue  # a repeated proper name, not a slip
            # The extractor unwraps macros, which manufactures adjacencies that are not in
            # the source: \end{minipage}\begin{minipage} renders as "minipage minipage".
            # Only a pair that survives in the source slice is a real doubled word.
            src_hit = re.search(r'\b' + re.escape(w) + r'([ \t]+|\n)' + re.escape(w) + r'\b',
                                sp.text)
            if not src_hit:
                continue
            out.append(_F('doubled-word', sp.start + src_hit.start(), 'batch', 'free', True,
                          f'"{w}" is typed twice in a row ("{src_hit.group(0)}")',
                          f'delete the second "{w}"'))


# ------------------------------------------ [20] a value run into its unit with no space
# Closed list. Every conventionally closed-up form (95%, 37degC, $5, 7B, 4x, A100, GPT-4o)
# fails to match rather than needing a veto.
_UNIT = (r'(?:ms|ns|µs|us|kB|KB|MB|GB|TB|PB|KiB|MiB|GiB|TiB|Hz|kHz|MHz|GHz|THz'
         r'|Kbytes|Mbytes|Gbytes|kbit|Mbit|Gbit|GFLOPs?|TFLOPs?|PFLOPs?|kWh|mAh)')
_CLOSED = re.compile(r'(?<![\w.\-])(\d+(?:\.\d+)?)(' + _UNIT + r')(?![\w\-])')


def _c_value_closed_up_to_unit(spans, out):
    for sp in spans:
        for m in _CLOSED.finditer(sp.rendered):
            out.append(_F('value-closed-up-to-unit', _loc(sp, m.group(0)), 'batch', 'free',
                          False,
                          f'"{m.group(0)}" runs the value into its unit',
                          f'write "{m.group(1)}~{m.group(2)}", changing no digits'))


# ------------------------- [31] a colon before a display that completes the sentence
_DISPLAY = re.compile(r'^\s*(?:\\\[|\\begin\{(?:equation|align|gather|multline|eqnarray)\*?\})')
# A colon after one of these leaves the sentence grammatically unfinished, so the display is
# supplying the complement rather than being introduced. "as follows:", "the following:" and
# "has two terms:" end on words that are deliberately absent from this list.
_COMPLETING = {
    'by', 'as', 'of', 'to', 'in', 'for', 'with', 'from', 'than', 'into', 'over', 'via',
    'is', 'are', 'was', 'were', 'be', 'becomes', 'become', 'equals', 'gives', 'yields',
    'satisfies', 'denotes', 'reads', 'means', 'define', 'defines', 'minimise', 'minimize',
    'minimises', 'minimizes', 'maximise', 'maximize', 'maximises', 'maximizes',
    'optimise', 'optimize', 'compute', 'computes', 'write', 'writes', 'obtain', 'obtains',
}


def _c_colon_before_display(spans, out):
    for i, sp in enumerate(spans):
        if sp.kind != 'mask' or not _DISPLAY.match(sp.text):
            continue
        prev = spans[i - 1] if i else None
        if prev is None or prev.kind != 'text':
            continue
        tail = prev.rendered.rstrip()
        wm = re.search(r'([A-Za-z]+)\s*:$', tail)
        if not wm or wm.group(1).lower() not in _COMPLETING:
            continue
        j = prev.text.rfind(':')
        out.append(_F('colon-before-display-completing-grammar',
                      prev.start + (j if j >= 0 else 0), 'batch', 'free', False,
                      f'the lead-in ends "{tail[-42:]}" and the display supplies its '
                      f'grammatical completion, so the colon interrupts one sentence',
                      'delete the colon, leaving the lead-in and the display as they are'))


# ------------------------------------------------------------------------------- gate
# Any word that could be carrying claim strength. A fix that proposes removing one of these
# raises the claim past its evidence, so the finding is dropped rather than shipped.
_HEDGE = ('may', 'might', 'could', 'appears', 'suggests', 'suggest', 'likely', 'almost',
          'largely', 'fairly', 'quite', 'virtually', 'generally', 'practically', 'seems',
          'we argue', 'we believe', 'we think', 'possibly', 'perhaps', 'tend', 'partially')
_WEAKEN = re.compile(r'\b(delete|remove|drop|cut|strip|weaken|soften|omit)\b', re.I)
# The one rule allowed a mechanical repair is a defect with exactly one correct output.
_REPAIRABLE = ('doubled-word', 'value-closed-up-to-unit',
               'colon-before-display-completing-grammar')


def _gate(findings):
    ok = []
    for f in findings:
        if f['tier'] == 'silent':
            continue
        blob = (f['text'] + ' ' + f['fix']).lower()
        if _WEAKEN.search(f['fix']) and any(h in blob for h in _HEDGE):
            continue
        if f['fix'] and f['rule'] not in _REPAIRABLE:
            f = dict(f, fix='')
        ok.append(f)
    return ok


def checks(src, spans, ctx):
    """Return findings. Never raises: a broken check yields what was collected so far."""
    out = []
    try:
        text = []
        for sp in spans:
            if sp.kind == 'text' and sp.rendered.strip():
                text.append(sp)
                _findings_for(sp.rendered, sp.start, out)
        _c_doubled_word(text, out)
        _c_value_closed_up_to_unit(text, out)
        _c_colon_before_display(spans, out)
    except Exception:
        pass
    return _gate(out)


if __name__ == '__main__':
    import pathlib, sys, collections
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import extract
    grand = collections.Counter()
    for p in sys.argv[1:]:
        src = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        per = collections.Counter()
        for f in checks(src, extract.extract(src),
                        {'stage': 'submission', 'path': p, 'style': {}}):
            per[f['rule']] += 1
            grand[f['rule']] += 1
            print(f"{pathlib.Path(p).name:16s} {f['rule']:38s} {f['text'][:86]}")
        print('  >>', pathlib.Path(p).name, dict(per) or '(clean)')
    print('TOTAL', dict(grand))
