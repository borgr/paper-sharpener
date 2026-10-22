#!/usr/bin/env python3
"""Mechanical checks for a recommendation letter (.tex, .md or .txt).

Settles only what a pattern can settle and reports it by the level of letter-guide.md that
owns it. Every finding names the guide entry that gives its reason. Nothing is rewritten.

    python3 letter_check.py main.tex [--cap-words 1000] [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# --- lexicons -------------------------------------------------------------------------------
# Hedges and doubt raisers: Madera et al. 2019 typology; Houser & Lemmons 2018. Matched only in
# sentences that are about the candidate (see _about_candidate), to spare "I may be reached at".
HEDGES = [
    r"\bmight\b", r"\bmay\b", r"\bperhaps\b", r"\bpossibly\b", r"\bhopefully\b", r"\bI hope\b",
    r"\bseems?\b", r"\bappears? to\b", r"\bsomewhat\b", r"\bfairly\b", r"\brelatively\b",
    r"\breasonably\b", r"\bcould become\b", r"\bshould be able to\b", r"\bwith time\b",
    r"\bnot sure\b", r"\buncertain\b", r"\bslightly\b", r"\bto some extent\b", r"\bpotentially\b",
]
NEGATIVES = [
    r"\blacks?\b", r"\bweakness(es)?\b", r"\bstruggl\w*", r"\blimited (experience|knowledge)\b",
    r"\bnot yet\b", r"\bdoes(n't| not) matter\b", r"\bdo(n't| not) matter\b",
    r"\bstrong opinions\b", r"\bcriticism\b", r"\bchallenging personality\b",
    r"\bdoes(n't| not) have\b", r"\bdifficult(y|ies)? (with|in)\b",
]
FAINT = [
    r"\bcompetent\b", r"\badequate\b", r"\bsatisfactory\b", r"\bsolid\b", r"\bcapable\b",
    r"\bmeets expectations\b", r"\bminimal supervision\b", r"\bcan do the job\b",
    r"\bbetter than average\b", r"\breliable\b", r"\bgood\b",
]
STANDOUT = [
    r"\bexceptional\w*", r"\boutstanding\b", r"\bsuperb\b", r"\bremarkabl\w+", r"\bbrilliant\b",
    r"\bunparalleled\b", r"\bextraordinar\w+", r"\bbest\b", r"\bstrongest\b", r"\btop\b",
    r"\bsurpass\w*", r"\bstands? out\b", r"\brare\b", r"\bfar ahead\b",
    r"\b(well|far) (past|beyond)\b", r"\bhard to compare\b", r"\bnone (of them )?compares?\b",
    r"\b(a )?handful\b", r"\bfewer than\b",
]
# Advisory only (letter-guide: Swap the candidate, not the words). Schmader 2007; Madera 2009.
GRINDSTONE = ["hardworking", "hard-working", "hard working", "diligent", "conscientious",
              "meticulous", "dependable", "dedicated", "tireless", "persistent", "thorough",
              "organized", "on time", "timely"]
ABILITY = ["talented", "intelligent", "brilliant", "gifted", "insightful", "creative",
           "original", "analytical", "skilled", "inventive", "a scientist", "a researcher",
           "vision", "independent"]
COMMUNAL = ["caring", "warm", "kind(?! of)", "helpful", "nurturing", "sympathetic", "sensitive",
            "agreeable", "tactful", "compassionate", "pleasant"]
PERSONAL = [r"\bhusband\b", r"\bwife\b", r"\bchildren\b", r"\bpregnan\w*", r"\bmaternity\b",
            r"\bmother of\b", r"\bfather of\b", r"\bhis family\b", r"\bher family\b",
            r"\battractive\b", r"\bpretty\b", r"\bpetite\b", r"\bhandsome\b"]
STEREOTYPE = [r"\bnot (overly )?emotional\b", r"\bfor a (woman|girl|man)\b",
              r"\bdespite being\b", r"\bsurprisingly\b"]
RESIDUE = [r"\bTODO\b", r"\bXXX\b", r"\bTBD\b", r"\\lipsum", r"\blorem ipsum\b",
           r"\bThis paragraph (describes|is the place|should)\b", r"\bInsert\b",
           r"<[A-Za-z ]+>", r"\[(candidate|name|program|venue|NAME)\]"]
# Venue or status words: a paper mention with none of these gets a finding
# (letter-guide: Describe the research, and translate its currency).
VENUE = [r"\barXiv\b", r"\baccepted\b", r"\bunder review\b", r"\bworkshop\b", r"\bconference\b",
         r"\bjournal\b", r"\bpublished\b", r"\bpreprint\b", r"\bin submission\b",
         r"\b(NeurIPS|ICML|ICLR|ACL|EMNLP|NAACL|EACL|COLM|CVPR|ICCV|ECCV|AAAI|IJCAI|KDD|"
         r"SIGIR|WWW|TACL|JMLR|TMLR|COLING|CHI|UIST|STOC|FOCS|SODA|PLDI|POPL|OSDI|SOSP|"
         r"Nature|Science|PNAS)\b"]
VENUE += [r"\b(in preparation|in progress|under submission|writing or review|reviewing)\b"]
PAPER = r"\b(papers?|publications?|findings|preprints?|manuscripts?)\b"
POTENTIAL = [r"\bpotential\b", r"\bfuture\b", r"\bbecome\b", r"\bgrow\w*", r"\bfruits?\b",
             r"\blater on\b", r"\bdevelop into\b", r"\bresearcher\b", r"\bscientist\b"]
RANK = [r"\btop \d+ ?(%|percent)", r"\bbest\b", r"\bstrongest\b", r"\bone of the\b",
        r"\bamong the\b", r"\bsurpass\w*", r"\bcompare\w*\b", r"\bin my (\d+|\w+) years\b",
        r"\bI would hire\b", r"\branks?\b"]
POOL = r"\b(\d+|dozens|hundreds)\b[^.]{0,40}\b(students?|people|researchers|"\
       r"interns|postdocs|mentees|candidates|undergraduates)\b"
WINDOW = r"\b(since (19|20)\d\d|(over|in|during) (the (past|last) )?(\d+|a few|several|two|three|"\
         r"four|five|six|seven|eight|nine|ten|twelve|fifteen|twenty|thirty) years)\b"
CANDIDATE = [r"\b(he|she|they|him|her|them|his|their)\b", r"\\fname", r"\\lname"]


def _rx(pats):
    return re.compile("|".join(f"(?:{p})" for p in pats), re.IGNORECASE)


HEDGE_RX, NEG_RX, FAINT_RX, STANDOUT_RX = map(_rx, (HEDGES, NEGATIVES, FAINT, STANDOUT))
PERSONAL_RX, STEREO_RX, RESIDUE_RX, VENUE_RX, RANK_RX, POTENTIAL_RX = map(
    _rx, (PERSONAL, STEREOTYPE, RESIDUE, VENUE, RANK, POTENTIAL))
PAPER_RX, POOL_RX, WINDOW_RX = (re.compile(p, re.IGNORECASE) for p in (PAPER, POOL, WINDOW))
HIRE_RX = re.compile(r"\bI would (hire|recruit|take)\b", re.IGNORECASE)
CANDIDATE_MACRO = re.compile(r"\\candidate\{([^{}]*)\}\{([^{}]*)\}")


# --- reading the letter ---------------------------------------------------------------------
def _strip_comment(line):
    out, i = [], 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if line[i] == "%":
            break
        out.append(line[i])
        i += 1
    return "".join(out)


def _strip_footnotes(text):
    """Drop \\footnote{...} (balanced braces): a writer note is not the letter's body."""
    out, i = [], 0
    while True:
        j = text.find("\\footnote{", i)
        if j < 0:
            return "".join(out) + text[i:]
        out.append(text[i:j])
        depth, k = 0, j + len("\\footnote")
        while k < len(text):
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
            if depth == 0:
                break
        i = k


def _detex(text):
    text = re.sub(r"\\(textbf|textit|emph|underline)\{([^{}]*)\}", r"\2", text)
    text = re.sub(r"\\(fname|lname|recto)\{\}", r"\\\1", text)
    text = text.replace("~", " ").replace("\\&", "&").replace("\\%", "%")
    text = re.sub(r"\\(opening|closing)\{[^{}]*\}", "", text)
    return text


def read_body(path):
    """Return [(line_no, text)] for the letter body, comments stripped."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    is_tex = str(path).endswith(".tex")
    start, end = 0, len(lines)
    if is_tex:
        for i, l in enumerate(lines):
            if "\\begin{document}" in l:
                start = i + 1
            if "\\end{document}" in l:
                end = i
                break
    body = []
    for i in range(start, end):
        t = _strip_comment(lines[i]) if is_tex else lines[i]
        body.append((i + 1, _detex(t) if is_tex else t))
    return body


def paragraphs(body):
    """Group lines into paragraphs: [(first_line_no, text, line_starts)], where line_starts maps
    character offsets in text back to source lines, so a sentence reports its own line."""
    paras, cur, starts = [], [], []
    for no, t in body:
        if t.strip():
            starts.append((len(" ".join(cur)) + (1 if cur else 0), no))
            cur.append(t.strip())
        elif cur:
            paras.append((starts[0][1], " ".join(cur), starts))
            cur, starts = [], []
    if cur:
        paras.append((starts[0][1], " ".join(cur), starts))
    paras = [(no, _strip_footnotes(t), st) for no, t, st in paras]
    return [p for p in paras if len(p[1].split()) > 3]


def sentences(paras):
    out = []
    for _, text, starts in paras:
        pos = 0
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", text):
            at = text.find(s, pos)
            pos = at + len(s)
            line = [no for off, no in starts if off <= max(at, 0)][-1]
            if s.strip():
                out.append((line, s.strip()))
    return out


MECH = 9  # mechanical: fixed without asking, listed last


# --- checks ---------------------------------------------------------------------------------
def finding(level, entry, line, what, quote=""):
    return {"level": level, "entry": entry, "line": line, "what": what, "quote": quote[:160]}


def candidate_names(path):
    """First and last name from the template's \\candidate{First}{Last}, if present."""
    src = Path(path).read_text(encoding="utf-8")
    m = CANDIDATE_MACRO.search(src)
    if m:
        return [n.strip() for n in m.groups() if n.strip()]
    # Older templates set the names directly: \newcommand{\fname}{First}
    names = []
    for macro in ("fname", "lname"):
        d = re.search(r"\\(?:re)?newcommand\{?\\" + macro + r"\}?\{([^{}]*)\}", src)
        if d and d.group(1).strip():
            names.append(d.group(1).strip())
    return names


def _count(lexicon, low):
    return sum(len(re.findall(rf"\b{w}\b", low)) for w in lexicon)


def check(path, cap_words=None):
    body = read_body(path)
    paras = paragraphs(body)
    sents = sentences(paras)
    names = candidate_names(path)
    cand_rx = _rx(CANDIDATE + [rf"\b{re.escape(n)}\b" for n in names])
    text = " ".join(p for _, p, _ in paras)
    counted = text
    for _, s in sents:
        if RESIDUE_RX.search(s):
            counted = counted.replace(s, "")
    words = len(re.findall(r"\b\w+\b", counted))
    out = []

    # Level 0: the literal name beside the \fname macro
    if names and "\\fname" in text:
        name_rx = re.compile(rf"\b{re.escape(names[0])}\b")
        hits = [no for no, s in sents if name_rx.search(s)]
        if hits:
            lines = ", ".join(str(n) for n in sorted(set(hits)))
            out.append(finding(MECH, "Template residue and names", hits[0],
                               f"literal name '{names[0]}' beside the \\fname macro "
                               f"({len(hits)} sentences; lines {lines})"))

    # Level 0: residue, cap
    for no, s in sents:
        m = RESIDUE_RX.search(s)
        if m:
            out.append(finding(MECH, "Template residue and names", no,
                               f"template or placeholder text ('{m.group(0)}')", s))
    if cap_words and words > cap_words:
        out.append(finding(0, "Obey the call before anything else", None,
                           f"{words} words, over the {cap_words}-word cap"))

    # Mechanical: layout problems that only show in the output
    src = Path(path).read_text(encoding="utf-8")
    if "\\documentclass" in src and "\\opening" not in src:
        out.append(finding(MECH, "Template residue and names", None,
                           "no \\opening: the letterhead, date and To: line may not print"))
    if len(paras) == 1 and words > 200:
        out.append(finding(MECH, "Template residue and names", paras[0][0],
                           f"the whole letter is one paragraph ({words} words): blank lines "
                           "missing?"))

    # Level 1: paragraph one, rank
    if paras:
        no, p1, _ = paras[0]
        for rx, kind in ((HEDGE_RX, "hedge"), (NEG_RX, "negative")):
            for m in rx.finditer(p1):
                out.append(finding(1, "The first paragraph carries the verdict", no,
                                   f"{kind} in the first paragraph ('{m.group(0)}')", p1))
        if not RANK_RX.search(p1) and not STANDOUT_RX.search(p1):
            out.append(finding(1, "The first paragraph carries the verdict", no,
                               "no verdict or rank language in the first paragraph", p1))
    rank_sents = [(no, s) for no, s in sents
                  if RANK_RX.search(s) and STANDOUT_RX.search(s) and cand_rx.search(s)]
    if not rank_sents:
        out.append(finding(1, "A rank is believed only when it is rationed and reproducible",
                           None, "no rank or comparative claim anywhere in the letter"))
    for no, s in rank_sents:
        if HIRE_RX.search(s):
            continue  # a tier statement ("I would hire him") is the calibration itself
        missing = [n for n, rx in (("pool size", POOL_RX), ("time window", WINDOW_RX))
                   if not rx.search(s)]
        if missing:
            out.append(finding(1, "A rank is believed only when it is rationed and reproducible",
                               no, "rank sentence without " + " or ".join(missing), s))
        if HEDGE_RX.search(s) or re.search(r"\b(one of the better|among the better)\b", s, re.I):
            out.append(finding(1, "A rank is believed only when it is rationed and reproducible",
                               no, "hedged rank", s))

    # Level 2: papers without venue or status
    for i, (no, s) in enumerate(sents):
        # "these papers" may lean on venues named in the sentence before, in the same paragraph
        # ... or in the sentence after; hypothetical papers ("could have led to papers") have none
        prev = sents[i - 1][1] if i else ""
        nxt = sents[i + 1][1] if i + 1 < len(sents) else ""
        hypothetical = re.search(r"\b(could|would|might) have\b", s, re.I)
        if (PAPER_RX.search(s) and not hypothetical
                and not any(VENUE_RX.search(x) for x in (s, prev, nxt))):
            out.append(finding(2, "Describe the research, and translate its currency", no,
                               "papers mentioned without venue or status", s))

    # Level 3: hedges, negatives, faint praise as top descriptor
    for no, s in sents:
        if not cand_rx.search(s):
            continue
        for rx, kind in ((HEDGE_RX, "hedge"), (NEG_RX, "negative or doubt raiser")):
            for m in rx.finditer(s):
                # A hedge counts when it qualifies the candidate: the candidate is named in the
                # words just before it, or the sentence is about potential. Spares "who might
                # need a paper's results".
                near = " ".join(s[:m.start()].split()[-6:] + s[m.end():].split()[:4])
                if kind == "hedge" and not cand_rx.search(near) and not POTENTIAL_RX.search(s):
                    continue
                out.append(finding(3, "No hedges; at most one real limitation", no,
                                   f"{kind} ('{m.group(0)}') in a sentence about the candidate", s))
    if not STANDOUT_RX.search(text):
        faint = sorted({m.group(0).lower() for m in FAINT_RX.finditer(text)})
        if faint:
            out.append(finding(3, "No hedges; at most one real limitation", None,
                               "strongest descriptors are faint praise: " + ", ".join(faint)))

    # Level 1 (fairness, advisory): personal life, stereotypes, word balance
    for no, s in sents:
        for rx, kind in ((PERSONAL_RX, "personal-life detail"), (STEREO_RX, "stereotype")):
            m = rx.search(s)
            if m:
                out.append(finding(1, "Swap the candidate, not the words", no,
                                   f"{kind} ('{m.group(0)}'): does it bear on the role?", s))
    low = text.lower()
    counts = {name: _count(lst, low)
              for name, lst in (("grindstone", GRINDSTONE), ("ability", ABILITY),
                                ("communal", COMMUNAL))}
    advisory = {"words": words, "paragraphs": len(paras), **counts}
    if counts["ability"] == 0:
        out.append(finding(1, "Swap the candidate, not the words", None,
                           "advisory: no ability or originality word; is ability described "
                           "only through effort or results?"))
    if counts["grindstone"] > counts["ability"]:
        out.append(finding(1, "Swap the candidate, not the words", None,
                           f"advisory: effort words ({counts['grindstone']}) outnumber ability "
                           f"words ({counts['ability']})"))

    # The one-minute read shows what the reader sees, so expand the template's macros.
    first = paras[0][1] if paras else ""
    recipient = re.search(r"\\recipient\{([^{}]*)\}", src)
    for macro, value in (("\\recto", recipient.group(1) if recipient else None),
                         ("\\fname", names[0] if names else None),
                         ("\\lname", names[1] if len(names) > 1 else None)):
        if value:
            first = first.replace(macro, value)
    return {"file": str(path), "stats": advisory, "first_paragraph": first,
            "findings": sorted(out, key=lambda f: (f["level"], f["line"] or 0))}


def render(report):
    s = report["stats"]
    lines = [f"{report['file']}: {s['words']} words, {s['paragraphs']} paragraphs "
             f"(advisory counts: effort {s['grindstone']}, ability {s['ability']}, "
             f"caring {s['communal']})", "",
             "One-minute read, first paragraph:", "  " + report["first_paragraph"][:600], ""]
    level = None
    for f in report["findings"]:
        if f["level"] != level:
            level = f["level"]
            lines.append("Mechanical (fix without asking)" if level == MECH else f"Level {level}")
        where = f"line {f['line']}" if f["line"] else "letter"
        lines.append(f"  [{where}] {f['what']}  -> {f['entry']}")
        if f["quote"]:
            lines.append(f"      \"{f['quote']}\"")
    if not report["findings"]:
        lines.append("No mechanical findings. Judgement levels still need a read.")
    return "\n".join(lines)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # the Windows console garbles curly quotes
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("letter")
    ap.add_argument("--cap-words", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rep = check(a.letter, a.cap_words)
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else render(rep))


if __name__ == "__main__":
    sys.exit(main())
