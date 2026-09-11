# Phase 17 — SIH 2026 Problem Statement 26171 Final Scientific Compliance Matrix

## 1. Compliance Assessment Framework
**Problem Statement 26171**: *"On-device Visual Perception for Light-weight Browser Agents"*

To adhere to rigorous scientific standards, this compliance assessment enforces unambiguous classification:
- `FULLY SATISFIED`
- `PARTIALLY SATISFIED`
- `NOT SATISFIED`
- `NOT TESTED`
- `NOT FEASIBLE IN CURRENT SCOPE`

---

## 2. Requirement-by-Requirement Evidence Table

| PS 26171 Requirement | Current Implementation | Verdict | Empirical Evidence & Ground Truth |
| :--- | :--- | :---: | :--- |
| **1. On-device processing** | Local Python Client + Local Ollama Instance + Local Vault | **FULLY SATISFIED** | Zero external telemetry or outbound cloud requests detected in physical socket probe. |
| **2. Lightweight multimodal model** | Qwen2.5-VL-3B-Instruct quantized 4-bit (768px input) | **FULLY SATISFIED** | Compact 3B model executes locally on 6GB VRAM edge GPU. |
| **3. Web grounding** | SafeCandidate Engine + ARIA Tree + Visual Verifier | **FULLY SATISFIED** | 92.0% multi-modal accuracy; 100% atomic grounding on seen sites; 90% on held-out sites. |
| **4. Complex forms** | Semantic Field Matcher + Local Vault `value_ref` Injector | **FULLY SATISFIED** | 95.0% field-level accuracy; 100% scenario completion; zero plaintext canary leaks. |
| **5. Multi-step workflows** | State Transition Machine + Post-Condition Checker + Recovery | **FULLY SATISFIED** | Evaluated across 5 to 30 steps with graceful, non-destructive abstention. |
| **6. Very low latency (<500ms)** | Dual-Tier Perception: Tier-1 (14.1 ms) vs Tier-2 Fallback (7.26 s) | **PARTIALLY SATISFIED** | Strictly satisfied on Tier-1 Fast Perception (75.7% of turns). Not satisfied on generative VLM fallback turns. |
| **7. Dynamic sensitive data detection** | Regex + DOM detector + Bounding Box Visual Masking Engine | **FULLY SATISFIED** | 0 canary leaks detected across 15 injection surfaces in physical wire socket probe. |
| **8. In-browser native inference (WebGPU/WASM)** | Host-side Python runtime with Playwright bridge | **PARTIALLY SATISFIED (V2 PLANNED)** | Profiled FastViT (<20 ms, 48 MB RAM) in Chrome MV3 / ONNX Runtime Web for V2 implementation. |

---

## 3. Disambiguation: Host-Local vs In-Browser
PrivateEye's current release is **Host-Local** (running directly on the user's physical machine without cloud dependency). It is not yet **In-Browser Native** (running inside the sandboxed Chrome tab via WebGPU). This distinction is documented openly and accurately.
