# Live-Agent Risk Paper Arc

## Working Thesis

Static benchmark scores and brand-level model prestige are poor proxies for live agent quality.

In a bounded strategic environment with real turn timers, parser constraints, and multi-phase decision loops:
- the best end-to-end agent is not necessarily the newest or most expensive model
- system decomposition across planning and execution can matter more than raw model rank
- lower-cost alternatives that look frontier-adjacent on benchmarks can still lag materially in operational play

## What The Paper Is Actually About

This paper should **not** be framed as:
- “the universal intelligence ranking of LLMs”
- “Risk proves model X is smarter than model Y”
- “we solved strategic reasoning”

It should be framed as:

**A live-agent systems study of LLM strategic behavior under bounded execution constraints.**

That is stronger, more honest, and more broadly useful.

## Reader Contract

By the end of the paper, the reader should understand four things:

1. Why benchmark-adjacent model claims can fail in live agent loops.
2. Why the execution scaffold matters so much.
3. Why provider differences shrink once execution is standardized.
4. How to think about building cheaper, stronger hybrid LLM systems in practice.

## One-Sentence Abstract

We evaluate frontier and near-frontier LLMs in a timed multi-phase Risk environment and show that live-agent performance depends heavily on execution scaffolding, objective tracking, and timeout resilience, with Gemini emerging as the strongest full-stack provider while planner-only differences compress sharply once execution is standardized to a shared cheap scaffold.

## Section Arc

### 1. Introduction

Open with the real problem:
- developers do not deploy models as abstract chatbots
- they deploy them inside bounded workflows with timers, format constraints, and repeated action loops
- benchmark rank does not tell them which model stack will actually work best there

Close the section with the paper question:

> What changes when we evaluate LLMs as live strategic agents instead of static benchmark respondents?

### 2. Why Risk Is A Useful Agent Benchmark

Explain why Risk is useful:
- long-horizon objective
- multi-step attack chains
- adversarial multi-agent environment
- constrained action grammar
- repeated planning/execution loop
- cheap enough to run repeatedly, rich enough to expose system behavior

Important tone:
- do not oversell Risk as a universal intelligence test
- sell it as a controlled live-agent benchmark with enough strategic structure to expose operational differences

### 3. Experimental Harness

Describe the system clearly and compactly:
- turn structure
- planning phase vs execution phases
- timer policy
- parser/output grammar
- legality assistance from the engine
- live-provider logging
- primary endpoint = wins under `65%` territory control
- secondary endpoints = attack conversion, fallback burden, strategic score, token usage, estimated cost

This section must be very explicit, because both humans and AIs need the setup to be machine-readable and reproducible.

### 4. Main Full-Stack Result: Gemini Wins The Provider Field

Lead with the strongest replicated result:
- provider replicate 1
- provider replicate 2
- pooled `32`
- Gemini `20 / 32`

Key claim:
- Gemini is the current full-stack leader in this frozen live strategic condition

Important nuance:
- this is not “Gemini is universally best”
- it is “Gemini is the strongest tested full-stack live agent in this harness”

### 5. Newest / Most Expensive Does Not Mean Best

This is where the OpenAI lineage work fits.

Use the `gpt-5.1` result:
- newer OpenAI variants did not automatically beat it in this live loop

Key lesson:
- synchronous agent loops punish overthinking, latency, and execution drag
- model release prestige and static benchmark strength are not enough

This section broadens the relevance beyond provider rivalry.

### 6. Kimi And The Benchmark Mirage

This is the sharp public-interest section.

Use the anchor results:
- near `gpt-4.1`
- below `gemini-2.5-pro`
- competitive with older Anthropic Sonnet 4 tier
- far below pooled Gemini `3.1`

Framing:
- Kimi 2.6 arrives roughly `10-13` months after Gemini 2.5 Pro, yet only reaches near-parity or modestly trails that older Gemini tier in this live environment

Claim carefully:
- not “months behind” as a theorem
- but “our live-agent anchors place it closer to older strong closed tiers than to current frontier leaders”

This is the section likely to travel furthest in public discussion.

### 7. The System Design Turn: Decomposition Beats Monolithic Thinking

This is probably the most important section for builders.

Show:
- cost gate result
- `gemini-3.1` planning + `gemini-3-flash` execution
- cheaper than `gemini-3.1` full-stack
- strong enough to become the practical scaffold

Then show the planner bakeoff result:
- once execution is standardized to Flash, the provider spread compresses sharply

Main conclusion:
- much of the earlier “model difference” was really **system architecture difference**

This is the section that upgrades the paper from a leaderboard report to a systems paper.

### 8. Mechanism 1: Goal-Directed Planning Traces

Use the planning-trace note:
- Gemini references the win condition explicitly in `58.5%` of saved plans
- Claude `3.1%`
- GPT `0.4%`
- Kimi `1.4%`
- Gemini goal tracking rises from `39.8%` early to `100%` late

Claim:
- Gemini appears to maintain the terminal objective more explicitly in its observable planning traces

This is your first mechanism section.

### 9. Mechanism 2: Execution Conversion

Use the execution-trace note:
- Gemini is not the cleanest runtime
- Claude is cleaner
- GPT is similarly aggressive but timeout-dragged
- Gemini wins because it converts more turns into deep conquest chains

Key numbers:
- Gemini `6+` conquest-turn share `38.7%`
- Claude `28.9%`
- GPT `23.4%`
- Kimi `26.7%`

Claim:
- the winner is the model that best couples acceptable reliability with high-yield attack chaining

This is the second mechanism section.

### 10. Implications For Building LLM Systems

This is where the paper pays off for practitioners.

State the design lessons directly:
- evaluate models inside workflows, not just on benchmarks
- split planning and execution when it helps
- optimize for objective tracking and conversion, not only apparent sophistication
- track cost and fallback burden explicitly
- pick a benchmark agent that is both strong and affordable

This section should read like a translation layer from the experiments into general engineering practice.

### 11. Limitations

Be unusually explicit here.

List:
- one game domain
- one prompt grammar family
- one specific timer regime
- planning-trace analysis is observational
- anchor-based “months behind” interpretation is approximate
- some planner-only comparisons remain inconclusive

Strong limitations make the paper more credible, not less.

### 12. Conclusion

End with the simplest version of the message:

> Live-agent quality is a systems property, not a benchmark rank.

Then summarize:
- Gemini won the full-stack field
- Kimi was materially behind the current frontier despite strong benchmark reputation
- cheap hybrid decomposition produced a more practical benchmark agent
- once execution was standardized, planner differences narrowed sharply

## Figures And Tables To Include

### Core figures
- provider `32`-game pooled win chart
- Kimi anchor comparison table
- Flash cost-gate cost/performance chart
- planner-bakeoff pooled `32` result showing compression
- goal-directedness trace chart
- execution chain-distribution chart

### Core tables
- full experiment roster / timer protocol table
- pooled provider metrics
- Kimi anchor summary table
- planning-trace feature table
- execution-trace feature table

## Claim Discipline

### Claims you can make strongly
- Gemini is the strongest full-stack provider in this tested harness.
- Kimi is not operationally frontier-class here.
- Cost-aware decomposition can improve practical deployment value.
- Standardizing execution compresses a large part of the provider spread.

### Claims that should stay softer
- exact universal planner ranking
- exact “N months behind” statement
- broad generalization to all agent domains
- causal proof that goal-directed language causes better play

## Human + AI Readability Rules

The paper should be easy for both humans and AIs to parse.

That means:
- define the primary endpoint early and repeat it
- use exact dates and exact model names
- separate “established” from “suggestive” claims explicitly
- keep the protocol table compact and machine-readable
- keep section openings declarative
- avoid rhetoric that hides the inferential boundary
- keep footnote-level caveats near the claim they qualify

## Recommended Writing Order

1. Methods
2. Provider `32` result
3. Kimi anchor section
4. Cost gate / hybrid scaffold section
5. Goal-directedness trace section
6. Execution trace section
7. Implications
8. Introduction
9. Conclusion
10. Abstract

That order is easier because the paper’s narrative is evidence-first.

## Practical Bottom Line

The story is strong enough now for a preprint if it is framed as:

**a study of live-agent LLM systems under bounded strategic execution**

That is the strongest and most defensible version of the work.
