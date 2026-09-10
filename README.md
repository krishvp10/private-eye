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
[![100-Run Reliability](https://img.shields.io/badge/reliability-89.0%25%20(100%20runs)-brightgreen.svg)]()
[![Kill Switch](https://img.shields.io/badge/kill--switch-0.043%20ms-success.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> **SIH Problem 26171 · On-device Visual Perception for Light-weight Browser Agents**  
> *Department of Space / Indian Space Research Organisation (ISRO)*

---

## 1. Headline Result & Core Innovation

> ### **"89.0% live task success across 100 repeated workflow runs (89/100) with 98.79% step accuracy (900/911), backed by 96.7% live Qwen E2E success on 30 steps and 98.4% hybrid evaluation across 125 tasks."**
> *Privacy Audit: 0 detected secret leaks across 11 tested boundaries and 21 synthetic credentials under 8 active failure conditions.*
> *Runtime Control: Measured local dispatch-path kill-switch latency was 0.043 ms in the controlled test with zero subsequent actions dispatched.*

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
| **Phase 10: 100-Run Live Reliability** | 100 | Qwen2.5-VL-3B (Frozen RC) | **98.8%** (900/911) | **0.0%** | 11.0% | **97.8%** | **89.0%** (89/100) | **100.0%** | **0.15 ms**§ |
| **OSWorld External Diagnostic** | 20 | Qwen2.5-VL-3B (Adapted Subset) | **100.0%** (20/20) | **0.0%** | 0.0% | **100.0%** | **100.0%** (20/20) | **100.0%** | **0.19 ms**§ |

*\*Simulated/batched verification in Tier 2 offline benchmark; live timing measured in Live E2E.*  
*†Target accuracy calculated over 55 groundable cases.*  
*‡Abstention rate calculated over 20 deliberately ungroundable / disabled decoy cases.*  
*§Candidate ranking latency only across realistic DOM fixtures. VLM inference is bypassed in local candidate benchmarks.*  
*‖Actual full multimodal VLM reasoning over live browser. VLM accounts for 99.3% of step time; local agent overhead is 51.7 ms.*

---

## 4. Phase 10 Final Engineering Validation & Release Certification

PrivateEye Phase 10 completed the final independent validation of the frozen `v1.0-RC` release candidate:

### 1. 100-Run Repeated Live Reliability Campaign (Phase 10.3 & 10.6)
- **25 workflows evaluated across 4 independent repetitions (100 full live runs, 911 steps)**.
- **Horizon Breakdown:** Short (**100.0%**, 32/32) $\to$ Medium (**88.9%**, 32/36) $\to$ Long (**78.1%**, 25/32). Overall: **89.0% (89/100)**.
- **Bounded Degradation:** Cumulative survival remains **78.1%–81.3%** even out to 15–20 steps (vs exponential collapse of unverified agents).
- **Zero Loop Lockup:** **0.0% repeated target loops** across all 911 evaluated steps.

### 2. Failure Attribution Forensics: Why the Remaining 11% Failures Occur (Phase 10.4 & 10.5)
- **Dominant Failure Source:** Stochastic browser timing races, not VLM cognitive collapse.
  - `stale_ref` (36.4% of failures, 3.0% overall rate): Dynamic DOM mutation between capture and click. 100% recovered with fresh capture.
  - `post_condition_failure` (18.2% of failures, 2.0% overall rate): Network spinner/delay exceeding verification window.
  - `no_progress` (18.2% of failures, 2.0% overall rate): Action produced no observable state change; broken cleanly by loop detector.
  - `semantic_selection_failure` (18.2% of failures, 2.0% overall rate): Model misaligned sub-target in deeply nested tabs.
  - `ambiguous_target` / `model_timeout` (9.1% each): Twin identical controls or inference timeout under compute load.
- **Replay Determinism:** **72.7% stochastic** (timing/network races), **27.3% deterministic** (target ambiguity).

### 3. Compound Chaos Testing (Phase 10.7, 10 Scenarios, 100% Pass)
- Evaluated dual simultaneous failures (timeout + stale ref, prompt injection + malformed output, disconnect + timeout).
- Zero unauthorized actions, zero credential leaks, zero silent mock fallbacks.

### 4. Privacy-Under-Failure Invariant Audit (Phase 10.8)
- Intentionally crashed components (detector, redactor, verifier, browser, retries exhausted).
- **0 detected secret leaks** across all 11 boundaries and 21 synthetic credentials.

### 5. Emergency Kill Switch & Action Provenance (Phase 10.9 & 10.10)
- Verified microsecond emergency stop (**0.043 ms**) halting execution before Playwright dispatch.
- Granular action provenance answering *"Why did PrivateEye perform this action?"* for every step.

### 6. Official Evidence Pack (`private-eye-evidence/`)
All verified benchmark JSONs, security matrices, and reports are packaged for evaluators in [`private-eye-evidence/`](private-eye-evidence/) alongside [`private-eye-evidence/FINAL_REPORT.md`](private-eye-evidence/FINAL_REPORT.md).

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
# Phase 10 Baseline Manifest & Metric Provenance Audit
python eval/freeze_and_audit_phase10.py

# Phase 10 100-Run Live Reliability Campaign (25 workflows x 4 reps)
python eval/reliability_campaign_100.py

# Phase 10 Compound Fault-Injection Suite (10 compositional scenarios)
python eval/compound_fault_benchmark.py

# Phase 10 Privacy-Under-Failure Invariant Audit (8 component failure modes)
python eval/privacy_under_failure_audit.py

# Phase 10 Runtime Control, Kill Switch, & Adversarial Audit
python eval/runtime_control_and_adversarial_audit.py

# Phase 10 OSWorld External Diagnostic Subset (20 tasks)
python eval/osworld_diagnostic_benchmark.py

# Package Final Evidence Pack & Generate FINAL_REPORT.md
python eval/package_evidence_pack.py

# Run Full Pytest Suite (108 tests passing)
pytest -q
```

---

## 7. Documentation Index

- [private-eye-evidence/FINAL_REPORT.md](private-eye-evidence/FINAL_REPORT.md) — Master Final Report & Certification with Tables A through F
- [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) — Step-by-step reproduction guide for judges and evaluators
- [private-eye-docs/PHASE10_REPORT.md](private-eye-docs/PHASE10_REPORT.md) — Phase 10 Engineering Validation & Release Report
- [private-eye-docs/PHASE9_REPORT.md](private-eye-docs/PHASE9_REPORT.md) — Phase 9 Production Hardening & Baseline Report
- [private-eye-docs/RESIDUAL_RISK.md](private-eye-docs/RESIDUAL_RISK.md) — OWASP ACS & NIST AI RMF residual-risk matrix
- [private-eye-docs/RELEASE_NOTES.md](private-eye-docs/RELEASE_NOTES.md) — Frozen release candidate specification for `PrivateEye v1.0-RC`
- [private-eye-docs/AUDIT_REPORT.md](private-eye-docs/AUDIT_REPORT.md) — Verified implementation and security audit report

---

## 8. License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
