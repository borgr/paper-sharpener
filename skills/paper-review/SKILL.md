---
name: paper-review
description: >
  Simulate a multi-reviewer academic paper review process and produce actionable revision plans.
  Use this skill whenever the user wants feedback on an academic paper, research manuscript,
  conference submission, or draft — especially for venues like NeurIPS, ACL, ICML, EMNLP, ICLR,
  AAAI, or any CS conference/journal. Trigger when the user says things like "review my paper",
  "give me feedback on my draft", "simulate reviewers", "help me improve my paper",
  "what would reviewers say", "prepare for submission", or provides a PDF/tex and asks for
  critique. Also trigger when the user references improving a manuscript, addressing reviewer
  comments, or iterating on a draft. This skill orchestrates the full loop: reading the paper,
  generating reviews, triaging action items interactively, and applying edits.
---

# Paper Review Skill

You are orchestrating a structured academic paper review and revision process. The goal is to
produce **useful, actionable feedback** that helps the author improve the paper — regardless of
whether the paper is currently strong or weak. This is not about predicting acceptance; it's
about finding every real problem and fixing it efficiently.

## Overview

The process has five phases:
0. **Memory** — Load (or initialize) the review memory files for this paper
1. **Read** — Thoroughly read and understand the paper, establish project structure
2. **Review** — Generate three independent reviews via parallel subagents
3. **Triage** — Synthesize action items, surface consensus, and let the user decide what to act on
4. **Revise** — For each accepted action item, propose a concrete fix, get agreement, then apply the edit

Each phase is described in detail below. Move through them sequentially. Do not skip ahead.

---

## Phase 0: Review Memory

This skill maintains two memory files in the skill directory (`.claude/skills/paper-review/`):

- **`.paper-review-memory.md`** (repo-level) — Committed to git, shared with all
  collaborators. Contains paper metadata, author conventions, standing instructions for the
  paper, rejected items, and deferred items. Any collaborator benefits from knowing what's
  already been decided.
- **`.paper-review-memory.local.md`** (user-level) — Gitignored, local to each collaborator.
  Contains personal preferences: editing mode, shorthand command, tone preferences, and any
  user-specific instructions. Each collaborator has their own.

### At the start of every session

1. **Read `.paper-review-memory.md`** (repo-level) if it exists. It contains prior decisions
   that must be respected:
   - Items the author previously **rejected** should not be re-raised unless the paper has
     changed in a way that makes them relevant again. If you believe a previously rejected
     item is now worth revisiting (e.g., the author added a new section that reintroduces
     the same problem), you may raise it, but explicitly flag it: "You previously rejected
     this, but the new Section X may warrant reconsidering."
   - Items the author previously **deferred** should be re-surfaced, explicitly marked as
     "previously deferred" so the author knows this isn't a new issue.
   - **Author conventions** (intentional spelling, notation, style choices) must be respected
     by all three reviewers. Do not flag as issues things the author has already declared
     intentional.
   - **Standing instructions** override default review behavior (e.g., "don't flag passive
     voice in methods sections").
2. **Read `.paper-review-memory.local.md`** (user-level) if it exists. It contains the
   current user's preferences (editing mode, shorthand, tone). If it specifies an editing
   mode and shorthand, skip the editing mode question in Step 1.3.
3. **If the repo-level file doesn't exist**, create it after Phase 1 completes (once you
   know the paper title and root directory) using the template below.
4. **If the user-level file doesn't exist**, create it after the user answers the editing
   mode question in Step 1.3, using the template below.

### What gets written to memory (and when)

Update memory files as decisions are made during the session — don't wait until the end.
This way, if a session is interrupted, nothing is lost.

**Repo-level memory (`.paper-review-memory.md`):**
- **When the user rejects an item in triage:** Add it under `## Rejected Items` with the
  item label, a brief reason if the user gave one, and the date.
- **When the user defers an item:** Add it under `## Deferred Items` with the item label
  and date.
- **When the user states a convention or preference:** Add it under `## Author Conventions`.
  This includes things like "X is not a typo", "I prefer Y notation over Z", "don't touch
  the abstract until the experiments section is final", etc.
- **When the user gives a standing instruction about the paper:** Add it under
  `## Standing Instructions`.
- **When a deferred item is later accepted or rejected:** Move it from `## Deferred Items`
  to the appropriate section.

**User-level memory (`.paper-review-memory.local.md`):**
- **When the user states a personal preference:** editing mode, shorthand, tone, interaction
  style. These go under `## User Preferences`.

### Memory file templates

**Repo-level (`.paper-review-memory.md`):**

```markdown
# Paper Review Memory (Repo)
**Paper:** [title]
**Root directory:** [path]
**Main file:** [filename]
**Created:** [date]
**Last updated:** [date]

## Author Conventions
<!-- Intentional choices that reviewers should not flag -->

## Standing Instructions
<!-- Persistent directives for all future review sessions -->

## Rejected Items
<!-- Items the author chose not to address, with optional reason -->

## Deferred Items
<!-- Items postponed for a future session -->
```

**User-level (`.paper-review-memory.local.md`):**

```markdown
# Paper Review Memory (User: [name/initials])
<!-- This file is local and not committed to the repo. -->

## User Preferences
- Editing mode: [author/collaborator], shorthand: [e.g. \yp{}]
- [Any other personal preferences]
```

### When the user asks you to remember something

If the user says "remember this" or "save this for next time," ask whether it should go in:
- **Repo-level memory** — if it applies to the paper and all collaborators should see it
  (e.g., "don't flag X as an issue," "this notation is intentional")
- **User-level memory** — if it's a personal preference (e.g., "I prefer terse feedback,"
  "use \lc{} for my comments")

### Important: memory is append-friendly, not precious

Memory files are working documents, not polished artifacts. Keep entries short — one or
two lines each. The author may edit them directly between sessions, and that's fine. If
the author deletes something from a memory file, treat that as an intentional reset.

---

## Phase 1: Read the Paper

### Step 1.1: Establish project structure

If this is the first session (no repo-level memory file exists), ask the user to confirm:
- **Root directory** — the top-level directory containing the paper source files
- **Main file** — the entry point (e.g., `main.tex`, `paper.tex`, `paper.md`)

Store both in the repo-level memory file. On subsequent sessions, read them from memory.
If the user has reorganized files, they can update the memory file or tell you the new paths.

Identify all source files that constitute the paper (included `.tex` files, `.bib` files,
figure directories, etc.) so you have the full picture of what can be edited.

### Step 1.2: Read and summarize

Read the full paper carefully. Write a short internal summary (2-3 sentences) of the paper's
core contribution, methodology, and main results. Share this with the user as a sanity check:
"Here's my understanding of the paper — does this capture the key points, or am I missing
something?"

This step matters because a misunderstanding of the paper's contribution will cascade into
bad reviews. Wait for user confirmation before proceeding.

### Step 1.3: Pre-review briefing

Before generating reviews, ask the user:

1. **Target venue** — Where is this being submitted? (e.g., NeurIPS 2026, ACL 2026 main
   conference, TMLR, a workshop, internal draft). This calibrates the review standards:
   - Top-tier conference (NeurIPS, ICML, ACL, ICLR): hold to the highest bar — novelty,
     rigor, and presentation all matter. Reviewers should ask "would this survive a strong
     AC?"
   - Mid-tier or specialized venue: technical correctness and clarity matter most; novelty
     bar is lower, but the paper must clearly serve its audience.
   - Workshop: focus on whether the core idea is interesting and clearly presented. Don't
     penalize for incomplete experiments or missing ablations — these are expected.
   - Journal (TMLR, JMLR, TACL): thoroughness and completeness matter more than flash.
     Reviewers should check for comprehensive related work and solid experimental coverage.
   - Internal draft / not yet decided: review at a top-venue standard but flag which
     concerns are venue-dependent.
2. **Draft stage** — Is this a first draft, camera-ready polish, resubmission, or something
   else? A first draft needs structural feedback; a camera-ready needs surface polish and
   final sanity checks.
3. **Author concerns** — "Is there anything specific you want reviewers to focus on or
   anything you already know is weak?" This avoids wasting review bandwidth on problems
   the author is already aware of and plans to fix independently.
4. **Editing mode** — "Are you the paper's author, or a collaborator?"
   - **Author:** Edits in Phase 4 will be applied directly to the file. The user owns the
     text and can see exactly what changed via diffs. Typos and mechanical fixes are applied
     directly; substantive rewrites are applied directly too (the author reviews via diff).
   - **Collaborator:** Ask for their comment shorthand (e.g., `\yp`, `\lc`, `\jd`). Edits
     in Phase 4 will use `\old{old text}` and `\<shorthand>{suggested text}` on separate
     lines so the author can accept or reject each change. Typos and mechanical fixes are
     still applied directly.

   Store the editing mode and shorthand in the user-level memory file
   (`.paper-review-memory.local.md`). If a user-level memory file already exists and
   specifies an editing mode and shorthand, use that and skip this question.

Store the venue and draft stage in the repo-level memory file under a `## Session Context`
section (overwritten each session — this is ephemeral, not persistent). Pass venue and draft
stage context to all reviewer subagents so their standards are calibrated.

If the user says "just review it" or doesn't want to answer, default to: top-venue standard,
mid-stage draft, no specific concerns, author mode (direct edits).

---

## Phase 2: Generate Reviews

Each review must be generated **independently** to avoid anchoring bias. The biggest failure
mode in simulated reviews is that later reviewers unconsciously adjust to fill gaps left by
earlier ones, producing artificially complementary reviews rather than genuinely independent
perspectives.

### How to generate independent reviews

Spawn **three parallel subagents**, one per reviewer. Each subagent receives the prompt
assembled from the template below. Use the strongest available model for each subagent.
The subagents must not see each other's outputs. Once all three complete, collect the
reviews and present them to the user.

If subagents are not available (e.g., running in Claude.ai), generate the reviews sequentially
but with this critical discipline: **write each review as if you have not written the others.**
Before writing Reviewer 2, do not re-read Reviewer 1's output. Before writing Reviewer 3,
do not re-read Reviewers 1 or 2. This is hard to do perfectly, but being explicit about the
goal helps. If you catch yourself thinking "Reviewer 1 already covered X, so I'll focus on Y"
— that's the anchoring bias. Reviewer 2 should also cover X if it's something they'd notice.

### Subagent prompt template

Each subagent receives exactly this prompt (fill in the bracketed sections). Do not
paraphrase or restructure — the wording has been chosen to minimize common failure modes.

```
You are an academic reviewer for a {venue_type} submission. You must produce a single,
independent review of the paper below. You have NOT seen any other reviews of this paper
and you must NOT speculate about what other reviewers might say.

## Your Persona

{persona_section — copy the relevant section from references/reviewer-personas.md verbatim,
including "Primary focus areas" and "What they tend to skip or underweight"}

## Venue and Draft Context

- Target venue: {venue} ({venue_type}: {venue_calibration_note from Step 1.3})
- Draft stage: {draft_stage}
- Author's stated concerns: {author_concerns or "None specified"}

Calibrate your standards to this venue and stage. A workshop draft does not need the
experimental rigor of a top-conference submission. A camera-ready does not need structural
feedback — focus on polish.

## Author Conventions (respect these — do NOT flag as issues)

{author_conventions from repo-level memory file, or "None declared."}

## Standing Instructions

{standing_instructions from repo-level memory file, or "None."}

## The Paper

{full paper content — all .tex/.md source files concatenated in reading order}

## Your Task

Write a review following this exact structure:

### Summary
[2-3 sentence summary of the paper as YOU understand it]

### Strengths
- [Strength 1]
- [Strength 2]
- ...

### Weaknesses
- [Weakness 1 — cite specific sections/figures/equations. Be concrete.]
- [Weakness 2]
- ...

### Detailed Comments
[Paragraph-form detailed feedback. Reference specific sections, figures, equations,
tables by number. Be constructive — identify the problem AND gesture at what a fix
might look like, but do not prescribe exact wording.]

### Minor Issues
[Bullet list of small things: typos, notation inconsistencies, formatting, missing
references, figure readability, etc.]

## Important

- Be genuinely critical. The purpose is to find real problems before actual reviewers do.
  Even an excellent paper has things to improve.
- Be specific. "The experimental section is weak" is not useful. "Table 3 only compares
  against Baseline-X from 2021; adding Baseline-Y (2023) would strengthen the evaluation"
  is useful.
- Evaluate every figure and table: check caption self-containedness, readability at print
  size, color accessibility, visual-textual consistency, and information density.
- There are no numerical scores. The point is the comments, not a rating.
- Do NOT soften your review. Do NOT add reassuring preambles like "Overall this is a nice
  paper." Start directly with the Summary section.
```

### Review format

Each review must follow this structure:

```
## Reviewer [N]: [Role Label]

### Summary
[2-3 sentence summary of the paper as understood by this reviewer]

### Strengths
- [Strength 1]
- [Strength 2]
- ...

### Weaknesses
- [Weakness 1 — be specific, cite sections/figures/equations]
- [Weakness 2]
- ...

### Detailed Comments
[Paragraph-form detailed feedback. Reference specific sections, figures, equations,
tables by number. Be constructive — identify the problem AND gesture at what a fix
might look like, but do not prescribe exact wording.]

### Minor Issues
[Bullet list of small things: typos, notation inconsistencies, formatting, missing
references, figure readability, etc.]
```

There are no numerical scores. The point is the comments, not a rating.

### Important guidelines for review generation

These guidelines should be included in each subagent's prompt:

- **Be genuinely critical.** The whole point of this process is to find real problems before
  actual reviewers do. Pulling punches defeats the purpose. A reviewer who says "everything
  looks great" is useless — even an excellent paper has things to improve.
- **Be specific.** "The experimental section is weak" is not helpful. "Table 3 only compares
  against Baseline-X from 2021; the user should add Baseline-Y (2023) and Baseline-Z (2024)
  which achieve state-of-the-art on this benchmark" is helpful.
- **Respect memory files.** If the author has declared conventions (e.g., a specific
  spelling is intentional, a notation choice is deliberate), do not flag those as issues.
  If standing instructions exist (e.g., "don't comment on passive voice"), follow them.
- **Evaluate figures and tables deliberately.** Visual elements are often the first thing
  a reviewer looks at and the last thing authors polish. For every figure and table, check:
  - **Self-contained captions:** Can a reader understand the figure from caption alone,
    without reading the main text? Captions should state what is shown, what the axes/columns
    represent, and what the takeaway is.
  - **Readability at print size:** Would this be legible in a single-column PDF at 100%?
    Check font sizes on axis labels, legends, and annotations. Thin lines and small markers
    are common problems.
  - **Color accessibility:** Does the figure rely solely on color to distinguish elements?
    Would it work in grayscale or for a color-blind reader? Suggest patterns, markers, or
    direct labels as alternatives.
  - **Visual-textual consistency:** Does the figure tell the same story as the text that
    references it? If the text says "X consistently outperforms Y" but the figure shows
    mixed results, flag the mismatch.
  - **Information density:** Is the figure earning its space? A figure that shows one
    obvious data point could be a sentence instead. Conversely, a table with 50 rows
    might work better as a figure.
  - **Table formatting:** Are tables properly aligned? Do they use consistent decimal
    precision? Are the best results bolded? Are column headers clear?

---

## Phase 3: Triage

This is the most interactive phase. After presenting the three reviews, you synthesize them
into a structured action item list and work through it with the user.

### Step 3.1: Consensus and conflicts

Before listing action items, surface two things:

**Unanimous issues** — things all three reviewers flagged (possibly in different words).
These are almost certainly real problems. Present them first, clearly labeled:

```
## Unanimous Issues (all reviewers flagged these)

1. **[Label]**: [Brief description]. Raised by all three reviewers.
   - R1 angle: [what the senior reviewer said about it]
   - R2 angle: [what the mid-career reviewer said about it]
   - R3 angle: [what the junior reviewer said about it]
```

**Disagreements** — places where reviewers contradict each other. These reveal genuine
ambiguity in the paper:

```
## Reviewer Disagreements

1. **[Topic]**: Reviewer A thinks [X], while Reviewer B thinks [Y].
   This likely means [interpretation of what's ambiguous in the paper].
```

### Step 3.2: Re-surface deferred items

If the repo-level memory file contains deferred items from a previous session, present them now before
compiling new action items:

```
## Previously Deferred Items

These were deferred in a prior session. Now's a good time to decide on them:
1. **[Label]** (deferred [date]) — [description]
2. ...
```

The user can accept, reject, or defer again. Items accepted here join the relevant tier.
Items rejected here move to `## Rejected Items` in the repo-level memory file.

### Step 3.3: Compile action items

Organize all actionable feedback into three tiers. Each action item gets:
- A short label
- Which reviewer(s) raised it (and whether it's unanimous)
- The specific section/location it applies to, **including a `file_path:line_number` reference**
  (e.g., `parts/results.tex:42`) so the user can click to jump there in the IDE
- A one-sentence description of the issue

#### Cross-cutting groups

Before presenting items tier by tier, identify items that are **logically related or would
conflict if applied independently** — for example, a notation change that ripples through
the whole paper, or a reframing of the contribution that affects the intro, related work,
and conclusion.

Group these under a shared label: "These N items are related and should be addressed
together." A group is presented as a single unit during triage (one accept/reject/defer
decision for the whole group) and handled as a single coordinated edit in Phase 4. Assign
the group to whichever tier its highest-leverage item belongs to.

#### Tier definitions

**Tier 3 — Surface (no-brainers, do first)**
Typos, grammar, formatting, minor reference issues. These are quick and low-risk.

**Tier 2 — Technical (medium leverage)**
These affect methodology clarity, formalization, notation, figure quality, or
presentation of results without changing the paper's core story. Examples: "Equation 4
uses inconsistent notation with Equation 2", "Figure 3 is unreadable at print size",
"The algorithm description in Section 4.2 is ambiguous about step 3".

**Tier 1 — Structural (highest leverage, do last)**
These affect the paper's narrative, framing, contribution claims, experimental design,
or missing content. Examples: "The related work section misses an entire line of work",
"The main claim in Section 3 is not supported by the experiments in Section 5",
"Missing ablation study for component X".

### Step 3.4: Interactive triage

Work through all items one by one, starting with Tier 3 (surface), then Tier 2
(technical), then Tier 1 (structural). Cross-cutting groups are presented as single units.

For each item (or group), the user decides:
- **Accept** — We will address this
- **Reject** — Skip
- **Defer** — Come back to it later

Tier 3 items are still triaged individually, but the expectation is that most will be
quick accepts. If the user is clearly accepting all of them, you can ask: "Want me to
just accept the rest of the surface items?" But don't assume — let them drive.

---

## Phase 4: Revise

Work through all accepted action items in tier order (Tier 3 first, then Tier 2, then
Tier 1).

### Step 4.1: Propose the fix

For the current action item (or group of related items), present:

```
## Action Item: [Label]

**Problem:** [What's wrong, as identified in the reviews]
**Location:** [Section X.Y, paragraph Z / Figure N / Equation M] — `file_path:line_number` (e.g., `parts/results.tex:42`)
**Proposed approach:** [How you think this should be fixed — the strategy, not the exact text.
For example: "Rewrite the opening paragraph of Section 3 to foreground the distinction between
our method and prior work X, making the novelty claim explicit rather than implicit."]
```

Do **not** propose exact replacement text yet. The user needs to agree on the *approach* first.
This avoids wasted effort writing polished prose for a fix the user doesn't want.

For Tier 3 (surface) items, the "proposed approach" can be very brief — often just "Fix the
typo: X → Y" is enough. These should move fast.

### Step 4.2: Get agreement

Wait for the user to agree, modify, or reject the proposed approach. They might say:
- "Yes, go ahead" → proceed to Step 4.3
- "I think the fix should be more like [X]" → revise the approach and re-present
- "Actually skip this one" → move to the next action item

### Step 4.3: Apply the edit

Once the approach is agreed upon, write the actual replacement text and apply it. The
editing mode (determined in Step 1.3) controls how edits are applied:

- **Author mode (direct edits):** Apply the replacement text directly using the appropriate
  editing tool. The author reviews changes via diff.
- **Collaborator mode:** Insert `\old{old text}` and `\<shorthand>{suggested text}` on
  separate lines in the source file, where `<shorthand>` is the collaborator's chosen
  command (e.g., `\yp`, `\lc`). This lets the paper's author accept or reject each change.

In both modes, typos and mechanical fixes (spelling, punctuation, broken LaTeX) are applied
directly without annotation.

**Writing quality:** Before writing replacement text, load `references/writing-guide.md` and
apply relevant writing principles — sentence strength (subject performs the verb), stress
control, precision, minimalism, familiar-before-new ordering, and parallelism. The guide
should inform how you write, not what you write (the "what" was decided in Step 4.2).
Always respect the author's existing voice and tone.

For **grouped cross-cutting items**, apply all related changes in sequence within this single
step, making sure they're consistent with each other. Show a brief summary of all changes made
in the group before moving on.

After applying, show a brief summary of what changed and move to the next action item.

### Progress tracking

As you work through action items, keep a running tally: "Completed 3/7 items. Next: [Label]."
This helps the user know where they are in a potentially long revision session.

---

## Phase 5: Re-review (Spot Check)

After all accepted action items have been applied, do a lightweight verification pass. This
is not a full re-review — it's a targeted check that the revisions actually work.

### Step 5.1: Re-read edited sections

For each section that was modified in Phase 4, re-read the edited version in context (not
just the replacement text — read the surrounding paragraphs too). Check for:

- **Coherence breaks:** Does the new text flow naturally with what comes before and after?
  Edits that are locally correct can still create jarring transitions or redundancies.
- **Internal consistency:** Did a change in one place create a contradiction elsewhere?
  (e.g., changing a claim in the introduction but not updating the conclusion, or updating
  a table without updating the text that references it.)
- **Introduced errors:** Typos, broken LaTeX, dangling references, or formatting issues
  introduced by the edits themselves.

### Step 5.2: Cross-reference check

If any Tier 1 (structural) changes were made, verify that the paper's narrative still holds
end-to-end. Read the abstract, introduction (contributions list), and conclusion together —
do they still tell a consistent story after the revisions?

### Step 5.3: Report

Present a brief report:
- **Clean:** "All edits look consistent, no issues found." (Move on.)
- **Issues found:** List each problem with its location, and offer to fix it. These are
  treated as new micro-items — propose the fix, get agreement, apply.

This phase should be fast. If the revisions were all Tier 3 surface fixes, the spot check
is a quick scan. Only Tier 1/2 changes need careful re-reading.

---

## General principles

- **The user is the author.** You are simulating reviewers and acting as a revision assistant,
  but all decisions about what to change belong to the user. Never unilaterally edit the paper.
- **Anchor to specific locations.** Every piece of feedback should reference a section, figure,
  table, equation, or paragraph number. Vague feedback wastes time during the revision phase.
- **Respect the author's voice.** When writing replacement text in Phase 4, match the paper's
  existing style, tone, and level of formality. Don't impose a different writing voice.
- **Never suggest citations not already in the paper.** Only reference works the author has
  already cited. Hallucinated or unfamiliar references erode trust and waste verification time.
- **Productive over performative.** Don't waste time on review theater. Every comment should
  lead to either a concrete fix or a conscious decision not to fix. If a review comment
  wouldn't change anything about the paper, it shouldn't be there.
- **Update memory as you go.** Every rejection, deferral, and convention should be written to
  the appropriate memory file immediately when it happens — not batched at the end of the
  session. Paper-level decisions go to `.paper-review-memory.md` (repo-level); user
  preferences go to `.paper-review-memory.local.md` (user-level). If the session is
  interrupted, the memory should still be useful.
