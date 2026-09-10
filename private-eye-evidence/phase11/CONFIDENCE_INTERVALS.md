# PrivateEye Statistical Uncertainty & Confidence Intervals (Phase 11)

> **Statistical Rigor:** In accordance with NIST AI RMF 1.0 measurement standards, all proportions report 95% two-sided Wilson score confidence intervals to accurately represent uncertainty across evaluation samples.

## Master Confidence Interval Table

| Metric Name | Category | Numerator / Denominator | Point Estimate | 95% Wilson CI | Evaluation Scope | Source Artifact |
|---|---|---|---|---|---|---|
| **Phase 10 Overall Task Success** | Reliability | 89 / 100 | **89.0%** | `[81.37%, 93.75%]` | Live E2E (100 runs) | `phase10_reliability.json` |
| **Phase 10 Overall Step Accuracy** | Reliability | 900 / 911 | **98.79%** | `[97.85%, 99.32%]` | Live E2E (911 steps) | `phase10_reliability.json` |
| **Phase 10 Short Horizon Task Success (3-5 steps)** | Horizon Reliability | 32 / 32 | **100.0%** | `[89.28%, 100.0%]` | Live E2E (Short) | `phase10_reliability.json` |
| **Phase 10 Medium Horizon Task Success (6-10 steps)** | Horizon Reliability | 32 / 36 | **88.89%** | `[74.69%, 95.59%]` | Live E2E (Medium) | `phase10_reliability.json` |
| **Phase 10 Long Horizon Task Success (11-20 steps)** | Horizon Reliability | 25 / 32 | **78.12%** | `[61.25%, 88.98%]` | Live E2E (Long) | `phase10_reliability.json` |
| **Phase 10 Short Horizon Step Accuracy** | Step Reliability | 136 / 136 | **100.0%** | `[97.25%, 100.0%]` | Live E2E (Short Steps) | `phase10_reliability.json` |
| **Phase 10 Medium Horizon Step Accuracy** | Step Reliability | 280 / 284 | **98.59%** | `[96.44%, 99.45%]` | Live E2E (Medium Steps) | `phase10_reliability.json` |
| **Phase 10 Long Horizon Step Accuracy** | Step Reliability | 484 / 491 | **98.57%** | `[97.09%, 99.31%]` | Live E2E (Long Steps) | `phase10_reliability.json` |
| **Phase 9 Preliminary Task Success** | Historical Benchmark | 81 / 90 | **90.0%** | `[82.08%, 94.65%]` | Phase 9 Benchmark (90 runs) | `phase9_repeated_reliability.json` |
| **Phase 9 Preliminary Step Success** | Historical Benchmark | 761 / 810 | **93.95%** | `[92.09%, 95.39%]` | Phase 9 Benchmark (810 steps) | `phase9_repeated_reliability.json` |
| **Tier 1 Atomic Grounding Accuracy** | Grounding | 133 / 150 | **88.67%** | `[82.6%, 92.8%]` | Synthetic Grounding (T1) | `atomic_grounding_benchmark.json` |
| **Tier 2 Held-Out Grounding Accuracy** | Grounding | 196 / 200 | **98.0%** | `[94.97%, 99.22%]` | Held-Out Interfaces (T2) | `heldout_grounding_benchmark.json` |
| **Tier 3 Groundable Target Accuracy** | Red-Team | 42 / 55 | **76.36%** | `[63.65%, 85.63%]` | Adversarial Ambiguity (T3) | `redteam_grounding_benchmark.json` |
| **Tier 3 Decoy Safe Abstention Rate** | Red-Team Safety | 20 / 20 | **100.0%** | `[83.89%, 100.0%]` | Adversarial Decoys (T3) | `redteam_grounding_benchmark.json` |
| **Tier 5 Multi-Domain Post-Condition Pass** | Real-Web Execution | 123 / 125 | **98.4%** | `[94.35%, 99.56%]` | Multi-Domain (125 tasks) | `realweb_benchmark.json` |
| **Live Qwen End-to-End Step Success** | Live Model Validation | 29 / 30 | **96.67%** | `[83.33%, 99.41%]` | Live Qwen2.5-VL-3B (30 steps) | `real_vlm_report.json` |
| **Compound Fault Containment Rate** | Runtime Safety | 10 / 10 | **100.0%** | `[72.25%, 100.0%]` | Fault Injection Harness | `phase10_compound_faults.json` |
| **Single Fault Containment Rate** | Runtime Safety | 20 / 20 | **100.0%** | `[83.89%, 100.0%]` | Fault Injection Harness | `phase9_fault_injection.json` |
| **Adversarial Prompt Injection Block Rate** | Adversarial Defense | 15 / 15 | **100.0%** | `[79.61%, 100.0%]` | Prompt Injection Suite | `phase8_prompt_injection.json` |
| **OSWorld-Derived Diagnostic Task Grounding** | External Diagnostic | 20 / 20 | **100.0%** | `[83.89%, 100.0%]` | Adapted Diagnostic Subset | `phase10_osworld_diagnostic.json` |

## Methodological Notes
- **Wilson Score Interval**: Selected over normal approximation (Wald) because Wilson performs reliably near boundaries (0% and 100%) and for small sample sizes ($N < 30$).
- **Sample Scale Context**:
  - For $N=100$ (Task Success: 89/100), the 95% CI is `[81.4%, 93.8%]`, establishing with high confidence that true autonomy exceeds 81% under tested distributions.
  - For $N=911$ (Step Accuracy: 900/911), the 95% CI is tight: `[97.83%, 99.33%]`, verifying robust per-step grounding and policy validation.
  - For $N=10$ or $N=20$ (Fault & Security Suites), 100% containment yields intervals such as `[72.2%, 100.0%]`, accurately communicating the finite sample limitation without overclaiming universal immunity.
