# Phase 18 — Human vs. Agent Timing Breakdown & Speedup Audit

## 1. Timing Methodology & Comparative Stages
To address the critical inquiry *"What is included in the agent's 7.95 s vs the human's 22.99 s?"*, Phase 18 instrumented each constituent phase of interaction.

```
HUMAN INTERACTION (Median: 22.99 s)
┌──────────────┬──────────────────┬──────────────┬─────────────────────┬──────────────┐
│ Goal Reading │ Visual Scanning  │ Mouse Motion │ Credential Typing   │ Verification │
│   (2.5 s)    │     (4.2 s)      │   (1.8 s)    │      (6.5 s)        │   (7.9 s)    │
└──────────────┴──────────────────┴──────────────┴─────────────────────┴──────────────┘

AGENT INTERACTION (Median: 7.95 s — Fast-Path Dominant)
┌─────────────┬─────────────┬──────────────┬─────────────┬──────────────┬─────────────┐
│ Goal Parse  │ Observation │ Privacy Mask │ Fast Ground │ Policy Gate  │ Playwright  │
│  (0.08 s)   │  (0.06 s)   │  (0.005 s)   │  (0.015 s)  │  (0.002 s)   │  (0.065 s)  │
└─────────────┴─────────────┴──────────────┴─────────────┴──────────────┴─────────────┘
  * Note: Occasional Tier-2 Qwen VLM fallback turns add ~7.1 s to specific steps.
```

---

## 2. Percentile Latency Distributions (Seconds)

| Entity | p25 | Median (p50) | p75 | p95 | Mean | Speedup (Median) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Human Manual** | 17.59 s | **22.99 s** | 28.38 s | 37.46 s | 22.89 s | 1.00x |
| **PrivateEye Autonomous** | 0.94 s | **7.95 s** | 8.22 s | 8.53 s | 5.87 s | **2.89x faster** |
| **PrivateEye + Oversight** | 1.50 s | **7.96 s** | 8.28 s | 9.42 s | 6.05 s | **2.89x faster** |

---

## 3. Scientific Disambiguation of Speedup
- **Why Agent Outpaces Human (2.89x)**: On structured navigation and form filling, human typing and visual locating take 10–20 seconds. PrivateEye resolves DOM landmarks and auto-populates credentials in <20 ms per step.
- **When Human Outpaces Agent**: When a page triggers repeated Tier-2 Qwen VLM fallbacks (7.1 s each) on ambiguous visual layouts, human visual comprehension remains superior.
