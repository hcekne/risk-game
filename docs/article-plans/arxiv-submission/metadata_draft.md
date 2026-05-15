# arXiv Metadata Draft

## Primary Category

`cs.AI`

## Cross-list Recommendation

`cs.CL`

## License Recommendation

**Recommended license:** `CC BY 4.0`

Reason:

- it is the most permissive standard Creative Commons option you are likely to want for a paper
- it preserves attribution
- it is aligned with the fact that your code and artifacts are already public
- it is cleaner for reuse, translation, excerpting, and derivative discussion than more restrictive `NC` or `ND` options

Important note:

- arXiv says they cannot advise which license is right for your situation
- once a version is public, that version's license cannot be changed
- if you later target a venue with unusual copyright rules, re-check before final submission

## Title

Evaluating LLMs as Live Strategic Agents: Provider Ranking, Hybrid Decomposition, and Operational Gaps in Timed Risk Play

## Authors

H. C. Ekne

## Comments

14 pages, 7 figures. Code, manuscript sources, and tracked experiment notes: https://github.com/hcekne/risk-game

## Journal Reference

Leave blank for now.

## DOI

Leave blank for now.

## Report Number

Leave blank unless you want to assign one.

## Abstract

Static benchmark scores are an incomplete proxy for how large language models behave inside real agent loops. We evaluate frontier and near-frontier LLMs in a timed multi-phase Risk environment with constrained output grammar, explicit victory targets, and repeated planning/execution cycles. In a replicated 32-game cross-provider championship under frozen rules, gemini-3.1-pro-preview was the strongest full-stack live agent, winning 20 of 32 games against gpt-5.1, claude-opus-4-7, and kimi-k2.6; the pooled winner distribution differs strongly from the equal-strength null (p approx 1.5 x 10^-5). However, the main applied result is not only a provider leaderboard. Once execution is standardized to a shared cheap Gemini Flash scaffold, the provider spread compresses sharply, and a pooled 32-game planner bakeoff is consistent with near-equality (p approx 0.821). We then analyze saved planning and execution traces from the provider championship. Gemini's visible plans reference the terminal objective far more often than the others and scale that objective tracking as victory approaches. On execution, Gemini is not the cleanest runtime, but it converts more turns into deep conquest chains than the rest of the field. These findings suggest that live-agent performance depends on the interaction between objective tracking, execution conversion, cost, and runtime reliability, not just benchmark rank or release recency.
