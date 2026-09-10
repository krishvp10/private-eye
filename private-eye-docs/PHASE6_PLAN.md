# Phase 6 — Grounding 2.0 + Verification

## Status: COMPLETED WITH MEASURED LIMITATIONS

The local candidate architecture and deterministic benchmark are implemented and
tested. Live Qwen grounding remains a separate measured failure surface; the
local benchmark must not be interpreted as VLM accuracy.

---

## 1. Objectives & Architectural Achievement

Phase 6 addresses the real-model grounding bottleneck by implementing a hybrid grounding architecture:
- **Local Playwright/ARIA Candidate Engine**: Extracts privacy-safe, executable elements.
- **Deterministic Explainable Ranker**: Uses token overlap, role compatibility, exact matching, and geometry to rank top candidates.
- **Visual & Semantic Verifier**: Provides bounded local disambiguation using
  localized, privacy-redacted screenshot crops; a live VLM verifier evaluation
  remains pending.
- **VLM Candidate Selection**: Remote model selects `candidate_ref` over sanitized context.
- **Action-Specific Post-Conditions**: Validates observable UI/state changes.
- **Fresh Re-reasoning Recovery**: Re-captures, re-detects, and re-queries the model upon failure.

---

## 2. Completed Milestones

- [x] **Stage 1: Freeze Baseline** (`eval/freeze_phase6_baseline.py` → `eval/reports/phase6_baseline.json`)
- [x] **Stage 2: 150-Case Atomic Grounding Benchmark** (`eval/grounding_benchmark.py` → `eval/reports/atomic_grounding_benchmark.json`)
- [x] **Stage 3: Safe Candidate Extraction & Ranking** (`client/candidates.py` & `tests/test_candidates.py`)
- [x] **Stage 4: VLM Action Protocol for Candidate Ref** (`shared/protocol.py`, `client/executor/execute.py`)
- [x] **Stage 5: Visual/Semantic Verifier on Redacted Crops** (`client/verifier.py` & `tests/test_verifier.py`)
- [x] **Stage 6: Action-Specific Post-Conditions** (`client/agent.py`)
- [x] **Stage 7: Fresh Re-reasoning Recovery** (`tests/test_recovery.py`)
- [x] **Stage 8: Controlled A/B/C Evaluation** (`eval/ablation_grounding.py`)
- [x] **Stage 9: Architecture Ablation (V0 vs V3)** (+72.0% accuracy improvement)
- [x] **Stage 10: Model Comparison (Qwen2.5-VL-3B vs 7B)** (3B validated as primary edge backbone)
- [x] **Stage 11: Image Resolution Sweep** (Medium 768px confirmed as sweet spot)
- [x] **Stage 12: Privacy Regression Verification** (Zero leaks across candidate metadata, crops, and telemetry)

---

## 3. Key Measured Metrics

- **Target Accuracy (Top-1):** **88.7%** on the deterministic local corpus
- **Top-3 Recall:** **100.0%**
- **Top-5 Recall:** **100.0%**
- **Wrong Target Rate:** **11.3%**
- **Unknown Target Rate:** **0.0%**
- **Action Type Accuracy:** **100.0%**
- **Evaluation Latency:** **16.8 ms** (~0.11 ms/case)
- **Zero Privacy Leaks:** Verified across 21 synthetic vault secrets.

Detailed local results are documented in
`eval/reports/atomic_grounding_benchmark.md`. Live Qwen failure evidence is
documented in `eval/reports/phase6_live_smoke.md`.
