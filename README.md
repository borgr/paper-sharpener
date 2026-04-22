# Paper Sharpener

Agentic skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that help you write better academic papers — review simulation, writing improvement, and revision assistance.

Based on the [evergrowing writing tips document](https://docs.google.com/document/d/14Wax8M5w8F_8miDlYJ9-I6wqpelxlXjCEUbkNzNMqqE/edit?usp=sharing).

## Using with Overleaf

Clone your Overleaf project locally via [git](https://www.overleaf.com/learn/how-to/Git_integration), `cd` into it, and use the skills with Claude Code. Push changes back to Overleaf when done.

## Skills

### Paper Review

Simulates a full multi-reviewer academic paper review. Three independent reviewers (senior adjacent-area, mid-career same-subfield, early-career same-subfield) generate reviews in parallel, then you triage and apply revisions interactively.

**Say things like:** "review my paper", "simulate reviewers", "what would reviewers say", "help me prepare for submission"

### Writing Assistant

Improves your academic writing at any granularity — from a single sentence to a full section. Analyzes text against writing principles (sentence strength, stress control, precision, parallelism, etc.) and proposes rewrites with cited reasoning.

**Say things like:** "improve this paragraph", "rewrite this section", "check my writing", "make this sentence stronger"

## Installation

<details>
<summary><b>Option 1: Plugin install (recommended)</b></summary>

```sh
claude plugin add --repo borgr/paper-sharpener
```

This makes the skills available in all your projects.

</details>

<details>
<summary><b>Option 2: Global install (all projects)</b></summary>

Clone into your global Claude Code skills directory:

```sh
git clone git@github.com:borgr/paper-sharpener.git ~/.claude/skills/paper-sharpener
```

The skills will be available in every project you open with Claude Code.

</details>

<details>
<summary><b>Option 3: Per-project install</b></summary>

Clone into a specific paper project's `.claude/` directory:

```sh
cd your-paper-repo
git clone git@github.com:borgr/paper-sharpener.git .claude/skills/paper-sharpener
```

The skills will only be available in that project.

</details>

## Customizing

The skills are just Markdown files — you can tweak them by asking Claude Code directly. For example: "add a reviewer persona focused on statistical rigor" or "make the writing assistant ignore passive voice."

Each paper repo also gets its own memory automatically. The skills remember your decisions (rejected review items, conventions, editing preferences) across sessions, stored in your paper's `.claude/` directory.

## Contributing

This is an evergrowing project — contributions welcome!

- **Improve an existing skill:** Edit the `SKILL.md` or reference files under `skills/<skill-name>/` and open a PR.
- **Add a new skill:** Create a new directory under `skills/` with a `SKILL.md` file. Use the existing skills as a template for the frontmatter format. Add any reference files your skill needs under `references/`.
- **Improve the writing guide:** The guide in `references/writing-guide.md` is shared across skills — improvements there benefit everything.

**Skills we'd love to see:**
- **Rebuttal assistant** — Help draft responses to reviewer comments, using the rebuttal strategies from the writing guide
- **Figure & table auditor** — Dedicated pass for graphics quality, caption clarity, color accessibility, and consistency
- **Research question debater** — Challenge and sharpen your research question, framing, and scope before you start writing

## Credits

The writing tips were mostly written by [Leshem Choshen](https://github.com/borgr), with the help of the community.
The skill adaptations were done by [Yotam Perlitz](https://github.com/ype).
The improvements are now up to all of us — used it? Adapted it? Aid others.
