# PrivateEye Phase 9 Master Plan: Production Hardening, Reproducibility & Final Evidence

**Milestone:** Phase 9 — Final Engineering & Release Candidate Hardening  
**Target Release:** `PrivateEye v1.0-RC`  
**Execution Status:** COMPLETED  
**Primary Engine:** Qwen2.5-VL-3B @ 768px via Ollama  

---

## 1. Executive Mission

The objective of Phase 9 is **not** to introduce additional AI models, grounding architectures, or speculative UI features. Rather, Phase 9 addresses the foundational question:

> **"Can we make every important claim about PrivateEye independently reproducible, clearly scoped, and defensible?"**

Phase 9 establishes the production-hardened governance layer around PrivateEye's frozen core architecture:

```
               USER INTENT
                    │
                    ▼
          LOCAL OBSERVATION & ARIA
                    │
                    ▼
          LOCAL PRIVACY GATE
        (Regex + NER + Masking)
                    │
            sanitized context
                    ▼
             QWEN2.5-VL-3B
         (Ollama @ 768px, T=0)
                    │
            candidate selection
                    │
                    ▼
        SELECTIVE VISUAL VERIFIER
         (High-res crop on 0.65-0.88)
                    │
                    ▼
          LOCAL POLICY ENGINE
         (LOW / MEDIUM / HIGH Tiers)
                    │
             ┌──────┴──────┐
           allow           deny
             │               │
             ▼               ▼
         PLAYWRIGHT       ASK/ABSTAIN
             │
             ▼
        POST-CONDITION
             │
        ┌────┴────┐
      PASS       FAIL
                  │
                  ▼
           FRESH REASONING
```

---

## 2. Completed Phase 9 Workstreams

### 2.1 Metric Provenance & Terminology Audit (Phase 9.1 & 9.16)
- **Decoupled Latencies:** Explicitly distinguished Tier 5 hybrid evaluation (0.16 ms candidate ranking) from live Qwen E2E multimodal inference (7.29 s p50).
- **Abolished Overclaims:** Banished the word "guarantee"; replaced with *"0 detected secret leaks across 11 tested boundaries and 21 synthetic secrets in the tested corpus"*.
- **External Diagnostics:** Strictly categorized ScreenSpot and Mind2Web evaluations as `PRIVATEEYE ADAPTED DIAGNOSTIC`.
- **Output:** `eval/reports/phase9_metric_audit.json` and `.md`.

### 2.2 Run Manifest Generator (Phase 9.2)
- Implemented `client/manifest.py` generating immutable SHA-verified execution manifests capturing Git commit, host OS, Python, Playwright version, Ollama version, model parameters, and benchmark dataset SHA256 fingerprints.

### 2.3 Frozen Release Candidate Specification (Phase 9.3)
- Implemented `client/release_config.py` and `private-eye-docs/RELEASE_NOTES.md` defining frozen hyperparameters for `PrivateEye v1.0-RC`.

### 2.4 Fail-Closed Runtime Invariant (Phase 9.4)
- Implemented `client/fail_closed.py` providing deterministic fail-closed protection across 12 failure classes. Enforces the invariant: *"When the system cannot prove that an action is safe and grounded, it does not execute it."* Strictly prohibits silent mock fallback.

### 2.5 Emergency Kill Switch (Phase 9.5)
- Implemented `client/kill_switch.py` providing a thread-safe runtime stop switch halting browser dispatch within 5ms and emitting structured audit events.

### 2.6 Action Provenance & Replay Logging (Phase 9.6)
- Implemented `client/provenance.py` recording granular `ActionProvenance` records answering *"Why did PrivateEye perform this action?"* with zero raw credential leakage.

### 2.7 Runtime Fault-Injection Suite (Phase 9.7)
- Implemented and executed `eval/fault_injection_benchmark.py`: 20 controlled failure scenarios (timeouts, crashes, DOM mutations, detector failures, unknown refs) with **100% fail-closed compliance**.

### 2.8 Repeated Live Reliability Benchmark (Phase 9.8 & 9.9)
- Implemented and executed `eval/repeated_reliability_benchmark.py`: 30 workflows x 3 repetitions = 90 full live workflow runs (810 total steps).
- Achieved **90.0% overall task completion**, **73.3% 3-run consistency**, and **0.0% repeated-target loops**.

### 2.9 Selective Autonomy Tradeoff Curve (Phase 9.10)
- Implemented and executed `eval/selective_autonomy_curve.py` demonstrating that PrivateEye v1.0-RC operates on the Pareto frontier (97.5% autonomy, 0.0% wrong actions) by selective visual verification.

### 2.10 Security Residual-Risk Matrix (Phase 9.11)
- Implemented `private-eye-docs/RESIDUAL_RISK.md` formalizing residual risk across 15 threats in alignment with OWASP ACS (Sep 2026), OWASP Agentic Top 10, and NIST AI RMF.
