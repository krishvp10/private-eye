# PrivateEye — Privacy-Preserving On-Device Visual Browser Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/browser-Playwright-green.svg)](https://playwright.dev/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-108%2F108%20passed-brightgreen.svg)]()
[![CI](https://github.com/krishvp10/private-eye/actions/workflows/ci.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/ci.yml)
[![CodeQL](https://github.com/krishvp10/private-eye/actions/workflows/codeql.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/codeql.yml)
[![Dependency Review](https://github.com/krishvp10/private-eye/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/dependency-review.yml)
[![Release Candidate](https://img.shields.io/badge/release-v1.0--RC-blueviolet.svg)]()
[![Privacy Audit](https://img.shields.io/badge/privacy-0%20detected%20leaks-success.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> **SIH Problem 26171 · On-device Visual Perception for Light-weight Browser Agents**  
> *Department of Space / Indian Space Research Organisation (ISRO)*

---

## 1. Headline Result & Core Innovation

> ### **"96.7% live end-to-end success on 30 Qwen-powered steps, backed by 98.4% hybrid real-world-environment evaluation across 125 tasks."**
> *Privacy Audit: 0 detected secret leaks across 11 tested boundaries and 21 synthetic secrets.*

Modern vision-based browser agents require transmitting raw screenshots, DOM hierarchies, and user credentials directly to cloud-hosted Vision-Language Models (VLMs). In sensitive workflows—such as **KYC onboarding, banking, healthcare, and government portals**—this exposes personally identifiable information (PII), government ID numbers, authentication secrets, and biometric facial data to model providers and intermediate network logs.

**PrivateEye** solves this by physically splitting the browser agent pipeline across a strict client-side trust boundary:
1. **On-Device Perception**: A local client drives the browser via Playwright, captures the viewport, and extracts interactive elements.
2. **Multi-Signal Privacy Detection**: Identifies sensitive information using a 4-layer local hierarchy: DOM heuristics, regex text pattern recognition, offline named entity recognition (NER), and local OpenCV face detection.
3. **Pixel-Exact Redaction**: Masks sensitive content directly in client memory (blackout, blur, digit masking) and constructs a cryptographic formal contract (`RedactionMap`).
4. **Sanitized Context POST**: Transmits **only** the sanitized screenshot, anonymized structural screen graph, and candidate metadata to the VLM server.
5. **Local Value Vault (`value_ref`)**: The VLM plans actions using indirect references (e.g. `value_ref: "user_profile.pan"`). The local client resolves values exclusively on the user's machine—**raw secrets never traverse the network**.

```text
NORMAL AGENT:
User Screen ──────────────────────────────────────────► Cloud AI Server (❌ Raw PII, Passwords, Faces Exposed)

PRIVATEEYE:
User Screen ────► Local Privacy Gate ────► Sanitized JPEG ────► Server VLM (Qwen2.5-VL:3B)
                       │ (Local Masking)       │                       │
                  [Aadhaar, PAN, Face]    [Only Structure]             ▼
                       │                       │                  Safe Action JSON
                       ▼                       ▼                       │
                Local Vault (value_ref) ◄──────┴───────────────────────┘
                       │
                  Playwright Local Fill / Click
```

---

## 2. Frozen Architecture (`PrivateEye v1.0-RC`)

The core grounding, policy, and execution architecture is frozen in `client/release_config.py`:

```text
                    USER INTENT
                         │
                         ▼
               SANITIZED OBSERVATION
                  ↙             ↘
           SCREENSHOT          SCREEN GRAPH
                  \             /
                   ↓           ↓
                LOCAL CANDIDATES
                        ↓
                 LOCAL RANKING
                        ↓
                      TOP-K
                        ↓
               SELECTIVE VLM VERIFIER
                        ↓
                 SAFE CANDIDATE
                        ↓
              LOCAL POLICY GATE
                        ↓
                  PLAYWRIGHT
                        ↓
              POST-CONDITION
                        ↓
              PROGRESS EVALUATOR
                  ↙           ↘
               PASS          FAIL
                              ↓
                      FRESH REASONING
```

Surrounded by Phase 9 Production Hardening:
- **Run Manifests (`client/manifest.py`):** Immutable SHA256-verified configuration fingerprint for every benchmark.
- **Fail-Closed Runtime Invariant (`client/fail_closed.py`):** Actions not proven safe and grounded are aborted. Silent fallback to mock is strictly prohibited.
- **Emergency Kill Switch (`client/kill_switch.py`):** Instant thread-safe agent containment emitting structured audit events.
- **Action Provenance (`client/provenance.py`):** Replay tracking answering *"Why did PrivateEye execute this action?"* without logging raw secrets.
- **Security Residual-Risk Model (`private-eye-docs/RESIDUAL_RISK.md`):** Aligned with OWASP Agent Control Standard (ACS, Sep 2026) and NIST AI RMF.

---

## 3. Standardized Evaluation Results

All evaluations are strictly partitioned with complete denominators ($N$). Local hybrid candidate scoring is rigorously decoupled from live multimodal VLM inference:

| Evaluation Tier | N | Model / Engine | Step Target Accuracy | Wrong Execution | Safe Abstention | Post-Condition | Task Success | Recovery Rate | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Local Deterministic** | 150 | Local Hybrid (ARIA + Heuristics) | **88.7%** (133/150) | 6.7% | 4.7% | 100.0% | N/A | N/A | 0.08 ms |
| **Tier 2: Controlled Held-Out** | 200 | Hybrid + Qwen2.5-VL Baseline | **98.0%** (196/200) | **0.0%** | 2.0% | 100.0% | 98.0% | 100.0% | ~7.29 s* |
| **Tier 3: Adversarial Red-Team** | 75 | Hybrid + Safety Gates | **76.4%** (42/55)† | 1.3% | **100.0%** (20/20)‡ | 98.1% | 76.4% | 100.0% | ~7.35 s |
| **Tier 4: ScreenSpot Adapted Diagnostic** | 50 | Hybrid Engine (Diagnostic Subset) | **100.0%** (50/50) | 0.0% | 0.0% | 100.0% | 100.0% | N/A | 0.12 ms |
| **Tier 4: Mind2Web Adapted Diagnostic** | 25 | Hybrid Engine (Diagnostic Subset) | **100.0%** (25/25) | 0.0% | 0.0% | 100.0% | 100.0% | N/A | 0.11 ms |
| **Tier 5: Real-Web Hybrid Execution** | 125 | Playwright DOM + Policy Engine | **98.4%** (123/125) | 1.6% | 0.0% | **98.4%** | **98.4%** | 100.0% | **0.16 ms**§ |
| **Live End-to-End Qwen Pipeline** | 30 | Qwen2.5-VL-3B @ 768px via Ollama | **96.7%** (29/30) | 3.3% | 0.0% | **96.7%** | **96.7%** | **100.0%** | **7.29 s**‖ |

*\*Simulated/batched verification in Tier 2 offline benchmark; live timing measured in Live E2E.*  
*†Target accuracy calculated over 55 groundable cases.*  
*‡Abstention rate calculated over 20 deliberately ungroundable / disabled decoy cases.*  
*§Candidate ranking latency only across 125 realistic DOM fixtures. VLM inference is bypassed in this local hybrid test.*  
*‖Actual full multimodal VLM reasoning over live browser. VLM accounts for 99.3% of step time; local agent overhead is 51.7 ms.*

---

## 4. Phase 9 Hardening & Reliability Evidence

### 1. Repeated Live Reliability Across 90 Runs (Phase 9.8 & 9.9)
- **30 workflows evaluated across 3 independent repetitions (90 full runs, 810 steps)**.
- **Task Success:** Short (100.0%, 30/30) $\to$ Medium (90.0%, 27/30) $\to$ Long (80.0%, 24/30). Overall: **90.0% (81/90)**.
- **3-Run Consistency:** **73.3%** of workflows ran with perfect 3/3 consecutive success.
- **Repeated-Target Loops:** **0.0%** across 810 steps due to progress-aware fresh reasoning (vs 86.7% loop lockup on blind retries).

### 2. Runtime Fault-Injection Suite (20 Scenarios, 100% Pass)
- Evaluates 20 controlled failure scenarios: timeouts, browser disconnects, DOM mutations, detector exceptions, redaction errors, and unknown refs.
- **Fail-Closed Guarantee:** 100% safe containment. Zero unauthorized actions; zero silent mock fallbacks.

### 3. Selective Autonomy Tradeoff Curve (Phase 9.10)
- Operates on the Pareto frontier: **97.5% autonomy with 0.0% wrong execution** by selectively escalating candidate crops in the $[0.65, 0.88)$ confidence band to the secondary verifier.
- **96% compute reduction:** Verifier invoked on only 4.0% of steps.

### 4. Security Residual-Risk Matrix
- Aligned with the **OWASP Agent Control Standard (ACS, Sep 2026)** and **NIST AI RMF 1.0**.
- Complete threat-by-threat analysis across 15 attack vectors in [`private-eye-docs/RESIDUAL_RISK.md`](private-eye-docs/RESIDUAL_RISK.md).

---

## 5. Quick Start & Flagship Demo

### Installation
```bash
git clone https://github.com/krishvp10/private-eye.git
cd private-eye
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Run Flagship Live Privacy & Safety Demo
```powershell
python eval/live_privacy_demo.py
```
Demonstrates complete end-to-end KYC & checkout execution:
1. PII detection and client-side redaction
2. Sanitized remote reasoning (0 secret leaks)
3. Local vault `value_ref` resolution
4. Explainable human abstention on ambiguous twin targets
5. Transient stale reference failure recovery
6. 11-boundary privacy invariant audit (0 leaks across 21 synthetic credentials)

### Launch Interactive Supervisor Cockpit
```powershell
python demo.py
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) for side-by-side visual inspection of raw vs sanitized screens.

---

## 6. Run Complete Benchmark & Audit Suite

```powershell
# Phase 9 Metric Provenance Audit
python eval/freeze_and_audit_phase9.py

# Runtime Fault-Injection Suite (20 scenarios)
python eval/fault_injection_benchmark.py

# Repeated Live Reliability Benchmark (90 runs)
python eval/repeated_reliability_benchmark.py

# Selective Autonomy Tradeoff Curve
python eval/selective_autonomy_curve.py

# Run Full Pytest Suite (108 tests passing)
pytest -q
```

---

## 7. Documentation Index

- [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) — Step-by-step reproduction guide for judges and evaluators
- [private-eye-docs/PHASE9_REPORT.md](private-eye-docs/PHASE9_REPORT.md) — Master Phase 9 report with standardized Tables A through E
- [private-eye-docs/RESIDUAL_RISK.md](private-eye-docs/RESIDUAL_RISK.md) — OWASP ACS & NIST AI RMF residual-risk matrix
- [private-eye-docs/RELEASE_NOTES.md](private-eye-docs/RELEASE_NOTES.md) — Frozen release candidate specification for `PrivateEye v1.0-RC`
- [private-eye-docs/PHASE9_RESEARCH.md](private-eye-docs/PHASE9_RESEARCH.md) — Research analysis on BrowserGym, OSWorld, and OWASP ACS
- [private-eye-docs/PHASE9_PLAN.md](private-eye-docs/PHASE9_PLAN.md) — Phase 9 architectural hardening plan
- [private-eye-docs/AUDIT_REPORT.md](private-eye-docs/AUDIT_REPORT.md) — Verified implementation and security audit report

---

## 8. License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
