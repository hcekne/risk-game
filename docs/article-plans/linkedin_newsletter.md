# The Best LLM Isn’t the One That Tops the Benchmark
## What a live Risk tournament taught me about planning, execution, cost, and why production AI systems should be built as stacks, not single-model bets

In 2024, I ran an early experiment to test whether large language models could play Risk strategically. That first round was interesting, but it was still a first pass: fewer games, fewer controls, and a much narrower view of what “good performance” actually means inside a live system. This year, I went much further. I ran a much larger set of replicated Risk experiments across frontier and near-frontier models, split planning from execution, measured costs, tracked fallbacks and timeouts, and analyzed the models’ actual planning traces. The result is not just a leaderboard. It is a deeper lesson about how LLM systems really work when they are forced to operate inside a bounded, adversarial, timed environment. And the main takeaway is one that I think every builder using LLMs in production should pay attention to: the smartest-looking model is often not the best system component.

## In Brief

- **Benchmark strength does not equal operational strength.**  
  Some models that look excellent on public benchmarks performed much worse when they had to act repeatedly inside a timed, multi-step decision loop. For production builders, this matters because most real systems are loops, not one-shot prompts.

- **Execution matters more than many people expect.**  
  Once I standardized the execution layer across models, a lot of the differences between providers shrank. That suggests many model comparisons are partly measuring runtime behavior, latency, and action conversion, not just abstract reasoning quality.

- **Hybrid systems can beat monolithic ones.**  
  One of the strongest applied findings was that a more expensive single-model setup was not the best practical answer. A hybrid with a stronger planner and a cheaper execution layer delivered a better cost-performance profile.

- **Open-source and benchmark-optimized models may be closer on paper than in practice.**  
  Some models that appear nearly frontier-level in benchmark discourse were much less convincing in this live strategic setting. For practitioners, this is a warning: a benchmark-near model may still be several months behind where it matters operationally.

## From “Which model is smartest?” to “Which system actually works?”

That shift is really the center of the whole project.

When most people compare LLMs, they ask a relatively simple question: which model scores highest on a test? That is useful, but it is incomplete. In real applications, models don’t just answer a question once. They operate inside workflows. They get partial information, produce structured actions, hit latency constraints, recover from mistakes, and interact with other agents or systems that push back.

Risk turned out to be a very useful environment for studying this.

It forces a model to do several things at once: pursue a long-term objective, sequence actions over multiple phases, adapt to opponents, balance local tactical gains against global position, and close out a win condition under pressure. It is also noisy enough to be realistic, but structured enough to analyze.

That makes it a good test not only of “reasoning” in the abstract, but of something more important for builders: live agent performance.

## The first big result: there is a real full-stack winner

Across the strongest cross-provider setup I tested, one provider stood out clearly in full-stack play: Gemini.

That result replicated.

This matters because it tells us the outcome was not just a lucky small-sample blip. But the more interesting point is *why* Gemini won. It was not simply because it was “smarter” in a vague sense. It seems to be better at staying locked on the objective and converting turns into decisive conquest chains.

That is a very different type of strength than what most benchmarks measure.

In practice, it means a model may be particularly strong not because it writes the most impressive explanation, but because it keeps driving toward the goal while the rest drift, stall, overthink, or burn budget on less useful reasoning.

## The second big result: planner differences shrink when execution is fixed

This was maybe the most important systems finding in the whole project.

After identifying Gemini as the strongest full-stack player, I ran a different kind of experiment. Instead of letting every provider do everything, I standardized the execution layer and only changed the planning model.

In other words: same operational scaffold, different “brains” writing the plan.

Once I did that, the provider spread compressed sharply.

That tells us something important: a meaningful part of what people call “model performance” is actually **system performance**. It is about how well the model functions inside a specific loop, under specific constraints, with specific action formatting and time budgets.

For builders, this is a big deal.

If your product has a planning phase, an action phase, and a monitoring phase, it is entirely possible that you should *not* use the same model for all three. And it is also possible that the most expensive model is only worth using in one of those stages.

## The third result: cheaper hybrids can be better engineering choices

This is where the experiments become directly useful for anyone shipping with APIs.

After the early rounds, I started looking seriously at cost. Not just who wins, but what each architecture costs per game, per win, and per useful unit of strategic output.

One of the clearest applied findings was that a hybrid setup using stronger Gemini planning with a much cheaper Gemini execution layer performed extremely well. It beat a more expensive monolithic configuration on practical terms.

That is exactly the kind of result that matters in production.

Because at some point, every builder runs into the same question: do I really need the frontier model for the whole pipeline?

Often, the answer is no.

You may need the stronger model for goal formation, decomposition, or strategic planning. But for repeated, tightly scoped execution steps, a cheaper and faster model may be more than enough. If that is true, the right architecture is a stack, not a single-model choice.

That is a much more useful lesson than yet another abstract leaderboard.

## The Kimi result is a warning about benchmark narratives

Another thread I wanted to explore was the gap between benchmark reputation and operational performance.

Kimi is interesting here because it is frequently discussed as being very close to the top closed models. On some benchmark narratives, it can sound as if the gap is only a few months.

In these Risk experiments, that story did not hold up cleanly.

Kimi was often competitive with older strong closed-model tiers. But it did not look like a current frontier-class live agent. In some direct comparisons, it looked closer to models from an earlier capability band than the public discourse would suggest.

I want to be careful here. This does *not* mean “Kimi is bad,” and it does not mean benchmarks are useless. It means something narrower and more important: benchmark proximity does not guarantee operational equivalence.

For production teams, this is a serious caution. If a model is being optimized to look good on public test suites, that may not fully translate into long-horizon objective pursuit inside a live system.

## The mechanism story may be the most interesting part

The ranking results matter, but the deeper story is about *how* the stronger models seem to win.

When I looked into the planning traces, Gemini appeared much more explicitly goal-directed than the others. Its plans more often referenced the distance to victory, the number of territories still needed, and the fastest route to closing the game.

That matters because good agents are not just reactive. They keep a live objective model in memory and keep updating against it.

Then, when I looked at execution traces, Gemini was not always the cleanest runtime. Claude, for example, was often cleaner operationally in some conditions. But Gemini was better at turning turns into deep conquest chains and meaningful midgame territory conversion.

That gives a more satisfying explanation than “Gemini is just better.”

It suggests that the real edge may be a combination of:
- stronger objective tracking
- more aggressive but coherent execution
- better conversion of planning into actual board gains

That is exactly the kind of insight that matters when you build real agent systems.

## So what should builders take from this?

Three things.

First, stop assuming that benchmark leaders are automatically the best production models.

Second, stop assuming the best system uses one model end to end.

Third, measure the whole loop.

That means tracking not just answer quality, but:
- latency
- cost
- fallbacks
- timeout behavior
- action conversion
- and whether the model actually stays aimed at the objective

Because in the end, that is what your users experience.

They do not experience a benchmark score.  
They experience a system.

## Where this goes next

This second round of Risk experiments started as a strategic-model comparison project. But it ended up pushing me toward a broader conclusion about LLM architecture.

The important question is no longer just: *Which model is best?*

It is: *Which model should do which part of the work?*

That is a much more practical question. It is also a more mature one.

And I suspect it is where a lot of serious AI system design is headed next.

If the first generation of LLM products was about picking the strongest model, the next generation will be about designing the strongest stack.
