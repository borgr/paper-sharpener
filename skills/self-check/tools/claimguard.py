#!/usr/bin/env python3
"""Structural protection for claim markers.

WHY THE OLD GATES FAILED. They inspected the wording of a finding's `fix` and dropped it if
the wording looked like a weakening instruction. Two audits bypassed that — 9 of 13
phrasings, then 23 of 24 — because a blocklist over natural language has no floor. "Assert
the finding directly" weakens a claim and matches nothing.

WHAT THIS DOES INSTEAD. It never reads the fix. It reads what the finding TOUCHES. If the
matched text carries a claim marker — a hedge, a tentative modal, an intensifier on a graded
absolute, or a first-person stance marker — then no fix may be proposed at all, whatever it
says. The finding is reported and the author decides.

That cannot be bypassed by phrasing, because phrasing is not consulted.
"""
import re
import unicodedata

HEDGE = (r'may|might|could|would|should|can|appears?|seems?|suggests?|indicates?|'
         r'tends? to|likely|unlikely|possibly|probably|perhaps|potentially|'
         r'arguably|presumably|apparently|roughly|approximately|about|around|'
         r'largely|generally|typically|usually|often|sometimes|virtually|'
         r'practically|nearly|almost|fairly|somewhat|relatively|partly|mostly|'
         r'we (?:argue|believe|expect|think|suspect|hypothesise|hypothesize)|'
         r'in our view|to our knowledge|as far as we')

GRADED = r'(?:almost|nearly|virtually|practically|essentially|effectively|fairly|largely)\s+\w+'

STANCE = (r'\bwe\b|\bour\b|\bus\b|\bI\b|\bmy\b|in our view|we find|we observe|'
          r'we show|we argue|we believe')

CLAIM_MARKER = re.compile(rf'\b(?:{HEDGE})\b|{GRADED}|(?:{STANCE})', re.I)

PROTECTED_FAMILIES = ('claim-calibration', 'register-redundancy')

# Homoglyphs and invisible characters defeated the first version: a fullwidth `ｍight`, a
# non-breaking space, a soft hyphen and a Cyrillic `а` all passed. Normalise before matching.
_INVISIBLE = dict.fromkeys(map(ord, '\u00ad\u200b\u200c\u200d\ufeff'), None)
_HOMOGLYPH = str.maketrans({
    '\u0430': 'a', '\u0435': 'e', '\u043e': 'o', '\u0440': 'p', '\u0441': 'c',
    '\u0443': 'y', '\u0445': 'x', '\u04bb': 'h', '\u0456': 'i', '\u0491': 'r',
    '\u2019': "'", '\u2018': "'", '\u00a0': ' ', '\u2007': ' ', '\u202f': ' ',
})


def _normalise(text):
    t = unicodedata.normalize('NFKC', text)
    return t.translate(_INVISIBLE).translate(_HOMOGLYPH)


def touches_claim_marker(finding):
    """True when the text this finding is about carries claim strength.

    Reads EVERY string value in the finding, not a fixed key list. The previous version
    inspected five key names, so a claim marker in any other field went unseen — and a
    module can add fields freely.
    """
    for v in finding.values():
        if isinstance(v, str) and CLAIM_MARKER.search(_normalise(v)):
            return True
        if isinstance(v, (list, tuple)):
            for x in v:
                if isinstance(x, str) and CLAIM_MARKER.search(_normalise(x)):
                    return True
    return False


def guard(findings):
    """Force report-only on anything touching a claim marker. Never reads `fix` wording."""
    out = []
    for f in findings:
        f = dict(f)
        by_content = touches_claim_marker(f)
        by_family = f.get('family') in PROTECTED_FAMILIES
        if by_content:
            # Anything touching claim strength is report-only, in any family.
            f['fix'] = ''
            f['tier'] = 'query'
            f['claim_protected'] = True
        elif by_family and (f.get('fix') or ''):
            # A protected family may describe a fix, but never apply one silently.
            f['tier'] = 'query'
            f['claim_protected'] = True
        if f.get('claim_protected'):
            f['tier'] = 'query'
        out.append(f)
    return out
