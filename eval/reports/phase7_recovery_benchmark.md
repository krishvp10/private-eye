# Phase 7 Recovery Benchmark, Per-Step Correctness & Error Taxonomy

**Sample Size:** 25 Injected Failure Scenarios

## 1. Recovery Mode Comparison

| Mode | Recovery Success | Workflow Success | Repeated Same-Target Rate | Avg Retries | Avg Recovery Latency |
|---|---|---|---|---|---|
| **R0_Blind_Retry** | **0.0%** | **0.0%** | 100.0% | 3.0 | 21.0 s |
| **R1_Fresh_Reasoning** | **100.0%** | **100.0%** | 0.0% | 1.0 | 7.2 s |
| **R2_Fresh_Reasoning_Plus_Verifier** | **100.0%** | **100.0%** | 0.0% | 1.0 | 7.8 s |

## 2. Failure Class Error Taxonomy (Phase 7.10)

| Failure Class | Count | Rate | Primary Cause |
|---|---|---|---|
| `semantic_selection_failure` | 8 | 10.67% | Lexical overlap favored wrong role (e.g. input vs submit) |
| `stale_ref` | 8 | 10.67% | Element unmounted or DOM mutated during step execution |
| `post_condition_failure` | 9 | 12.0% | Expected state transition not observed after execution |
| `no_progress` | 25 | 33.33% | Page URL and DOM unchanged after click action |
| `repeated_action` | 25 | 33.33% | System repeated exact same action after no progress |

## 3. Key Findings
- **R0 (Blind Retry):** 0% recovery, 100% repeated same-target rate. Demonstrates that retrying without state memory is fatally flawed.
- **R1 (Fresh Reasoning):** 96.0% recovery (24/25) by incorporating fresh capture and no-progress feedback.
- **R2 (Fresh Reasoning + Crop Verifier):** **100.0% recovery** (25/25) with zero repeated same-target actions.
