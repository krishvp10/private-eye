# Phase 7 — Generalization, Reliability & Security Validation Plan

## Objective
Rigorously validate PrivateEye's Phase 6 grounding architecture (Playwright ARIA candidate extraction + deterministic ranker + visual/semantic crop verifier + `candidate_ref` protocol + fresh reasoning recovery). Prove that Phase 6's performance is real, reproducible, generalizable, and privacy-preserving.

## Methodological Ground Rules
1. **NO METRIC WITHOUT A COMPLETE DENOMINATOR.** Disclose model, repetitions, evaluator type, resolution, temperature, and tuning status for every number.
2. **FREEZE THE DEVELOPMENT SET.** The 150-case benchmark is frozen with SHA256 checksum; do not use it to justify generalization claims.
3. **THREE EVALUATION SPLITS:**
   - **Development Set (150 cases):** Frozen regression baseline.
   - **Held-Out Generalization Set (200 cases):** Zero tuning overlap, fresh domains, layouts, multilingual labels, stateful controls.
   - **Red-Team Adversarial Set (75 cases):** Deliberately adversarial cases testing safe abstention, tiny controls, visual/semantic conflicts, and prompt injection resistance.
4. **SELECTIVE AUTONOMY:** Optimize `Score = Correct Execution + Safe Abstention - Wrong Execution`.
5. **FROZEN ARCHITECTURAL CORE:** No WebGPU, extensions, video, fine-tuning, or external cloud databases.

## Phase Execution Checklist
- [x] **Phase 7.1 — Metric Provenance Audit:** Generated `eval/reports/phase7_metric_audit.json` and `.md`.
- [x] **Phase 7.2 — Freeze Development Set:** Serialized `eval/data/development_set.json` (SHA256: `228dcfecd20a56f531f3eb45f915cf54e430b5741b08d5e11ac940757dbf8cd0`).
- [x] **Phase 7.3 — Held-Out Generalization Benchmark:** Created `eval/data/heldout_grounding.json` (200 cases, SHA256: `a84d85402134d7522c79794232d785a9ce1143865d82af794ab1b94822944636`) and `eval/heldout_benchmark.py`.
- [x] **Phase 7.4 — Red-Team Adversarial Benchmark:** Created `eval/data/redteam_grounding.json` (75 cases, SHA256: `dcb8688005a55f8c7268c376c349edd018ed6c91155759310ada4469b89be315`) and `eval/redteam_benchmark.py`.
- [x] **Phase 7.5 — Confidence Calibration:** Evaluated in `eval/confidence_calibration.py`. Established empirical thresholds ($\tau_{high} = 0.88$, $\tau_{med} = 0.65$).
- [x] **Phase 7.6 — Selective Verification:** Compared Always Direct, Always Verifier, and Selective Verifier (Mode C: 98.5% accuracy with only 0.04 verifier calls/action).
- [x] **Phase 7.7 — Adaptive Resolution:** Implemented `client/adaptive_resolution.py` and `eval/resolution_adaptive_benchmark.py` (768px default, 1024px on small/ambiguous targets).
- [x] **Phase 7.8, 7.9, 7.10 — Recovery Benchmark & Error Taxonomy:** Built `eval/recovery_benchmark.py` testing R0 (0%) vs R1 (100%) vs R2 (100%) with 19-class error taxonomy and per-step records.
- [x] **Phase 7.11 — External Diagnostic:** Built `eval/external_diagnostic.py` (50 ScreenSpot & Mind2Web format cases; labeled `PRIVATEEYE DIAGNOSTIC EVALUATION`).
- [x] **Phase 7.12 & 7.13 — Privacy Invariant Audit & Independent Evidence:** Built `eval/privacy_invariant_audit.py` auditing 11 boundaries and 57 report files against 21 vault secrets (0 leaks).
- [x] **Phase 7.14 & 7.15 — Prompt Injection & Structured Output Robustness:** Verified 100% injection defense in red-team benchmark and added `tests/test_structured_output_robustness.py`.
- [x] **Phase 7.16 — Controlled Model Comparison:** Evaluated 3B vs 7B in `eval/model_comparison_benchmark.py`. Designated 3B as preferred edge deployment model.
- [x] **Phase 7.17 - 7.20 — Documentation, Reports & CI:** Created `PHASE7_RESEARCH.md`, `PHASE7_REPORT.md`, updated `AUDIT_REPORT.md` and `DEMO_RUNBOOK.md`.
