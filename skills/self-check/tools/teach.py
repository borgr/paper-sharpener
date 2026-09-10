#!/usr/bin/env python3
"""Attach the teaching layer to findings.

A finding that only names a defect trains obedience. A finding that carries the mechanism
once, then cites it afterwards, teaches — and the ledger already holds the mechanism for
every family, plus a page that derives the family's rules from it.

State is kept per project so the second run is quieter than the first, and per user so the
second paper is quieter than the first. That fade is the difference between teaching and
lecturing.
"""
import json, pathlib

LEDGER = pathlib.Path(__file__).resolve().parent.parent / 'references'
STATE = pathlib.Path.home() / '.sharp_taught.json'

PAGE = {
    'integrity': 'family_integrity.md',
    'evidence-surface': 'family_evidence-surface_A.md',
    'claim-calibration': 'family_claim-calibration.md',
    'cohesion': 'family_cohesion.md',
    'naming-notation': 'family_naming-notation.md',
    'register-redundancy': 'family_register-redundancy.md',
    'sentence-mechanics': 'family_sentence-mechanics.md',
    'process': 'family_process.md',
}

# One sentence per family, stating the mechanism rather than the rule. Drawn from the
# family pages' own mechanism sections.
MECHANISM = {
    'integrity': 'This family compares the document against itself, which is why a '
                 'non-specialist can check it and why almost none of it can be auto-fixed. '
                 'Detecting that two numbers disagree never tells you which is right.',
    'evidence-surface': 'A number or a graph is a claim in compressed form, and the '
                        'compression is where meaning gets lost. Precision rules apply only '
                        'to measured quantities, never to exact ones.',
    'claim-calibration': 'Hedges and modals encode the distance between what was measured '
                         'and what is asserted. Deleting one is grammatical, preserves '
                         'meaning by every mechanical test, and silently raises the claim.',
    'cohesion': 'A reader arrives at each sentence expecting known material first and the '
                'new point last. Cohesion faults are produced by editing moves, so the '
                'check belongs to the move.',
    'naming-notation': 'Elegant variation is a virtue in prose and a defect in science, '
                       'because a synonym reads as a second concept. Detection is '
                       'mechanical and the repair is always a query.',
    'register-redundancy': 'Redundancy costs attention and makes one claim look like '
                           'several. Register costs credibility, because a reviewer reads '
                           'self-praise as a substitute for evidence.',
    'sentence-mechanics': 'A sentence is a processing load. The corpus says experts spend '
                          'almost no review effort here, so this pass runs late and cheap.',
}


def _load():
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def _save(d):
    try:
        STATE.write_text(json.dumps(d, indent=1))
    except Exception:
        pass


def annotate(findings, project='default', fade=True):
    """Add `mechanism` and `page` to the first finding of each family, per project."""
    taught = _load()
    seen_here = set(taught.get(project, []))
    seen_ever = {f for v in taught.values() for f in v}
    for f in findings:
        fam = f.get('family', '')
        f['page'] = PAGE.get(fam, '')
        if fam in seen_here:
            f['mechanism'] = ''
        elif fade and fam in seen_ever:
            f['mechanism'] = ''  # taught on an earlier document; cite the page only
        else:
            f['mechanism'] = MECHANISM.get(fam, '')
            seen_here.add(fam)
    taught[project] = sorted(seen_here)
    _save(taught)
    return findings


def reset(project=None):
    d = _load()
    if project:
        d.pop(project, None)
    else:
        d = {}
    _save(d)
