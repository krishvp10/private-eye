# Phase 19 external-methods note

**Purpose.** This note records current, primary-source methodological references for Phase 19. It is not evidence that PrivateEye has run, matched, or scored any of these benchmarks. Sources were checked on 2026-09-11.

## Evidence and long-horizon evaluation

- [OSWorld 2.0's official project page](https://osworld-v2.xlang.ai/) describes 108 long-horizon workflows on 31 self-hosted sites, with 69.6% taking skilled humans over one hour, more than 250 average agent steps, and 27.25 average scoring checkpoints. Its primary 500-step binary metric reports the best listed result as 20.6% completion and 54.8% partial score. The page also diagnoses failures involving state tracking, dynamic updates, constraint loss, premature guessing, and skipped verification. This supports measuring horizon-specific survival, recovery, and first decisive failure; it does **not** validate a PrivateEye score or causal intervention.
- [WebArena-Verified's maintained repository](https://github.com/ServiceNow/webarena-verified) and its [network-event evaluation documentation](https://servicenow.github.io/webarena-verified/dev/evaluation/network_event_based_evaluation/) describe audited/versioned tasks, captured HAR-derived network events, offline re-evaluation, and deterministic/type-aware evaluation rather than LLM judging. Phase 19 should therefore separate raw trace capture, deterministic scoring, JSON metrics, and human-readable reports.
- [ST-WebAgentBench's maintained repository](https://github.com/segev-shlomov/ST-WebAgentBench) defines Completion under Policy (CuP): task completion with zero policy violations. Its materials describe 375 tasks, 3,057 policy instances, safety dimensions, human deferral, and 80 modality-challenge tasks. It supports retaining separate task-success, safety, and abstention/oversight measures rather than collapsing them into one score.

## Independence, repeatability, and auditability

- The [NIST AI RMF Measure function](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) calls for documented test sets, metrics, and tools; measures in conditions similar to deployment; documented generalization limitations; regular safety/security/resilience evaluation; and involvement of non-front-line internal experts and/or independent assessors (Measure 1.3). This supports an evaluator that consumes raw traces and computes deterministic metrics independently of report generation. It does not convert an internal evaluator into an external independent assessment.
- NIST's [agent-evaluation guidance on evaluation cheating](https://www.nist.gov/caisi/cheating-ai-agent-evaluations) identifies transcript review and explicit, benchmark-specific affordances/restrictions as methods to detect/prevent invalid evaluation behavior. Keep complete trajectory records and specify agent capabilities, environmental controls, and scorer inputs.

## Runtime-control and security methodology

- The [OWASP Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) states that agents should be inspectable, traceable, and instrumentable, and describes runtime middleware hooks for declarative policy enforcement. This supports testing the complete proposed-action → validation → policy → execution-gate → browser-action path, including races and malformed inputs.
- The [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) is the appropriate current OWASP taxonomy reference for control-plane fuzz design. Phase 19 must cite the precise categories used in its eventual test matrix; this note does not assert coverage or compliance.

## Browser-native proof of value

- [ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/) supports browser inference through `onnxruntime-web`, with WASM, WebGPU, WebGL, and WebNN execution-provider options. Its [performance guidance](https://onnxruntime.ai/docs/tutorials/web/performance-diagnosis.html) recommends model selection appropriate to the web scenario (commonly tiny/small models), documents WASM proxy-worker/UI-responsiveness trade-offs, and provides CPU/WebGPU profiling and tracing. A prototype should report the actual model and package sizes, cold/warm start, inference percentiles, memory/CPU/GPU observations, and browser responsiveness for both WASM and WebGPU; browser-local inference cannot be claimed until actually executed in-browser.
- [Chrome's `chrome.offscreen` API documentation](https://developer.chrome.com/docs/extensions/reference/api/offscreen) specifies that MV3 extensions on Chrome 109+ can create one hidden offscreen document per installed extension/profile to use DOM APIs without a visible tab/window. The document requires the `offscreen` permission and communicates through `chrome.runtime`; it is not a general replacement for a service worker. This makes an MV3 content-script + service-worker + explicitly scoped offscreen prototype technically plausible, not already implemented.

## SIH 26171 verification status

No authoritative public SIH/ISRO problem-statement page was located in this review. A third-party mirror, [SIH26171 — On-device Visual Perception for Light-weight Browser Agents](https://zaidsayyed.in/tools/sih-problem-statements/sih26171), reproduces the stated browser-local visual-perception/redact-before-server architecture and the claimed weights (visual context 25%, sensitive-PII detection 20%, redaction 20%, client resources 20%, end-to-end latency 15%). Because it is not an official SIH/ISRO source, Phase 19 must label those requirements and weights **unverified pending an official problem-statement URL or supplied source**. Do not present the mirror as authoritative.

## Claims deliberately not made

- No official benchmark score is inferred from this project without executing that benchmark's stated protocol and release.
- None of the above establishes that existing Phase 17/18 reports are raw-evidence-backed, independently scored, causally comparable, privacy-complete, or externally validated.
- No public primary source was found here for the specific claim that a prior 51.3%/81.0% comparison used matched tasks, initial states, models, seeds, and fault schedules. That is an evidence-audit question, not a literature fact.
