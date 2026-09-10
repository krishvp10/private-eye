# Held-Out Grounding Benchmark Report (Phase 7)

**Dataset:** `eval/data/heldout_grounding.json` (200 cases, zero tuning overlap)
**Dataset SHA256:** `a84d85402134d7522c79794232d785a9ce1143865d82af794ab1b94822944636`

## Summary Results

| Metric | Result | Count / Total | Notes |
|---|---|---|---|
| **Target Accuracy** | **98.0%** | 196/200 | Primary generalization accuracy |
| **Top-3 Recall** | **98.0%** | 196/200 | Target in top-3 candidates |
| **Wrong-Target Rate** | **0.0%** | 0/200 | Selected incorrect candidate |
| **Abstention Rate** | **2.0%** | 4/200 | Ambiguous gate trigger |
| **No Valid Candidate** | **0.0%** | 0/200 | Zero candidates extracted |
| **Post-Condition Success** | **100.0%** | 196/196 | For correctly grounded actions |
| **p50 Latency** | **0.15 ms** | - | Deterministic local engine |
| **p95 Latency** | **0.37 ms** | - | Tail latency |

## Domain Breakdown

| Domain | Total | Correct | Accuracy |
|---|---|---|---|
| `ecommerce` | 30 | 28 | **93.33%** |
| `cloud_devops` | 35 | 35 | **100.0%** |
| `healthcare` | 25 | 25 | **100.0%** |
| `saas_billing` | 30 | 29 | **96.67%** |
| `multilingual` | 25 | 25 | **100.0%** |
| `responsive` | 30 | 29 | **96.67%** |
| `nested_state` | 25 | 25 | **100.0%** |

## Difficulty Breakdown

| Difficulty | Total | Correct | Accuracy |
|---|---|---|---|
| `medium` | 85 | 82 | **96.47%** |
| `hard` | 115 | 114 | **99.13%** |
