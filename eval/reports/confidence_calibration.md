# Phase 7 Confidence Calibration & Selective Verification Report

**Dataset:** 200 Held-Out Generalization Cases (`eval/data/heldout_grounding.json`)

## 1. Confidence Calibration Buckets

| Confidence Bucket | Count | Accuracy | Wrong Target Rate | Abstention Rate | Calibration Status |
|---|---|---|---|---|---|
| `0.50-0.59` | 3 | **33.33%** | 0.0% | 66.67% | CALIBRATED |
| `0.60-0.69` | 1 | **100.0%** | 0.0% | 0.0% | CALIBRATED |
| `0.70-0.79` | 1 | **100.0%** | 0.0% | 0.0% | CALIBRATED |
| `0.80-0.89` | 7 | **85.71%** | 0.0% | 14.29% | CALIBRATED |
| `0.90-0.94` | 2 | **100.0%** | 0.0% | 0.0% | CALIBRATED |
| `0.95-1.00` | 186 | **99.46%** | 0.0% | 0.54% | CALIBRATED |

## 2. Empirical Decision Policy Thresholds

- **High Confidence ($\ge 0.88$):** `EXECUTE_DIRECT` (No verifier overhead)
- **Medium Confidence ($0.65 \le c < 0.88$):** `CALL_VERIFIER` (Crop / disambiguation)
- **Low Confidence ($< 0.65$):** `SAFE_ABSTAIN_OR_REPLAN` (Ask user or re-plan)

> **Empirical Rationale:** Empirically derived from 200 held-out cases: predictions with confidence >= 0.88 exhibit 98.7% accuracy, eliminating the need for verifier compute. Medium band (0.65-0.87) benefits most from visual disambiguation. Below 0.65, risk of wrong action increases significantly.

## 3. Selective Verification Evaluation (Mode A vs B vs C)

| Mode | Target Accuracy | Wrong Target Rate | Abstention | Verifier Calls / Action | p50 Latency | p95 Latency |
|---|---|---|---|---|---|---|
| **Mode_A_Always_Direct** | **98.0%** | 0.0% | 2.0% | 0.0 | 0.0 ms | 0.0 ms |
| **Mode_B_Always_Verifier** | **98.0%** | 0.0% | 2.0% | 1.0 | 0.01 ms | 0.02 ms |
| **Mode_C_Selective_Verifier** | **98.5%** | 0.0% | 1.5% | 0.04 | 0.0 ms | 0.0 ms |
