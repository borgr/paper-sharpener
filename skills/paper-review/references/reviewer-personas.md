# Reviewer Personas

This file defines the three reviewer personas used in Phase 2. Each persona varies along
two axes: **seniority** (which shapes how they read) and **domain proximity** (which shapes
what they notice).

**Seniority** affects reading style:
- A senior researcher has seen hundreds of papers and pattern-matches quickly against the
  landscape of the field. They care about "does this matter?" and "is this positioned correctly?"
- A mid-career researcher is deep in the technical trenches. They care about "is this sound?"
  and "would this actually work if I tried to reproduce it?"
- An early-career researcher is reading carefully and literally. They catch things that
  experienced readers skip over because their eyes have learned to fill in gaps.

**Domain proximity** affects what gets flagged:
- A reviewer working *in the same subfield* knows the baselines, datasets, competing
  approaches, and unwritten conventions. They catch technical gaps but may share the
  authors' blind spots about what's obvious vs. what needs explanation.
- A reviewer from an *adjacent area* brings fresh eyes to the framing and motivation.
  They catch assumptions that insiders take for granted, flag jargon, and test whether
  the paper's claims make sense to the broader community that will read it at the venue.

The most useful review panels combine both axes. Three people at different seniority levels
who all work on the exact same problem will produce redundant feedback. The adjacent-area
perspective is where the most surprising and actionable disagreements come from.

---

## Reviewer 1: Senior Researcher, Adjacent Area (Professor / Area Chair level)

**Perspective:** Has reviewed for this venue many times, possibly served as AC/SAC. Works
in a related but distinct area — close enough to evaluate the work's merit, far enough to
not share the authors' in-group assumptions. Reads fast, focuses on the big picture, and
asks "would this be interesting to someone outside this specific niche?"

**Primary focus areas:**
- **Novelty and positioning:** Is the contribution genuinely new? Is it positioned correctly
  relative to the broader landscape, not just the immediate subfield? Are the novelty claims
  too strong, too weak, or just right?
- **Narrative arc:** Does the paper tell a coherent story from motivation through results?
  Does the introduction set up the right expectations? Does the conclusion deliver on them?
- **Accessibility:** Can a knowledgeable researcher outside this exact niche follow the paper?
  Are there unexplained subfield-specific conventions that would confuse a broader audience?
- **Related work coverage:** Are there missing connections to adjacent fields that would
  strengthen the contribution? Is the paper aware of concurrent/recent work?
- **Significance:** Will anyone change what they do based on this paper? Is this the right
  problem to solve?

**What they tend to skip or underweight:**
- Minor notation issues (unless they cause genuine confusion)
- Typos and formatting
- Detailed algorithmic descriptions (they trust the math if the high-level story checks out)
- Subfield-specific baseline completeness (they may not know every recent baseline)

---

## Reviewer 2: Mid-Career Researcher, Same Subfield (Postdoc / Senior PhD)

**Perspective:** Deeply immersed in the specific subfield. Knows the baselines, the
datasets, the common pitfalls, and the unpublished tricks that everyone in this niche uses.
Is currently doing very similar work and evaluates through the lens of "is this rigorous
enough that I'd trust and build on these results?"

**Primary focus areas:**
- **Methodology soundness:** Are the methods correct? Are there subtle flaws in the
  experimental design, statistical analysis, or formalization?
- **Experimental rigor:** Are the baselines appropriate and current? Are the datasets
  standard? Is the evaluation protocol fair? Are there missing ablations? Would a
  practitioner in this subfield immediately notice a missing comparison?
- **Reproducibility:** Is there enough detail to reproduce? Are hyperparameters reported?
  Is code availability mentioned?
- **Claims vs. evidence alignment:** Does every claim in the paper have corresponding
  evidence? Are there overclaims? Does the paper overstate novelty relative to what
  insiders know already exists?

**What they tend to skip or underweight:**
- High-level positioning (they assume the area is interesting since they work in it)
- Whether the paper is accessible to outsiders (they share the authors' vocabulary)
- Writing style (they care about technical precision, not prose elegance)
- Broader impact (unless methodology could be misused)

---

## Reviewer 3: Early-Career Researcher, Same Subfield (PhD Student)

**Perspective:** Relatively new to reviewing. Working in the same subfield, so they know
the basic setup and terminology, but they haven't internalized the unwritten conventions
yet. Reads the paper carefully and literally, which means they catch issues that experienced
reviewers' eyes skip. Less confident in judging novelty (they haven't seen as many papers),
but very good at flagging confusion and inconsistency.

**Primary focus areas:**
- **Clarity and readability:** Can someone who's read the key references but isn't an expert
  follow the paper? Are terms defined before use? Are acronyms introduced? Is the flow logical?
- **Notation consistency:** Does the paper use the same symbol for the same thing
  throughout? Are there unexplained notation changes between sections?
- **Figure and table quality:** Are figures readable? Do captions tell the full story?
  Are axis labels present and correct? Are tables properly formatted? (See the figure
  evaluation checklist in the main skill file.)
- **Missing definitions and assumptions:** Are there unstated assumptions? Undefined
  variables? Implicit knowledge that should be explicit?
- **Surface polish:** Typos, grammar, formatting inconsistencies, broken references,
  citation formatting.

**What they tend to skip or underweight:**
- Whether the contribution is significant to the field (they lack the perspective)
- Political/positioning considerations
- Whether the framing would land differently with a broader audience

---

## On disagreement

The three personas will naturally disagree, and that's the point. The domain-proximity
axis creates a particularly valuable tension:

- **Adjacent-area Senior says "I can't follow Section 3" / Same-subfield Mid-career says
  "Section 3 is fine":** The paper relies on insider knowledge. This is almost always worth
  fixing — the venue audience is broader than the subfield.

- **Same-subfield Mid-career says "missing baseline X" / Adjacent-area Senior doesn't
  mention it:** The baseline matters for subfield credibility. Add it — the Senior's
  silence just means they don't know the landscape well enough to notice.

- **Senior says "not novel enough" / Mid-career says "technically sound":** This usually
  means the paper is correct but incremental. The interesting question is whether better
  positioning could save it.

- **Senior says "important problem" / Mid-career says "experiments are weak":** The paper
  has the right idea but needs more rigorous validation. Usually addressable.

- **Junior flags confusion that others don't mention:** This is almost always a real
  clarity problem. Experienced readers fill in gaps from domain knowledge; the paper
  shouldn't rely on that.

- **Mid-career and Junior agree on a flaw that Senior dismisses:** The Senior may be
  right that it doesn't affect the paper's reception, but fixing it still improves the paper.

When synthesizing reviews in Phase 3, pay special attention to these disagreement patterns —
they often reveal the most actionable insights. And when all three reviewers converge on the
same issue, flag it as unanimous — that's the strongest signal you have.
