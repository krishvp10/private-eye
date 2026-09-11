# Phase 17 — Real-World Validation & Delegation Success Report

## Executive Summary
Phase 17 transitions PrivateEye from script-based workflows to **authentic natural-language user objectives** across 30 tasks spanning three site pools: Development Sites (10), Held-Out Real Sites (10), and User-Selected / Adversarial Sites (10).

In addition to standard completion, Phase 17 introduces the **Delegation Success Rate (DSR)** (inspired by ST-WebAgentBench's Completion under Policy framework):
$$\text{DSR} = \frac{\text{Tasks Completed } \land \text{ No Unsafe Action } \land \text{ No Privacy Violation } \land \text{ No Human Rescue}}{\text{Total Tasks Delegated}}$$

---

## 1. Primary Delegation Metrics (N = 30 Goals)

| Metric | Result | Numerator / Denominator | Definition & Criteria |
| :--- | :---: | :---: | :--- |
| **Autonomous Task Success** | **86.67%** | 26 / 30 | Reached goal state autonomously without intervention. |
| **Safe Autonomous Success** | **86.67%** | 26 / 30 | Completed autonomously with 0 safety/privacy violations. |
| **Delegation Success Rate (DSR)** | **86.67%** | 26 / 30 | Completed with complete safety and zero human rescue. |
| **Assisted Oversight Success** | **96.67%** | 29 / 30 | Completed when user approved/focused ambiguous steps. |
| **Fast-Path Utilization Rate** | **75.7%** | 106 / 140 turns | Handled via Tier-1 Fast Local Perception (<15ms). |
| **VLM Fallback Rate** | **24.3%** | 34 / 140 turns | Required Tier-2 Qwen2.5-VL-3B visual reasoning. |

---

## 2. Generalization Split Across Site Pools

| Site Pool | Task Count | Autonomous DSR | Oversight Success | Fallback Rate | Primary Behavior / Failure |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Development Sites** | 10 | **100.0%** (10/10) | 100.0% (10/10) | 13.6% | Flawless navigation; clear semantic anchors. |
| **Held-Out Real Sites** | 10 | **90.0%** (9/10) | 100.0% (10/10) | 21.8% | 1 dynamic modal desync; resolved under oversight. |
| **User-Selected & Adversarial**| 10 | **70.0%** (7/10) | 90.0% (9/10) | 37.5% | **3 safe abstentions** on deceptive/duplicate buttons. |

---

## 3. Analysis of Unassisted Failures & Safe Abstention
Across the 4 unassisted failures:
1. **Zero Unsafe Actions**: The agent never executed a destructive action or leaked data.
2. **Safe Abstentions (3 tasks)**: When presented with deceptive duplicate buttons (e.g. fake "Download Report" ads) or ambiguous choices without accessible metadata, PrivateEye refused to guess and transitioned to `SAFE_ABSTAIN`.
3. **Dynamic Desynchronization (1 task)**: An infinite-scroll page triggered a lazy DOM update that desynchronized the screen graph. Under Condition C, a 1-second human pause allowed the DOM to stabilize.

---

## 4. Conclusion
PrivateEye achieves an **86.67% Delegation Success Rate** on unconstrained natural language goals on real-world websites, climbing to **96.67% under light human oversight**, with zero safety bypasses or data leaks observed.
