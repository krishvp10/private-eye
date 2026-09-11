# Phase 15 Baseline & Release Protection Record

**Date:** 2026-09-11  
**Authoritative Release Candidate Tag:** `v1.0-RC-final` (Commit: `f689654`)  
**Audit Completion Commit:** `31597e9` (main)  
**Phase 15 Work Branch:** `phase15-ps-compliance`  
**Frozen Baseline Commit:** `5d697dc`  

---

## 1. Release Integrity Verification

Prior to any modifications, the frozen state was verified:

```powershell
git status
# Output: On branch main, nothing to commit, working tree clean

git rev-parse HEAD
# Output: 31597e9acb4b259f0f094a72e33b4674666f020e

git tag -l
# Output: v1.0-RC-final

git diff 5d697dc -- client server privacy shared
# Output: 0 lines diff (production code byte-for-byte identical to frozen Phase 11 baseline)
```

---

## 2. Frozen Configuration Baseline

- **Model:** Qwen2.5-VL-3B via local Ollama daemon (`http://127.0.0.1:11434`)
- **Default Resolution:** 768px (`--resolution 768`), adaptive 1024px zoom for ambiguous candidates
- **Sampling Temperature:** 0.0 (fully deterministic)
- **Candidate Generator:** $k=5$ SafeCandidate selection
- **Visual Crop Verifier:** Active, threshold $\Delta < 0.10$ triggers `ASK_USER`
- **Execution Runtime:** Playwright Chromium headless/headful
- **Target Hardware Environment:** NVIDIA RTX 4060 Laptop GPU 8GB VRAM / AMD Ryzen / Windows 11

---

## 3. Phase 15 Objectives (SIH PS 26171 Alignment)

1. **P0: Privacy Boundary Repair:** Close visual false-negative pixel leak into `image_b64` on unredacted/obfuscated secrets.
2. **P0: Policy Integration:** Unify the authoritative `LocalPolicyEngine` directly into `client/agent.py` so real execution passes through risk/confidence gates.
3. **P0: Wire-Level Privacy Probe:** Instrument real network requests to guarantee no raw secrets/pixels leak across the wire.
4. **P1: Fast Local Perception Engine:** Build a deterministic hybrid perception path (<500 ms) using DOM, ARIA, geometry, and lightweight visual heuristics; invoke Qwen2.5-VL-3B only as a slow fallback for ambiguous/complex visual states.
5. **P1: Real Latency Profiling:** Profile p50/p95/p99 breakdown of capture, privacy, candidate generation, verification, and inference.
6. **P1: Complex Form & Long-Horizon Benchmarks:** Evaluate multi-section forms, conditional fields, dropdown dependencies, and 5–30 step workflow survival.
7. **P2: Browser-Local / WebGPU Feasibility:** Produce technical feasibility study for ONNX/WebGPU in-browser inference.
