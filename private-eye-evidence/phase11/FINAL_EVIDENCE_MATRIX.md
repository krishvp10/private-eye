# PrivateEye v1.0-RC: Authoritative Master Evidence Matrix (Phase 11)

> **Standard Compliance:** Aligned with **NIST AI RMF 1.0** and **OWASP Agent Control Standard (ACS 2026)**.  
> **Integrity Verification:** Every figure is mechanically validated against canonical JSON evidence by `eval/final_metric_validator.py`.

---

## Master Evaluation Matrix

| Metric Name | Numerator | Denominator | Result | 95% Wilson CI | Evaluation Scope | Benchmark Harness Type | Source JSON Artifact | Notes / Limitations |
|---|---|---|---|---|---|---|---|---|
| **Phase 10 Overall Task Success** | 89 | 100 | **89.0%** | `[81.4%, 93.8%]` | Live E2E (100 runs) | Live Multi-Domain Execution | `phase10_reliability.json` | 25 distinct workflows x 4 repetitions; hero autonomy result |
| **Phase 10 Overall Step Accuracy** | 900 | 911 | **98.79%** | `[97.8%, 99.3%]` | Live E2E (911 steps) | Live Multi-Domain Execution | `phase10_reliability.json` | Local action accuracy across all evaluated turns |
| **Short Horizon Task Success** | 32 | 32 | **100.0%** | `[89.3%, 100.0%]` | Short (3–5 steps) | Live Multi-Domain Execution | `phase10_reliability.json` | Atomic operations show perfect multi-run consistency |
| **Medium Horizon Task Success** | 32 | 36 | **88.89%** | `[74.7%, 95.6%]` | Medium (6–10 steps) | Live Multi-Domain Execution | `phase10_reliability.json` | State accumulation introduces initial DOM races |
| **Long Horizon Task Success** | 25 | 32 | **78.12%** | `[61.2%, 88.9%]` | Long (11–20 steps) | Live Multi-Domain Execution | `phase10_reliability.json` | Bernoulli compounding $(0.9879)^{20} \approx 78.36\%$ |
| **Phase 11 Held-Out Validation Tasks** | 86 | 100 | **86.0%** | `[77.9%, 91.5%]` | Held-Out (50 patterns x 2) | Independent Blind Benchmark | `phase11_independent_validation.json` | 8 unseen sectors, uncalibrated blind validation |
| **Phase 11 Held-Out Step Accuracy** | 898 | 912 | **98.46%** | `[97.4%, 99.1%]` | Held-Out (912 steps) | Independent Blind Benchmark | `phase11_independent_validation.json` | Consistent with Phase 10 per-step execution fidelity |
| **Phase 9 Preliminary Task Success** | 81 | 90 | **90.0%** | `[82.0%, 94.8%]` | Historical Trial (90 runs) | Multi-Domain Development | `phase9_repeated_reliability.json` | Reconciled historical trial across 30 workflows |
| **Phase 9 Preliminary Step Success** | 761 | 810 | **93.95%** | `[92.1%, 95.4%]` | Historical Trial (810 steps)| Multi-Domain Development | `phase9_repeated_reliability.json` | Reconciled from 761/810; formerly approximated as 94.2% |
| **Tier 1 Atomic Grounding** | 133 | 150 | **88.67%** | `[82.6%, 92.8%]` | Synthetic Grounding | Component Unit Test | `atomic_grounding_benchmark.json` | Baseline local candidate engine without crop verifier |
| **Tier 2 Held-Out Grounding** | 196 | 200 | **98.00%** | `[95.0%, 99.2%]` | Held-Out Synthetic (200) | Synthetic Grounding Suite | `heldout_grounding_benchmark.json` | Selective visual crop verifier active; 0 wrong executions |
| **Tier 3 Red-Team Groundable Target**| 42 | 55 | **76.36%** | `[63.6%, 85.7%]` | Adversarial Ambiguity (55) | Red-Team Stress Suite | `redteam_grounding_benchmark.json` | Groundable cases under adversarial noise |
| **Tier 3 Decoy Safe Abstention** | 20 | 20 | **100.0%** | `[83.9%, 100.0%]` | Red-Team Decoys (20) | Red-Team Stress Suite | `redteam_grounding_benchmark.json` | Safe refusal (`ASK_USER`) on ungroundable controls |
| **Tier 5 Multi-Domain Post-Condition** | 123 | 125 | **98.40%** | `[94.3%, 99.6%]` | Real-Web Tasks (125) | Multi-Domain Execution | `realweb_benchmark.json` | Evaluated across 25 real-world websites |
| **Live Qwen Multimodal Turn Success** | 29 | 30 | **96.67%** | `[83.3%, 99.4%]` | Live Qwen2.5-VL-3B | Real Browser API Execution | `real_vlm_report.json` | Full multimodal inference turns (p50: 7.29 s) |
| **Compound Fault Containment** | 10 | 10 | **100.0%** | `[72.2%, 100.0%]` | Multi-Layer Faults (10) | Controlled Chaos Harness | `phase10_compound_faults.json` | 10/10 compound failure scenarios contained |
| **Single Fault Containment** | 20 | 20 | **100.0%** | `[83.9%, 100.0%]` | Single Fault Scenarios (20) | Fault Injection Harness | `phase9_fault_injection.json` | 20/20 single fault injections safely handled |
| **Adversarial Prompt Injection Block** | 15 | 15 | **100.0%** | `[79.6%, 100.0%]` | Prompt Vectors (15) | Adversarial Security Suite | `phase8_prompt_injection.json` | 15/15 direct & indirect injections blocked |
| **Privacy Under Failure Secret Leaks** | 0 | 11 | **0 Leaks** | `[0.0%, 25.9%]` | 11 Representation Surfaces | Chaos Security Harness | `phase10_privacy_failure_audit.json` | 0 leaks across 11 surfaces & 21 credentials under 8 faults |
| **OSWorld Adapted Diagnostic** | 20 | 20 | **100.0%** | `[83.9%, 100.0%]` | Adapted Diagnostic (20) | External Diagnostic Harness| `phase10_osworld_diagnostic.json` | 20/20 on adapted diagnostic subset; not official OSWorld score |
| **Kill Switch Local Dispatch Latency**| 0.043 ms | 1 test | **0.043 ms** | Controlled measurement | Local Dispatch Interrupt | Controlled Unit Benchmark | `phase10_kill_switch_event.json` | Local dispatch-path interrupt; zero subsequent actions |

---

## Key Methodological Principles
1. **Separation of Evaluation Tiers:** Synthetic benchmarks, live multi-domain runs, chaos harnesses, and external diagnostics are kept distinct and never conflated into an aggregated score.
2. **Wilson 95% Confidence Intervals:** Every binary outcome reflects the mathematical sample size limitation, communicating true scientific uncertainty.
3. **Reproducibility Guarantee:** All rows map directly to canonical JSON reports verified by `eval/final_metric_validator.py`.
