#!/usr/bin/env python3
"""Write findings into the .tex as addressed notes at the defect site.

The corpus is unambiguous about this. Across five independent samples of real revisions,
roughly a quarter of every cross-author edit is not an edit — it is an addressed question
left at the exact site of a problem the editor could not resolve, and the note is deleted
by whoever answers it.

SAFETY — every rule here exists because an adversarial audit broke the previous version.

  * Offsets are VALIDATED. A note is never written into a masked span (math, verbatim,
    tabular, float) and never splits a word or a control word. The previous version wrote a
    note inside \documentclass{...} and made a file unbuildable, and 11 of 135 sited
    offsets landed in masked spans.
  * Note bodies are ESCAPED. A raw % comments out the note's own closing brace and the
    author's following text. 133 of 274 real finding texts contain a backslash and 13 a %.
  * Encoding and line endings are PRESERVED. The previous version read with
    errors='replace', which turned a latin-1 byte into U+FFFD, and normalised CRLF to LF.
    Both were irreversible and sweep re-inflicted them, so its byte-identical claim was
    false. This version refuses a file it cannot decode strictly.
  * A file must be TRACKED and clean. An empty `git status` was previously read as clean,
    which approved .gitignore'd files that git cannot restore.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

# Must not collide with any kernel or package macro. \sharp is the musical symbol,
# and \providecommand silently declines to redefine an existing name, so notes
# written under that tag never rendered.
TAG = 'scnote'
NOTE_RE = re.compile(r'\\' + TAG + r'\{\[[0-9a-f]{8}\][^{}]*(?:\{[^{}]*\}[^{}]*)*\}')
# Kernel commands only. \textcolor needs xcolor, which nothing here loads and nothing here
# may add to a co-author's preamble, so an annotated file failed to build on the colour.
MACRO_DEF = (r'\providecommand{\%s}[1]{{\bfseries\footnotesize [#1]}}' % TAG)

WORD = re.compile(r'[A-Za-z0-9]')

# The note macro must be removable by `sweep` from wherever it was placed, and must not
# depend on a package the document may not load.
MACRO_RE = re.compile(r'[ \t]*' + re.escape(MACRO_DEF) + r'\n?')


class MixedEndings(ValueError):
    """The file uses both CRLF and LF, so no single ending can be restored."""


def _git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, text=True)


def read_source(path):
    r"""Decode strictly and preserve line endings. Returns (text, newline) or raises.

    A mixed-ending file is REFUSED. Guessing one ending and expanding every \n back to it
    converted a file with two CRLFs into a file with five, on a run that wrote zero notes,
    and `sweep` had no route back. There is no correct guess, so there is no guess.
    """
    raw = pathlib.Path(path).read_bytes()
    text = raw.decode('utf-8')          # strict on purpose; a failure must stop the write
    crlf = raw.count(b'\r\n')
    lf = raw.count(b'\n') - crlf
    if crlf and lf:
        raise MixedEndings('mixed line endings')
    return text.replace('\r\n', '\n'), ('\r\n' if crlf else '\n')


def write_source(path, text, nl):
    data = text.replace('\n', nl) if nl != '\n' else text
    pathlib.Path(path).write_bytes(data.encode('utf-8'))


def is_clean(path):
    """Tracked by git AND free of uncommitted changes. Both halves matter."""
    path = pathlib.Path(path).resolve()
    repo = path.parent
    if not _git(repo, 'rev-parse', '--show-toplevel').stdout.strip():
        return False, 'not in a git repository'
    if _git(repo, 'ls-files', '--error-unmatch', '--', str(path)).returncode != 0:
        return False, 'not tracked by git, so a bad write could not be reverted'
    st = _git(repo, 'status', '--porcelain', '--', str(path)).stdout.strip()
    if st:
        return False, f'has uncommitted changes ({st.split()[0]})'
    return True, 'tracked and clean'


def owner(path, line):
    path = pathlib.Path(path).resolve()
    out = _git(path.parent, 'blame', '-L', f'{line},{line}', '--porcelain',
               '--', str(path)).stdout
    for l in out.splitlines():
        if l.startswith('author-mail'):
            return l.split('<', 1)[-1].rstrip('>')
        if l.startswith('author '):
            return l[7:].strip()
    return ''


def escape(body):
    r"""Make a note body safe as a single macro argument.

    A raw % ends the line and swallows the closing brace. A raw backslash starts a control
    word that will not exist. Braces unbalance the argument.
    """
    body = body.replace('\\', '/').replace('%', 'pct').replace('$', '')
    body = body.replace('{', '(').replace('}', ')')
    body = re.sub(r'[#&~^_]', ' ', body)
    return re.sub(r'\s+', ' ', body).strip()


def _blank_comments(text):
    """Comment bodies replaced by spaces, so offsets stay exact.

    A `}` inside a line comment previously unbalanced the depth map and routed notes into a
    live `\\emph{...}` argument.
    """
    return re.sub(r'(?<!\\)%[^\n]*', lambda m: ' ' * len(m.group(0)), text)


def _depth_map(text):
    """Brace depth at every offset, and the offset where the body begins.

    An offset at depth > 0 sits inside a macro argument — `\\section{...}`,
    `\\citep{...}`, `\\author{...}`, a pgfkeys list — and inserting there corrupts the
    macro. An audit found 33 of 376 real offsets doing exactly that, plus 7 in the preamble
    where a note cannot render at all.
    """
    text = _blank_comments(text)   # a brace in a comment is not a real brace
    depth = [0] * (len(text) + 1)
    d = 0
    i = 0
    while i < len(text):
        c = text[i]
        if c == '\\':
            depth[i] = d
            depth[i + 1] = d
            i += 2
            continue
        if c == '{':
            depth[i] = d
            d += 1
        elif c == '}':
            d = max(0, d - 1)
            depth[i] = d
        else:
            depth[i] = d
        i += 1
    depth[len(text)] = d
    m = re.search(r'\\begin\{document\}', text)
    return depth, (m.end() if m else 0)


def safe_offset(text, spans, off, depth=None, body_start=None):
    """Nearest offset at which a macro call may be inserted, or None.

    Refuses masked, comment and annotation spans; refuses depth > 0, which is inside a
    macro argument; refuses the preamble; and refuses to split a word or a control word.
    """
    if not (0 < off <= len(text)):
        return None
    if depth is None:
        depth, body_start = _depth_map(text)
    sp = next((s for s in spans if s.start <= off < s.end), None)
    if sp is None or sp.kind != 'text':
        return None
    if off <= body_start:
        return None
    # Do not split a word.
    if off < len(text) and WORD.match(text[off - 1] or '') and WORD.match(text[off] or ''):
        m = re.compile(r'[A-Za-z0-9]*').match(text, off)
        off = m.end() if m else off
    # Do not land inside a control word: back up to before its backslash.
    left = text.rfind('\\', max(0, off - 40), off)
    if left != -1 and re.fullmatch(r'\\[A-Za-z@]*', text[left:off]):
        off = left
    if depth[min(off, len(text))] != 0:
        return None          # inside a macro argument or a group
    if not (sp.start <= off <= sp.end):
        return None
    return off


def note_text(f):
    who = (f.get('owner') or '').split('@')[0]
    body = f"{f.get('rule', '?')}: {f.get('text', '')}"
    ask = f.get('fix') or ''
    if ask and ask != f.get('text'):
        body += f' -- {ask}'
    if f.get('mechanism'):
        body += f' [why: {f["mechanism"]}]'
    if f.get('page'):
        body += f' [see {f["page"]}]'
    if who:
        body = f'@{who} {body}'
    return escape(body)


def digest(f):
    """Note id. Two SITES of one defect must get two ids.

    Hashing only rule and text collapsed both sites of a repeated defect onto one id, and
    the second was then discarded as an already-written duplicate, so the note landed at one
    site and the other went unmarked.
    """
    key = f"{f.get('rule','')}|{str(f.get('text',''))[:80]}|{int(f.get('offset') or 0)}"
    return hashlib.sha1(key.encode()).hexdigest()[:8]


def _install_macro(src):
    r"""Insert MACRO_DEF after the \documentclass line, never before it.

    Prepending at offset 0 puts a \providecommand ahead of \documentclass, which is an
    error before the class is loaded, so every annotated file failed to build.
    """
    at = 0
    for m in re.finditer(r'\\documentclass\s*(\[[^\]]*\])?\s*\{[^}]*\}[^\n]*\n?', src):
        line = src.rfind('\n', 0, m.start()) + 1
        if '%' in src[line:m.start()].replace('\\%', ''):
            continue                     # a commented-out \documentclass loads nothing
        at = m.end()
        break
    return src[:at] + MACRO_DEF + '\n' + src[at:]


def write(findings, dry_run=True, force=False, add_macro=True):
    import extract as ex
    import claimguard
    # Defence in depth. run.scan already guards, but a caller reaching write() directly
    # would otherwise bypass claim protection completely, which an audit demonstrated.
    findings = claimguard.guard(findings)
    by_file = {}
    for f in findings:
        if f.get('path'):
            by_file.setdefault(f['path'], []).append(f)
    report = []
    for path, fs in by_file.items():
        ok, why = is_clean(path)
        if not ok and not force:
            report.append((path, 0, f'SKIPPED: {why}'))
            continue
        try:
            src, nl = read_source(path)
        except UnicodeDecodeError:
            report.append((path, 0, 'SKIPPED: not valid UTF-8, refusing to rewrite it'))
            continue
        except MixedEndings:
            report.append((path, 0, 'SKIPPED: mixed line endings, refusing to rewrite it'))
            continue
        original = src
        spans = ex.extract(src)
        existing = {m.group(0)[len(TAG) + 3:len(TAG) + 11] for m in NOTE_RE.finditer(src)}
        fs = [f for f in fs if digest(f) not in existing]
        depth, body_start = _depth_map(src)
        sited, unsited = [], []
        for f in fs:
            o = safe_offset(src, spans, int(f.get('offset') or 0), depth, body_start)
            (sited.append((o, f)) if o is not None else unsited.append(f))
        for o, f in sorted(sited, key=lambda x: -x[0]):
            src = src[:o] + '\\%s{[%s] %s}' % (TAG, digest(f), note_text(f)) + src[o:]
        # Test for the DEFINITION, not for the tag. An \input'd file has no
        # \begin{document}, so the "preamble" was the whole file including the note just
        # inserted — which made the condition unsatisfiable and left 17 of 21 files on a real
        # multi-file paper receiving notes with no definition, so they would not compile.
        if add_macro and sited and MACRO_DEF not in src:
            src = _install_macro(src)
        # A run that writes nothing must leave the file byte-identical, mtime included.
        # The previous version called write_source unconditionally, so a clean file was
        # rewritten — and with a mixed-ending file that rewrite was not reversible.
        changed = src != original
        if changed and not dry_run:
            write_source(path, src, nl)
        if not changed:
            note = 'unchanged'
        else:
            note = ('would write' if dry_run else 'written')
        if unsited:
            note += f'; {len(unsited)} unsited, report only'
        report.append((path, len(sited), note))
    return report


def sweep(paths, dry_run=True):
    """Remove every note and the macro definition. Returns (path, notes_removed).

    The write is gated on the CONTENT changing, not on a note having matched. Gating on
    the note count left a file holding only the macro definition dirty for ever, because
    that file has zero notes to remove.
    """
    out = []
    for path in paths:
        try:
            src, nl = read_source(path)
        except UnicodeDecodeError:
            out.append((path, -1))
            continue
        except MixedEndings:
            out.append((path, -1))
            continue
        new, n = NOTE_RE.subn('', src)
        new = MACRO_RE.sub('', new)
        if new != src and not dry_run:
            write_source(path, new, nl)
        out.append((path, n))
    return out
