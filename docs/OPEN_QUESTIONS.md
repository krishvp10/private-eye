# OPEN_QUESTIONS.md

## BLOCKING (answer before build)
- Q-001 Will the finale provide the evaluation use-case sites in advance, or live? → Shapes whether we
  harden generic-form handling vs the 3 demo flows. **Ask organizers/mentor ASAP.**
- Q-002 Is a cloud GPU endpoint allowed for the *demo*, or must the server be on the LAN?
  → Shapes DEPLOYMENT.md topology. (Problem statement says cloud-hosted OSS allowed during SIH — likely fine.)
- Q-003 Exact rubric measurement protocol for "client side resource utilization" — do judges read our
  dashboard, or run their own monitors? → Shapes dashboard necessity.

## IMPORTANT (can resolve during build)
- Q-004 Firefox a11y fidelity vs Chromium on our demo sites — run parity check in Phase 4.
- Q-005 Best threshold set for face detector on projector-lit webcam frames — tune in Phase 7.
- Q-006 Will the VLM reliably emit strict JSON without vLLM guided decoding? — spike in Phase 3
  (fallback: outlines-style constrained generation).

## NON-BLOCKING
- Q-007 UI-TARS-1.5-7B as drop-in better server? (V1 experiment.)
- Q-008 In-browser extension with Transformers.js — WASM vs WebGPU perf on judge hardware? (V1.)
- Q-009 Multi-language PII (Hindi names) — spaCy models? (Future.)
