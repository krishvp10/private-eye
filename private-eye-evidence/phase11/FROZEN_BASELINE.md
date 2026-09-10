# PrivateEye v1.0-RC Frozen Baseline Manifest (Phase 11)

> **Evaluation Identity:** Immutable baseline snapshot for independent validation, statistical evidence, and hackathon submission.

## 1. Release & Git Identity
- **Release Tag:** `v1.0-RC`
- **Git Commit SHA:** `70f0e1b35b94078d5e0b39f1a8d8f55002c00dd8`
- **Verdict:** `READY WITH DOCUMENTED LIMITATIONS`
- **Python Version:** `3.13.3`
- **Operating System:** `Windows-11-10.0.26200-SP0`

## 2. Frozen Runtime Configuration
| Component | Frozen Value | Architectural Rationale |
|---|---|---|
| **Model Backbone** | `Qwen2.5-VL-3B` | Frozen 3B multimodal backbone; no parameter tuning during evaluation |
| **Visual Resolution** | `768px (adaptive escalation to 1024px for ambiguous crops)` | 768px default preserves high fidelity while minimizing inference latency |
| **Sampling Temperature** | `0.0` | Deterministic greedy decoding for repeatable evaluations |
| **Candidate Generation (k)** | `5` | Top-5 interactable candidates extracted deterministically via Playwright ARIA |
| **Selective Crop Verifier** | `True` | Triggers visual crop inspection when top candidate score margin < 0.15 |
| **Recovery Mechanism** | `Fresh reasoning with explicit progress-state DOM re-observation` | Fresh DOM re-observation on fault; blind retries strictly banned |
| **Local Policy Engine** | `Enabled (OWASP ACS 2026 alignment)` | OWASP ACS 2026 runtime action gating with mandatory human confirmation for high-risk |
| **Fail-Closed Runtime** | `Strict Fail-Closed (banned silent mock fallback)` | Any unhandled exception halts safely (`SAFE_STOP`); zero mock fallback |
| **Emergency Kill Switch** | `Enabled (Measured local dispatch-path latency: 0.043 ms in controlled test)` | Thread-safe dispatch-path interrupt halting execution with zero subsequent actions |

## 3. Dependency Environment
| Package | Version |
|---|---|
| `playwright` | `1.62.0` |
| `fastapi` | `0.141.1` |
| `pydantic` | `2.13.5` |
| `httpx` | `0.28.1` |
| `pillow` | `12.3.0` |
| `pytest` | `9.1.1` |
| `pytest_playwright` | `0.9.0` |
| `opencv_python` | `unknown` |

## 4. Frozen Evaluation Corpora
- **Phase 10 Live Reliability:** 100 runs, 911 steps (89.0% task success, 98.79% step accuracy).
- **Phase 9 Preliminary Trial:** 90 runs, 810 steps (90.0% task success, 93.95% step accuracy).
- **Tier 1 Atomic Grounding:** 150 cases (88.67% accuracy).
- **Tier 2 Held-Out Grounding:** 200 cases (98.00% accuracy).
- **Tier 3 Red-Team Grounding:** 75 cases (76.36% groundable accuracy, 100.0% decoy safe abstention).
- **Tier 5 Multi-Domain Benchmark:** 125 cases (98.40% post-condition pass).
- **Fault Containment:** 20 single-fault and 10 compound-fault scenarios (100.0% contained).
- **Privacy Under Failure:** 11 boundaries, 21 credentials, 8 active failure conditions (0 detected leaks).
- **External Diagnostic:** 20 tasks under documented adapted OSWorld diagnostic protocol.
