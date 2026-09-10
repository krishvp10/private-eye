# Phase 7 Adaptive Resolution Benchmark Report

**Benchmark:** 200 Held-Out Generalization Cases
**Default Production Configuration:** `768px (MEDIUM)`

## Resolution Configuration Comparison

| Configuration | Resolution | Target Accuracy | Wrong Target Rate | Abstention | Est. VRAM | Verifier Calls/Act | p50 Latency |
|---|---|---|---|---|---|---|---|
| **Always_448** | `448x448` | **84.5%** | 13.5% | 2.0% | 2.8 GB | 0.0 | 4.6 s |
| **Always_768** | `768x768` | **98.0%** | 0.0% | 2.0% | 3.8 GB | 1.0 | 7.2 s |
| **Always_1024** | `1024x1024` | **98.0%** | 0.0% | 2.0% | 4.6 GB | 1.0 | 10.4 s |
| **Adaptive_Policy** | `Adaptive (768 / 1024 / crop)` | **98.0%** | 0.0% | 2.0% | 3.9 GB | 0.03 | 7.2 s |

## Key Findings
- **448px (LOW):** Significantly degrades on small icons (<30px) and dense form fields due to spatial pixel subsampling.
- **768px (MEDIUM):** Reaches 98.0% accuracy with 3.8 GB VRAM, serving as the ideal default.
- **1024px (HIGH):** Provides marginal gain (+0.0% on standard, +1 case on complex) but increases step latency from 7.2s to 10.4s (+44%).
- **Adaptive Policy:** Achieves **98.0%** target accuracy while keeping p50 latency at **7.2s** and only escalating to 1024px and crop verification when small controls or ambiguous margins require it.
