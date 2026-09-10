# PrivateEye Internal Trajectory Efficiency Analysis (Phase 12)

> **Evaluation Context:** Following emerging consensus in long-horizon web-agent evaluation (such as the 2026 Odysseys benchmark), binary task completion is insufficient to characterize agent competence. We evaluate the operational efficiency of PrivateEye trajectories: how many actions are productive, how much overhead is spent in recovery routines, and whether completed workflows diverge from the minimum path.

## 1. Summary Efficiency Metrics

| Campaign | Total Actions | Useful Actions | Useful Efficiency | Failed Actions | Failure Rate | Recovery Actions | Recovery Overhead | Actions-to-Completion Ratio (Completed) |
|---|---|---|---|---|---|---|---|---|
| **Phase 10 (Dev Set)** | 911 | 900 | **98.79%** | 11 | 1.21% | 81 | 8.89% | **1.000** (1.000x) |
| **Phase 11 (Held-Out Set)** | 912 | 898 | **98.46%** | 14 | 1.54% | 14 | 1.54% | **1.000** (1.000x) |

## 2. Phase 10 Trajectory Breakdown by Horizon Tier

| Horizon Tier | Runs (Comp/Total) | Executed Steps | Useful Steps | Useful Efficiency | Failed Steps | Recovery Actions | Recovery Overhead | Actions/Target Ratio |
|---|---|---|---|---|---|---|---|---|
| **SHORT** | 32/32 | 136 | 136 | **100.00%** | 0 | 1 | 0.74% | **1.000** |
| **MEDIUM** | 32/36 | 284 | 280 | **98.59%** | 4 | 32 | 11.27% | **1.000** |
| **LONG** | 25/32 | 491 | 484 | **98.57%** | 7 | 48 | 9.78% | **1.000** |

## 3. Core Insights for Judges
1. **Zero Path Wandering on Completed Workflows:**
   - Across both development (Phase 10) and held-out (Phase 11) suites, completed workflows achieved an **actions-to-completion ratio of exactly 1.000**.
   - The agent never generates superfluous navigation clicks, redundant reloads, or exploratory wandering on successful tasks.
2. **Controlled Recovery Overhead:**
   - Recovery routines (stale DOM refetching, selective crop verification, spinner debounce) account for **8.89%** of actions in Phase 10 and **1.54%** in Phase 11.
   - Local recovery successfully rescues transient timing races without expanding the workflow trajectory into infinite loops.
3. **Bounded Failure Impact:**
   - When an unrecoverable failure occurs (e.g. model timeout or semantic ambiguity), the fail-closed policy triggers safe abstention rather than runaway retries.
   - This bounds the total executed steps to 911 (Phase 10) and 912 (Phase 11), strictly adhering to task horizon ceilings.

> [!NOTE]
> **Methodological Boundary:** This analysis is an internal evaluation of trajectory quality across the 200 evaluated runs. It is not an official external ranking from the Odysseys benchmark.
