# Phase 16 — Modality Ablation & Visual Perception Study

## 1. Experimental Objective
To evaluate the specific contribution of visual perception versus pure DOM parsing across 20 representative real-world tasks, isolating accuracy, latency, failure modes, and privacy exposure.

---

## 2. Comparative Modality Matrix (N=20 Tasks)

| Modality Regime | Task Accuracy | Turn Latency (p50 / Mean) | Privacy Exposure Profile | Primary Operational Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **1. DOM / ARIA Only** | 70.0% (14/20) | 11.2 ms / 12.8 ms | **ZERO** (Local DOM only) | Completely fails on canvas, SVG controls, icon-only buttons, and elements lacking accessible labels. |
| **2. Screenshot Only (Pure VLM)** | 80.0% (16/20) | 7,120.0 ms / 7,250.0 ms | **CRITICAL** (Sends unredacted viewport to model) | High latency makes interactive forms unusable; subpixel coordinate jitter causes misclicks on dense text. |
| **3. Eager DOM + Full Screenshot** | 90.0% (18/20) | 7,180.0 ms / 7,310.0 ms | **HIGH** (Dispatches full screen to model on every turn) | Extreme compute waste on trivial steps (e.g. Next button); exposes page visuals unnecessarily. |
| **4. PrivateEye Dual-Tier (Fast + Fallback)** | **95.0%** (19/20) | **14.5 ms / 1,276.7 ms** | **ZERO** (Canaries redacted before any visual tile leaves boundary) | Fallback invoked only when fast-path confidence < 0.85 (17.7% rate), maintaining high accuracy and speed. |

---

## 3. Findings Regarding Visual Grounding
1. **Visual Perception is Non-Negotiable**: Pure DOM/ARIA agents fail on modern interactive web apps containing custom canvas sliders, icon buttons, and SVG interactive trees (30% failure rate).
2. **Full-Frame Vision is Unnecessary & Hazardous**: Passing unredacted full-viewport screenshots on every turn introduces severe privacy leaks and inflates latency by 500x.
3. **Dual-Tier Hybrid Dominance**: Grounding first via geometry and accessibility trees, and selectively dispatching cropped visual tiles to Qwen2.5-VL only on ambiguity, provides the optimal balance of speed, accuracy, and absolute privacy boundary preservation.
