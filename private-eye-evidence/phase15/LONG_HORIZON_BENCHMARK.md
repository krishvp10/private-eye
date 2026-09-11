# Phase 15: Long-Horizon Compounding Benchmark (PS 26171)

## Executive Summary
Prior evaluations revealed a notable divergence:
* **Step-level accuracy**: High (~97.64%)
* **Long-horizon task completion**: Degraded to ~63.33% at 20 steps.

In Phase 15, we evaluated 120 trajectories across 6 depth tiers (5, 10, 15, 20, 25, 30 steps), profiling survival $S(t)$, hazard rates $h(t)$, failure modes, and recovery overhead.

---

## Empirical Benchmark Results

From [`eval/reports/phase15_long_horizon.json`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/eval/reports/phase15_long_horizon.json):

### Summary Across All Horizons:
* **Total Trajectories Evaluated**: 120
* **Total Steps Executed**: 1,906
* **Overall Step Accuracy**: **98.85%**
* **Overall Task Completion**: **81.67%**
* **Active Recovery Attempts**: 40
* **Recovery Success Rate**: **45.0%**
* **Primary Failure Modes**:
  - `stale_ref` (DOM mutated between turns): 9 occurrences
  - `semantic_grounding_error` (ambiguous candidate): 10 occurrences
  - `no_progress` (looping without state change): 3 occurrences

### Depth Tier Breakdown:

| Depth Tier | Trajectories | Total Steps | Step Accuracy | Task Completion | Theoretical Survival ($p^N$) | Hazard Rate at Horizon ($h_N$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5 Steps** | 20 | 100 | **100.0%** | **100.0%** | 100.0% | 0.00 |
| **10 Steps** | 20 | 198 | **98.99%** | **90.0%** | 90.35% | 0.05 |
| **15 Steps** | 20 | 296 | **98.53%** | **80.0%** | 79.80% | 0.06 |
| **20 Steps** | 20 | 382 | **97.91%** | **65.0%** | 65.30% | 0.07 |
| **25 Steps** | 20 | 486 | **99.14%** | **80.0%** | 79.80% | 0.05 |
| **30 Steps** | 20 | 584 | **99.12%** | **75.0%** | 76.50% | 0.06 |

---

## Scientific Interpretation & Findings

1. **Compounding vs. Cognitive Amnesia**:
   The empirical task completion rate across extended depths (100% $\to$ 90% $\to$ 80% $\to$ 65% $\to$ 80% $\to$ 75%) tracks the theoretical compounding formula $p_{\text{step}}^N$ closely (within 1-2% margin of error).
   * **Verdict**: Empirical degradation is **consistent with cumulative step-level failure compounding over deep horizons**, rather than sudden context loss or model amnesia.

2. **The Role of State Recovery**:
   In complex long-horizon tasks (20-30 steps), individual step accuracy of 98.8% is insufficient on its own ($0.988^{30} \approx 69.6\%$). Trajectory survival requires structured post-condition verification and state recovery. PrivateEye's recovery mechanism rescued 45% of stalled steps, preventing early trajectory termination.
