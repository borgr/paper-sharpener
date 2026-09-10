#!/usr/bin/env python3
"""Resolve which .tex files a document actually builds from.

Globbing *.tex sweeps in scratch files, notes and abandoned drafts, and every finding in
those is noise. Only files reachable from a main file via \\input or \\include count.
"""
import pathlib, re

MAIN_HINT = re.compile(r'\\documentclass')

# Generated and vendored trees are never the document. Scanning them is wasted work and any
# finding inside them is noise, since nobody edits a build artefact.
SKIP_DIRS = {'build', 'out', 'output', '_build', 'dist', 'node_modules', '.git',
             'texmf', 'latex.out', 'auto', '_minted', 'anc'}


def _skipped(p: pathlib.Path, root: pathlib.Path) -> bool:
    """True when p sits inside a generated tree BELOW root.

    The test must be relative. An absolute one deletes every path under a directory that
    happens to be called `build`, which is where this project's own corpus lives.
    """
    try:
        rel = p.relative_to(root)
    except ValueError:
        return False
    return bool(SKIP_DIRS & set(rel.parts[:-1]))


def _tex_files(root: pathlib.Path):
    for p in root.rglob('*.tex'):
        if not _skipped(p, root):
            yield p
INPUT_RE = re.compile(r'\\(?:input|include|subfile)\s*\{([^}]*)\}')


def mains(root: pathlib.Path):
    out = []
    for p in sorted(_tex_files(root)):
        try:
            head = p.read_text(encoding='utf-8', errors='replace')[:4000]
        except Exception:
            continue
        if MAIN_HINT.search(head):
            out.append(p)
    return out


def reachable(main: pathlib.Path, root: pathlib.Path = None):
    """Transitive closure of \\input from `main`."""
    root = root or main.parent
    seen, queue = set(), [main]
    while queue:
        cur = queue.pop()
        if cur in seen or not cur.exists():
            continue
        seen.add(cur)
        try:
            src = cur.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        for m in INPUT_RE.finditer(src):
            name = m.group(1).strip()
            if not name or '\\' in name or '#' in name:
                continue
            for base in (cur.parent, root, main.parent):
                for cand in (base / name, base / (name + '.tex')):
                    if cand.exists():
                        queue.append(cand.resolve())
                        break
    return seen


def documents(paths):
    """Map each main document to the files it builds from, newest main first.

    A project with several \\documentclass files usually has one live document and
    several abandoned variants. Reporting per document keeps them separate instead of
    unioning them, and the caller can pick.
    """
    paths = [pathlib.Path(p).resolve() for p in paths]
    roots = {p.parent for p in paths}
    top = min(roots, key=lambda r: len(r.parts)) if roots else None
    paths = [p for p in paths if not (top and _skipped(p, top))]
    found = mains(top) if top else []
    found = sorted(set(m.resolve() for m in found))
    docs = [(m, reachable(m, m.parent)) for m in found]

    def rank(item):
        m, files = item
        try:
            body = m.read_text(encoding='utf-8', errors='replace')
        except Exception:
            body = ''
        # A template is not the document, however recently it was touched.
        template = bool(re.search(r'\\lipsum|\\blindtext|YOUR TITLE|Anonymous submission'
                                  r'|placeholder', body, re.I)) or \
            bool(re.search(r'templ|sample|example|skeleton|boilerplate', m.stem, re.I))
        return (template, -len(files), -len(body), -m.stat().st_mtime, m.name)

    docs.sort(key=rank)
    covered = set().union(*[f for _, f in docs]) if docs else set()
    orphans = {p for p in paths if p not in covered}
    return docs, orphans


def document_set(paths):
    """Given candidate paths, return the subset that some main document builds from,
    plus the orphans, so a caller can report the split rather than silently dropping files."""
    paths = [pathlib.Path(p).resolve() for p in paths]
    roots = {p.parent for p in paths}
    built = set()
    found_mains = []
    for r in roots:
        for m in mains(r):
            found_mains.append(m)
            built |= reachable(m.resolve(), r)
    if not found_mains:
        return set(paths), set(), []
    keep = {p for p in paths if p in built}
    orphans = {p for p in paths if p not in built}
    return keep, orphans, found_mains
