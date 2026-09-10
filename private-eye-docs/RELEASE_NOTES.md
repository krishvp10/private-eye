# PrivateEye v1.0-RC Release Notes & System Specification

**Release Version:** `v1.0-RC` (Phase 9 Release Candidate)  
**Status:** Architecture Frozen · Quality Gate Certified  
**Date:** September 2026  
**Primary Engine:** Qwen2.5-VL-3B via Ollama  

---

## 1. Release Overview

PrivateEye v1.0-RC represents the culmination of a systematic 9-phase engineering cycle focused on **privacy-preserving autonomous browser agents**. It solves the core privacy dilemma of multimodal web agents by enforcing a strict client-side trust boundary: raw user credentials, payment details, and private identifiers never leave the user's local workstation.

This release candidate transitions PrivateEye from an experimental research system to an auditable, reproducible, production-hardened release with comprehensive failure-mode resilience, deterministic action provenance, and formal fail-closed guarantees.

---

## 2. Frozen Configuration Specification

The following parameters are frozen in `client/release_config.py` and must not be altered:

| Configuration Parameter | Frozen Release Value | Purpose & Architectural Justification |
|---|---|---|
| **Primary VLM** | `qwen2.5-vl:3b` | Lightweight multimodal VLM delivering competitive visual reasoning with local execution capability. |
| **Inference Backend** | `Ollama` (Local HTTP API) | Self-hosted local inference eliminating third-party cloud data exfiltration. |
| **Default Resolution** | `768px` | Proven Pareto optimal resolution: achieves identical 98.0% target accuracy as 1024px while cutting inference latency by 28%. |
| **Resolution Escalation** | `1024px` (Adaptive only) | Activated solely when secondary verifier detects fine-grained icon ambiguity. |
| **Decoding Temperature** | `0.0` (Greedy) | Enforces deterministic action generation and reproducible reasoning paths. |
| **Candidate Count ($k$)** | `5` | Top-5 accessibility candidates extracted locally by Playwright ARIA engine before VLM dispatch. |
| **Confidence High Threshold** | `0.88` | Decisions $\ge 0.88$ execute directly without invoking the secondary visual verifier. |
| **Confidence Low Threshold** | `0.65` | Decisions $< 0.65$ trigger safe abstention (`ASK_USER`) to eliminate false clicks. |
| **Verification Architecture** | `Selective Verifier` | Selectively evaluates high-res crops for candidates in the $[0.65, 0.88)$ band. Invoked on only 4% of actions. |
| **Recovery Strategy** | `Fresh Reasoning` | Re-captures DOM and re-reasons upon transient locator detachment. Eliminates blind retry loops (0.0% loop rate). |
| **Policy Engine** | `Enabled` | Client-side rule engine classifying actions into LOW, MEDIUM, and HIGH risk tiers. |
| **Fail-Closed Runtime Policy** | `Enabled` | Strict invariant: actions not proven safe and grounded are aborted (`DO_NOT_EXECUTE` / `DO_NOT_TRANSMIT`). |
| **Emergency Kill Switch** | `Enabled` | Thread-safe runtime stop switch halting browser dispatch within 5ms. |
| **Human Confirmation** | `Mandatory for HIGH Risk` | Destructive operations (transfers, deletions, account modifications) strictly require manual approval. |

---

## 3. Supported & Tested Environments

### Supported Operating Systems
- **Microsoft Windows 11 / 10** (Tested on Windows 11 x86_64, Python 3.13.3)
- **Linux (Ubuntu 22.04 / 24.04 LTS)** (Verified via GitHub Actions CI)
- **macOS (Apple Silicon M1/M2/M3)** (Playwright Chromium headless)

### Hardware Requirements
- **VRAM / GPU:** Minimum 6GB VRAM recommended for Ollama `qwen2.5-vl:3b` GPU offload (~7.2s p50 step latency).
- **CPU Fallback:** Fully operational on standard x86_64 CPU (16GB RAM recommended; step latency increases to ~28s).
- **Disk Space:** 4.5 GB for Ollama model weights + 500 MB for Python dependencies and browser binaries.

### Software Prerequisites
- Python $\ge 3.10$ (Python 3.11–3.13 recommended)
- Playwright $\ge 0.9.0$ with installed Chromium (`playwright install chromium`)
- Ollama $\ge 0.3.0$ with `qwen2.5-vl:3b` pulled (`ollama pull qwen2.5-vl:3b`)

---

## 4. Key Performance Indicators

- **Live End-to-End Success Rate:** **96.7%** across 30 live Qwen-powered browser steps.
- **Hybrid Real-Web Multi-Domain Evaluation:** **98.4%** across 125 tasks on 25 realistic website fixtures.
- **3-Run Workflow Consistency:** **73.3%** of workflows executed with 100% success across 3 consecutive trials.
- **Repeated-Target Loop Rate:** **0.0%** across 810 evaluated steps (compared to 86.7% loop failure with blind retries).
- **Controlled Fault-Injection Pass Rate:** **20/20 (100%)** runtime failure modes handled fail-closed.
- **Detected Secret Leaks:** **0** across 11 tested boundaries, 21 synthetic secrets, and all run artifacts.
- **Local Client Overhead:** $\approx 51.7\text{ ms}$ p50 (VLM reasoning accounts for 99.3% of step time).

---

## 5. Explicitly Documented System Limitations

In alignment with NIST AI RMF trustworthiness principles, the following limitations are explicitly documented:
1. **Model Dependence:** Reasoning accuracy depends fundamentally on Qwen2.5-VL-3B multimodal quality. Outages or corrupted weights trigger safe stops rather than autonomous repairs.
2. **Untested Complex Canvas / WebGL Apps:** Grounding relies heavily on DOM semantics and ARIA bounding boxes. Interfaces rendered entirely inside opaque `<canvas>` elements without accessibility trees cannot be grounded.
3. **Finite Synthetic Privacy Corpus:** The 0-leak evidence applies to the evaluated 11 boundaries and 21 synthetic secrets. It does not constitute a universal mathematical guarantee against OS-level side-channel attacks or kernel keyloggers.
4. **Long-Horizon Degradation:** Reliability scales predictably from 100% on short workflows (3–5 steps) to 80.0% on long workflows (15–20 steps). Workflows exceeding 25 steps should incorporate human checkpoints.
