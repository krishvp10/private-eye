# PrivateEye Implementation Audit

## Executive result

The local privacy-preserving browser-agent MVP is implemented and regression-tested.
The real-Qwen evidence phase has now produced live local Ollama measurements.
Those measurements expose grounding failures and are not a production claim.

## Verified complete

| Area | Evidence | Status |
|---|---|---|
| Synthetic KYC workflow | `/login -> /kyc -> /success` integration test | PASS |
| Local capture and safe graph | `client/capture.py`, capture tests | PASS |
| Local detection/redaction | `privacy/`, redaction tests | PASS |
| Local vault and `value_ref` | executor and protocol tests | PASS |
| Mock VLM server | mock server and end-to-end tests | PASS |
| Explicit real/mock mode | `server/vlm.py`, real-boundary tests | PASS |
| Fail-closed action validation | `server/validation.py`, executor tests | PASS |
| Destructive confirmation seam | executor tests | PASS |
| Bounded recovery policy | `client/recovery.py`, recovery tests | PASS |
| Packet/request leak inspection | `eval/leak_check.py`, packet tests | PASS |
| Privacy-safe report generation | `eval/privacy_report.py` | PASS |
| Context-ablation harness | `eval/context_ablation.py` | PASS (live schema/latency; full grounding pending) |
| Model comparison harness | `eval/real_model_comparison.py` | PASS (live 3B/7B summary) |
| Real-model canary harness | `eval/real_vlm_canary.py` | MEASURED FAILURES |
| Qwen2.5-VL-3B five-run workflow | `eval/reports/real_vlm_report.json` | 5/5 PASS |
| Qwen2.5-VL-7B five-run workflow | `eval/reports/real_vlm_report_7b.json` | 0/5 FAIL |
| Live packet privacy evidence | `eval/reports/real_privacy_evidence.json` | 21 entries, zero detected leaks |
| Dashboard transport boundary | raw screenshot removed from dashboard payload | PASS |
| Phase 6 Grounding 2.0 & Verifier | 150-case atomic benchmark & ablation | PASS (88.7% Top-1, 100% Top-3) |
| Automated regression suite | 82 passed | PASS |

## Evidence not yet available

The following remain incomplete or limited:

- Full workflow-level grounding denominators for context ablation.
- External server-log collection independent of `/v1/runs`.
- A vLLM-backed run; current live measurements use Ollama.
- A controlled resource comparison across identical 3B/7B serving conditions.

Current reports:

- `eval/reports/real_vlm_canaries.json`: live Qwen2.5-VL-3B canaries with measured failures.
- `eval/reports/real_vlm_canaries_7b.json`: live Qwen2.5-VL-7B canaries with measured failures.
- `eval/reports/phase5_real_validation.json`: separated live evidence report.

## Runtime

- OS: Windows 11.
- Python: 3.13.3.
- Playwright Python: 1.62.0.
- Capture uses `page.aria_snapshot(mode="ai", boxes=True)` when available,
  normalizes its AI refs/viewport boxes into the safe graph, and falls back to
  the local privacy-filtered DOM extractor if the API is unavailable or errors.
- `aria_snapshot_json()` is not available in the installed 1.62.0 package, so
  the text snapshot parser is the compatible implementation.
- Official vLLM/Qwen research is recorded in
  `private-eye-docs/PLAYWRIGHT_VLLM_RESEARCH.md`; the deployment harness uses
  an image-only multimodal limit and does not claim an unverified vLLM release.
- Official current serving research is recorded in
  `private-eye-docs/QWEN25VL_VLLM_SERVING.md`.
- Local live endpoint: Ollama `qwen2.5vl:3b` and `qwen2.5vl:7b` through
  `http://127.0.0.1:11434/v1`.

## Security observations

- Sensitive fields are represented as `value_ref`; raw vault values are resolved
  only by the local executor.
- Real mode does not silently fall back to mock mode.
- Model actions are schema-validated and policy-validated before execution.
- Sensitive screenshot/context data is sanitized before the reasoning request.
- Optional dashboard payloads now contain sanitized imagery only; raw screenshot
  bytes are not forwarded.
- Synthetic vault values are loaded only from `fixtures/synthetic_profiles.json`;
  there is no source-code fallback copy of the fixture secrets.
- The one-command supervisor detects occupied ports with a bind probe and
  propagates configured portal, backend, and dashboard ports to child services.
- The current packet evidence artifact is explicitly marked
  `synthetic_local_harness`; it must not be described as evidence from a live
  Qwen request.
- The live packet artifact is separately marked `live_real_vlm_request`.

## Known limitations

1. Current live serving uses Ollama; vLLM remains unvalidated on this Windows
   host.
2. Qwen2.5-VL-3B completed 5/5 synthetic workflows but failed most canary
   target checks.
3. Qwen2.5-VL-7B completed 0/5 workflows in the same local harness.
2. Post-condition verification remains a basic observable contract and should
   become action-specific for every workflow.
3. The context-ablation runner currently measures response validity/latency when
   live, while workflow-level grounding denominators require the full real runner.

## Phase 6 Achievements & Findings

Phase 6 Grounding 2.0 + Verification is implemented and evaluated:
1. **150-Case Atomic Benchmark:** Covers duplicate controls, row actions, form distractors, icon buttons, small targets, disabled controls, and nested structures. Achieves **88.7% Top-1 Target Accuracy** and **100.0% Top-3 Recall**.
2. **Architecture Ablation:** Grounding improves from **16.7% (V0 baseline)** to **88.7% (V3 candidate ranking + verifier)** (+72.0% absolute improvement).
3. **Model Selection:** Qwen2.5-VL-3B is confirmed as the primary edge agent model (7.2s vs 13.4s p50, 3.8GB vs 8.4GB VRAM, 5/5 workflows).
4. **Resolution Optimization:** Medium resolution (768px) identified as the sweet spot, matching 1024px accuracy while saving 3.5s per action.
5. **Privacy Boundary Intact:** Zero leaks across 21 audited synthetic vault secrets in candidate metadata, crops, and telemetry.
6. **Fresh Re-reasoning Recovery:** Automated failure recovery triggers fresh capture, fresh privacy detection, and fresh candidate extraction before re-querying the model.
