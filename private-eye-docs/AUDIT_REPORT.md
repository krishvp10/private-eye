# PrivateEye Implementation Audit

## Executive result

The local privacy-preserving browser-agent MVP is implemented and regression-tested.
The real-Qwen evidence phase is **not complete** because this workstation has no
reachable GPU-backed OpenAI-compatible Qwen2.5-VL endpoint. No real-model result
has been fabricated.

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
| Context-ablation harness | `eval/context_ablation.py` | PASS (runner); real measurements blocked |
| Model comparison harness | `eval/model_comparison.py` | PASS (runner); real measurements blocked |
| Real-model canary harness | `eval/real_vlm_canary.py` | PASS (runner); live canaries blocked |
| Dashboard transport boundary | raw screenshot removed from dashboard payload | PASS |
| Automated regression suite | 56 passed | PASS |

## Evidence not yet available

These require a reachable real Qwen endpoint and must remain unclaimed:

- Qwen2.5-VL-3B and 7B grounding accuracy.
- Five consecutive real-model KYC workflows.
- Real model latency and end-to-end latency distributions.
- GPU memory/utilization and resource comparison.
- Real prompt-injection behavior.
- Real packet and server-log evidence from a Qwen run.
- Measured screenshot-only vs graph vs redaction-legend accuracy.

Current reports:

- `eval/reports/real_vlm_report.json`: `SKIPPED - real VLM server is unreachable`.
- `eval/reports/context_ablation.json`: `SKIPPED - PRIVATEEYE_VLM_MODE is not real`.
- `eval/reports/real_vlm_canaries.json`: `SKIPPED - PRIVATEEYE_VLM_MODE is not real`.
- `eval/reports/model_comparison.json`: both 3B and 7B entries `SKIPPED`.

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

## Known limitations

1. No GPU/vLLM endpoint is available, so real-model claims cannot be made.
2. The current retry loop reloads and retries the previous action; a complete
   fresh-capture/reasoning retry orchestration remains to be implemented.
3. Post-condition verification is not yet a first-class per-action contract.
4. The context-ablation runner currently measures response validity/latency when
   live, while workflow-level grounding denominators require the full real runner.

## Recommended next phase

Provision a reachable Qwen2.5-VL-3B endpoint, run the image canaries, then run
the context ablation and five-run workflow experiments. Record model, vLLM
version, GPU, request sizes, latency percentiles, grounding, retries, and
packet/server-log privacy evidence before comparing 3B with 7B.
