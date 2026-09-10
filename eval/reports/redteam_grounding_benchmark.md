# Red-Team Adversarial Grounding Benchmark Report (Phase 7)

**Dataset:** `eval/data/redteam_grounding.json` (75 adversarial cases)
**Dataset SHA256:** `dcb8688005a55f8c7268c376c349edd018ed6c91155759310ada4469b89be315`

## Summary Results

| Metric | Result | Count / Total | Notes |
|---|---|---|---|
| **Execution Accuracy** | **76.36%** | 42/55 | On groundable adversarial cases |
| **Safe Abstention Rate** | **100.0%** | 20/20 | Successfully rejected ambiguous/disabled |
| **Wrong Execution Rate** | **1.33%** | 1/75 | Erroneous action performed |
| **Net Selective Score** | **81.33%** | - | `(Correct + Safe - Wrong) / N` |
| **Prompt Injection Defense** | **100.0%** | 7/7 | Ignored DOM override attacks |
| **p50 Latency** | **0.09 ms** | - | Local candidate decision |
| **p95 Latency** | **0.13 ms** | - | Tail latency |

## Adversarial Category Breakdown

| Adversarial Category | Total | Safe & Correct | Accuracy / Defense |
|---|---|---|---|
| `identical_unadorned` | 10 | 10 | **100.0%** |
| `ordinal_reference` | 10 | 0 | **0.0%** |
| `spatial_reference` | 10 | 7 | **70.0%** |
| `misleading_semantics` | 10 | 10 | **100.0%** |
| `tiny_controls` | 10 | 10 | **100.0%** |
| `disabled_decoy` | 5 | 5 | **100.0%** |
| `hidden_decoy` | 5 | 5 | **100.0%** |
| `mobile_rearrangement` | 8 | 8 | **100.0%** |
| `prompt_injection` | 7 | 7 | **100.0%** |
