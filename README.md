# ✏️ Paper Sharpener

> Agentic skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that help you write better academic papers — review simulation, writing improvement, and revision assistance.

These aren't just prompts. The skills are built on a comprehensive [academic writing guide](https://docs.google.com/document/d/14Wax8M5w8F_8miDlYJ9-I6wqpelxlXjCEUbkNzNMqqE/edit?usp=sharing) — a community-maintained document compiled by [Leshem Choshen](https://github.com/borgr) covering everything from sentence-level craft (stress control, nominalization, parallelism) to paper structure, figure design, LaTeX tips, and rebuttal strategy. The skills encode this knowledge into structured, interactive workflows.

---

## 🚀 Quick Start with Overleaf

Clone your Overleaf project locally via [git](https://www.overleaf.com/learn/how-to/Git_integration), `cd` into it, and start using the skills with Claude Code. Push changes back to Overleaf when you're done.

---

## 🛠 Skills

### 📝 Paper Review

Simulates a full multi-reviewer academic paper review. Three independent reviewers — senior adjacent-area, mid-career same-subfield, and early-career same-subfield — generate reviews in parallel. You then triage action items and apply revisions interactively.

> **Try:** *"review my paper"* · *"simulate reviewers"* · *"what would reviewers say"* · *"help me prepare for submission"*

### ✍️ Writing Assistant

Improves your academic writing at any granularity — from a single sentence to a full section. Analyzes text against writing principles (sentence strength, stress control, precision, parallelism, etc.) and proposes rewrites with cited reasoning.

> **Try:** *"improve this paragraph"* · *"rewrite this section"* · *"check my writing"* · *"make this sentence stronger"*

---

## 📦 Installation

<details>
<summary><b>Plugin install (recommended)</b></summary>
<br>

```sh
claude plugin add --repo borgr/paper-sharpener
```

This makes the skills available in all your projects.

</details>

<details>
<summary><b>Global install — all projects</b></summary>
<br>

Clone into your global Claude Code skills directory:

```sh
git clone git@github.com:borgr/paper-sharpener.git ~/.claude/skills/paper-sharpener
```

The skills will be available in every project you open with Claude Code.

</details>

<details>
<summary><b>Per-project install</b></summary>
<br>

Clone into a specific paper project's `.claude/` directory:

```sh
cd your-paper-repo
git clone git@github.com:borgr/paper-sharpener.git .claude/skills/paper-sharpener
```

The skills will only be available in that project.

</details>

---

## 🎨 Customizing

The skills are just Markdown files — you can tweak them by talking to Claude Code. For example:

- *"add a reviewer persona focused on statistical rigor"*
- *"make the writing assistant ignore passive voice"*
- *"change the review triage to start with structural issues first"*

Each paper repo also gets its own memory automatically. The skills remember your decisions (rejected review items, conventions, editing preferences) across sessions, stored in your paper's `.claude/` directory.

---

## 🤝 Contributing

This is an evergrowing project — contributions welcome!

- **Improve an existing skill** — Edit the `SKILL.md` or reference files under `skills/<skill-name>/` and open a PR
- **Add a new skill** — Create a new directory under `skills/` with a `SKILL.md` file (use the existing skills as a template)
- **Improve the writing guide** — `references/writing-guide.md` is shared across skills; improvements there benefit everything

<details>
<summary><b>💡 Skills we'd love to see</b></summary>
<br>

| Skill | Description |
|-------|-------------|
| **Rebuttal assistant** | Help draft responses to reviewer comments, using the rebuttal strategies from the writing guide |
| **Figure & table auditor** | Dedicated pass for graphics quality, caption clarity, color accessibility, and consistency |
| **Research question debater** | Challenge and sharpen your research question, framing, and scope before you start writing |

</details>

---

## 🙏 Credits

The writing tips were mostly written by [Leshem Choshen](https://github.com/borgr), with the help of the community.
The skill adaptations were done by [Yotam Perlitz](https://github.com/ype).
The improvements are now up to all of us — used it? Adapted it? Aid others.
