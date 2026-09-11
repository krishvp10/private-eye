# Phase 16 — Granular End-to-End Latency Profile

## 1. Disambiguation of Agent Latency vs. Perception Latency

> [!IMPORTANT]
> **Scientific Integrity Requirement**: Under no circumstances must Tier-1 Fast Perception latency (~14 ms) be conflated with the total end-to-end task turn latency or generative VLM reasoning latency.
> 
> "Sub-500 ms" applies strictly and exclusively to the **Tier-1 Local Fast Perception & Grounding Path**.

---

## 2. Measured Stage Latency Distributions (147 Operational Steps)

| Pipeline Stage | Implementation Layer | p50 (ms) | p95 (ms) | p99 (ms) | Mean (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DOM / ARIA Extraction** | Playwright / JS In-Tab | 4.8 | 6.2 | 8.1 | 5.0 |
| **Dynamic Regex & DOM Masking** | Local Python Engine | 3.2 | 4.5 | 5.9 | 3.5 |
| **Candidate Generation & Ranking** | Local SafeCandidate Engine | 6.5 | 7.9 | 9.8 | 6.8 |
| **Visual Crop Verification (Selective)**| PIL / OpenCV Local | 12.1 | 16.4 | 21.0 | 13.2 |
| **Tier-1 Fast Perception Aggregate** | Host Local (DOM + Ref + Rank) | **14.57** | **17.29** | **22.40** | **14.08** |
| **Tier-2 Qwen VLM Fallback** | Local Ollama Qwen2.5-VL-3B | **7,153.0**| **7,410.0**| **7,890.0**| **7,240.5** |
| **Local Policy Engine Evaluation** | LocalPolicyEngine Rule Gate | 1.1 | 1.8 | 2.4 | 1.2 |
| **Action Dispatch & Execution** | Playwright Automation Bridge| 45.2 | 82.0 | 110.0 | 52.4 |
| **Post-Condition State Verification** | Local DOM Observer | 18.4 | 28.6 | 36.2 | 20.1 |

---

## 3. Fast-Path Utilization & Weighted Average Latency

Across the 147 steps executed during the real-world validation program:
- **Tier-1 Fast-Path Turns**: 82.31% (121 / 147 steps)
- **Tier-2 Qwen Fallback Turns**: 17.69% (26 / 147 steps)

### Weighted Latency Formula:
$$\text{Perception Latency}_{\text{weighted}} = (0.8231 \times 14.08\text{ ms}) + (0.1769 \times 7240.5\text{ ms}) \approx 1,276.74\text{ ms}$$

### Turn-Level Latency (Perception to Dispatched Action):
- **p50 Turn Latency**: **120.4 ms** (Governed by Fast-Path DOM/ARIA matches)
- **Mean Turn Latency**: **1,354.33 ms** (Reflecting the 17.7% Qwen fallback penalty)

---

## 4. Conclusion
By offloading 82.3% of routine navigation and input actions to the Tier-1 Fast Perception pipeline, PrivateEye delivers a median interactive turn latency of **120.4 ms**, far exceeding human interactive responsiveness while reserving heavy generative reasoning for genuinely ambiguous visual elements.
