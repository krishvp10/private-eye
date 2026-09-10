# Phase 7 Model Comparison: Qwen2.5-VL-3B vs Qwen2.5-VL-7B

**Benchmark Split:** 275 Cases (200 Held-Out + 75 Red-Team Adversarial)
**Experimental Control:** Strictly identical prompts, 768px resolution, $k=5$, selective verifier, temperature 0.0.

## 1. Controlled Model Performance Table

| Evaluation Metric | Qwen2.5-VL-3B | Qwen2.5-VL-7B | Comparison / Delta |
|---|---|---|---|
| **Overall Target Accuracy** | **93.82%** (258/275) | **94.91%** (261/275) | +1.09% for 7B |
| **Held-Out Accuracy (N=200)** | 98.0% | 98.5% | +0.5% (+1 case) |
| **Red-Team Accuracy (N=55)** | 76.36% | 80.0% | +3.6% (+2 cases) |
| **Safe Abstention (N=20)** | **100.0%** (20/20) | **100.0%** (20/20) | Parity (Zero false actions) |
| **Wrong-Target Rate** | **0.73%** (2/275) | **0.73%** (2/275) | Parity |
| **Workflow Success** | **5/5 (100.0%)** | 4/5 (80.0%) | **3B superior (+20%)** |
| **Recovery Success** | **100.0%** | 96.0% | 3B superior (no timeouts) |
| **p50 Step Latency** | **7.2 s** | 13.4 s | **3B is 1.86x faster** |
| **p95 Step Latency** | **9.8 s** | 18.2 s | 3B is 1.86x faster |
| **VRAM Footprint** | **3.8 GB** | 8.4 GB | **7B exceeds 8GB hardware class** |
| **Edge Hardware Fit** | **YES (<= 8GB)** | NO (requires offload/swap) | 3B edge-compliant |

## 2. Pareto Trade-Off & Deployment Decision

> **Official Stance:** 3B is the preferred deployment model for the current PrivateEye evaluation workload. 7B offers a marginal +1.1% gain in target grounding on difficult edge cases, but at prohibitive costs in latency (+86%), memory (+121%), and end-to-end workflow completion. 3B operates comfortably inside the 8 GB edge VRAM envelope with responsive execution.

### Why 3B is the Preferred Deployment Model:
1. **Dominates Latency:** 7.2s vs 13.4s allows interactive browser control without agent stalls or client timeout disconnects.
2. **Strict Edge Compliance:** 3.8 GB VRAM comfortably fits modern consumer laptops (RTX 4060 / 3070 8GB, Apple M-series), whereas 8.4 GB causes memory paging and CUDA OOM.
3. **Higher End-to-End Success:** 5/5 complete workflows vs 4/5 for 7B (7B suffered timeout drift during multi-step modal handling).
4. **Pareto Optimal:** The +1.1% grounding difference on isolated screenshots does not justify the 86% latency penalty and 121% memory expansion.
