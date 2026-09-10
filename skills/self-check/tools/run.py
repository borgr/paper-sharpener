#!/usr/bin/env python3
"""Load every checks_*.py module plus the built-in checks, run them, print findings."""
import collections, importlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extract as ex
import check as builtin
import docset
import claimguard

import re

HERE = pathlib.Path(__file__).resolve().parent

# A rule that fires dozens of times in one file is almost never finding dozens of defects.
# It is detecting an environment or configuration fact — assets not checked out, a
# \graphicspath the check ignores, a house convention it does not know. A corpus sweep over
# 2140 real files found eight rules exceeding 30 findings in a single file, one reaching 285.
# Enumerating those buries everything else, so they collapse to one honest line.
SATURATION = 12


def collapse_saturated(findings):
    by = {}
    for f in findings:
        by.setdefault((f.get('file'), f.get('rule')), []).append(f)
    out = []
    for (fname, rule), group in by.items():
        if len(group) <= SATURATION:
            out.extend(group)
            continue
        first = dict(group[0])
        first['text'] = (f'{len(group)} occurrences in this file — reported as one finding. '
                        f'A rule firing this often is usually detecting a configuration fact '
                        f'rather than {len(group)} defects. First: {first.get("text", "")}')
        first['saturated'] = len(group)
        first['blocks'] = False          # never block on a saturated rule
        first['cost'] = 'lookup'
        out.append(first)
    return out


# A finding whose fix is a confirmation from on-page material is free by construction,
# whatever the module declared. Cost must reflect what the author DOES, not how much the
# defect matters — conflating the two is what pushes cheap fixes into the expensive bucket
# and defeats the triage.
CONFIRM_FIX = re.compile(r'^\s*(confirm|check whether|decide whether|verify that the|'
                         r'read the|compare the)\b', re.I)
REWORK_MARK = re.compile(r'\b(regenerate|re-?run|retrain|recompute|redraw|re-?plot|'
                         r'obtain|measure|new experiment|ablation)\b', re.I)


def normalise_cost(findings, log=None):
    for f in findings:
        fix = (f.get('fix') or '').strip()
        if f.get('cost') == 'rework' and CONFIRM_FIX.match(fix) and not REWORK_MARK.search(fix):
            if log is not None:
                log.append((f['rule'], 'rework->free', fix[:60]))
            f['cost'] = 'free'
    return findings



FAILED = []
_MOD_CACHE = {}


def modules():
    """Load once per process. FAILED accumulates and is never cleared, because a failure
    that disappears on a later call is a partial scan reported as a clean one."""
    if _MOD_CACHE:
        return list(_MOD_CACHE.items())
    out = []
    for f in sorted(HERE.glob('checks_*.py')):
        try:
            out.append((f.stem, importlib.import_module(f.stem)))
        except Exception as e:
            FAILED.append((f.stem, f'{type(e).__name__}: {e}'))
    _MOD_CACHE.update(out)
    return out


def project_context(paths):
    """Whole-project facts. Cross-references and citations resolve across files, so a
    per-file check reports false positives the moment a paper is split into sections."""
    import re
    labels, refs, cites, bibkeys, files = set(), {}, {}, set(), {}
    roots = set()
    for p in paths:
        p = pathlib.Path(p)
        roots.add(p.parent)
        try:
            src = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        files[p.name] = src
        # Strip line comments before collecting either side. Comparing a commented \ref
        # against a live label set reports commented-out sections as missing labels, which
        # was nine of eleven findings on a real paper.
        live = re.sub(r'(?<!\\)%[^\n]*', '', src)
        labels |= set(re.findall(r'\\label\{([^}]*)\}', live))
        refs[p.name] = set(re.findall(r'\\(?:auto|c|C|eq)?ref\*?\{([^}]*)\}', live))
        for m in re.finditer(r'\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}', live):
            cites.setdefault(p.name, set()).update(
                k.strip() for k in m.group(1).split(',') if k.strip())
    for root in roots:
        for b in root.glob('*.bib'):
            try:
                bibkeys |= set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', b.read_text(encoding='utf-8', errors='replace')))
            except Exception:
                pass
    return {'labels': labels, 'refs': refs, 'cites': cites, 'bibkeys': bibkeys, 'files': files}


def project_findings(pc, stage):
    """Checks that are only sound at project scope."""
    out = []
    for fname, rs in pc['refs'].items():
        for r in sorted(rs - pc['labels']):
            if '#' in r or not r.strip():
                continue
            out.append({'rule': 'dangling-reference-project', 'family': 'integrity', 'offset': 0,
                        'tier': 'query', 'cost': 'free', 'blocks': True, 'file': fname, 'line': 0,
                        'text': f'\\ref{{{r}}} has no \\label anywhere in the project',
                        'fix': 'add the missing label, or correct the reference'})
    if pc['bibkeys']:
        for fname, ks in pc['cites'].items():
            for k in sorted(ks - pc['bibkeys']):
                if '[' in k or ']' in k:
                    continue
                out.append({'rule': 'undefined-citation-project', 'family': 'integrity', 'offset': 0,
                            'tier': 'query', 'cost': 'lookup', 'blocks': True, 'file': fname, 'line': 0,
                            'text': f'cite key {k} resolves to no entry in any .bib in the project',
                            'fix': 'add the bib entry, or correct the key'})
    return out


QUOTE_RE = re.compile(r'"([^"\n]{4,240})"')


def resite_quotes(f, src):
    """Make every quoted fragment in a finding's text findable in the source.

    A check that quotes `.rendered`, or its own token stream, quotes a string the document
    does not contain — `b2.tex` reported `"WP explains locating the architecture and ..."`
    where the file reads `WP1 explains, locating the architecture and`. A reader who
    searches for the quoted words then fails to find them. Replace each quote with the
    verbatim source slice where the fragment can be located, and label it as normalised
    where it cannot. A slice that spans a source line break is cut to its longest whole
    line, with an ellipsis marking the cut, so the quote stays a verbatim substring of the
    file that a reader can actually search for.
    """
    text = f.get('text') or ''
    unfound = []

    def one(m):
        inner = m.group(1)
        core, lead, trail = inner.strip(), '', ''
        if core.startswith('...'):
            lead, core = '... ', core[3:].lstrip()
        if core.endswith('...'):
            trail, core = ' ...', core[:-3].rstrip()
        if len(core) < 4 or core in src:
            return m.group(0)
        off, hit = builtin.locate(src, core)
        if off is None:
            unfound.append(core)
            return m.group(0)
        piece, cut_l, cut_r = builtin.oneline(hit)
        return '"%s%s%s"' % ('... ' if (lead or cut_l) else '', piece,
                             ' ...' if (trail or cut_r) else '')

    new_text = QUOTE_RE.sub(one, text)
    if unfound:
        # Plainly stated. The quote may be normalised beyond recovery, or it may come from a
        # .bib or a sibling file rather than this one. Either way a reader must not spend
        # time searching this file for a string it does not contain.
        new_text += ' [quoted text is not a verbatim string in this file]'
    if new_text != text:
        f['text'] = new_text
    return f


def scan(paths, stage='submission', style=None):
    mods = modules()
    findings = []
    for p in paths:
        p = pathlib.Path(p)
        try:
            src = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        spans = ex.extract(src)
        ctx = {'stage': stage, 'path': str(p), 'style': style or {}}
        for f in builtin.run(src, str(p), stage=stage):
            if f.rule in ('dangling-reference',):
                continue  # superseded by the project-scope check
            findings.append(resite_quotes({
                'rule': f.rule, 'family': f.family, 'cost': f.cost,
                'blocks': f.blocks, 'text': f.text, 'file': p.name,
                # `path` is what the annotation writer groups by. Without it no finding from
                # any module could ever be written into a document.
                'path': str(p), 'offset': f.offset,
                'line': f.line, 'tier': 'query'}, src))
        for name, m in mods:
            try:
                for f in m.checks(src, spans, ctx):
                    f = dict(f)
                    f['file'] = p.name
                    f['path'] = str(p)
                    # `f.get('offset', 0)` defaulted only on a MISSING key; a key present and
                    # None made the slice unbounded, so every unlocalised finding was
                    # attributed to the last line of the file. 0 means no site, and
                    # project_findings already uses line 0 for that.
                    off = f.get('offset') or 0
                    f['offset'] = off
                    f['line'] = src.count('\n', 0, off) + 1 if off else 0
                    findings.append(resite_quotes(f, src))
            except Exception as e:
                FAILED.append((name, f'raised on {p.name}: {type(e).__name__}: {e}'))
    pfs = project_findings(project_context(paths), stage)
    by_name = {pathlib.Path(x).name: str(pathlib.Path(x)) for x in paths}
    for f in pfs:
        f.setdefault('path', by_name.get(f.get('file'), ''))
    findings += pfs
    # Applied to EVERY finding from EVERY module, so no module can opt out and no future
    # module has to remember. Two wording-based gates were bypassed at 69% and 96%.
    findings = claimguard.guard(findings)
    findings = collapse_saturated(findings)
    _log = []
    normalise_cost(findings, _log)
    if _log:
        seen = sorted({(r, w) for r, w, _ in _log})
        for r, w in seen:
            print(f'  cost normalised: {r} {w}', file=sys.stderr)
    return findings


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    stage = 'draft' if '--draft' in sys.argv else 'submission'

    # Only inspect files the document actually builds from. Scratch files, notes and
    # abandoned variants generate findings nobody will ever act on.
    # Do not guess which document is meant. Ranking by mtime picked a \lipsum template over
    # a 13-file paper; ranking by size picked a statistics annex over the ERC's own b1/b2.
    # Every real document gets reported, and only generated trees are dropped.
    doc_sets = None
    if '--all-files' not in sys.argv:
        docs, orphans = docset.documents(args)
        real = [(m, f) for m, f in docs if len(f) > 1 or m.stat().st_size > 2000]
        named = {pathlib.Path(a).resolve() for a in args}
        # Naming a file must check that file. Expanding to every document in the directory
        # made `run.py b1.tex` report 91 findings from eight documents, which is the wrong
        # kind of surprise. Only a document the caller named, or one building from a named
        # file, is in scope.
        scoped = [(m, f) for m, f in real
                  if m.resolve() in named or (named & {x.resolve() for x in f})]
        chosen = scoped or real
        if chosen:
            doc_sets = chosen
            other = len(real) - len(chosen)
            bits = [f'{len(chosen)} document(s) in scope']
            if other:
                bits.append(f'{other} other document(s) in this tree not named')
            if orphans:
                bits.append(f'{len(orphans)} orphaned file(s) skipped')
            print(', '.join(bits))
            for m, f in chosen:
                print(f'  {m.name}  ({len(f)} file{"s" if len(f) != 1 else ""})')
            print()

    if doc_sets and len(doc_sets) > 1:
        allf = []
        for m, files in doc_sets:
            sub = scan([str(x) for x in sorted(files)], stage=stage)
            for x in sub:
                x['document'] = m.name
            allf.append((m, sub))
        for m, sub in sorted(allf, key=lambda kv: -len(kv[1])):
            print(f'=== {m.name}: {len(sub)} findings '
                  f'({sum(1 for x in sub if x.get("blocks"))} blocking)')
            for r, c in collections.Counter(x['rule'] for x in sub).most_common(8):
                print(f'     {c:3d}  {r}')
        seen, fs = set(), []
        for _, sub in allf:
            for x in sub:
                key = (x.get('file'), x.get('rule'), x.get('offset'), str(x.get('text',''))[:60])
                if key in seen:
                    continue      # a file shared by two documents is one defect, not two
                seen.add(key)
                fs.append(x)
        dropped = sum(len(sub) for _, sub in allf) - len(fs)
        if dropped:
            print(f'  ({dropped} duplicate findings from files shared between documents)')
        print()
    else:
        if doc_sets:
            args = [str(f) for f in sorted(doc_sets[0][1])]
        fs = scan(args, stage=stage)

    if FAILED:
        print('!' * 66)
        print(f'INCOMPLETE — {len(set(n for n, _ in FAILED))} check module(s) did not run.')
        print('The families they cover are ABSENT from the counts below.')
        for name, why in sorted(set(FAILED)):
            print(f'  {name}: {why[:110]}')
        print('!' * 66)
        print()
    byfam = collections.Counter(f['family'] for f in fs)
    byrule = collections.Counter(f['rule'] for f in fs)
    blocks = [f for f in fs if f.get('blocks')]
    print(f'{len(fs)} findings  ({len(blocks)} would block submission)  stage={stage}\n')
    for fam, c in byfam.most_common():
        print(f'  {fam:22s} {c}')
    print()
    for r, c in byrule.most_common(30):
        cost = next((f.get('cost') for f in fs if f['rule'] == r), '?')
        print(f'  {c:4d}  {r:34s} [{cost}]')
    print('\n--- blocking, cheapest first ---')
    order = {'free': 0, 'lookup': 1, 'rework': 2}
    for f in sorted(blocks, key=lambda x: order.get(x.get('cost'), 3))[:14]:
        print(f"  [{f.get('cost'):6s}] {f['file']}:{f['line']}  {f['rule']}: {f['text'][:88]}")
    if FAILED:
        sys.exit(2)  # a partial scan must not look like a clean one to a caller
