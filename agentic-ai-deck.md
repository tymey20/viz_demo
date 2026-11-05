# Agentic AI: How Much Should the Model Decide?

Plain-text version of the deck: 12 slides plus 1 backup. Each slide lists its eyebrow, title, body and speaker notes.

**Look:** Source Serif 4 for headings, IBM Plex Sans for body.
Colors: ink #1C2430 · warm paper #F6F3EE · paper 2 #ECE6DC · blue #2F6A8A · terracotta #A3402A.
Dark slides: 1, 6, 12. Blue slide: 7.

---

## Slide 1 — Cover (dark)

**Eyebrow:** Agentic AI · a way to think about it
**Title:** How much should we let the model decide?
**Subtitle:** What an agent actually is, how to keep it inside the lines, and how to spot where it fits in your team.
**Footer:** [Your name] · [Date]

**Notes:** If you can, open with a quick live demo of the reporting engine before this slide. Then frame the session: this isn't a pitch. The goal is to leave with one question you can ask about any AI idea in your area: how much are we letting the model decide?

---

## Slide 2 — Where we are

**Eyebrow:** Where we are
**Quote:** "We'll build an agent that goes out and handles it."
**Title:** Everyone wants agents. Few of us can say what one is.
**Body:** Many "agents" today are prompts in an IDE that spin up more prompts. Fine for exploring, but nobody can own, test, or scale them.

**Notes:** Name the perception gently and don't point at anyone's project. The rest of the deck gives people a better mental model than "magic that goes and does things."

---

## Slide 3 — What an agent is

**Eyebrow:** What an agent is
**Title:** Four parts. That's the whole thing.

Four cards:
- **Model:** The LLM. It reads, reasons, and writes.
- **Instructions:** The prompt that defines the job and its limits.
- **Tools** (highlighted): The only actions it may take, like "run this query." Guardrails live here.
- **Loop:** Think, pick a tool, see the result, repeat until done.

**Body:** Everything an agent can do is defined by its tool list. If a tool doesn't exist, the agent can't take that action.
**Footer:** Framing after Huyen, *AI Engineering* (2025)

**Notes:** Huyen defines an agent by its environment and the set of actions it can take. The key distinction is between tools that read (look things up) and tools that write (send, update, approve). The loop is literally a few lines of code calling the model over and over with a list of allowed functions.

---

## Slide 4 — The one framework

**Eyebrow:** The one framework
**Title:** The real decision is how much the model decides.

| Setting | What the model does |
|---|---|
| **Build** (shaded) | Writes the code. No AI runs in production |
| **Assist** (shaded) | Fills one step in a workflow that code controls |
| **Look up** (shaded) | Chooses what to read, but can't change anything |
| **Propose** (shaded) | Drafts an action; a person approves it |
| **Act** | Acts on its own, with no approval |

**Body:** Autonomy is a dial we set on purpose. Most of the value today is in the shaded rows.
**Footer:** Degrees of autonomy after Ng, DeepLearning.AI *Agentic AI*

**Notes:** This is the slide everything else hangs off. Andrew Ng treats "agentic" as a spectrum rather than a yes-or-no, and argues most of the value comes from structured workflows where people decide the steps. Ask the room: when you picture an agent, which row are you picturing? Usually it's Act. The point is that you rarely need it.

---

## Slide 5 — Worked example

**Eyebrow:** Worked example · the monthly reporting deck
**Title:** One recurring deck, every setting of the dial.

| Setting | What happens | What keeps it safe |
|---|---|---|
| **Build** | AI helped write an engine that rebuilds every chart from source data | Plain code; no AI when it runs |
| **Assist** | An LLM drafts commentary from numbers the code already computed | The LLM never does the math |
| **Look up** | A checker reads the deck and the data and flags numbers that don't tie out | It can flag, not fix |
| **Propose** | It suggests corrected commentary and fixes | An analyst approves each change |
| **Act** | It emails the finished deck to leadership | We don't go here |

**Footer:** Before: Tableau screenshots pasted by hand. Now: [hours saved per cycle]

**Notes:** This is our reporting engine, so it's real. Before, an analyst screenshotted Tableau into PowerPoint every cycle. Now code reads the workbook, rebuilds each chart from source data and places it exactly. Notice that every safety measure in the right column is a design decision we made, not trust in the model.

---

## Slide 6 — Delegated authority (dark)

**Eyebrow:** A model we already use
**Title:** It's the delegated authority we already give people.

Four cards:
- **Assist:** Follows the checklist
- **Look up:** Pulls files on their own
- **Propose:** Drafts; the manager signs
- **Act** (highlighted): Signing authority, earned with limits

**Body:** An agent earns more authority the same way a new hire does: a limit, a reviewer, and a track record first.

**Notes:** Every leader here already manages delegated authority. Nobody gives a first-week analyst sign-off. Build isn't on this slide because it isn't delegation at all; it's just giving the team better tools.

---

## Slide 7 — The overlooked setting (blue)

**Eyebrow:** The overlooked setting · Build
**Title:** The lowest setting is where most of the value is right now.

Three cards:
- **Reporting engine:** Rebuilds recurring decks from source data instead of screenshots.
- **Scheduled dashboard:** Custom HTML refreshed from BigQuery on a schedule, changed through GitLab.
- **Deck checker:** Flags numbers that don't match across decks.

**Body:** Code got cheap. Software that once needed an IT project now takes an analyst weeks. **Cheap isn't free:** it still needs review, tests, and an owner.

**Notes:** Key line for the room: a lot of "we need an agent for that" is really "we never had budget to build software for that." That constraint has largely gone away. Show one of these live if you can. The caveat matters: without review and ownership, cheap code turns into shadow IT.

---

## Slide 8 — Guardrails

**Eyebrow:** Keeping it inside the lines
**Title:** Every setting has guardrails, and they're design choices.

Six cards:
- **Least privilege:** Read tools by default. Write tools are rare and scoped.
- **Code does the math:** The LLM never computes a number we report.
- **Fixed output shape:** Answers come back in a checked format, or they're rejected.
- **Check the plan first:** Validate what it intends to do before it does it.
- **People at the writes:** Approval before anything is sent, changed, or published.
- **Limits and a kill switch:** Rate limits, circuit breakers, an off button, and full logs.

**Footer:** Controls named in OCC Bulletin 2026-54; plan validation after Huyen, *AI Engineering*

**Notes:** Why these matter: agents fail in ways a demo never shows. They pick the wrong tool or wrong inputs, declare a task done when it isn't, loop and burn cost, or follow instructions hidden in a document they read. A 2% failure rate is invisible in a demo and very visible at volume. Each guardrail here is ordinary engineering, and none of it requires trusting the model to behave.

---

## Slide 9 — The regulator

**Eyebrow:** The regulator thinks the same way
**Title:** The OCC sets risk by the dial, not by how clever the model is.

**Left column:**
- Tiers turn on three things: **what happens if it's wrong**, **how much agency it's given**, and **how much a person oversees it**.
- A simple rules-based agent that can move money can be riskier than an advanced model that only drafts internal documents.
- Guidance for examiners, not new rules for banks. "Super intelligence" is the OCC's new term for AI.

**Right column:**

| Tier | Illustrative use |
|---|---|
| 1 · Critical | Autonomous, customer-facing payment agent |
| 2 · High | Agent-initiated customer communications |
| 3 · Moderate (shaded) | Internal summarization, research assist |
| 4 · Low (shaded) | Internal productivity, code assistance |

**Footer:** OCC Bulletin 2026-54, Supervisory Framework (Nov 4, 2026) · Shaded = where to start

**Notes:** Issued today. It fills the gap left by April's model risk guidance, which excluded generative and agentic AI. The tiers line up with the dial: Build and Assist work lands in the lower tiers, and Act with customer impact lands at the top. The framework is examiner guidance, but it shows how exams will be scoped.

---

## Slide 10 — The litmus test

**Eyebrow:** The litmus test
**Title:** Eight questions to ask about any agent.

1. What tools can it call?
2. Can any of them change data or send something?
3. Who approves before it does?
4. How would we know if it's wrong?
5. What did we test it against?
6. Where are the logs?
7. Who owns it?
8. What happens if we turn it off?

**Closing line:** Can't answer them? It's a demo, not a system.
**Footer:** Mirrors the Purpose pillar of OCC Bulletin 2026-54

**Notes:** Hand these to every leader. They're not my opinion; they track what the OCC's framework says an examiner will ask: what a system may do, who may invoke it, which data and systems it can reach, what actions it can take, and when it must stop for review.

---

## Slide 11 — In your team

**Eyebrow:** In your team
**Title:** Good first candidates pass three filters.

Three columns:
- **It recurs:** Weekly or monthly work someone rebuilds by hand.
- **The rules can be written down:** You could explain "done right" to a new hire.
- **Mistakes are easy to catch:** Someone reviews it before it matters, and it can be undone.

**Body:** Passes all three? Start at Build or Assist. Fails the last one? Keep a person at every step.

**Notes:** This is the practical takeaway. Most teams have a reporting cycle, a reconciliation, a recurring summary, or a data pull that passes all three. Those are better first projects than anything that sounds like an "agent."

---

## Slide 12 — Close (dark)

**Eyebrow:** Take it back to your team
**Title:** Start low on the dial. Move up on evidence.

Three prompts:
- What do we rebuild by hand every month?
- Where do people copy numbers from one system to another?
- If AI did it, what would we check first?

**Notes:** End on the three questions, not on risk. Invite leaders to bring their answers back; that list becomes the pipeline of real use cases.

---

## Backup — Evaluation

**Eyebrow:** Backup · evaluation
**Title:** One good run proves nothing.

Three cards:
- **Ng · Read the traces:** Do error analysis on real runs. Evaluate each step as well as the final answer.
- **Huyen · Define "correct" first:** Eval-driven development means success criteria and a test set before you build.
- **OCC · Test repeatedly:** Outputs vary run to run, so test many times against a consistency bar. An LLM judge needs its own validation.

**Body:** This is model validation discipline applied to a new kind of system, and it's work our analysts already know how to do.
**Footer:** Ng, DeepLearning.AI *Agentic AI*; Huyen, *AI Engineering*; OCC Bulletin 2026-54

**Notes:** Use this if someone asks "how do you know it works?" The scarce skill isn't the plumbing; it's writing the eval criteria and reading the failures, which is domain work.

---

## Placeholders to fill

- Slide 1: [Your name], [Date]
- Slide 5: [hours saved per cycle]

## Sources

- OCC News Release 2026-97 / Bulletin 2026-54, "Super Intelligence: Supervisory Framework" (Nov 4, 2026): https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-97.html
- Andrew Ng, *Agentic AI*, DeepLearning.AI
- Chip Huyen, *AI Engineering* (O'Reilly, 2025)
