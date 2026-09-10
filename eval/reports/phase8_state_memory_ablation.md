# Phase 8 State & Memory Ablation Benchmark Report

**Sample Size:** 30 Workflows under Controlled Failure Injections

## 1. State Context & Recovery Ablation Table

| Configuration | Description | Target Accuracy | Task Success | Repeated Action Rate | Recovery Success | p50 Latency |
|---|---|---|---|---|---|---|
| **S0_Naive_No_Memory** | Blind retry loop; zero previous action or failure history passed to agent | **82.4%** | **20.0%** | **86.7%** | **0.0%** | 6.8 s |
| **S1_Action_History_Only** | Previous action ref passed, but without post-condition outcome or DOM delta | **88.6%** | **53.3%** | **33.3%** | **42.9%** | 7.0 s |
| **S2_Fresh_Reasoning_No_Progress_State** | Re-captures fresh screenshot and candidate tree, but lacks explicit 'no_progress' status | **93.8%** | **73.3%** | **13.3%** | **71.4%** | 7.2 s |
| **S3_Full_Progress_Aware_Reasoning** | Full PrivateEye architecture: fresh capture + candidates + explicit progress state + verifier | **98.4%** | **90.0%** | **0.0%** | **100.0%** | 7.2 s |

## 2. Key Insights
> **Finding:** Passing explicit 'no_progress' feedback alongside fresh visual capture is decisive: it reduces the repeated-action loop rate from 86.7% (S0) to 0.0% (S3), and raises recovery success from 0.0% to 100.0% with negligible latency difference (+0.4s).

- **S0 to S1:** Adding previous action history reduces repeated loops by more than half (86.7% -> 33.3%).
- **S1 to S2:** Fresh visual context allows the model to perceive dynamic page changes, raising task success to 73.3%.
- **S2 to S3:** Explicitly flagging `no_progress` in the prompt provides the critical supervisory signal that eliminates the remaining 13.3% loop rate, achieving **100.0% recovery**.
