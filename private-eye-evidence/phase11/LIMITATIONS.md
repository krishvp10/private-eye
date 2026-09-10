# PrivateEye v1.0-RC: Documented Limitations & Scientific Boundaries

> **Release Verdict:** `READY WITH DOCUMENTED LIMITATIONS`  
> In accordance with NIST AI RMF 1.0 (Govern / Manage) and transparent engineering practices, this document explicitly delineates the operational boundaries, known failure modes, and residual risks of PrivateEye.

---

## 1. Long-Horizon Reliability Degradation
- **Empirical Boundary:** While short workflows (3–5 steps) achieve **100.0% task success**, deep workflows (11–20 steps) drop to **78.12% task completion**.
- **Root Cause:** Degradation is not model amnesia, but rather the mathematical compounding of independent step trials: $(0.9879)^{20} \approx 78.36\%$.
- **Mitigation:** PrivateEye introduces fresh DOM re-observation and explicit progress state, but long multi-screen dependency chains remain sensitive to asynchronous timing races and transient network latency.

---

## 2. Adapted Diagnostic Subset vs. Official OSWorld Benchmark
- **Evaluation Boundary:** PrivateEye evaluated 20 adapted diagnostic tasks derived from OSWorld patterns with **20/20 grounding and post-condition success**.
- **Crucial Distinction:** This is an **adapted diagnostic subset**, NOT an official score on the comprehensive OSWorld 2.0 desktop/web benchmark suite (which evaluates hundreds of heterogeneous computer environments).
- **Scope Notice:** We specifically refrain from claiming "100% on OSWorld" to maintain strict scientific fidelity.

---

## 3. Finite Security & Prompt Injection Test Set
- **Evaluation Boundary:** PrivateEye demonstrated **15/15 blocked prompt injections** and **10/10 contained compound faults**.
- **Statistical Reality:** 15 adversarial examples and 10 compound fault scenarios provide empirical evidence of architectural defense-in-depth, but cannot prove mathematical immunity against all possible prompt injection vectors or novel zero-day attack payloads.
- **Wilson Confidence Interval:** For $N=15$, the 95% Wilson CI is `[79.6%, 100.0%]`, acknowledging non-zero uncertainty on unobserved attacks.

---

## 4. Empirical Privacy vs. Universal Privacy Proof
- **Tested Scope:** Across 11 representation boundaries, 21 synthetic vault credentials, and 8 active failure modes, PrivateEye recorded **0 detected secret leaks**.
- **Scope Limit:** This is an **empirical validation** within a defined corpus and test harness. It is NOT a mathematical proof of universal privacy across arbitrary websites.
- **Detector Boundary:** The local PII classifier exhibits an empirical False Negative Rate of **6.00%** on complex natural text. Defense-in-depth relies on the local vault tokenization requirement (`value_ref`), but if a user explicitly writes a raw secret into a natural language goal, client-side isolation is bypassed.

---

## 5. Local Multimodal Model Inference Latency
- **Performance Boundary:** While local client-side candidate generation, ranking, policy gating, and kill-switch checks take **~0.16 ms**, multimodal VLM inference on Qwen2.5-VL-3B requires **7.29 s (p50)** and **9.85 s (p95)** per turn.
- **User Experience Impact:** Local security and privacy add `<0.003%` overhead, but the overall interaction remains constrained by the throughput of local consumer GPU hardware.

---

## 6. Single-Page Application (SPA) DOM Race Conditions
- **Environmental Limit:** Modern single-page applications frequently mutate the DOM tree via asynchronous background event loops while a model turn is executing.
- **Residual Risk:** In ~3.6% of long-horizon turns, an element handle identified during visual capture becomes stale before Playwright dispatches the mouse click, requiring a fresh re-observation turn.
