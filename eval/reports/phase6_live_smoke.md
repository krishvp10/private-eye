# Phase 6 Live Grounding Smoke

**Status:** `FAIL`

- Model: `qwen2.5vl:3b`
- Endpoint: local Ollama OpenAI-compatible API
- Steps: 12
- Workflow success: `false`
- Final URL: `/login`
- Observed action: repeated `click` on `e10`
- Execution success: `true` for observed actions
- Post-condition telemetry: `true` for observed actions
- Total latency: `100116.37 ms`

The model repeatedly selected the same executable target and never advanced the
workflow. This is measured evidence that candidate-constrained context alone
does not yet solve live task grounding. It is not combined with the deterministic
120-case local-ranking result.
