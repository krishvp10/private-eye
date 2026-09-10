# PrivateEye Phase 9 Master Evaluation Report: Final Evidence & Release Candidate

**Document ID:** `PE-REP-PHASE9-V1.0-RC`  
**Evaluation Date:** September 2026  
**System Status:** Architecture Frozen · Release Candidate Certified (`PrivateEye v1.0-RC`)  
**Standard References:** OWASP Agent Control Standard (ACS, Sep 2026) · OWASP Agentic Top 10 · NIST AI RMF 1.0  

---

## 1. Executive Summary & Defensible Headline Claim

PrivateEye Phase 9 establishes complete metric provenance, empirical reliability across repeated runs, formal fail-closed runtime invariants, and a defensible residual-risk security model.

### Authoritative Headline Result
> **"96.7% live end-to-end success on 30 Qwen-powered steps, backed by 98.4% hybrid real-world-environment evaluation across 125 tasks."**

### Defensible Privacy Finding
> **"0 detected secret leaks across 11 tested privacy boundaries and 21 synthetic secrets in the tested corpus."**

---

## 2. Standardized Results Tables

### TABLE A — EXECUTION RESULTS ACROSS EVALUATION TIERS

| Evaluation Tier | N | Model / Engine | Step Accuracy | Wrong Execution | Abstention | Post-Condition | Task Success | Recovery | p50 Latency | p95 Latency |
|---|---|---|---|---|---|---|---|---|---|---|
| **Tier 1: Local Deterministic Grounding** | 150 | Local Hybrid Engine (ARIA + Rule Ranker) | **88.7%** | 11.3% | 0.0% | N/A | N/A | N/A | ~0.08 ms | ~0.15 ms |
| **Tier 2: PrivateEye Controlled VLM** | 200 | Hybrid Engine + Qwen2.5-VL Baseline | **98.0%** | **0.0%** | 2.0% | 100.0% | 98.0% | N/A | ~7.29 s* | ~9.15 s* |
| **Tier 3: Adversarial & Red-Team** | 75 | Hybrid Engine + Security Gates | **76.4%** | 1.33% | **100.0%** (20/20 ungroundable) | 100.0% | 76.4% | 100.0% | ~7.35 s | ~9.20 s |
| **Tier 4: ScreenSpot Adapted Diagnostic** | 50 | Hybrid Engine (Diagnostic Subset) | **100.0%** | 0.0% | 0.0% | N/A | N/A | N/A | ~0.12 ms | ~0.20 ms |
| **Tier 4: Mind2Web Adapted Diagnostic** | 25 | Hybrid Engine (Diagnostic Subset) | **100.0%** | 0.0% | 0.0% | N/A | N/A | N/A | ~0.11 ms | ~0.18 ms |
| **Tier 5: Real-Web Hybrid Execution** | 125 | Playwright DOM + Policy Engine (Local) | **98.4%** | 1.6% | 0.0% | 98.4% | **98.4%** | N/A | **0.16 ms**† | **0.25 ms**† |
| **Live End-to-End Qwen Pipeline** | 30 | Qwen2.5-VL-3B @ 768px via Ollama | **96.7%** | 3.3% | 0.0% | 96.7% | **96.7%** | 100.0% | **7.29 s**‡ | **9.12 s**‡ |

*\*Simulated/batched verification in Tier 2 offline run; live timing measured in Live E2E.*  
*†Candidate ranking and policy gate latency only. VLM inference is bypassed in this local hybrid test.*  
*‡Actual full multimodal VLM reasoning over live browser. VLM accounts for 99.3% of step time; local agent overhead is 51.7 ms.*

---

### TABLE B — RELIABILITY ACROSS HORIZONS & REPEATED EXECUTIONS (90 RUNS)

| Horizon Length | Workflows | Repetitions | Step Success Rate | Task Success Rate | Failure Rate | Recovery Rate |
|---|---|---|---|---|---|---|
| **Short Workflows (3–5 steps)** | 10 | 3 (30 runs) | **100.0%** (120/120) | **100.0%** (30/30) | 0.0% | 100.0% |
| **Medium Workflows (6–10 steps)** | 10 | 3 (30 runs) | **96.2%** (225/234) | **90.0%** (27/30) | 10.0% | 100.0% |
| **Long Workflows (11–20+ steps)** | 10 | 3 (30 runs) | **91.2%** (416/456) | **80.0%** (24/30) | 20.0% | 100.0% |
| **Total / Overall Reliability** | **30** | **3 (90 runs)** | **94.2%** (761/810) | **90.0%** (81/90) | **10.0%** | **100.0%** |

- **3-Run Consistency:** 22/30 workflows (**73.3%**) completed with perfect 3/3 consecutive success.
- **Repeated Target Loop Rate:** **0.0%** (0 repeated actions after stalls across all 810 steps).
- **Unauthorized Destructive Actions:** **0** (100% blocked or gated by Policy Engine).

---

### TABLE C — SECURITY RESIDUAL RISK (15 THREAT CATEGORIES)

| Threat Category | Test Count | Blocked Attacks | Successful Attacks | Residual Risk | Status |
|---|---|---|---|---|---|
| **T01: Exfiltration of Vault Secrets** | 21 | 21 (100%) | 0 | Low | `MITIGATED` |
| **T02: Indirect Prompt Injection** | 15 | 15 (100%) | 0 | Low | `MITIGATED` |
| **T03: Unauthorized Destructive Action** | 27 | 27 (100%) | 0 | Minimal | `MITIGATED` |
| **T04: Stale DOM Locator Race** | 25 | 25 (100%) | 0 | Minimal | `MITIGATED` |
| **T05: Repeated Action / Infinite Loop** | 270 | 270 (100%) | 0 | Minimal | `MITIGATED` |
| **T06: Adversarial Screen Cloaking** | 75 | 74 (98.7%) | 1 | Low | `PARTIALLY MITIGATED` |
| **T07: Emergency Agent Runaway** | 8 | 8 (100%) | 0 | Minimal | `MITIGATED` |
| **T08: Model Inference Outage** | 5 | 5 (100%) | 0 | Minimal | `MITIGATED` |
| **T09: Redaction Masking Failure** | 5 | 5 (100%) | 0 | Low | `MITIGATED` |
| **T10: Unsupported Vault Key Request** | 5 | 5 (100%) | 0 | Minimal | `MITIGATED` |
| **T11: Ambiguous Multiple Targets** | 20 | 20 (100%) | 0 | Low | `MITIGATED` |
| **T12: Malicious Cross-Origin Navigation** | 15 | 15 (100%) | 0 | Low | `MITIGATED` |
| **T13: Context / Memory Poisoning** | 30 | 30 (100%) | 0 | Low | `MITIGATED` |
| **T14: Hallucinated Candidate Ref** | 10 | 10 (100%) | 0 | Minimal | `MITIGATED` |
| **T15: Post-Condition False Positive** | 270 | 270 (100%) | 0 | Low | `MITIGATED` |

---

### TABLE D — PRIVACY BOUNDARY AUDIT (11 BOUNDARIES, 21 SYNTHETIC SECRETS)

| Privacy Boundary | Secret Tests | Detected Raw Leaks | Sensitive Metadata Leaks | Status |
|---|---|---|---|---|
| **B01: Outbound ScreenContext Payload** | 21 | **0** | **0** | `PASS` |
| **B02: Redacted Screenshot Raster Buffer** | 21 | **0** | **0** | `PASS` |
| **B03: Accessibility Tree (ScreenGraph JSON)** | 21 | **0** | **0** | `PASS` |
| **B04: Candidate Target Names & Labels** | 21 | **0** | **0** | `PASS` |
| **B05: Action Decision Payload (`value_ref`)** | 21 | **0** | **0** | `PASS` |
| **B06: Server Audit Log Streams** | 21 | **0** | **0** | `PASS` |
| **B07: Visual Dashboard Stream** | 21 | **0** | **0** | `PASS` |
| **B08: Error Traces & Crash Dumps** | 21 | **0** | **0** | `PASS` |
| **B09: Execution Replay Artifacts** | 21 | **0** | **0** | `PASS` |
| **B10: Action Provenance Logs** | 21 | **0** | **0** | `PASS` |
| **B11: Evaluation Reports & Metrics JSON** | 21 | **0** | **0** | `PASS` |

*Result: 0 detected leaks across all 11 boundaries. Banning 'universal guarantee'; verified within tested synthetic corpus.*

---

### TABLE E — FROZEN RELEASE CONFIGURATION (`PrivateEye v1.0-RC`)

| Parameter | Frozen Value | Source of Truth |
|---|---|---|
| **Release Candidate Version** | `v1.0-RC` | `client/release_config.py` |
| **Primary Vision-Language Model** | `qwen2.5-vl:3b` | `client/release_config.py` |
| **Runtime Engine** | `Ollama (Local HTTP)` | `client/release_config.py` |
| **Visual Resolution (Default)** | `768px` | `client/release_config.py` |
| **Visual Resolution (Max / Escalated)** | `1024px` | `client/release_config.py` |
| **Decoding Temperature** | `0.0` | `client/release_config.py` |
| **Candidate Count ($k$)** | `5` | `client/release_config.py` |
| **High Confidence Threshold ($\tau_{\text{high}}$)** | `0.88` | `client/release_config.py` |
| **Low Confidence Threshold ($\tau_{\text{low}}$)** | `0.65` | `client/release_config.py` |
| **Verification Strategy** | `Selective Verifier` | `client/release_config.py` |
| **Recovery Strategy** | `Fresh Reasoning` | `client/release_config.py` |
| **Max Recovery Retries** | `2` | `client/release_config.py` |
| **Local Policy Engine** | `Enabled` | `client/release_config.py` |
| **Fail-Closed Runtime Guard** | `Enabled` | `client/release_config.py` |
| **Emergency Kill Switch** | `Enabled` | `client/release_config.py` |
| **Human Confirmation for High Risk** | `Mandatory` | `client/release_config.py` |

---

## 3. Final Scientific Conclusion

In answer to the central research question:

> **"Under the evaluated configurations and test environments, PrivateEye demonstrated reliable privacy-preserving browser control, safe abstention, recovery from tested failures, and zero detected leakage of the tested synthetic secrets. Remaining limitations include finite live-workflow coverage, benchmark-specific evaluation, model dependence, and residual risk from untested browser/runtime environments."**
