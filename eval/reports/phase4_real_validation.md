# PrivateEye Phase 4 Master Validation Report

**Generated:** 2026-09-10T14:47:28Z
**Environment:** Windows-11-10.0.26200-SP0
**GPU Hardware:** NVIDIA GeForce RTX 4060 Laptop GPU (8188 MiB, Driver 581.86)
**Pinned Model Setup:** `Qwen/Qwen2.5-VL-3B-Instruct` via vLLM

---

## 1. Tier 1 — Deterministic Synthetic Benchmark
- **Status:** PASS (65/65 unit tests passing)
- **PII Detection F1:** 1.0 (Precision: 100%, Recall: 100%)
- **Redaction Precision:** 100.0% (Over-mask: 0.0%)
- **Client Processing RAM / Latency:** 60.2 MB / 38.5 ms

## 2. Tier 2 — Realistic Synthetic Corpus (10 Challenge Fixtures)
- **Status:** PASS (10 challenge fixtures evaluated)
- **Full Pipeline F1 Score:** **0.949** (Recall: 90.3%)
- **Decoy Number False Positives:** 0 (Zero over-masking of non-PII logistics/order codes)
- **Average Channel Latency:** 0.42 ms per page

## 3. Tier 3 — Real-VLM Wire & Outbound Privacy Proof
- **Four-Boundary Wire Verification:** ⏸ SKIPPED (synthetic harness only)
- **Secrets Audited Across Outbound Traffic:** 21 credential entities
- **Evidence Source:** `synthetic_local_harness`
- **Raw Screenshots Transmitted:** NO (Sanitized visual context only)
- **Server Log PII Leaks:** ZERO
- **Live Real-VLM Execution Status:** `SKIPPED`
  - *Status Note:* PRIVATEEYE_VLM_MODE is not real

---

## 4. Architectural Limitations & Next Steps
- Live GPU model execution requires a reachable OpenAI-compatible endpoint serving Qwen2.5-VL via vLLM or Ollama.
- Synthetic and realistic benchmark scores reflect local evaluated corpora and must not be extrapolated as 100% guarantees on arbitrary uncurated web domains.
- Client memory budget remains strictly under 150MB by relying on lightweight local CV and regex instead of multi-gigabyte browser-side neural models.
