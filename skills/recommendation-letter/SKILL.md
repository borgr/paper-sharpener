---
name: recommendation-letter
description: >
  Write, revise or retarget recommendation and evaluation letters — PhD and MSc admission,
  fellowships (industry, Rhodes, Marshall, NSF GRFP, Israeli calls such as Rothschild, Azrieli,
  Clore, Zuckerman), postdoc and faculty jobs, tenure and external review. Works top-down: genre
  and call, then the verdict and its calibration, then evidence, then selection, then sentences,
  and explains each finding so the writer learns the principle. Trigger on "recommendation
  letter", "reference letter", "letter for my student", "improve this letter", "write a letter
  for", "tenure letter", "external review letter", or a .tex letter on a letterhead template.
---

# Recommendation Letter Skill

A letter is read twice: a one-minute first pass that decides whether there is a second, and a
close second read that notes what was said and what was not. Praise is inflated almost
everywhere, so praise alone carries little. What carries the signal is a calibrated verdict,
evidence only the writer has, and the writer's own calibration. Everything this skill does
serves those three things. The reasons, with sources, are in `references/letter-guide.md`
(*The model underneath*).

## References

```
references/letter-guide.md   the tips: defect, cue, repair, boundary, why. Read by entry.
references/letter-types.md   what each genre and call expects. Read the section in hand.
references/sources.md        the evidence behind each tip, with how far it was verified.
references/writing-guide.md  the shared paper guide (symlink); sentence and word level only.
references/model-habits.md   this model's own failure modes; check every suggestion against it.
tools/letter_check.py        what a regex can settle: hedges, rank sentence, residue, length.
```

Read entries as findings need them; do not read the guides end to end. If `writing-guide.md`
holds only a path (a checkout without symlink support), read
`../paper-review/references/writing-guide.md` instead.

## Memory

Two files under `~/.claude/recommendation-letter/`, the writer's own and never inside a letter
or skill repository, since they span every letter the writer writes:

- **`writer.local.md`** — the writer's profile:
  - comparison pools (who, how many, at what level, since when, where some went);
  - the "about the writer" text they use;
  - LaTeX conventions (template, candidate macros such as `\fname`);
  - standing preferences (e.g. whether to bold the rank sentence).
- **`ledger.local.md`** — the rank ledger: one line per letter with a pseudonym, the
  date, the call, the rank sentence given. Used to warn when the same top rank goes to several
  candidates in a cycle, and to keep a candidate's rank the same across calls.

**Never store candidate personal data in memory** — no names, grades, or the brag sheet. Letters
stay in the writer's own files. If the writer pastes identifiable records, say what will and will
not be kept.

At the start of a session, read both files if they exist. If the profile is missing, offer to
build it (Step 1 of *Draft*); do not block a quick revision on it.

## Modes

Decide the mode from the request:

| Request | Mode |
|---|---|
| "improve / check / review this letter", a draft is given | **Revise** |
| "write a letter for X", notes or a brag sheet are given | **Draft** |
| "adapt this letter for [call]" | **Retarget** |
| "should I write this?", "I don't know them well" | **Scope** |

A single sentence or paragraph is a **quick fix**: cite the entry, propose the rewrite, done.

---

## Revise

### Step 0 — Genre and call

If the letter lives in a synced repository (an Overleaf git clone), pull before reading and again
before writing back: the writer often edits it in the browser between turns.

Ask, unless already clear: what genre (`letter-types.md` Contents), for what call, read by whom
(field, country), and the writer's relation to the candidate (advisor, prospective advisor,
co-mentor, collaborator). Ask for the call text or the referee form if there is one, and note its
cap for this session. When a read-only review is wanted, say so and skip the pulls and writes.

**Read the template before the letter.** Classes differ: find where the candidate's names come
from (`\candidate{}{}` or `\newcommand{\fname}`), where the recipient is (`\recipient`, or a "To:"
line tucked into another field), what the letterhead fields say (`\name`, `\position`, `\email`),
and whether the body uses `\opening`. Check that the candidate macros name *this* candidate; a
copied letter often keeps the previous one. Read commented-out passages too: they are the
writer's own drafts and evidence.

**A reused letter goes stale.** If the letter was written for an earlier cycle or another
candidate, check what has changed since: the writer's title, email and counts against the writer
profile, the candidate's papers (a "submission" that is now accepted, a venue or year that was
wrong), and the program's name.

### Step 1 — Mechanical pass

Run the checker on the letter:

```bash
python3 tools/letter_check.py path/to/main.tex [--cap-words N]   # `py` on Windows
```

Pass `--cap-words` only when the call sets a cap. The output feeds the levels below and decides
nothing on its own; its advisory counts are prompts, not findings.

Then **draft all the findings** (Step 3) for yourself before sweeping, because the sweep needs to
know which sentences they will rewrite.

### Step 2 — Mechanical batch (no permission needed)

Mechanical problems never lead the findings: they cost the writer nothing to fix and change
little for the reader, and a writer who meets them first stops trusting the order. Fix them
directly and **list what changed** in one block ("Fixed without asking: 6 — 'recieved' →
'received'; literal 'Noa' → `\fname{}` ×4 …"). No explanation, no asking.

- **Template mechanics:** leftover template or placeholder text, the literal name beside the
  candidate macro, a recipient or program name that is plainly wrong when the right one is known.
- **Typos, grammar, spelling, punctuation.**
- **When a mechanical fix needs a fact** (the addressee, the program's name, a cap), ask for it
  in one short block of questions *before* the findings, not as a finding.

- **Only sentences no Level 0–1 finding will rewrite.** Those are swept after the finding is
  settled (Step 4), so no polish is done twice. Lower-level findings rarely delete a sentence, so
  their sentences are swept now.
- **A fix that exposes another problem waits.** Adding a missing `\opening`, for example, prints a
  "To:" line that may be stale. List the dependency in the question block and ask first.
- **Grammar, not rewording.** Fix agreement, articles, prepositions, tense, spelling. Anything
  that rephrases (an awkward non-native idiom, a long sentence) is a Level 5 finding with its
  own What and Why, since the voice is the writer's.
- **Never sweep** venues, technical terms, anything that changes a claim's strength, or a
  deleted passage that held content (say what it held, as a finding at its level).

### Step 3 — Findings, most important first

Order findings by **what they change for the reader**, which is the order of the levels below. A
fix at a higher level rewrites what lies under it, so **stop reporting at the highest level that
has findings**, finish that level with the writer, then descend. Within a level, lead with the
finding whose fix changes the committee's decision most, not the one that appears first in the
letter.

**Facts to confirm come first, at any level.** A wrong or stale fact (a venue or year the sources
contradict, a submission that is now accepted, an author position the letter misstates, a stale
writer title or count) goes in a short block above the findings, with the source, whatever level
its finding sits at. A factual error that ships is worse than any wording.

**Previews.** After the current level's findings, list the lower levels' findings one line each
when the writer asks for the whole picture, or in a read-only review. The full block for each
comes when its level is reached.

Level 0 holds only problems that change what the letter *is*: the wrong genre stance, a call
rule that would get it discarded or unread (over a hard cap, a referee question left
unanswered). Names, addressees and template text are Step 2, never Level 0.

| Level | Asks | Entries |
|---|---|---|
| 0 Genre and call | Right stance? A hard call rule broken? | *Know which genre…*, *Obey the call…* |
| 1 Verdict and calibration | Does paragraph 1 carry the verdict? Is the rank rationed and reproducible? Does the writer paragraph calibrate? Would the verdict survive the swap test? | *The first paragraph…*, *A rank is believed…*, *Your credentials calibrate…*, *Swap the candidate…* |
| 2 Evidence | Do the claims the reader acts on have stories only the writer could tell? Is the research described and translated? Is anything the genre expects missing? | *A claim the reader acts on…*, *Describe the research…*, *Say what the file cannot*, *The close reader…* |
| 3 Selection | Weak claims diluting strong ones? Hedges, negatives, faint praise? Tailoring real? Length earned? | *Cut claims, not evidence*, *No hedges…*, *Tailor the evidence…*, *Length follows evidence* |
| 4 Voice | All claims traceable? Generic paragraphs? Culture calibration? | *Keep the letter yours*, *Explicit for American readers…* |
| 5 Sentences | Shared guide, entries listed in `letter-guide.md` §5 | `writing-guide.md` |

Run the **one-minute read** for Level 1 literally: read only the first paragraph and say what a
committee member would take away. Run the **close read** for Level 2 against the genre's
expected items in `letter-types.md`.

**Group findings that land on one passage.** When several findings, of any level, touch the same
paragraph, present them as one unit led by the highest-level one: one points list, one
Before/After that applies them together, and a line per finding saying what it changed and why.
Separate Afters for one paragraph force the writer to merge them by hand. Number the changes
inside a group (3a, 3b…) so each can still be accepted or rejected on its own, which keeps *one
issue per edit*. A sentence that moves belongs to the group of the passage it moves into.

**Budget:** at most five findings per level per round. If there are more, give the five that
change the most for the reader and say how many remain.

**No ledger yet?** The check that a top rank was not given to others this cycle cannot run
from memory. Ask the writer which ranks they gave recently, and offer to start the ledger.

### Finding format

Every finding teaches. Use this block:

```
### [N]/[total in this level] — [short label]       Level [0–5]

**Where:** `main.tex:42` (or `main.tex:28–31`, or "whole letter") — "quoted span"
**What:** the defect in this letter, in one or two sentences.
**Why:** what it does to the reader, with the principle — *Entry name* (letter-guide) and the
  evidence in a clause ("one hedged sentence lowered rated competence in an experiment with
  305 professors [madera2019]").
**Suggestion:**
  - Before: …
  - After: … (or "pending your answer" when the fix needs a fact only you have)
**Needs from you:** (only when the fix needs a fact only the writer has — a pool size, a story,
  a judgement) the exact question.
```

**Look up before asking.** Public facts are yours to find, not the writer's: the candidate's
papers, author positions, venues and acceptance status (the arXiv API,
`export.arxiv.org/api/query?search_query=au:"First+Last"`, then each abstract page; filter out
namesakes by field), repository stars and forks (`gh search repos`), a call's rules. Put what you
found, with its source, into the Suggestion, and ask only for what remains.

Name the entry by its heading so the writer can look it up. Quote figures only from rows marked
*verified* in `sources.md`.

### Step 4 — Triage and apply

The writer accepts, rejects, modifies, or answers the question. Apply accepted edits directly in
the file (author mode); the writer reviews the diff. Keep a running tally ("3/7 done; next: …").
After the last structural change, run the surface sweep once more, since rewrites introduce new
typos.

**Rules for rewriting**
- **Edit, don't regenerate.** Start from the writer's sentences and change only what the finding
  names. The writer's points survive every edit; an aside that reads as a hedge may carry a
  stance, so restate the stance rather than cut it. Rewrite a whole passage only when asked.
- **Check every suggestion against `references/model-habits.md` before showing it.** That file
  lists this model's own failure modes (regenerating, embellishing facts, prose tics), kept apart
  from the guide because they are not writing advice.
- **Never change a claim's strength silently.** Removing a hedge makes the claim stronger and
  adding one makes it weaker; both belong to the writer. Propose, explain, and let them decide.
- **Never invent content.** No story, number, venue, rank or limitation the writer did not
  supply. Where one is needed, ask for it (*Needs from you*).
- **Keep the writer's voice.** Edit for clarity and calibration, not register. Do not push the
  tone toward effusiveness.
- **One issue per edit**, so each can be accepted on its own.
- **Respect the template.** Use the letter's macros (`\fname`, `\lname`, `\recto`) and check
  what they expand to in context (`\recto` is the recipient line, not the program's name). Text
  the writer wrote outside the body (an "about the writer" note, a signature block) is part of
  the letter: read it and review it like the body. Files shared by several letters (the class,
  an included settings file) are proposed as findings, never edited silently.

### Step 5 — Close

If a TeX compiler is available, compile and look at page 1 as an image before reporting (without
one, read the class file to see what the macros print). Macros
expand into sentences nobody wrote ("recommend her to the PhD Admissions Committee as a PhD
student"), and notes, headers and page breaks only show in the output. Compare the page count
with the version before your edits: an edit that pushes the signature block onto a page of its
own needs a tighter wording, not a new page.

Report what changed by level, what was deferred, and, if a rank was given, offer to record it in
the ledger. Offer the next level down if findings remain there.

---

## Draft

1. **Writer profile.** If missing, ask once for the comparison pools and the "about the writer"
   text; store them in `~/.claude/recommendation-letter/writer.local.md`.
2. **Intake.** Genre, call text and cap, reader (field, country), deadline, the candidate's
   materials (CV, statement, the call) and the writer's own notes. Use the candidate's
   materials as **evidence**, never as prose; if the writer has a student-drafted letter, treat
   it the same way.
3. **Evidence inventory.** Before drafting, list with the writer:
   - the verdict and the rank, with pool and size (or the decision to give none);
   - the two or three claims the reader will act on, each with its story or calibrating number;
   - the one or two key works, with venue, status, convention and the candidate's role;
   - the genre's expected items from `letter-types.md`, and which the writer cannot assess;
   - at most one real limitation, for a junior candidate, if the writer wants one.
   A claim without evidence does not enter the draft; ask for the evidence or drop the claim.
4. **Draft** into the writer's template, in the order: relationship and verdict; evidence
   paragraphs; the one tailored paragraph for the call; the limitation if any; the closing
   verdict. Use the writer's own phrases from the inventory.
5. **Revise the draft** with the Revise steps, from Level 0. Model drafts carry their own bias
   and genericness; *Swap the candidate, not the words* and *Keep the letter yours* are not
   optional here.

## Retarget

Take the existing letter and the new call. Keep the relationship, the stories and **the rank**.
Rewrite the one tailored paragraph so its evidence answers the new call's criteria, fix
addressee, cap and format, then run Level 0 and the close read against the new genre's expected
items. Check the ledger: the rank must match.

## Scope

When the writer doubts whether to write: do not default to declining. Help them choose and word
one of:
- a full letter, if they can rank and tell stories;
- a short, honest letter about what they saw, saying its scope, with no hedges and no rank — and
  a note to the candidate that a writer who knows their research would help more;
- a decline, only when the letter would have to say something negative or the writer cannot
  vouch for the basics, with a suggestion of who could write instead.

Flag when the candidate may have few other writers (first-generation, small institution,
international): a short honest letter usually serves them better than none.

---

## General principles

- **Highest level first, and stop there.** Polishing a sentence that a Level 1 rewrite deletes
  is work done twice.
- **Teach.** Every finding names its entry and its reason. The writer's second letter should need
  fewer findings than the first.
- **Calibration over enthusiasm.** The goal is a letter the reader believes, not a louder one.
- **Bias checks are prompts, not verdicts.** Never report "no bias found".
