# PrivateEye — Privacy-Preserving On-Device Visual Browser Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/browser-Playwright-green.svg)](https://playwright.dev/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-100%2F100%20passed-brightgreen.svg)]()
[![CI](https://github.com/krishvp10/private-eye/actions/workflows/ci.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/ci.yml)
[![CodeQL](https://github.com/krishvp10/private-eye/actions/workflows/codeql.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/codeql.yml)
[![Dependency Review](https://github.com/krishvp10/private-eye/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/dependency-review.yml)
[![SIH Problem 26171](https://img.shields.io/badge/SIH-Problem%2026171-orange.svg)]()
[![Zero Raw PII](https://img.shields.io/badge/privacy-zero--leak%20guarantee-success.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> **SIH Problem 26171 · On-device Visual Perception for Light-weight Browser Agents**  
> *Department of Space / Indian Space Research Organisation (ISRO)*

---

## 1. Overview & Core Differentiator

> **"Normally, an AI browser agent has to see your entire screen. PrivateEye doesn't."**

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
User Screen ────► Local Privacy Gate ────► Sanitized JPEG ────► Server VLM (Qwen2.5-VL / Mock)
                       │ (Local Masking)       │                       │
                  [Aadhaar, PAN, Face]    [Only Structure]             ▼
                       │                       │                  Safe Action JSON
                       ▼                       ▼                       │
                Local Vault (value_ref) ◄──────┴───────────────────────┘
                       │
                  Playwright Local Fill / Click
```

---

## 2. Frozen Architecture (Phase 8 Verified Core)

The core grounding and execution architecture is frozen:

```text
                    USER INTENT
                         ↓
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

---

## 3. 5-Tier Evaluation Taxonomy & Standardized Results

All headline evaluations are strictly partitioned into five independent evaluation tiers with complete denominators ($N$):

| Tier | Evaluation Set | N | Model / Engine | Target Accuracy | Wrong Execution | Safe Abstention | Post-Condition Success | Task Success | Recovery Success | p50 Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Local Deterministic (Frozen) | 150 | Local Ranker + Verifier | **88.7%** (133/150) | 6.7% | 4.7% | 100.0% | N/A | N/A | 0.18 ms |
| **Tier 2** | Controlled Unseen Held-Out | 200 | Hybrid Engine (Selective) | **98.0%** (196/200) | **0.0%** | 2.0% | 100.0% | 100.0% | 100.0% | 0.15 ms |
| **Tier 3** | Adversarial Red-Team | 75 | Hybrid Engine (Selective) | **76.4%** (42/55)* | **1.3%** | **100.0%** (20/20)** | 98.1% | N/A | 100.0% | 0.21 ms |
| **Tier 4** | Adapted External Diagnostics | 50 | Hybrid Engine (Adapted) | **100.0%** (50/50) | 0.0% | 0.0% | 100.0% | 100.0% | N/A | 0.15 ms |
| **Tier 5** | Real-World Multi-Domain Web | 125 | Hybrid + Policy Engine | **98.4%** (123/125) | **0.0%** | 1.6% | **98.4%** | **98.4%** | 100.0% | 0.16 ms |
| **Live** | Full End-to-End Pipeline | 30 | Qwen2.5-VL-3B @ 768px | **96.7%** (29/30) | **0.0%** | 3.3% | **96.7%** | **96.7%** | 100.0% | **7.29 s** |

*\*Target accuracy calculated over the 55 groundable cases.*<br/>
*\*\*Abstention rate calculated over the 20 deliberately ungroundable / disabled decoy cases.*

---

## 4. Key Scientific Breakthroughs in Phase 8

### 1. Real-World Multi-Domain Web Benchmark (Tier 5)
- **25 distinct web interfaces** across 10 commercial categories (E-commerce, fintech, banking, health, SaaS, admin, travel, productivity, tables, search).
- **5-Level Hierarchical Tracking**:
  - **L1 (Action Type Correct):** 100.0% (125/125)
  - **L2 (Target Correct):** 98.4% (123/125)
  - **L3 (Browser Execution):** 98.4% (123/125)
  - **L4 (Post-Condition Contract):** 98.4% (123/125)
  - **L5 (Task State Advanced):** 98.4% (123/125)

### 2. Long-Horizon Reliability Benchmark (270 Action Steps)
- Evaluated across Short (3–5 steps), Medium (6–10 steps), and Long (11–20+ steps) workflows.
- Task completion remains high: **100.0% (Short) $\to$ 90.0% (Medium) $\to$ 80.0% (Long)**.
- **0.0% repeated-target loops** across all 270 action steps due to progress-aware fresh reasoning.

### 3. State & Memory Ablation
- **S0 (Memoryless):** 20.0% task success, **86.7% repeated-action loops**, 0.0% recovery.
- **S3 (Full Progress-Aware Fresh Reasoning):** **90.0% task success**, **0.0% loops**, **100.0% recovery**.

### 4. Authoritative Local Safety Policy Engine (`client/policy_engine.py`)
- **LOW RISK (scroll, navigation):** Min confidence 0.50. Executed automatically.
- **MEDIUM RISK (select, form edits):** Min confidence 0.65.
- **HIGH RISK (delete, payment, sensitive PII):** Min confidence 0.88 + mandatory visual verifier + human confirmation seam for irreversible actions.

### 5. Explainable Human-in-the-Loop Abstention
When ambiguous twin targets are detected (candidate margin $<0.10$), PrivateEye refuses to guess:
> *"I did not click because: 2 candidates matched 'Confirm Submission' with confidence 0.61; visual verifier could not distinguish between them safely. Please clarify whether to click Primary or Secondary confirmation button."*
- **100.0% safe abstention** on ungroundable adversarial cases.
- **0.73% false execution rate**.
- **97.45% net selective autonomy score**.

### 6. Security Threat Model & Prompt Injection Defense
- Formal 15-threat security model documented in [`private-eye-docs/THREAT_MODEL.md`](private-eye-docs/THREAT_MODEL.md) (T01–T15).
- **100.0% prompt injection defense (15/15 blocked)** across hidden text, system prompt spoofing, and malicious attributes (`eval/reports/phase8_prompt_injection.md`).

### 7. Full Pipeline Latency Profile
- Client-side operations (capture, OCR detection, redaction, candidate ranking, policy check, execution) consume **51.7 ms p50 (<1% of total step latency)**.
- Remote VLM reasoning consumes **99.3% of total step time** (~7.2s p50).
- **Primary Edge Deployment Model Frozen:** Qwen2.5-VL-3B @ 768px (3.8 GB VRAM, 7.2s p50, 5/5 workflow completion).

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
4. Explainable human abstention on ambiguous targets
5. Transient stale reference failure recovery
6. 11-boundary privacy invariant audit (0 leaks across 21 synthetic credentials)

### Launch Interactive Supervisor & Cockpit
```powershell
python demo.py
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) for side-by-side visual inspection of raw vs sanitized screens.

---

## 6. Run Complete Benchmark Suite

```powershell
# Real-World Web Benchmark (Tier 5, 125 tasks across 25 sites)
python eval/realweb_benchmark.py

# Long-Horizon Reliability Benchmark (270 steps)
python eval/long_horizon_benchmark.py

# State & Memory Ablation (S0-S3)
python eval/state_memory_ablation.py

# Explainable Human Abstention Benchmark
python eval/abstention_quality_benchmark.py

# Expanded Prompt Injection Suite (15 Vectors)
python eval/prompt_injection_expanded.py

# Full Pipeline Latency Profiler
python eval/performance_profile.py

# Run Full Pytest Suite (100 tests passing)
pytest -q
```

---

## 7. Documentation Index

- [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) — Step-by-step reproduction guide for judges and evaluations
- [private-eye-docs/PHASE8_REPORT.md](private-eye-docs/PHASE8_REPORT.md) — Comprehensive Phase 8 final report with all 4 standardized tables
- [private-eye-docs/THREAT_MODEL.md](private-eye-docs/THREAT_MODEL.md) — 15-threat security and privacy threat model
- [private-eye-docs/PHASE8_PLAN.md](private-eye-docs/PHASE8_PLAN.md) — Phase 8 architectural freeze and 5-tier taxonomy plan
- [private-eye-docs/PHASE8_RESEARCH.md](private-eye-docs/PHASE8_RESEARCH.md) — Literature review and grounding design rationale
- [private-eye-docs/AUDIT_REPORT.md](private-eye-docs/AUDIT_REPORT.md) — Verified implementation and security audit report

---

## 8. License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
