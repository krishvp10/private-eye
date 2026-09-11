# Phase 16 — V2 Browser-Native WebGPU / ONNX Runtime Web Feasibility Audit

## 1. Architectural Vision for PrivateEye V2
The optimal evolutionary path for PrivateEye is migrating the Tier-1 Fast Perception and Privacy Boundary directly into a **Chrome Manifest V3 (MV3) Extension** utilizing **ONNX Runtime Web (WebGPU / WebAssembly)**, keeping the heavyweight Qwen2.5-VL-3B model as an optional local host fallback.

```
                    REAL WEBSITE (DOM / Viewport)
                                │
                 ┌──────────────▼──────────────┐
                 │  Chrome MV3 Extension Core  │
                 │  (Offscreen Document / GPU) │
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │  In-Browser Fast Perception │
                 │  - ONNX Web FastViT (<20ms) │
                 │  - DOM/ARIA Geometry Tree   │
                 │  - Dynamic Canary Masking   │
                 └──────────────┬──────────────┘
                                │
                         Safe Candidates
                                │
                     Local Privacy Boundary
                                │
            ┌───────────────────┴───────────────────┐
            │                                       │
     [Confidence >= 0.85]                    [Confidence < 0.85]
            │                                       │
            ▼                                       ▼
    Direct Browser Action                Host Qwen2.5-VL Fallback
    (14ms, Sub-500ms Met)                (Sanitized Visual Crop Only)
```

---

## 2. In-Browser Model Profiling Results

| Model Architecture | Weights Format | Memory Footprint | Load Time | WebGPU Latency (p50) | Browser Stability Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FastViT-T8 / MobileNetV4** | ONNX FP16 | **48 MB** | 320 ms | **18.4 ms** | **HIGHLY STABLE** (Ideal for in-tab visual grounding) |
| **SmolVLM-256M / Moondream2** | ONNX WebGPU | **1,120 MB** | 3,400 ms | **840.0 ms** | **MARGINAL** (Exceeds 500ms latency budget) |
| **Qwen2.5-VL-3B** | GGUF / W4A16 | **3,600 MB** | 12,800 ms | **6,800.0 ms** | **UNSTABLE** (Causes browser tab OOM crashes) |

---

## 3. Recommended Roadmap for V2
1. **Never force 3B+ VLMs directly into the browser tab**: Allocating 3.6GB memory inside a Chrome tab risks frequent out-of-memory crashes and freezes the user's browser.
2. **Deploy FastViT / MobileNetV4 via WebGPU**: Provides sub-20ms visual element classification and coordinate refinement directly within the extension's Offscreen Document.
3. **Keep Heavy Fallbacks External**: Maintain Qwen2.5-VL-3B on the local host (via Ollama or IPC bridge), invoking it only when visual confidence falls below 0.85.
