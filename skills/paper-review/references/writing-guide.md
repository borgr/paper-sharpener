# Academic Writing Guide

## About This Guide

This guide splits tips into several categories:

- Tips related to **specific sections** of an academic paper
- Tips for writing at **different granularities** (sentence, paragraph, section, story)
- **Tools beyond writing**: LaTeX, rebuttal, and graphics

It focuses on scientific and domain-specific papers (not Nature or Science), but much of it may be useful for other purposes.

---

## Writing

### Where to Start?

#### Top-Down

A good option for coherence is to first understand the story. What is the main idea you want to convey (a new method, a surprising finding, criticism on X)? Then write an argumentation line. Then make it into an abstract or introduction following exactly this line of thought. Last, fill the needed sections given by this story.

#### Bottom-Up

A good option when it is hard to start is to begin by filling in the obvious information. When there are very clear results, strong bottom lines, a method that would be long to describe anyway. Sometimes, when all the main content is already there, connecting it becomes clearer and easier. This is very useful when there is clear and distinct content and less so when there are many results, some of which may not eventually support the main story.

---

### Story Level

#### Take the reader on a journey of understanding, not the journey you made

Almost always, the way towards a finding was not direct and involved roundabouts. Those do not matter anymore, neither is the chronological order of experiments you've made, nor including everything you tested along the way.

**What should you do?** Discuss only the things that teach the reader, add the background that leads to understanding them, and feel good about your way that led you here, even if others would not share it.

#### Reader's attention is your most valuable asset, use it well

This principle is the basis of many tips:

- Put the most effort in the beginning where many read.
- The things you care about should grab attention (be salient).
- The things you want readers to remember should be clear early on (early abstract, early introduction, early in each section, early in each paragraph).

You can also think about it from a different perspective: a paper is not a regular story where surprise and process are appreciated. You want the memorable information to appear as early as possible and allow people to learn what they needed (some just need the bottom lines).

#### What, how, why, and then the crux

Papers have different readers with different goals. Tell them:

1. **What** did you do? So they will choose if it is worth reading.
2. **How** did you do it? So they can reproduce or criticize.
3. **Why** did you do it (in that way)? So they would gain insights as well.
4. **What happened?** Because you both care most about the new findings and deep knowledge gained.

#### Kill your darlings, cut unless serving the story

As an expert, you know more than anyone else. You've learnt many interesting things. But eventually, you want to tell the readers something they will remember and follow. So often all kinds of side findings should stay out of the paper if they do not contribute to the main finding (or at least move to an appendix). Everything in the paper should follow the purpose of telling a coherent story.

Beginners are just learning how to fill the page; expert writers learn to cut down.

Concentrate your tale to a very specific line of thought, usually a single finding supported by evidence. Everything should serve this tale -- if it doesn't, then why is it here? If the tale is not convincing, you are overclaiming. And if your findings do not give this bottom line, maybe you're telling the wrong story and capturing the interest of the wrong people (who would be disappointed by the findings).

**Why cut?**

- Because the readers are there due to the previous parts calling them to read the paper (e.g., title) and the audience of something else is likely just not that audience.
- Because it competes on attention with more relevant parts.
- Because it makes for easy reading and is the way that people consume information.

#### Minor Tips

- **Avoid repetitions:** A good structure presents what it needs once (motivation in advance, details in a separate section) and then almost never repeats it. Then, every topic is almost standalone. For example, an experiment should be mostly understood and the details (e.g., what model is that?) are found somewhere else.
- **The paper happens in the present.** Previous work, previous sections, and previously run experiments are in the past.
- **When many examples could fit, pick the example that would return later.** Don't waste the mental fatigue of the reader on understanding just a concept; pick the one you later have a graph on, lay the ground to the issue that this opens later on, or have the same example returning with variations each time.

#### Every claim should be substantiated

In most venues, every claim should be supported. Refrain from claiming what you can't show, to a believable amount. Every claim you make, whether it is the main claim of the paper or a side claim, should be cited, explained, or supported by new evidence (experiment or proof).

> **Exercise:** "These failures, frequently dismissed as minor, carry rich information about model limitations." -- This needs a citation. Even this small example contains a claim ("frequently dismissed"). Prove to the reader so they can judge for themselves or dig deeper into the claim.

#### A paper should support all depths of reading

- Some readers just try to figure if they want to read -- make them already remember your finding even if they don't.
- Some readers will read, but it is only half relevant to them, so they will skim. They should be able to get it from skimming.
- Most readers might care about a specific part, so they will skim but want to understand one part more deeply. You just have to write all parts well for them.
- Some people will want to base their work on yours; they will come back for the tiniest details. Make sure to be replicable and as full as possible.
- There will be a few reviewers -- don't give them a reason to criticize (unless it is good for science).

---

### Section Level

#### Early on, write the gist of what is achieved in this section

This reduces mental load as the reader would know what is coming, and also it allows readers to skim. This might also refer to section names -- preferred titles that give the answer ("RLHF can influence knowledge") rather than the question ("Can RLHF influence knowledge?").

#### Start the section with opening remarks connecting it

Connect to what is going to come or what just happened. This is often a preview of the main bottom line you will present in the section. For example: "We have shown..." or "In this section we will prove this is..."

#### Examples are easier than abstractions

It is often easier to understand a concept by a specific example where the reader can generalize by themselves than by telling the user all that they need to know. Also, examples often bring the message home much better. They are more convincing.

> **Example:** "Running evaluation experiments is often costly, it requires countless datasets and inference per each of the models needed to be ranked as well as tuning the models to ensure fair comparisons. In fact, one model evaluation costs HELM 40K$."

---

### Paragraph Level

#### Connect to the last statement

Most paragraphs continue some idea from the last paragraph. A part of the idea often repeats something that was said before (e.g., revisiting the same object mentioned before, but not with coreference to be standalone when skimming), has a connecting word (e.g., "Regardless"), or just continues the same idea.

#### Start by stating the point of the paragraph

This allows skimming and ensures the important messages are salient. Starting with a clear claim or an organizing order helps the reader understand how the details come together. This follows the same underlying thought as Beginning of Section and Introduction.

> **Exercise:** Read a whole section but only the first sentences of paragraphs (perhaps two). If you don't understand the section, use the ending of the last paragraph. If there are paragraphs you don't understand, they are not written well enough; perhaps two should be concatenated, or an opening should be written. If the flow is not convincing, maybe the paragraph order is wrong.

**Example openings:**

- "This writing guide is helpful in many ways." [sentences that explain, elaborate, or prove the claim]
- "There are many ways to open a can efficiently." [list of ways]
- "Solving the superintelligence problem is more complex than one thinks." [complexities, perhaps with references to misconceptions]

#### Use of Examples

Use examples -- people understand those better than complicated abstractions. Some even suggest starting with the examples before explaining; often speech would do that (and would ease understanding).

#### Better clear than overarching

If you have many "or"s and "and"s or complicated structure, perhaps you are trying to encompass more than a single example. An example is there to explain something broader easily; it should hence be easy even if there are other (just as good) examples. Avoid the temptation of adding more than one example into the same example.

#### Short statements are strong

Especially when sentence lengths vary, which makes it less boring. Beginner writers use very simple sentences all the time, which makes it seem simple and makes no rhythm. It often makes us avoid those short sentences as we grew out of them. This is wrong. Did you hear the vibrations of the last sentence? A short sentence stands out and is memorable as it can all be kept in memory at the same time, or because attention is not spread, or because the rhythm stops. Regardless, it is a tool one might use.

---

### Sentence Level

#### Actions are more understandable as verbs, and concrete nouns as nouns

Most actions can be syntactically represented as a noun or part of a noun phrase (shared representation, omittance, forgetfulness), but it is easier to read when those match the traditional role of a verb (share, represents, omitted, forgetting). Often rephrasing the same complex sentence by replacing the roles of who is the active entity (ideally subject), what is the activity (the verb), and which is a more passive entity acted upon.

#### Strong sentences let the subject perform the most important verb

In strong sentences, the subject is not just present but actively performing a clear, meaningful verb. This helps readers see quickly who or what is responsible for the main claim or result.

**Examples:**

| Weak | Strong |
|------|--------|
| "On the face of it, this may seem as a contradiction to the proofs in the RLHF literature." | "On the face of it, this may seem to contradict the proofs in the RLHF literature." (or even: "this contradicts the proofs") |
| "These findings suggest that the effectiveness of specific prompt components is dependent on the dataset" | "These findings suggest that the effectiveness of specific prompt components depends on the dataset" |
| "We contribute improvements to the overall translation quality" | "We improve the overall translation quality." |
| "To do that, we feed each prompt to all of the models and calculate a ranking of the models by their scores" | "To do that, we feed each prompt to all of the models and rank the models by their scores" |
| "The accuracy of the anchor-based evaluation is tightly linked to its performance against the other evaluated models" | "An anchor produces the most accurate rankings when it is comparable in strength to the models it is evaluating" |
| "While these are rare anecdotes, we see those as sparks of success that hint at the potential." | "While these are rare anecdotes, they serve as sparks of success that hint at the broader potential." |
| "It is important to note that there is evidence suggesting..." | "The evidence suggests..." |

#### Be precise, convey a clear and minimal statement

> **Example:** "Another trait that agents are expected to show is a manner of interacting with an environment." becomes "Agents are also expected to interact with the environment."

#### When there is parallelism in meaning, make it also parallel in form

Across sentences, when there is a general and a specific claim, they are easier to understand if the two sentences share the same components with the details changing. Such parallelism may include repeating keywords, making the same connections.

Inside a sentence, phrases may also ease reading.

> **Example:** "Prompt Agreement as Evidence for Agreement of the Ground Truth" becomes "Prompt Agreement as Evidence for Ground Truth Agreement"

#### Explicit is often better than implicit

Using pronouns/coreferences (it, they, his) requires effort from the reader to resolve and remember who we are talking about. Similarly, quantifiers (many, different) often obscure rather than help. Try replacing such words with their specific names.

**Examples:**

| Implicit | Explicit |
|----------|----------|
| "such/given/many/various studies" | "efficiency studies" |
| "He" | "Dan" |
| "There are different methods to understand what knowledge they use to perform a given task through custom datasets and metrics" | "Interpretability and analysis methods were devised to link internal knowledge to model outputs." |

#### Link to the last paragraph or sentence (but only once)

Explicitly stating how the new sentence is connected to the ones before creates a feeling of flow. For example by words like "furthermore," "instead," and "second."

However, overuse may be tedious. Don't use two linkers in the same sentence.

#### Familiar concepts come first, surprises and new information come later

This gives a feeling of continuity, reduces the mental load, and creates surprise. When new information is introduced, we already have all the context to understand it, and as it is new, we expect the next sentence to also talk about it. It also plays with stress where the opening (topic) and ending (surprise) have the most attention, as they are close to a long pause and have little cognitive burden.

**Examples:**

- If we want the efficient aspect to be the focus: "Large Language Model (LLM) scaling laws predict the performance of an LLM **efficiently**"
- More neutral emphasis: "Large Language Model (LLM) scaling laws efficiently predict the performance of an LLM"

#### You can control the stress, the emphasis

If you want a part emphasized, beyond bold, the writing can do it. By default, the sentence ending carries the stress. So does the beginning. Both come near a strong pause and when the reader has little effort to keep sophisticated information for later.

**Weak endings (stress falls on an unimportant word):**

| Weak | Strong |
|------|--------|
| "The sensitivity of the sensors was the primary metric we focused the optimization **on**." | "We focused the optimization on the primary metric: **sensor sensitivity**." |
| "The rapid degradation of the protein samples during the incubation period **occurred**." | "During the incubation period, the protein samples underwent **rapid degradation**." |
| "The hypothesis was supported by the experimental results, as shown in **Table 4**." | "As shown in Table 4, the experimental results strongly supported **the hypothesis**." |

**Controlling where stress falls:**

- **Colon (most aggressive):** "One factor was responsible for the sample degradation: **high solution acidity**." -- Forces the reader to wait for the explanation, increasing the weight of the final words.
- **"Not X, but Y" structure:** "It was not the mass, but **the kinetic energy**, that dictated the outcome." -- Signals a deliberate choice and places stress exactly on your intended target.
- **Em-dash appositive:** "This model utilizes a dynamic learning rate -- **a critical departure from standard architectures** -- to ensure convergence." -- Forces the reader to linger on a specific concept.
- **Tool vs. result emphasis:** "The high-resolution data was gathered using **the new laser spectrometer**." (tool emphasis) vs. "Using the new laser spectrometer, we gathered **high-resolution data**." (result emphasis)

#### Reduce the reader's mental load

- **Shorten the distance between connected concepts.** Many concepts in a sentence are connected (nouns to verbs, verbs to objects, adjectives to nouns, adverbs to verbs). Reducing the distance between related concepts, or the tree depth, makes it easier to follow.
- **Reduce ambiguities.** When there is more than one meaning, the reader needs to solve it by context. Coreferences and anaphors like "it," "this," and "those" may refer to many entities. Use them, but sparsely.

---

### Word Choice

#### "They will understand." No they won't.

People will NOT understand. Assume they already half missed what was up until now, as they are not from the field, missed some context, or skimmed. Catch the moments where you hint, leave anything unsaid, or refer to something but do not open it ("this," "the model" -- which?) and fix it.

#### Minimize abbreviations and jargon

Make every word as easy to understand as possible and require as little background knowledge as possible. If a term is useful and not absolutely known, define it. Abbreviations often seem less formal (e.g., "don't").

Some accepted abbreviations are those considered part of academic writing: e.g., i.e., and c.f.

**Examples:**

- "Recurrent Neural Networks (RNNs)"
- "Recurrent Neural Networks (hereafter RNNs)"
- "Recurrent Neural Networks -- networks where activations can pass the same neuron more than once."

#### Use strengthening words sparingly to emphasize what you really care about

Examples: very, really, quite, extremely.

#### Every word should count, avoid fillers

**Avoid underspecified verbs and helper verbs if a real verb can replace them.** Common offenders: use, leverage, utilize, make, get, take, is done, involve.

> E.g., "we use the training scheme" becomes "we train"

**Avoid underspecified "things."** Stuff, things, something, etc. are placeholder nouns. Find ways to replace them with more accurate words. (A higher level: replace words with their most specific counterparts, such as "decrease" becomes "plummets.")

**Beware of "simply," "easily," "trivially," "clearly," and their friends.** You gain nothing, but you can lose much. When the reader doesn't understand, such a word might just add to the frustration.

**"Various," "different," and many quantifiers might be redundant.** E.g., "We propose several methods to..." -- does "several" convey relevant information beyond the plurality of "methods"?

#### Know yourselves

Authors commonly repeat their word arsenal a lot. If you know you overuse "so" or "Indeed" or "still" or "in fact," consider changing or deleting those uses.

---

### Exercises

Improve the following:

> "However, repeatedly checking results as data is collected increases the chance of falsely detecting an effect that isn't actually there, making the results more complex."

Better: "However, repeatedly checking results as data is collected complicates the above as it increases the chance of falsely detecting an effect that isn't actually there."

---

### Collaboration in Writing

#### Reduce the overall workload, comment only when necessary

When you note something worth changing, in most stages of writing it is better to just write and reduce the overhead for the other parties.

**When is it necessary to comment?**

- When you don't know the answer or how to fix the issue.
- When the paper is close to ready.

---

### More Exercises

**Exercise 1:** Prefer actions as verbs, familiar objects as nouns.

| Before | After |
|--------|-------|
| "The effect of scaling model size differs between scaled families, but only slightly" | "Model families scale quite similarly by model size" |

**Exercise 2:** Nominalization of verbs (using a verb/action as a noun).

| Before | After |
|--------|-------|
| "While the majority of shared knowledge representation occurs among languages using the same script, there is still some knowledge transfer between languages with different scripts." | "While knowledge is mostly shared among languages using the same script, there is still some knowledge transfer between languages with different scripts." |

**Exercise 3:** Reduce unnecessary words.

| Before | After |
|--------|-------|
| "We present MICALA, a new dataset developed for editing factual knowledge" | "We present MICALA, a dataset for knowledge editing" |
| "We start by providing a comprehensive breakdown of the various procedural steps constituting our proposed approach." | "We start by breaking down our approach into steps" |
| "Our comprehensive analysis aims to help us understand on why our method works." | Delete this sentence. Instead: "We analyze the speed of convergence and find that our method converges faster when the input text is long." |
| "We gather a quantification of the amount of words in every sentence." | "We quantify the amount of words in every sentence." |
| "We collected together existing human-model conversations datasets" | "We collected existing human-model conversation datasets" |

**Exercise 4:** Symmetry between sentences.

| Before | After |
|--------|-------|
| "We want the plugin to be 'transparent' to the user." / "The user should be able to manage their data on their own." / "The plugin must conform to established privacy standards." | "The plugin should be 'transparent' to the user." / "The user should be able to manage their data on their own." / "The plugin must conform to established privacy standards." |

Symmetry between sentences or phrases improves understandability. Who is the active object (we/plugin) should stay consistent.

**Exercise 5:** Reduce fillers.

| Before | After |
|--------|-------|
| "Is it possible for a model to learn from a gradient step in the same way it learns from context?" | "Can a model learn from a gradient step in the same way it learns from context?" |

---

## Sections in an Academic Paper

> Paper writing is the art of layering one piece to fit all readers.

### Title

A concise, clear, and attention-grabbing phrase that accurately reflects the paper's main topic or finding.

- **Makes you want to read.** This includes reading the title itself in highly flooded fields (e.g., a 3-word title might stand out), but also reading more into the details. It might stand out by being unique, having humor or artistic value, or calling for an interesting finding.
- **Conveys accurately what you expect to find in the paper.** A reader who comes with the wrong expectations might be angry for being misled or just confused. Especially avoid the temptation to overclaim; it will make people read, but they will realize it is wrong. If narrow or not exact, you might also miss the readers who do care and gain the wrong ones instead.

### Abstract

A summary highlighting the motivation, main findings, and key contributions.

- **Abstract is a paper's promo.** It should make the reader want to read. It should get to the point fast and bring the most interesting aspects with as little unnecessary information as possible.
- **Abstract is the most read part of a paper after the title.** Make it count. Make sure you put your most important takeaways there.

### Introduction

An extension of the abstract that sets up the problem, explains its importance, and outlines the approach and findings.

- **Full paper summary.** Anything important in the paper should appear (shortly) in the introduction: motivation, main idea or methodology, and main findings. A way to verify: add a reference to each section in the introduction (exceptions exist, such as experimental setup). It helps the reader to skim and shows if some things are skipped, whether they are in the same order, and if the main finding from each part is found there.
- **The most valuable asset.** Title, abstract, and introduction are the most read parts of a paper. Make them clear, invest the most time, and write them to encourage reading more or include everything you want readers to remember even if they won't read further.
- **Should I cite everything here? No.** Add only what helps the story. If there is relevant but not needed information, find a place (related work?) for it.
- **Convey the main messages, don't build suspense.** An introduction should not end without the reader understanding the main thing they need to know. Most readers would not read most of the rest of the paper. So a paper should have all takeaway messages early. E.g., "We perform a thorough investigation" becomes "Our analysis shows..." and "We explain why could it work?" becomes "We find it works because..."
- **Refer to other sections.** Add links to where you discuss each concept more. This makes the introduction a kind of table of contents where readers can jump to parts that interest them.

#### Motivation

- **Choose the one that serves your purpose.** There are many motivations, and your idea has depth. But later you have findings -- pick the aspects that are most shown there, the ones that will lead a reader to already expect what you are doing from the problem setup.
- **Keep it short, usually.** You want to convince the reader this is an important problem. In most cases, it is quite obvious for a reader in the field. Reduce details, remove unnecessary motivations to the motivations. E.g., "LLMs are common, so we should care about LLM speed, but they are slow when..." -- skip straight to the speed argument.
- **Unless you provide a new problem.** If the point of your paper is to refocus what people study, this is central and worth the space.

### Background

Explains essential concepts or prior work needed to understand the paper.

- **Place it early.** Otherwise, readers would have to wait before they start to understand. And one thing readers do not have is patience.
- **Purpose:** Explain prerequisites that your work will not be understood without. These can be definitions and explanations you will keep using, or terms and findings that prior art brought.
- **This is not a related work section.** Don't just list prior art.

### Method (Body)

A description of what was developed or proposed, including how it works and why.

- **Explain the innovation that others might use as well.** If you propose an algorithm, one should understand what the algorithm is. Explain the details, the decisions, and other relevant information.
- **This is not an experimental setup section.** You explain what you propose for others to learn or do in the future or in general. In the Experimental Setup you explain what you did for this specific experiment(s), what choices you made, and how to reproduce your results (not how to use the findings).

### Experimental Setup

Details how experiments were run, including settings, parameters, and procedures.

- **Don't hide, don't deem unnecessary, don't underestimate its importance.** For good science it is absolutely necessary that others would be able to understand your work deeply. The people this paper matters most to will want to know how you broke ties, how long it took, and every other tiny detail. Reproducibility is key to scientific advancement.
- **Separate technicalities from the results.** In most cases, concentrate as much as possible in the experimental setup.

### Results

Reports outcomes of experiments, supported by figures, tables, and comparisons.

- **Be exact, neither overclaim nor underclaim.**
  - **Overclaiming:** Overclaimed results are factually wrong and misrepresent findings. People who notice will dislike what they find, and others would believe wrong findings and fail to replicate. When necessary, hedge: "Generally," "In most cases," "In X%," "It seems likely," "We found X can happen," "When Y, X is true."
  - **Underclaiming:** If you don't say what you actually find, you do not communicate the knowledge you gained.
- **What did you find?** This is the main thing you present. As little as possible about *how* you found it (that goes to background and experimental setup).
- **State in words.** It is not enough that the graph shows a result. The highlights and findings that the graphs or tables depict should be explicitly written.
- **Main points should be clear in a visual.** Crucial points should grab attention and be supported by direct evidence.
- **Little speculation, this is not discussion.** Aim for scientific report: "I told you in advance what I want to do and why, now I just give you the finding."

### Analysis

Interprets or broadens the main results to uncover patterns, implications, or deeper insights.

### Related Work

Reviews relevant literature to position the contribution and highlight differences.

- **This is not a background section.** Your paper should be understandable without it.
- **Place it near the end.** It is a scholarly section, but not your main claim.
- **Purpose:** Point to relevant work, give credit, differentiate your work from what others did.
- It is not enough to have a list of works somehow related to yours. The works should be organized to explain how each relates to or differs from your paper.
- Emphasize novelty concretely (by explaining differences and advantages). Just claiming to be novel is not convincing and does not give the reader useful information.
- Avoid over-discussing works; sometimes comparing too much gives too much saliency to a work and gives the feeling you tried hard to find differences because there aren't many.

### Conclusion and Discussion

Reflects on the contribution, broader impact, or future directions.

- **The place for deeper thoughts.** If you have ideas that you want to express, this may be the right place. At this point readers are open to speculations.

### Limitations (Section or In-Text)

- **Space should align with the problem's importance.** When you dedicate a lot of text it implies this is an important point. Sometimes, the explanation is convincing but so long that it makes the reader convinced it is a crucial problem regardless.

### Appendix

Acknowledges constraints, uncertainties, or weaknesses in the work.

- **The place for too-technical details and needs for reproduction.** This includes documentation, numbers, graphs, statistics, etc.
- **Additional findings which are too interesting to ignore** but you will not have a separate paper for. Note that this will likely still get ignored.
- **Purpose:**
  - Serve the most professional and interested researchers.
  - Share information that is important but too much for the main text.
  - Make it easier for the writer to cut what needs to be cut. Appendices often serve an emotional role: for most researchers the sentiment of putting it out somewhere still exists.

### Acknowledgments

An optional section to thank people who were not paper authors, or (most often) grants that supported the work. In double-blind papers, acknowledgments are often added only in the camera-ready.

---

## Common Academic Writing Needs

### Shortening (General)

- **Ignore length at the beginning, content first.** Tell the story well; length would be ok at the end.
- **Look for short lines at the end of the paragraph.** Rephrase the paragraph to reduce it. What is repeated? What uses many words instead of selecting the appropriate one?
- **Appendix time!** What paragraphs, sections, comments, or details can you do without? Getting rid of sidenotes and less-essential experiments often makes the overall story simpler and clearer.
- **Consider all non-text objects.** Footnotes have a small font but take up space. Tables might use a smaller font or be wrapped (in a one-column format).

---

## Rebuttal

### Reviewers are volunteers

They don't remember, they won't work hard. Repeat their comment briefly so they know what you refer to. Make it simple and clear.

### Write in 2 levels: AC and reviewer

There are two people you might convince: the reviewer, or the AC. Usually the latter will be convinced that the reviewer did not do a good job or is too harsh.

### You are at the bottom of the hierarchy, act accordingly

### People find it hard to be confronted

Try not to tell someone they are wrong (unless you appeal to the AC), but gracefully be understanding and provide more context, add a clarification, or gently help them reach a better conclusion.

### Treat the rebuttal as collaboration

Approach reviewers as peers working with you to improve the paper, not opponents to defeat. They invested time to read your work and point out weaknesses, so take their comments seriously and look for ways to accept or incorporate their suggestions when possible. Communicate and commit to specific improvements. Frame your responses from a cooperative mindset: clarify, improve, and show openness rather than defensiveness. People rarely change their minds when they feel opposed, but they are much more receptive when the discussion feels like a shared effort.

### Show you listened before you respond

Demonstrate that you understood the reviewer's concern before explaining your response. Briefly restate or paraphrase their point, then address it clearly. This simple act signals respect and careful reading, and it often encourages a more constructive reaction from reviewers.

### Hard facts are the most convincing

Even in a confrontational situation, if you just have a different opinion, they will likely keep their own. Especially so as they decide.

**Actionable items:**

- When allowed and possible, conduct an experiment to show what the reviewer was wondering about.
- Refer to where you did something they ask about -- better than long explanations.

### Make it skimmable

Aid busy ACs and overworked reviewers by shortening, stating important bottom lines early in each paragraph, repeating the referred criticism and the content from the paper, and referring to it clearly. For example, do you (politely) disagree, slightly correct, or agree?

### When possible, do rather than debate

Change already, or share the core change when planning to, or share the experiment if small and can be done in time, or answer with facts and data rather than with words. If not, say what you will change rather than just agreeing.

### Rebuttal Sources

- [How We Write Rebuttals -- Devi Parikh](https://deviparikh.medium.com/how-we-write-rebuttals-dc84742fece1)
- [How to Write an Author Response to *ACL/EMNLP Reviews -- Maarten Sap](https://maartensap.com/notes/rebuttals.html)

---

## Graphics

### Core Principles

#### Visualizing has a reason, make it show

You bothered visualizing your data, which means you wanted to convey an idea. Make this idea the first thing people see and understand. First, convey the main message. Any addition that makes other points clearer is ok, as long as it does not cost this main message.

#### Minimal is understandable

Details take the reader time, effort, and attention. Guide their every effort to focus on your priorities, whether that means spending more time for deeper understanding or just a brief glimpse to convey what you wish them to remember.

#### Pop-up is best, easy is second, takes time is worthless

Some messages can be understood without thinking about the visualization. A pop-up effect is when you can see a figure for a second and already tell things about it. If those things are your message, it reaches more audience and deeper. Otherwise, at least make the message fast.

#### People remember what they attended to

Saliency should equal importance. Look at all the fonts -- they should all be boringly the same. The one you change should be the one you want people to pay attention to. If too many things are salient, the effect is overstimulation and no specific thing is memorable.

#### Imagine the path the ideal eye would make

One way to explain what is fast to grasp is by the number of points the eye needs to attend to, how far they are, and how long the overall path is. From this: minimize unnecessary details, related objects should be close to each other.

### Tips

- **In bar plots, put the bar you care about on the right** (reading is left to right). Ideally, also make it largest (have a metric where larger is better) because it becomes more salient.
- **Reduce the amount of text.** It wastes time, is not intuitive, is not visual, and takes many jumps in the eye's path.
- **Related objects should be close to each other.** If you expect to go from one object to another, minimize the movement. Consider visualizing the path itself (e.g., by arrows or a shape like a horizon).
- **Minimize unnecessary details.** Remove anything that does not convey more information (lines, squares, text, bullets).
- **Color matching:** For readability and saliency, choose contrasting colors. For ease, choose similarly hued or matching colors in similar tones. ([Color combination toolkit](https://medium.com/swlh/two-color-combinations-a-toolkit-feeb9e51765c))
- **Be consistent.** Use the same colors across graphs to convey the same meaning. Use the same terms found in the text; don't use unreadable names or variable names from code.

### Graph Checklist

- [ ] Save as `.pdf` not `.jpg`/`.png` (resized with no pixelation in LaTeX)
- [ ] Readable by colorblind (markers/patterns/colorblind color palette)
- [ ] Large fonts (as large as `\small` or normal text in the paper)
- [ ] Same font as text (usually Times New Roman/Serif)
- [ ] Capitalized labels
- [ ] No `-`, `_`, jargon, or uncommon abbreviations in labels and legends
- [ ] Use `%` not `0.xx`
- [ ] Meaningful labels + legends
- [ ] No black lines around the figure (or other non-meaningful markings) -- despine
- [ ] All graphics follow the same theme (colors, names, backgrounds)
- [ ] Trim whitespace around images
- [ ] Can you replace any text with a visual solution (e.g., a legend of numbers becomes point width)?
- [ ] Does the legend repeat or have overlapping information?
- [ ] Remove title
- [ ] If sent to arXiv -- remove spaces from figure name
- [ ] Glimpse the graph for just a second -- did you look at the main thing? No? Fix. (popup, eye-path)
- [ ] Is it better to explicitly write shown values (e.g., on top of bar plots)?
- [ ] If relevant, does it convey significance or variation? Error bars, shades in lines, etc.
- [ ] If so, do you need STD or Standard Error? (often the latter)

### Captions

- Start with a short sentence claiming the main reason for the figure (e.g., "Training helps" / "Model stats.").
- Figure captions should start with the interesting part. This is like a paragraph where you first supply the information people need if they skim.
- No need for a title -- that is what the caption is for.

---

## LaTeX

### Citations

- **`\citep`** -- default citation. Use when attributing but the author name should not be part of the sentence. E.g., `This tips document was later shown to be the best in the world \citep{Einst1991}.`
- **`\citet`** -- use when referring to a paper directly. E.g., `\citet{Choshen} showed that` produces "Choshen (2053) showed that."
- **`\cite` warning:** It is defined differently depending on the style used. Sometimes it acts as `\citet` and sometimes `\citep`. This means, for example, that being rejected from ICML and submitting to ICLR would have changed all citations.

### Conferences often dictate the format, but you can still remove the ugly boxes

```latex
\usepackage{hyperref}
\usepackage{xcolor}
\hypersetup{
    colorlinks,
    linkcolor={red!50!black},
    citecolor={blue!50!black},
    urlcolor={blue!80!black}
}
```

### Cross-referencing

- Link to sections or captions with `\ref{}`
- Link to a random place (words) in the same document: `\hypertarget` / `\hyperlink`
- Between documents: `xref` package (sometimes hard to set up, avoid if possible)

### Punctuation in LaTeX

- Quotes: `"word"` doesn't work -- use ``` ``word'' ```
- Dashes: word compounds `-` (Spin-off), from `--` to, dash as punctuation `---`
- Non-breaking space: `Word~word` places a space considered as a regular character. Especially useful for `Fig.~\ref{}`, `Table~\ref{}`, etc.

### Shortening (LaTeX)

- **`\looseness=-1`** -- Tries to reduce 1 line by changing the spacing between words in the paragraph. Sometimes reduces those one-line overflows without altering wording.
- **`\linepenalty=1000`** -- Tells LaTeX to always highly penalize new lines. Between a new line and less space between characters, picks the latter.
- **`\vspace{-?cm}`** -- In most conferences this is not allowed (not following "LaTeX Zen"). Still, easiest hack to explicitly change the vertical space between two LaTeX objects.
- **`\mbox{words in same line}`** -- Ensures an expression is found in the same line.

---

## Useful Words

| Word | Meaning |
|------|---------|
| Facilitate | Make easier |
| Expedite, hasten | Speed up |
| Remediate | Make right, address (give remedy) |
| Mitigate | Make (an issue) less severe |
| Circumvent | Bypass a problem |
| Hinder | Create difficulties |
| Exacerbate | Worsen a problem |
| Preclude | Prevent in a final way, make it impossible |
| Obstacles, hurdles | Difficulties |
| Arduous | Difficult, requiring a lot of effort |
| Plethora, myriad, battery | Many, excess, plenty |
| Dearth | Lack, little |
| Deluge | Overwhelm, swamp |
| Eschew | Avoid deliberately, abstain |
| Refrain | Stop yourself from doing |
| Disregard | Ignore intentionally |
| Nascent | In its early days |
| Rudimentary, crude | Basic, immature, not processed |
| Evidently | X shows, finds, presents, demonstrates, we observe, exhibits, displays |
| Exemplify | Serves as an example |
| Epitomized | Served as the perfect example for |
| Permeate, pervade | A (problem) is spreading in X |
| Advent | Arriving of an important X ("Before the advent of the railways") |
| Ubiquitous | Widespread, widely used |
| Culminating | Resulting finally in, reaching the peak with |
| Two-pronged approach | Two ways of doing something (can be more) |
| Elucidate | Explain something currently unclear |
| Explicate | Explain with more details, break into parts and analyze |
| Purport | Appear or claim to be or do something, especially falsely |
| Posit | State as truth, assume as a fact; put forward as basis of argument |
| Performant | Has high performance |
| Subpar | Worse than usual/expected |
| Surpass | Is beyond, is better than |

---

## Links and Resources

- [Style: Ten Lessons in Clarity and Grace](https://www.google.com/search?q=Style+Ten+Lessons+in+Clarity+and+Grace) -- The unparalleled book for writing
- [How to Give Presentations -- MIT](https://www.youtube.com/watch?v=Unzc731iCUY)
- [How to Write a Great Research Paper -- Simon Peyton Jones](https://www.microsoft.com/en-us/research/academic-program/write-great-research-paper/)
- [How to Give a Talk -- Simon Peyton Jones](https://www.microsoft.com/en-us/research/academic-program/how-to-write-a-great-research-proposal/)
- [How We Write Rebuttals -- Devi Parikh](https://deviparikh.medium.com/how-we-write-rebuttals-dc84742fece1)
- [How to Write Rebuttals -- Maarten Sap](https://maartensap.com/notes/rebuttals.html)
