# Cross-Provider Frontier Strategic Full 16 Retry 2: Salvage Plan

## Identity

- Suite: `2026-Q2 Strategic Tests`
- Experiment label: `frontier_strategic_full_16_retry_2`
- Raw local artifacts: `/shared-game-results/experiments/experiment__2026-05-04_21-00-11__frontier_strategic_full_16_retry_2`
- Status: partial valid subset plus planned top-up

## Why This Batch Is Not Clean As-Is

This rerun completed all `16` games, but it is not a clean scored batch because Anthropic credits ran out mid-run.

Observed provider contamination:
- games `7-12` contain repeated Anthropic low-credit failures:
  - `Your credit balance is too low to access the Anthropic API`
- those billing failures affect only `claude-opus-4-7` in this batch
- no Gemini quota failures were observed in this rerun
- games `13-16` appear clean again after the Anthropic refill

Because the failure window is localized and the setup parser bug had already been fixed before this rerun, this batch can be salvaged by retaining only the uncontaminated games and then filling the missing seat rotations with a dedicated top-up batch.

## Clean Subset To Keep

Retain these games from `frontier_strategic_full_16_retry_2`:
- games `1-6`
- games `13-16`

Discard these games as invalid because of Anthropic billing failure:
- games `7-12`

This leaves a clean `10`-game subset.

Clean-subset winners:
- `gemini-3.1-pro-preview`: `6`
- `gpt-5.1`: `2`
- `claude-opus-4-7`: `2`
- `kimi-k2.6`: `0`

## Seat-Balance Repair Plan

The retained `10` games are not perfectly seat-balanced, so they should not be reported as the final research-facing provider result by themselves.

To restore the intended `16`-game balanced provider batch, append a clean `6`-game top-up with a deliberately chosen base seat order.

Top-up roster file:
- [configs/experiments/2026_q2_cross_provider_frontier_strategic_topup_6.json](../../../configs/experiments/2026_q2_cross_provider_frontier_strategic_topup_6.json)

Top-up command-book entry:
- [scripts/experiment_commands.sh](../../../scripts/experiment_commands.sh) line `6`

Top-up experiment label:
- `frontier_strategic_topup_6`

Top-up base seat order:
1. `gemini-3.1-pro-preview`
2. `kimi-k2.6`
3. `gpt-5.1`
4. `claude-opus-4-7`

With the normal 4-player seat rotation, that 6-game top-up contributes the exact missing seat counts needed to bring every provider to `4` appearances in each seat across the final combined `16` valid games.

## How To Compile The Final Balanced Experiment Later

If and only if the top-up batch runs clean, the final provider experiment should be compiled from:

1. `frontier_strategic_full_16_retry_2`
   - keep games `1-6`
   - keep games `13-16`
   - drop games `7-12`
2. `frontier_strategic_topup_6`
   - keep all `6` games if they are clean

That yields a combined `16`-game provider dataset with restored seat balance.

If the top-up run is itself quota/billing contaminated, do not partially splice around that contamination unless the same seat-balance repair logic is recomputed explicitly and recorded in a new tracked note.

## Practical Interpretation

Until the top-up is finished and validated, this retry should be treated as:
- stronger than the earlier invalid retry
- useful for directional analysis
- not yet the final scored cross-provider championship result
