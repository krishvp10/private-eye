# Phase 19 — Forensic Evidence Forensics & Byte Discrepancy Audit

## Executive Summary
This document reports the findings of the **Forensic Evidence Audit** evaluating the provenance, byte accounting, and methodological integrity of Phase 17 and Phase 18 claims in accordance with NIST AI RMF and TEVV-Athlon guidance.

---

## 1. Physical Wire Privacy Byte Discrepancy Audit

### The Question:
> *Why did the reported inspected wire bytes drop from 184,520 bytes in Phase 17 to 4,619 bytes in Phase 18?*

### Forensic Finding & Disambiguation:
The discrepancy is an accounting difference between **total multi-modal workflow network traffic** versus **isolated canary test harness payload bytes**:
1. **Phase 17 Accounting (184,520 bytes)**:
   - Measured **full-workflow wire traffic** including Base64-encoded visual context tiles (`image/png` visual verification crops sent during agent steps) alongside telemetry payloads.
   - 15 canary surfaces × full simulated viewport telemetry + visual tiles = **184,520 bytes**.
2. **Phase 18 Accounting (4,619 bytes)**:
   - Measured strictly the **isolated HTTP POST payload bodies** of the synthetic canary verification probe (`Phase18WireHandler`), using a minimal 1x1 base64 placeholder tile instead of full viewport screenshots.
   - 15 POST requests × ~308 bytes per JSON payload = **4,619 bytes**.

### Scientific Resolution:
Neither test leaked canaries, but reporting 4,619 bytes gave the misleading appearance of a narrower test. Phase 19 institutes **Complete Outbound Capture**, logging both HTTP telemetry bytes and visual frame payload bytes simultaneously to provide an exhaustive byte count.

---

## 2. Forensic Audit of the 51.3% -> 81.0% Checkpointing Claim

### The Question:
> *Were the exact same trajectories/tasks evaluated with and without checkpointing under identical initial states and random seed distributions?*

### Forensic Finding:
- In Phase 18, the reported numbers (`51.3%` baseline vs `81.0%` with checkpointing at 30 steps) were derived from an **empirical survival compounding model** ($0.978^{30} \approx 51.3\%$ vs $0.993^{30} \approx 81.0\%$) based on aggregate step recovery probabilities rather than a direct, matched-pair A/B run of 30 identical tasks.
- **Classification Downgrade**: The 51.3% -> 81.0% result is officially classified as **MODEL-PREDICTED COMPOUNDING ESTIMATE**, NOT a causal paired empirical proof.
- **Phase 19 Mandate**: Phase 19 must execute a **strictly matched-pair causal A/B trial** (Task $i$ run with `Checkpointing=OFF` vs Task $i$ run with `Checkpointing=ON` under identical seeds, starting states, and fault schedules) to prove or disprove causality.

---

## 3. Provenance Status Matrix of Prior Claims

| Metric Claimed | Phase 17/18 Value | Provenance Source | Forensic Classification |
| :--- | :---: | :--- | :---: |
| **Autonomous DSR** | 85.0% (17/20) | 20 JSON traces in `eval/reports/traces/phase18/` | **RAW-EVIDENCE-BACKED** |
| **Oversight Completion** | 100.0% (20/20) | Traces indicate human resolution on 3 steps | **RAW-EVIDENCE-BACKED** |
| **Control-Plane Policy Bypasses** | 0 bypasses | 5 vectors evaluated in `phase18_master_runner.py` | **RAW-EVIDENCE-BACKED** |
| **Emergency Halt Latency** | 11.4 ms median | Micro-benchmark timings | **RAW-EVIDENCE-BACKED** |
| **Human vs Agent Timing** | 2.89x speedup | Stage-by-stage distribution in `phase18_real_user.json` | **DERIVED** |
| **Checkpoint Survival Gain** | 51.3% -> 81.0% | Mathematical model calculation in script | **DOCUMENTATION ONLY (AWAITING CAUSAL RUN)** |
| **User Usability Survey** | N = 10 users | Aggregated summary records | **DOCUMENTATION ONLY (AWAITING RAW SURVEY LOGS)** |
