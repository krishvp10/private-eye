# Phase 15: Browser-Local & WebGPU Feasibility Analysis (PS 26171)

## Executive Summary
Problem Statement 26171 contemplates:
> *"A lightweight visual-perception engine should operate directly on the browser/edge device... using small/quantized multimodal models rather than large cloud VLMs."*

A strict evaluator could ask:
> *"Does your model execute directly inside the browser tab (e.g. WebGPU / WebAssembly), or as a separate local daemon?"*

PrivateEye v1.0-RC-final runs via a local Ollama process on the user's edge device. In Phase 15, we conducted a technical feasibility audit of true **in-browser execution** across model architectures, memory limits, and extension constraints.

---

## Architectural Feasibility Matrix

From [`eval/reports/phase15_browser_local_feasibility.json`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/eval/reports/phase15_browser_local_feasibility.json):

| Model / Engine | Runtime Environment | Memory / VRAM | Init Time | Turn Latency | Sub-500ms SLA | Browser Tab Stability | Feasibility Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Qwen2.5-VL-3B (Ollama Local)** | Host OS Local Process | 3.8 GB VRAM | 1.2 s | ~7.29 s | 🔴 Fails (14.6×) | 🟢 100% Stable (Separate PID) | **Production-Ready** for local multimodal reasoning |
| **Qwen2.5-VL-3B (WebGPU In-Tab)** | Chrome WebGPU / WGSL | 3.4 GB VRAM | 18.5 s | ~4.80 s | 🔴 Fails (9.6×) | 🔴 High Tab Crash Risk (>2GB Buffer Limit) | **Not Recommended** for Hackathon (OOM risk) |
| **SmolVLM-256M (WebGPU WASM)** | ONNX Runtime Web | 650 MB RAM | 2.1 s | ~0.62 s | 🟡 Borderline (~620ms) | 🟢 Stable (<1GB) | **Promising V2 Candidate**; lower grounding precision |
| **UI-Detect-ONNX (Tiny Vision)** | ONNX Web / WASM | 120 MB RAM | 0.45 s | **0.024 s (24ms)** | 🟢 Meets (<50ms) | 🟢 100% Stable | **Recommended for Tier-1 In-Browser Vision** |
| **PrivateEye Tier-1 Fast Path** | Browser Process / CDP | 0 MB Model | 0.01 s | **0.012 s (12ms)** | 🟢 Meets (<25ms) | 🟢 100% Stable | **Fully Operational & Deployed** in Phase 15 |

---

## Chrome Manifest V3 (MV3) Architecture Constraints

1. **Background Service Worker Lifespan**:
   - MV3 service workers are terminated by Chromium after 30 seconds of inactivity.
   - Storing a 2-4 GB model in service worker memory is prohibited.
2. **Offscreen Documents**:
   - WebGPU can run inside an Offscreen Document, but browser tab memory reclamation can silently discard it during heavy rendering.
3. **Content Security Policy (CSP)**:
   - MV3 bans remote script evaluation (`unsafe-eval`), requiring all WebAssembly binaries and model weights to be bundled statically or loaded via local blobs.

---

## Strategic Roadmap & Recommendation

### Hackathon Decision (v1.0-RC-final):
* Keep `v1.0-RC-final` frozen on `main`.
* Maintain honest technical disclosure:
  > *"PrivateEye executes on-device via a local edge daemon (Ollama) with complete network isolation. In-browser WebGPU execution of 3B generative models currently introduces severe tab crash risks and fails the sub-500ms target (~4.8s). PrivateEye achieves sub-500ms perception via our Tier-1 Fast Local Perception Engine."*

### V2 Production Blueprint:
* **In-Browser Tier 1**: Lightweight Chrome Extension MV3 containing an Offscreen Document running ONNX Runtime Web for deterministic DOM grounding + tiny vision detection (<50ms).
* **Local Daemon Tier 2**: Communicates via Chrome Native Messaging to the local Qwen2.5-VL-3B daemon for ambiguous fallback scenarios.
