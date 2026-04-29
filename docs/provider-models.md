# Provider Models Snapshot

Generated: 2026-04-27

This file separates three different questions:

1. What model IDs are visible in the provider account right now?
2. Which of those model IDs are already wired into this repo?
3. Which provider/API path should we use next if we add support?

## Sources

- OpenAI live account snapshot:
  - Queried from inside the `risk-game` container via `GET https://api.openai.com/v1/models`
- Anthropic live account snapshot:
  - Queried from inside the `risk-game` container via `GET https://api.anthropic.com/v1/models`
- Gemini live account snapshot:
  - Queried from inside the `risk-game` container via `GET https://generativelanguage.googleapis.com/v1beta/models`
- Moonshot live account snapshot:
  - Queried from inside the `risk-game` container via `GET https://api.moonshot.ai/v1/models`
- OpenAI official docs:
  - https://platform.openai.com/docs/models
- Anthropic official docs:
  - https://docs.anthropic.com/en/docs/models-overview
- Gemini official docs:
  - https://ai.google.dev/api/interactions-api
  - https://ai.google.dev/gemini-api/docs/models
  - https://cloud.google.com/vertex-ai/generative-ai/docs/models

## Current Repo Support

The repo is now wired for the current OpenAI, Anthropic, Gemini, and Moonshot text-model surfaces through the shared `create_llm_client()` and `AgentSpec` paths.

References:
- [risk_game/llm_clients/openai_client.py](/home/hcekne/repos/risk-game/risk_game/llm_clients/openai_client.py:1)
- [risk_game/llm_clients/anthropic_client.py](/home/hcekne/repos/risk-game/risk_game/llm_clients/anthropic_client.py:1)
- [risk_game/llm_clients/gemini_client.py](/home/hcekne/repos/risk-game/risk_game/llm_clients/gemini_client.py:1)
- [risk_game/llm_clients/moonshot_client.py](/home/hcekne/repos/risk-game/risk_game/llm_clients/moonshot_client.py:1)
- [risk_game/llm_clients/llm_client.py](/home/hcekne/repos/risk-game/risk_game/llm_clients/llm_client.py:1)

### OpenAI

Explicit OpenAI model strings now work for the main Risk-relevant text families, including snapshots:

- `gpt-5.5`
- `gpt-5.5-pro`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-5.4-pro`
- `gpt-5`
- `gpt-5-mini`
- `gpt-5-nano`
- `gpt-5-pro`
- `gpt-5.1`
- `gpt-5.2`
- `gpt-5.2-pro`
- `gpt-4.1`
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `gpt-4o`
- `gpt-4o-mini`
- `o3`
- `o3-mini`
- `o3-pro`
- `o4-mini`

Notes:
- explicit model IDs are preferred over legacy numeric selectors
- snapshot IDs like `gpt-5.5-2026-04-23` also resolve
- model-specific reasoning validation is enforced where the official docs are explicit
- for a few reasoning-first families where the docs do not publish one stable local table, the client accepts standard reasoning labels and lets the API return the authoritative error if a specific model rejects one

### Anthropic

Explicit Anthropic model strings now work for the current live account surface:

- `claude-opus-4-7`
- `claude-sonnet-4-6`
- `claude-opus-4-6`
- `claude-opus-4-5-20251101`
- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1-20250805`
- `claude-opus-4-20250514`
- `claude-sonnet-4-20250514`

Notes:
- the client also maps older aliases like `claude-sonnet-4-0` to the concrete current snapshot we support
- extended thinking is only enabled when the client is created with `enable_thinking=True`
- adaptive-thinking models can use `thinking_effort`
- manual-thinking models use `thinking_budget`, with per-call reasoning overrides mapped onto practical budget sizes

### Gemini

The repo now has a Gemini client via the Gemini Developer API REST surface.

Core Gemini model aliases supported directly:

- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-3-pro-preview`
- `gemini-3-flash-preview`
- `gemini-3.1-pro-preview`
- `gemini-3.1-flash-lite-preview`

Notes:
- any explicit model string that starts with `gemini-` is accepted
- explicit Gemini list responses like `models/gemini-3.1-pro-preview` are normalized automatically
- Gemini 3 models map the repo’s reasoning knob onto `thinkingLevel`
- Gemini 2.5 models map it onto `thinkingBudget`
- live Gemini runs require `GEMINI_API_KEY` or `GOOGLE_API_KEY`

### Moonshot

The repo now has a Moonshot client via Moonshot's OpenAI-compatible API surface.

Core Moonshot model aliases supported directly:

- `kimi-k2.6`
- `kimi-k2.5`
- `moonshot-v1-auto`
- `moonshot-v1-8k`
- `moonshot-v1-32k`
- `moonshot-v1-128k`

Notes:
- live Moonshot runs require `MOONSHOT_API_KEY`
- the current repo client uses Moonshot's chat-completions-compatible path
- `kimi-k2.6` is the first model we should treat as the benchmark candidate for cross-provider Risk experiments

### Mixed Provider Usage

The experiment layer can now mix these providers directly:

```python
from risk_game.experiments import AgentSpec, Experiment
from risk_game.game_config import GameConfig

experiment = Experiment(
    config=GameConfig(progressive=True, capitals=False, max_rounds=10),
    num_games=3,
    agent_specs=[
        AgentSpec("openai", "OpenAI", "gpt-5.5", reasoning_effort="high"),
        AgentSpec(
            "anthropic",
            "Anthropic",
            "claude-sonnet-4-6",
            enable_thinking=True,
            thinking_effort="medium",
        ),
        AgentSpec(
            "gemini",
            "Gemini",
            "gemini-3-flash-preview",
            reasoning_effort="high",
        ),
    ],
)
```

## OpenAI: Live Account Snapshot

### Short answer

Yes, your current OpenAI account can see:

- `gpt-5.5`
- `gpt-5.5-pro`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-5.4-pro`

It can also see older and parallel families like:

- `gpt-5`
- `gpt-5-mini`
- `gpt-5-nano`
- `gpt-5-pro`
- `gpt-5.1`
- `gpt-5.2`
- `gpt-5.3-chat-latest`
- `gpt-4.1`
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `gpt-4o`
- `gpt-4o-mini`
- `o1`
- `o3`
- `o3-mini`
- `o3-pro`
- `o4-mini`

### Most relevant text/reasoning model IDs for Risk experiments

- `gpt-5.5`
- `gpt-5.5-pro`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-5.4-pro`
- `gpt-5`
- `gpt-5-mini`
- `gpt-5-nano`
- `gpt-5-pro`
- `gpt-5.1`
- `gpt-5.2`
- `gpt-5.2-pro`
- `gpt-4.1`
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `gpt-4o`
- `gpt-4o-mini`
- `o3`
- `o3-mini`
- `o3-pro`
- `o4-mini`

### Other OpenAI model IDs currently visible in the account

```text
gpt-3.5-turbo
gpt-3.5-turbo-0125
gpt-3.5-turbo-1106
gpt-3.5-turbo-16k
gpt-3.5-turbo-instruct
gpt-3.5-turbo-instruct-0914
gpt-4
gpt-4-0613
gpt-4-turbo
gpt-4-turbo-2024-04-09
gpt-4.1
gpt-4.1-2025-04-14
gpt-4.1-mini
gpt-4.1-mini-2025-04-14
gpt-4.1-nano
gpt-4.1-nano-2025-04-14
gpt-4o
gpt-4o-2024-05-13
gpt-4o-2024-08-06
gpt-4o-2024-11-20
gpt-4o-audio-preview
gpt-4o-audio-preview-2024-12-17
gpt-4o-audio-preview-2025-06-03
gpt-4o-mini
gpt-4o-mini-2024-07-18
gpt-4o-mini-audio-preview
gpt-4o-mini-audio-preview-2024-12-17
gpt-4o-mini-realtime-preview
gpt-4o-mini-realtime-preview-2024-12-17
gpt-4o-mini-search-preview
gpt-4o-mini-search-preview-2025-03-11
gpt-4o-mini-transcribe
gpt-4o-mini-transcribe-2025-03-20
gpt-4o-mini-transcribe-2025-12-15
gpt-4o-mini-tts
gpt-4o-mini-tts-2025-03-20
gpt-4o-mini-tts-2025-12-15
gpt-4o-realtime-preview
gpt-4o-realtime-preview-2024-12-17
gpt-4o-realtime-preview-2025-06-03
gpt-4o-search-preview
gpt-4o-search-preview-2025-03-11
gpt-4o-transcribe
gpt-4o-transcribe-diarize
gpt-5
gpt-5-2025-08-07
gpt-5-chat-latest
gpt-5-codex
gpt-5-mini
gpt-5-mini-2025-08-07
gpt-5-nano
gpt-5-nano-2025-08-07
gpt-5-pro
gpt-5-pro-2025-10-06
gpt-5-search-api
gpt-5-search-api-2025-10-14
gpt-5.1
gpt-5.1-2025-11-13
gpt-5.1-chat-latest
gpt-5.1-codex
gpt-5.1-codex-max
gpt-5.1-codex-mini
gpt-5.2
gpt-5.2-2025-12-11
gpt-5.2-chat-latest
gpt-5.2-codex
gpt-5.2-pro
gpt-5.2-pro-2025-12-11
gpt-5.3-chat-latest
gpt-5.3-codex
gpt-5.4
gpt-5.4-2026-03-05
gpt-5.4-mini
gpt-5.4-mini-2026-03-17
gpt-5.4-nano
gpt-5.4-nano-2026-03-17
gpt-5.4-pro
gpt-5.4-pro-2026-03-05
gpt-5.5
gpt-5.5-2026-04-23
gpt-5.5-pro
gpt-5.5-pro-2026-04-23
gpt-audio
gpt-audio-1.5
gpt-audio-2025-08-28
gpt-audio-mini
gpt-audio-mini-2025-10-06
gpt-audio-mini-2025-12-15
gpt-image-1
gpt-image-1-mini
gpt-image-1.5
gpt-image-2
gpt-image-2-2026-04-21
gpt-realtime
gpt-realtime-1.5
gpt-realtime-2025-08-28
gpt-realtime-mini
gpt-realtime-mini-2025-10-06
gpt-realtime-mini-2025-12-15
o1
o1-2024-12-17
o1-pro
o1-pro-2025-03-19
o3
o3-2025-04-16
o3-deep-research
o3-deep-research-2025-06-26
o3-mini
o3-mini-2025-01-31
o3-pro
o3-pro-2025-06-10
o4-mini
o4-mini-2025-04-16
o4-mini-deep-research
o4-mini-deep-research-2025-06-26
omni-moderation-2024-09-26
omni-moderation-latest
```

## Anthropic: Live Account Snapshot

Your live Anthropic account currently lists:

```text
claude-opus-4-7
claude-sonnet-4-6
claude-opus-4-6
claude-opus-4-5-20251101
claude-haiku-4-5-20251001
claude-sonnet-4-5-20250929
claude-opus-4-1-20250805
claude-opus-4-20250514
claude-sonnet-4-20250514
```

### Most relevant Anthropic model IDs for Risk experiments

- `claude-sonnet-4-6`
- `claude-opus-4-7`
- `claude-opus-4-6`
- `claude-sonnet-4-20250514`
- `claude-opus-4-20250514`

### Important repo note

The Anthropic client should be updated before live experiments so it can use these current IDs directly instead of the stale alias map.

## Gemini: Current Official Model Surface

We did not run a live Gemini account listing because Gemini is not configured in this environment yet.

The current official Gemini API docs show these model/agent options on the Interactions API page:

### Core Gemini text/reasoning models

- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-3-flash-preview`
- `gemini-3-pro-preview`
- `gemini-3.1-pro-preview`
- `gemini-3.1-flash-lite-preview`

### Gemini image/audio/tts/computer-use variants

- `gemini-2.5-flash-image`
- `gemini-2.5-flash-native-audio-preview-12-2025`
- `gemini-2.5-flash-preview-tts`
- `gemini-2.5-pro-preview-tts`
- `gemini-3-pro-image-preview`
- `gemini-3.1-flash-image-preview`
- `gemini-3.1-flash-tts-preview`
- `gemini-2.5-computer-use-preview-10-2025`

### Gemini agent options shown in the docs

- `deep-research-pro-preview-12-2025`
- `deep-research-preview-04-2026`
- `deep-research-max-preview-04-2026`

### Deprecated Gemini models called out in the docs

- `gemini-2.0-flash`
- `gemini-2.0-flash-lite`

Reference:
- Google’s Gemini models page was last updated `2026-04-22 UTC`

## Where Gemini Calls Should Run

If we add Gemini next, the simplest path is the Gemini Developer API / Gemini API, not Vertex AI.

Use:

- endpoint: `https://generativelanguage.googleapis.com/v1beta/interactions`
- credential: `GEMINI_API_KEY` or `GOOGLE_API_KEY` provisioned for Gemini API access

That is the simplest equivalent to how this repo currently uses OpenAI and Anthropic key-based APIs.

Vertex AI is the alternative if you want:

- GCP project-level IAM
- enterprise billing/governance
- regional routing
- tighter integration with other Google Cloud infrastructure

## Recommended Next Steps

1. Extend the OpenAI client so the repo can use `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4-pro`, and optionally `o3` / `o4-mini`.
2. Refresh the Anthropic client model map to match the live account snapshot.
3. Add a Gemini client using the Gemini Developer API first.
4. After that, build experiment presets for:
   - OpenAI family comparisons
   - Anthropic family comparisons
   - cross-provider leagues
