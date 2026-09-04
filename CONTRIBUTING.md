# Contributing

Contributions are welcome, and the writing guide in particular is meant to keep growing.

One fact decides most of what follows. Everything in this repository is read by an agent and
never by a person. The human-facing version of these tips is the
[community guide](https://docs.google.com/document/d/14Wax8M5w8F_8miDlYJ9-I6wqpelxlXjCEUbkNzNMqqE/edit?usp=sharing),
and `skills/paper-review/references/writing-guide.md` is its port for a model that has to act on
each entry. Good advice that a model cannot execute belongs in the Doc and not here.

## What an entry needs

Three parts, in this order. The middle one is the one usually missing.

- **The defect.** What is wrong with the text, stated so it can be recognized in someone else's
  draft.
- **The cue.** How to find it. A count, a sorted list, a pass that reads only the sentence
  openers, a comparison between two places in the paper. Something with a yes-or-no answer.
- **The repair.** What to do instead, and where the fix belongs when it is not in the sentence
  that showed the symptom.

## Detectors cite principles

The guide holds the reasons and the `SKILL.md` files hold the looking. A new check in a skill
names the guide entry that supplies its reason, so the finding reaches the author as a principle
rather than as a raw count. When no entry fits, the guide is missing one, and writing that entry
is the contribution. Cite by the entry's full heading so that searching for the name finds it.

## What does not belong

- **A check only a human can run.** Reading a draft aloud is sound advice and it is deliberately
  absent, because the reader of this file has no ear. The same goes for glancing at a figure for
  a second, or noticing your own fatigue. Where a perception test is the real check, restate it
  as something inspectable. The graph checklist asks which element is largest, highest-contrast
  or most central, which is the same question a glance answers.
- **Metaprose.** Notes on how the guide is organized, how it grew, or how to edit it. Those go
  in this file.
- **A rule without its boundary.** A model applies every rule to every sentence that matches, so
  a rule that holds most of the time needs the exception in the same entry. *Reach for the most
  specific word* would turn a two-point drop into a plummet without the clause saying the word
  has to be true of the size of the effect. *Say what is* would invent a cause the draft never
  measured without the clause sending the negation back untouched. If you know where your rule
  stops, write that down. It is the half that keeps the guide from damaging papers.
- **Motivation and anecdote.** An entry that has grown past defect, cue and repair gets trimmed
  back to them. The sources at the end of the guide carry the argument for anyone who wants it.
- **A second entry for a rule that already exists.** Extend the entry that owns the rule and
  cross-reference it.
- **Reviewer-facing wording.** The guide addresses the writer working on their own draft. An
  entry that tells someone to flag what the author did has drifted into the reviewer's seat.

## Where things live

```
skills/paper-review/SKILL.md                    the review process
skills/paper-review/references/writing-guide.md the tips, and the only copy
skills/paper-review/references/reviewer-personas.md
skills/writing-assistant/SKILL.md               the lightweight interactive pass
skills/writing-assistant/references/            symlink to the paper-review references
```

The guide is one file. `skills/writing-assistant/references/writing-guide.md` is a symlink to it,
so editing either path changes both skills. A single skill directory copied out of the repo needs
that symlink resolved or the copy has no guide.

## Before opening a PR

- Every cross-reference resolves to a heading that exists, spelled the way the heading spells it.
- A new `###` subsection appears in the guide's Contents table, in the order it appears in the
  file.
- A new check in a skill names the guide entry it draws its reason from.
- You ran the change on a real paragraph and it found something you agree with.
- Nothing you added asks the reader to hear, glance, or feel.
