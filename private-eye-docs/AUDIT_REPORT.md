# PrivateEye Implementation & Security Audit Report

## Executive Result

PrivateEye has completed Phase 7 (Generalization, Reliability & Security Validation). The architecture is frozen, mathematically and empirically auditable, and verified across four separate evaluation splits.

All headline metrics have complete denominators, separating deterministic local candidate generation and ranking from remote model selection. 3B is designated as the preferred deployment model for edge workloads based on Pareto analysis (latency, memory, workflow reliability).

---

## Verified Evaluation Matrix

| Area | Evidence / Report | Status | Key Metric |
|---|---|---|---|
| **Phase 7 Metric Provenance Audit** | `eval/reports/phase7_metric_audit.md` | **PASS** | Complete denominators for all headline metrics |
| **Development Benchmark (Frozen)** | `eval/data/development_set.json` | **FROZEN** | SHA256: `228dcfec...`, 150 cases, 88.7% accuracy |
| **Held-Out Generalization Set** | `eval/reports/heldout_grounding_benchmark.md` | **PASS** | 200 cases, **98.0% accuracy**, **0.0% wrong-target rate** |
| **Red-Team Adversarial Set** | `eval/reports/redteam_grounding_benchmark.md` | **PASS** | 75 cases, **100.0% safe abstention**, 1.33% wrong-action |
| **Prompt Injection Defense** | `eval/redteam_benchmark.py` | **PASS** | **100.0% blocked** (7/7 injection attempts) |
| **Structured Output Robustness** | `tests/test_structured_output_robustness.py` | **PASS** | Strict schema validation, fail-closed rejection |
| **Confidence Calibration** | `eval/reports/confidence_calibration.md` | **PASS** | Empirical thresholds ($\tau_{high}=0.88, \tau_{med}=0.65$) |
| **Selective Verification (Mode C)** | `eval/reports/confidence_calibration.md` | **PASS** | **98.5% accuracy**, **0.04 verifier calls/action** |
| **Adaptive Image Resolution** | `eval/reports/phase7_adaptive_resolution.md` | **PASS** | 768px default, 1024px on small/ambiguous (<30px) |
| **Failure Recovery Benchmark** | `eval/reports/phase7_recovery_benchmark.md` | **PASS** | R0: 0% vs R1: **100.0%** vs R2: **100.0%** |
| **Privacy Invariant Audit** | `eval/reports/phase7_privacy_invariant.md` | **PASS** | 11 boundaries, 57 reports, **0 raw secret leaks** |
| **Controlled 3B vs 7B Comparison** | `eval/reports/phase7_model_comparison.md` | **PASS** | 3B designated preferred deployment model |
| **External Diagnostic Check** | `eval/reports/phase7_external_diagnostic.md` | **PASS** | 50 ScreenSpot & Mind2Web diagnostic cases (100.0%) |
| **Automated Test Suite** | Local pytest suite | **PASS** | 93 tests passing cleanly |

---

## Controlled Model Deployment Stance

> **Official Deployment Recommendation:**  
> **Qwen2.5-VL-3B is the preferred deployment model for PrivateEye.**
>
> **Rationale:**
> - **Edge GPU Fit:** 3.8 GB VRAM comfortably fits consumer 8 GB GPUs (RTX 3070/4060, Apple M1/M2/M3), whereas 7B requires 8.4 GB and exceeds the 8 GB edge budget.
> - **Turn Latency:** 7.2s p50 (3B) vs 13.4s p50 (7B). 3B is 1.86x faster, preventing browser execution timeouts.
> - **End-to-End Reliability:** 3B achieved 5/5 synthetic workflow completion vs 4/5 for 7B (7B suffered context drift on complex multi-step modals).
> - **Grounding Parity:** Backed by PrivateEye's local Playwright ARIA candidate extraction and crop verifier, 3B achieves 93.8% overall accuracy on 275 combined held-out and adversarial cases (within 1.1% of 7B's 94.9%).

---

## Universal Privacy Invariants

The privacy posture has evolved from single-request checks to universal invariants:
1. **Raw Screenshot:** Local client only; never crosses network.
2. **Redacted Screenshot:** PII regions covered by visual redaction masks before export.
3. **Safe ScreenGraph:** Text nodes scrubbed of raw secrets; names masked.
4. **Safe Candidates:** Expose only ref, role, sanitized name, visibility, and bbox.
5. **Marked Screenshot & Crops:** Rendered exclusively on already-redacted image bytes.
6. **Planner & Verifier Prompts:** Contain generic user task and candidate lists; zero vault values.
7. **Model Response:** Selects candidate reference; local executor resolves `value_ref` locally.
8. **Independent Interception:** Outbound HTTP interceptor scans all network payloads against 21 vault secrets.
