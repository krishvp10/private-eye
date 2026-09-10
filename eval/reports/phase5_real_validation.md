# PrivateEye Phase 5 Real-VLM Validation

**Status:** `COMPLETE_WITH_MEASURED_FAILURES`

## Evidence tiers

- Deterministic synthetic: **72 tests passing**.
- Realistic synthetic: detector benchmark retained separately.
- Real VLM: live Qwen2.5-VL-3B and Qwen2.5-VL-7B runs below.

## Live model comparison

| Model | Five-run workflow | Canary grounding | Schema validity | p50 workflow ms |
|---|---:|---:|---:|---:|
| qwen2.5vl:3b | 5/5 | 0.167 | 1.000 | 7234.82 |
| qwen2.5vl:7b | 0/5 | 0.333 | 1.000 | 13370.35 |

## Live packet privacy

- Evidence source: `live_real_vlm_request`
- Live traffic verified: `True`
- Secrets audited: `21`
- Zero-leak result: `True`

## Limitations

- Both models returned schema-valid actions, but canary target correctness was materially lower.
- The current context-ablation runner records response validity and latency, not full workflow grounding denominators.
- Server-log evidence uses the privacy-safe /v1/runs audit stream rather than an external log collector.
- No model superiority claim is made from this single-host experiment.
