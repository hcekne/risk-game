# Testing Guide

## Test Tiers

### Regression tests
- Purpose: protect game logic and state transitions
- Must be deterministic
- Must not call live model APIs
- Must run inside the `risk-game` container
- Command:
  ```bash
  make test
  ```

### Live API tests
- Purpose: manually check provider integrations and prompt/format behavior
- May require credentials, network access, and incur cost
- Never part of the default regression gate
- Command:
  ```bash
  make test-live
  ```

### Provider canaries
- Purpose: verify that configured provider keys can complete real paid requests
- Current canaries:
  - OpenAI: `gpt-5.4-nano` replying `OK`
  - Gemini: `gemini-3.1-pro-preview` answering `What is the capital of Norway?`
  - Moonshot: `kimi-k2.6` answering `What is the capital of Norway?`
- Combined command:
  ```bash
  make test-live-canary
  ```
- Provider-specific commands:
  ```bash
  make test-live-canary-openai
  make test-live-canary-gemini
  make test-live-canary-moonshot
  ```

## What Real Game-Logic Tests Should Cover
- Territory ownership invariants:
  - every territory has exactly one owner
  - no negative troop counts
  - board size remains 42 territories
- Move validation:
  - initial placement legality
  - troop placement totals
  - attack legality
  - fortify legality
- State transitions:
  - successful attacks transfer control correctly
  - failed attacks preserve defender control
  - fortify moves transfer troops correctly
  - player elimination updates active/dead player lists
- Rules:
  - continent bonuses
  - capital control
  - card trade validation
  - max-round winner logic
- Parsing:
  - expected Risk response format is parsed correctly
  - malformed model output fails safely

## Recommended Pattern
1. Build a small board state with stub players and no live API calls.
2. Apply one game action.
3. Assert the exact resulting state.
4. Assert board invariants still hold.

The current regression helpers live in `tests/helpers.py`.
