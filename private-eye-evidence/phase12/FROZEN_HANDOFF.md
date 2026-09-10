# PrivateEye v1.0-RC: Phase 12 Frozen Codebase Handoff

> **Release Phase:** Phase 12 (Final Statistical Audit, Demo Hardening & Hackathon Submission Freeze)  
> **Baseline Commit SHA:** `5d697dc996d2235a273884bf35e4c1b943d9c4b7`  
> **Production Code Status:** `FROZEN_AND_UNTOUCHED`  
> **Release Verdict:** `READY WITH DOCUMENTED LIMITATIONS`

---

## 1. Architectural Integrity & Non-Negotiable Lock
In accordance with experimental discipline and the master freeze instruction:
1. **Zero Model Modifications:** The agent backbone remains locked to `Qwen2.5-VL-3B` at greedy temperature `0.0`.
2. **Zero Prompt Drift:** Candidate generation, ranking, system prompts, and recovery context are unchanged.
3. **Zero Benchmark Overfitting:** No heuristics, custom selectors, or site-specific shortcuts have been added.
4. **Production Code Immutability:** The four operational directories (`client/`, `server/`, `privacy/`, `shared/`) have verified byte-for-byte identity with commit `5d697dc`.

---

## 2. Frozen Configuration Matrix

| Component | Frozen Parameter | Enforcement Mechanism |
|---|---|---|
| **Model Backbone** | `Qwen2.5-VL-3B` | Ollama API client (`client/client.py`) |
| **Input Resolution** | `768px` default / `1024px` crop | Local image preprocessor (`client/capture.py`) |
| **Grounding Candidates (k)** | `k = 5` | ARIA interactive node extractor (`client/capture.py`) |
| **Visual Verifier** | Selective crop verifier (`margin < 0.15`) | Contrastive crop scoring (`client/verifier.py`) |
| **Policy Engine** | OWASP ACS 2026 action risk gating | Local policy classifier (`client/policy_engine.py`) |
| **Runtime Policy** | Strict Fail-Closed (`SAFE_STOP`) | Exception boundary (`client/agent.py`) |
| **Emergency Kill Switch** | Local thread-safe dispatch gate | Hardware/UI interrupt (`client/kill_switch.py`) |
| **Vault Tokenization** | `value_ref` symbolic resolution | Local memory lookup (`client/vault.py`) |
| **Recovery Strategy** | Fresh DOM re-observation + state | Progress tracking (`client/progress.py`) |

---

## 3. Scope of Phase 12 Activities
All Phase 12 activities are strictly restricted to:
- Cluster-aware statistical sensitivity analysis (10,000 bootstrap iterations).
- Trajectory efficiency evaluation (useful action efficiency, recovery overhead, actions-to-completion).
- Scientific language and causal framing hardening.
- Deterministic demo infrastructure (`demo/preflight.py`, `demo/reset_demo.py`, 3 demo scenarios).
- Hostile reviewer / judge defense guide (`JUDGE_QA.md`).
- Master submission evidence matrix.
