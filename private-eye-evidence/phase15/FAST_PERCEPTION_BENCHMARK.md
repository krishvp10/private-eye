# Phase 15: Fast Perception & Grounding Benchmark (PS 26171)

## Executive Summary & Problem Statement Alignment
SIH Problem Statement 26171 states:
> *"On-device Visual Perception for Light-weight Browser Agents... A lightweight visual-perception engine should operate directly on the browser/edge device... locating clickable UI buttons and interacting with browser interfaces with sub-500 ms latency."*

Previously, relying solely on generative 3B VLM inference resulted in ~7.29 second per-turn latency—approximately **14.6× slower** than the stated sub-500 ms target.

In Phase 15, we designed and benchmarked a **Two-Tier Perception Engine**:
* **Tier 1 (Fast Local Perception Path)**: Deterministic DOM + ARIA + Geometry + Candidate Engine + Confidence Gating.
* **Tier 2 (Slow Generative Fallback)**: Qwen2.5-VL-3B local multimodal inference, invoked **only** when Tier-1 identifies ambiguity, low confidence, or visual-only content.

---

## Latency Profile Across 120 Interactions

From [`eval/reports/phase15_fast_perception.json`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/eval/reports/phase15_fast_perception.json):

### Hardware Environment:
* **Host Platform**: Windows 11 (AMD64)
* **Processor**: 13th Gen Intel(R) Core(TM) i7-13650HX (14 cores, 20 threads)
* **GPU**: NVIDIA GeForce RTX 4060 Laptop GPU (8GB GDDR6 VRAM)
* **Memory**: 16 GB DDR5 RAM
* **Python Runtime**: 3.13.3

### Granular Latency Breakdown:

| Pipeline Stage | p50 (ms) | p90 (ms) | p95 (ms) | p99 (ms) | Max (ms) | Mean (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DOM & ARIA Parsing** | 0.01 | 0.02 | 0.03 | 0.05 | 0.08 | 0.01 |
| **Privacy Detection** | 0.17 | 0.27 | 0.29 | 0.70 | 0.75 | 0.20 |
| **Image Redaction Masking** | 11.29 | 15.16 | 16.88 | 21.45 | 25.34 | 11.87 |
| **Candidate Ranking (Lexical/Role)**| 0.25 | 0.39 | 0.60 | 0.79 | 1.09 | 0.29 |
| **Decision Verification Gate** | 0.01 | 0.01 | 0.02 | 0.03 | 0.10 | 0.01 |
| **TIER-1 FAST PATH TOTAL** | **11.81** | **15.78** | **18.06** | **22.20** | **25.88** | **12.40** |
| **Tier-2 Qwen Fallback Baseline** | ~7,290.0 | ~7,290.0 | ~7,290.0 | ~7,290.0 | ~7,500.0 | ~7,290.0 |

---

## Two-Tier Routing & Sub-500ms Compliance Assessment

### 1. Can the FAST PATH perform visual perception + grounding in <500ms?
**YES.**
* **Measured Fast Path p50**: **11.81 ms** (42× faster than SLA).
* **Measured Fast Path p95**: **18.06 ms** (27× faster than SLA).
* **Fast Path Sub-500ms Compliance**: **100.0%** (120/120 steps).

### 2. What proportion of web interactions are resolved without VLM fallback?
* **Fast Path Accepted (No VLM required)**: **80.0%** (96/120 interactions).
* **Fallback Required (Ambiguity / Low Margin)**: **20.0%** (24/120 interactions).

### 3. Honest Statement on PS 26171 Compliance:
> PrivateEye's Tier-1 Fast Local Perception Path satisfies the sub-500ms target (p50 ~11.8 ms, p95 ~18.1 ms) for structured web grounding and form manipulation. However, **full generative multimodal reasoning with Qwen2.5-VL-3B remains ~7.29s**. PrivateEye achieves low latency through architectural tiering, not by claiming 3B generative models run in sub-500ms.
