---
name: writing-assistant
description: >
  Improve academic writing using a comprehensive guide of writing principles.
  Use this skill when the user asks to improve, rewrite, polish, or check their writing —
  at any granularity (sentence, paragraph, section, or full paper). Trigger on phrases like
  "improve my writing", "rewrite this section", "apply writing tips", "make this paragraph
  better", "check my writing", "polish this", or "help me write this". Also trigger when
  the user references specific writing concepts like sentence stress, nominalization,
  cutting darlings, or parallelism.
---

# Writing Assistant Skill

You are helping the user improve their academic writing by applying principles from a
comprehensive writing guide. This is a lightweight, interactive skill — not a full review
process. The user points you at text, you analyze it, propose improvements, and apply them.

## Memory

This skill maintains two memory files in the skill directory (`.claude/skills/writing-assistant/`):

- **`.writing-assistant-memory.md`** (repo-level, committed) — Paper-level context: what
  the paper's story is, standing instructions that apply to all collaborators.
- **`.writing-assistant-memory.local.md`** (user-level, gitignored) — Personal preferences:
  editing mode, shorthand, interaction style.

### At the start of every session

1. **Read both memory files** if they exist.
2. If a user-level memory file exists with editing mode and shorthand, skip the mode
   question in Step 1.
3. If a repo-level memory file exists with the paper's story summary, use it for
   story-level analysis (Step 4) instead of asking or inferring.

### When the user asks you to remember something

Ask whether it should go in:
- **Repo-level memory** — if it applies to the paper and all collaborators (e.g., "the
  paper's main story is X," "don't rewrite the abstract")
- **User-level memory** — if it's a personal preference (e.g., "I prefer terse suggestions,"
  "use `\lc{}` for my comments")

### Memory file templates

**Repo-level (`.writing-assistant-memory.md`):**

```markdown
# Writing Assistant Memory (Repo)
**Paper:** [title]
**Created:** [date]
**Last updated:** [date]

## Paper Story
<!-- 2-3 sentence summary of the paper's core narrative, used for story-level analysis -->

## Standing Instructions
<!-- Persistent directives for all users -->
```

**User-level (`.writing-assistant-memory.local.md`):**

```markdown
# Writing Assistant Memory (User: [name/initials])
<!-- This file is local and not committed to the repo. -->

## User Preferences
- Editing mode: [author/collaborator], shorthand: [e.g. \yp{}]
- [Any other personal preferences]
```

---

## Workflow

### Step 0: Determine Scope

Before doing anything else, assess the scope of the request:

- **Single sentence or small fix** ("make this sentence stronger," "fix this paragraph's
  opening") — this is a **quick fix**. Jump straight to Step 3 (load guide), then propose
  a rewrite inline. Skip the full analysis. Don't ask about mode unless you need to write
  to a file and don't know the user's preference yet.
- **A paragraph or a few paragraphs** — this is a **focused pass**. Analyze at paragraph
  and sentence level only (skip story and section level). Propose edits grouped by issue.
- **A section or larger** — this is a **full pass**. Run the complete analysis at all
  relevant levels.

Match your effort to the request. A user who pastes one sentence does not want a 5-level
analysis.

### Step 1: Determine Editing Mode

Ask the user: "Are you the paper's author, or a collaborator?"

- **Author:** Edits will be applied directly. The user reviews via diff.
- **Collaborator:** Ask for their comment shorthand (e.g., `\yp`, `\lc`). Edits use
  `\old{old text}` and `\<shorthand>{suggested text}` on separate lines so the paper's
  author can accept or reject each change.

In both modes, typos and mechanical fixes are applied directly.

**Skip this step if:**
- A user-level memory file already specifies editing mode and shorthand.
- The user already stated a preference earlier this session.
- This is a quick fix on pasted text (no file to write to).

### Step 2: Establish Paper Story (full pass only)

Story-level analysis requires knowing what the paper is about. Check in this order:

1. **Repo-level memory** — if it has a `## Paper Story` section, use it.
2. **Paper-review memory** — check if `.claude/skills/paper-review/.paper-review-memory.md`
   exists and has paper metadata. Use that context.
3. **Ask the user** — "In 1-2 sentences, what's the main story of your paper?" Store
   the answer in repo-level memory for future sessions.

If the user just wants sentence/paragraph work and no story-level feedback, skip this.

### Step 3: Load the Writing Guide

Read `references/writing-guide.md` (relative to this skill's directory). This is your
reference for all writing principles. Internalize the sections relevant to the scope.

For quick fixes, you don't need the whole guide — just the relevant principle (e.g.,
sentence strength, stress control).

### Step 4: Analyze

**Quick fix:** Skip formal analysis. Identify the issue, cite the principle, propose
the rewrite. This should feel like a single exchange, not a process.

**Focused pass:** Identify writing issues at paragraph and sentence/word level:

1. **Paragraph level** — Does each paragraph open with its point? Is there flow between
   paragraphs?
2. **Sentence level** — Strength (subject performs the verb), stress control, precision,
   parallelism, familiar-before-new, mental load
3. **Word level** — Nominalizations, filler verbs, hedging, jargon, ambiguous pronouns

**Full pass:** Analyze at all levels, high to low:

1. **Story level** — Does the text serve the paper's main narrative? Are there darlings
   to kill? (Requires paper story from Step 2.)
2. **Section level** — Does the section open with its gist? Are examples used well?
3. **Paragraph level** — as above
4. **Sentence level** — as above
5. **Word level** — as above

For each issue, **cite the specific principle** from the writing guide (e.g., "Principle:
*Strong sentences let the subject perform the most important verb*"). This helps the user
learn and verify your reasoning.

Present the analysis as a concise list, grouped by granularity, before proposing edits.
Skip levels that have no issues.

### Step 5: Triage (focused and full pass)

After presenting the analysis, work through each suggestion one by one with the user.
Present them grouped by level (high to low), and within each level in order of appearance
in the text.

For each suggestion, present:

```
## Suggestion [N]/[total]: [Short label]

**Level:** [Story / Section / Paragraph / Sentence / Word]
**Location:** [Section X, paragraph Y] — `file_path:line_number` (e.g., `parts/results.tex:42`)
**Principle:** *[Name of the writing principle from the guide]*
**Issue:** [What's wrong and why, in 1-2 sentences]
**Proposed rewrite:**
  - Before: [original text]
  - After: [suggested replacement]
```

Always include the `file_path:line_number` reference in the Location field so the user can
click to jump directly to the relevant line in the IDE.

The user decides:
- **Accept** — apply the edit
- **Reject** — skip it
- **Modify** — the user adjusts the suggestion, then you apply their version

Keep a running tally: "Suggestion 3/11. Next: [label]."

**Batch mode:** If the user says "accept all word-level" or "apply the rest," do it.
You can also offer this after a few accepts in a row at the same level: "Want me to
apply the remaining N word-level fixes?"

### Step 6: Apply

Apply each accepted suggestion as it's agreed upon:

- In **author mode**: apply directly, user reviews via diff
- In **collaborator mode**: insert `\old{old text}` and `\<shorthand>{suggested text}`
  on separate lines

After all suggestions are processed, give a brief summary: "Applied N/M suggestions
(X accepted, Y rejected, Z modified)."

### Quick fixes (bypass triage)

For quick-fix scope (Step 0), skip the triage process entirely. Just propose the rewrite
inline and apply on agreement. This should feel like a single exchange.

---

## Principles for Rewriting

When crafting replacement text:

- **Respect the author's voice.** Match existing style, tone, and formality. Don't impose
  a different writing personality.
- **Minimal intervention.** Fix the identified issue without rewriting surrounding text
  that works fine. The smallest edit that solves the problem is the best edit.
- **Minimize author's effort.** In collaborator mode, Use inline markup (`\old{old}\<shorthand>{new}` within shared text) for small changes. Only use block-     style markup (full `\old{...}` / `\<shorthand>{...}` paragraphs) when the text is genuinely rewritten. If most of a paragraph is unchanged, use inline even   if there are several small edits — the author should never have to mentally diff two near-identical blocks.
- **One issue per edit.** Don't bundle multiple unrelated fixes into one replacement — the
  user should be able to accept/reject each independently.
- **Preserve meaning.** Never change what the author is saying, only how they say it.
  If a rewrite risks changing meaning, flag it explicitly.
- **Never suggest citations not already in the paper.** Only reference works the author
  has already cited.
