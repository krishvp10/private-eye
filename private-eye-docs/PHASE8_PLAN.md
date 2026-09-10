# Phase 8 Execution Plan: Trust, Real-Web Robustness & Demo Hardening

**Lead Engineer:** PrivateEye Core Architecture Team  
**Milestone:** Phase 8 Final  
**Status:** `ACTIVE / FROZEN CORE`

---

## 1. Executive Direction & Architecture Freeze

Phase 8 does **NOT** build another grounding architecture, migrate to the cloud, implement WebGPU, or add browser extensions. 

The core grounding architecture is **frozen**:
```
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

The objective is to establish scientific rigor, real-world web robustness, long-horizon reliability, an explicit security threat model, and a hackathon-ready demo.

---

## 2. 5-Tier Evaluation Taxonomy

To ensure scientific honesty and prevent mixing synthetic classifiers with real-world browser benchmarks, all evidence is strictly partitioned into 5 independent tiers:

1. **Tier 1 — Local Deterministic:** Playwright ARIA candidate extraction and lexical/role ranking.
2. **Tier 2 — PrivateEye Controlled Multimodal:** 200 held-out synthetic test cases evaluating hybrid grounding.
3. **Tier 3 — Adversarial Red-Team:** 75 malicious/ambiguous synthetic cases testing refusal, decoys, and injection.
4. **Tier 4 — Adapted External Diagnostics:** 50 adapted ScreenSpot and Mind2Web diagnostic cases (explicitly labeled `PRIVATEEYE ADAPTED DIAGNOSTIC`).
5. **Tier 5 — Real-World Multi-Domain Web:** 125 realistic web tasks across 25 distinct web interfaces with 5-level hierarchical success tracking.

---

## 3. Detailed Work Breakdown

| Workstream | Focus Area | Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **8.1 & 8.16** | Metric Audit & External Diagnostic Relabeling | `eval/reports/phase8_metric_audit.json`, `.md` | **Completed** |
| **8.2 & 8.3** | Real-World Web Benchmark (25 sites, 125 tasks, L1–L5) | `eval/data/realweb_benchmark.json`, `eval/realweb_benchmark.py` | **Completed** |
| **8.4** | Long-Horizon Reliability (Short, Medium, Long) | `eval/long_horizon_benchmark.py`, `eval/reports/phase8_long_horizon.md` | **Completed** |
| **8.5** | State & Memory Ablation (S0, S1, S2, S3) | `eval/state_memory_ablation.py`, `eval/reports/phase8_state_memory_ablation.md` | **Completed** |
| **8.6** | Local Safety Policy Engine | `client/policy_engine.py`, `tests/test_policy_engine.py` | **Completed** |
| **8.7 & 8.8** | Explainable Human Abstention UX & Quality Benchmark | `eval/abstention_quality_benchmark.py`, `eval/reports/phase8_abstention_quality.md` | **Completed** |
| **8.9** | Security Threat Model (15 Threats) | `private-eye-docs/THREAT_MODEL.md` | **Completed** |
| **8.10** | Expanded Prompt Injection Benchmark (15 Attack Vectors) | `eval/prompt_injection_expanded.py`, `eval/reports/phase8_prompt_injection.md` | **Completed** |
| **8.11–8.13** | Privacy Invariant Audits & Live Real-Web Privacy Demo | `eval/live_privacy_demo.py`, `eval/reports/phase8_live_privacy_demo.md` | **Completed** |
| **8.14** | Full Pipeline Latency Profiler (p50 / p95) | `eval/performance_profile.py`, `eval/reports/phase8_performance_profile.md` | **Completed** |
| **8.15** | Primary Edge Model Freeze (Qwen2.5-VL-3B @ 768px) | Configuration frozen in `client/adaptive_resolution.py` & docs | **Completed** |
| **8.17 & 8.18**| Flagship Demo & Visual Evidence | `eval/live_privacy_demo.py`, `DEMO_RUNBOOK.md` | **Completed** |
| **8.19–8.23**| Documentation, Full Testing & Remote CI/CodeQL Verification | `PHASE8_REPORT.md`, `README.md`, GitHub Actions CI | **In Progress** |

---

## 4. Key Success Criteria

1. Complete separation of evaluation tiers with full denominators ($N$).
2. Diagnostic results explicitly relabeled as `PRIVATEEYE ADAPTED DIAGNOSTIC`.
3. 5-level hierarchical tracking for real-world tasks (L1 action, L2 target, L3 execution, L4 post-condition, L5 task advancement).
4. Long-horizon degradation curves measured across 270 action steps.
5. State/memory ablation confirming the necessity of fresh reasoning with progress awareness.
6. Local safety policy formalized with LOW, MEDIUM, and HIGH action-risk classes.
7. Explainable abstention UX ("Why did I refuse?") with 0 raw secret leaks.
8. Comprehensive 15-threat security model documented and tested against 15 prompt injection vectors.
9. Full pipeline latency profile computed (identifying remote VLM as 97%+ latency source, local pipeline <55ms).
10. Flagship demo runnable end-to-end with verified abstention, recovery, and 0 secret leaks.
