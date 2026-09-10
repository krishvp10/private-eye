# PrivateEye: Final Machine-Validated Metric Integrity Report

**Validation Scope:** 19 Authoritative Published Metrics Reconciled Against Canonical JSON Artifacts
**Validation Verdict:** **CERTIFIED CONSISTENT** (19/19 Passed)

## 1. Metric Reconciliation Matrix

| Metric Name | Evaluation Scope | Canonical Source | Reported | Recomputed | Exact Formula ($N / D$) | Status |
|---|---|---|---|---|---|---|
| **Phase 10 Overall Task Success Rate** | Live 100-Run Campaign (25 workflows x 4 reps) | `phase10_reliability.json` | `89.0%` | `89.0` | `89 / 100 * 100` | **PASS** |
| **Phase 10 Overall Step Accuracy Rate** | Live 100-Run Campaign (911 evaluated steps) | `phase10_reliability.json` | `98.8% (98.79%)` | `98.79` | `900 / 911 * 100` | **PASS** |
| **Phase 10 Short Workflow Task Success** | Short Horizons (3-5 steps) | `phase10_reliability.json` | `100.0%` | `100.0` | `32 / 32 * 100` | **PASS** |
| **Phase 10 Medium Workflow Task Success** | Medium Horizons (6-10 steps) | `phase10_reliability.json` | `88.9%` | `88.89` | `32 / 36 * 100` | **PASS** |
| **Phase 10 Long Workflow Task Success** | Long Horizons (11-20 steps) | `phase10_reliability.json` | `78.1%` | `78.12` | `25 / 32 * 100` | **PASS** |
| **Phase 9 Repeated Task Success Rate** | Historical Phase 9 (30 workflows x 3 reps = 90 runs) | `phase9_repeated_reliability.json` | `90.0%` | `90.0` | `81 / 90 * 100` | **PASS** |
| **Phase 9 Preliminary Trial Step Success (Reconciled)** | Phase 9 Preliminary 810-Step Observation | `phase9_repeated_reliability.json (prelim trial)` | `93.95% (reconciled from 761/810)` | `93.95` | `761 / 810 * 100` | **PASS** |
| **Tier 1 Atomic Grounding Target Accuracy** | Deterministic Grounding (150 cases) | `atomic_grounding_benchmark.json` | `88.7%` | `88.67` | `133 / 150 * 100` | **PASS** |
| **Tier 2 Held-Out Grounding Target Accuracy** | Held-Out Synthetic Grounding (200 cases) | `heldout_grounding_benchmark.json` | `98.0%` | `98.0` | `196 / 200 * 100` | **PASS** |
| **Tier 3 Red-Team Groundable Target Accuracy** | Adversarial & Ambiguous Targets (55 groundable cases) | `redteam_grounding_benchmark.json` | `76.4%` | `76.36` | `42 / 55 * 100` | **PASS** |
| **Tier 3 Red-Team Safe Abstention Rate** | Adversarial Decoys / Ungroundable Controls (20 cases) | `redteam_grounding_benchmark.json` | `100.0%` | `100.0` | `20 / 20 * 100` | **PASS** |
| **Tier 5 Real-Web Execution Success Rate** | Hybrid DOM + Policy Engine (125 tasks across 25 sites) | `realweb_benchmark.json` | `98.4%` | `98.4` | `123 / 125 * 100` | **PASS** |
| **Live Qwen2.5-VL-3B E2E Pipeline Success** | Live Multimodal Browser Inference (30 steps) | `real_vlm_report.json` | `96.7%` | `96.67` | `29 / 30 * 100` | **PASS** |
| **Compound Fault-Injection Containment Rate** | Compositional Chaos Testing (10 scenarios) | `phase10_compound_faults.json` | `100.0%` | `100.0` | `10 / 10 * 100` | **PASS** |
| **Single Fault-Injection Fail-Closed Rate** | Runtime Failure Invariant Testing (20 scenarios) | `phase9_fault_injection.json` | `100.0%` | `100.0` | `20 / 20 * 100` | **PASS** |
| **Prompt Injection Attack Blocking Rate** | Webpage Adversarial Content (15 injection vectors) | `phase8_prompt_injection.json` | `100.0%` | `100.0` | `15 / 15 * 100` | **PASS** |
| **Privacy-Under-Failure Secret Leak Count** | Privacy Under Injected Failures (11 boundaries, 21 secrets, 8 failure modes) | `phase10_privacy_failure_audit.json` | `0 detected leaks` | `0.0` | `0 detected out of 21 secrets` | **PASS** |
| **OSWorld External Diagnostic Subset Accuracy** | PRIVATEEYE EXTERNAL DIAGNOSTIC SUBSET — OSWORLD (20 tasks) | `phase10_osworld_diagnostic.json` | `100.0%` | `100.0` | `20 / 20 * 100` | **PASS** |
| **Emergency Kill Switch Local Dispatch-Path Latency** | Local Thread-Safe Interrupt Bench | `phase10_kill_switch_event.json` | `0.043 ms` | `0.043` | `0.043 ms elapsed, 0 subsequent actions dispatched` | **PASS** |

## 2. Key Mathematical Reconciliations

### A. Phase 10 100-Run Campaign (Current Release Milestone)
- **Task Success:** **89/100 = 89.0%** across 25 workflows evaluated 4 times.
- **Step Accuracy:** **900/911 = 98.79%** (reported as 98.8%).
- **Breakdown by Horizon:**
  - Short: 32/32 tasks (**100.0%**), 136/136 steps (**100.0%**).
  - Medium: 32/36 tasks (**88.89%**), 280/284 steps (**98.59%**).
  - Long: 25/32 tasks (**78.12%**), 484/491 steps (**98.57%**).
- **Repeated-Target Loops:** **0 / 911 = 0.0%**.

### B. Phase 9 90-Run Benchmark (Historical Baseline)
- **Task Success:** **81/90 = 90.0%** across 30 workflows evaluated 3 times.
- **Preliminary Step Observation:** **761/810 = 93.95%** (formerly approximated as 94.2% in text; formally reconciled here to 93.95%).
- **Repeated-Target Loops:** **0 / 810 = 0.0%**.

### C. External Diagnostic Attribution
- The 20/20 result is an **adapted diagnostic subset** from OSWorld Web taxonomy, not an official leaderboard submission.

### D. Kill Switch Scope
- 0.043 ms represents **measured local dispatch-path kill-switch latency** in the controlled test, blocking Playwright dispatch with zero subsequent actions.

## 3. Conclusion
All headline numbers across documentation and reports are mathematically verified and bound directly to their canonical JSON artifacts. Zero numerical discrepancies remain.