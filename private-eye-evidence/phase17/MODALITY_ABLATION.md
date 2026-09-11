# Phase 17 — Modality Ablation & Grounding Performance

## 1. Experimental Setup
Ablation across 25 representative multi-domain tasks to isolate the performance, latency, and privacy impact of DOM perception versus visual grounding:
1. **DOM / ARIA Only**: Zero vision inputs.
2. **Vision Only**: Pure screenshot VLM grounding without DOM accessibility tree.
3. **Eager DOM + Vision**: Passing full DOM and full viewport screenshot to VLM on every turn.
4. **PrivateEye Dual-Tier**: Fast Local Perception (DOM + Ref) with selective Qwen fallback on ambiguous visual targets.

---

## 2. Modality Performance Matrix (N = 25 Tasks)

| Modality Regime | Task Completion | Turn Latency (p50 / Mean) | Privacy Exposure | Primary Bottleneck |
| :--- | :---: | :---: | :---: | :--- |
| **DOM / ARIA Only** | 68.0% (17/25) | 11.2 ms / 12.5 ms | **ZERO** | Inability to ground canvas, SVG graphs, icon-only buttons, and elements lacking ARIA accessibility trees. |
| **Vision Only (Pure VLM)** | 76.0% (19/25) | 7,160 ms / 7,240 ms | **CRITICAL** | Raw viewport dispatched to model; subpixel coordinate drift causes misclicks on dense text links. |
| **Eager DOM + Vision** | 88.0% (22/25) | 7,210 ms / 7,280 ms | **HIGH** | Redundant compute and severe latency on trivial navigation buttons; unredacted visual context leaked. |
| **PrivateEye Dual-Tier** | **92.0%** (23/25) | **128.5 ms / 1,860 ms** | **ZERO** | Selective fallback isolates visual crops; achieves high accuracy with 75.7% fast-path acceleration. |

---

## 3. Conclusions for System Architecture
- Pure DOM agents fail on modern visual web elements (32% failure rate).
- Full-viewport visual agents introduce intolerable latency (7.2s/step) and unacceptable privacy risks.
- PrivateEye's dual-tier architecture remains the only design that satisfies high accuracy, low latency, and zero wire data leakage simultaneously.
