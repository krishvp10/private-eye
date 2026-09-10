# PrivateEye Execution Plan

## Objective

Prove the architectural differentiator with a real multimodal model while keeping
all private browser state on the client:

```text
local capture -> local privacy gate -> sanitized context -> VLM reasoning
-> safe action -> local validation -> local vault/execution
```

## Status

### Completed and verified

- Synthetic KYC site and `/login -> /kyc -> /success` workflow.
- Playwright screenshot and safe screen graph capture.
- Local DOM, regex, heuristic NER, and face detection layers.
- Local screenshot redaction and `RedactionMap`.
- Local secret vault and `value_ref` protocol.
- Mock VLM and FastAPI reasoning server.
- OpenAI-compatible real-VLM adapter boundary.
- Safe element references and local reference mapping.
- Fail-closed response validation and unknown namespace rejection.
- Machine-readable request privacy inspection.
- Destructive-action confirmation seam.
- Reference visibility/name validation.
- 37 passing automated tests.
- Context-ablation runner and honest SKIPPED report generation.
- GitHub CI, CodeQL, Dependency Review, Dependabot, and manual benchmark workflows.
- Playwright 1.62 AI ARIA snapshot integration with safe fallback.
- Reproducible vLLM/Qwen deployment and health-check harness.
- Model comparison report runner with explicit SKIPPED behavior.
- Optional dashboard receives sanitized imagery only; raw screenshots stay local.

### Current environment blocker

Live Qwen2.5-VL execution is not verified in this workstation because no reachable
GPU-backed vLLM endpoint is configured. Real mode must remain explicitly configured;
it must not silently fall back to mock reasoning.

The same blocker applies to the context-ablation and five-run reports:
`eval/reports/context_ablation.json` and `eval/reports/real_vlm_report.json` are
SKIPPED, not PASS, until a reachable real endpoint is provided.

## Ordered milestones

### M1 — Real Qwen image canary

1. Prepare a GPU host with a pinned vLLM build.
2. Serve Qwen2.5-VL-3B-Instruct first.
3. Send one sanitized image plus safe graph.
4. Validate one structured `AgentAction`.
5. Repeat with Qwen2.5-VL-7B-Instruct.

Exit evidence: model/version/GPU, request size, model latency, valid action, no
raw secret in request/response/logs.

### M2 — Grounding and recovery

1. Prefer current Playwright ARIA snapshot APIs when the installed version supports them.
2. Validate ref, role, name, visibility, enabled state, and page state before execution.
3. Add fresh-capture retries for stale or failed actions.
4. Escalate to `ask_user` after bounded retries.
5. Add post-condition checks.

Exit evidence: deterministic grounding accuracy and retry/escalation report.

### M3 — Human confirmation

1. Require approval for submit/pay/send/delete/confirm actions.
2. Support interactive and CI auto-approval modes.
3. Test both approval and denial.

Exit evidence: denied destructive actions never reach Playwright.

### M4 — Privacy evidence

1. Capture exact outbound request components.
2. Scan URL, headers, body, encoded image, response, and server audit logs.
3. Generate a machine-readable privacy report.
4. Add realistic synthetic variants and decoy PII.

Exit evidence: zero secret matches across all captured transport/log artifacts.

### M5 — Reliability and demo

1. Run five consecutive real-model KYC workflows.
2. Compare mock, 3B, and 7B on grounding, completion, latency, retries, and invalid actions.
3. Add live privacy-safe dashboard.
4. Prepare offline fallback and five-run rehearsal.

## Explicitly deferred

- Browser extension.
- ONNX Runtime Web and WebGPU.
- Video understanding.
- Second demo workflow.
- Kubernetes and multi-tenancy.
- Persistent database.
- Model fine-tuning.

## Evidence discipline

Synthetic benchmark numbers must be labeled as synthetic. Real-model results must
include the exact model, serving version, hardware, latency, grounding accuracy,
retry count, workflow success, and packet-level privacy result.
