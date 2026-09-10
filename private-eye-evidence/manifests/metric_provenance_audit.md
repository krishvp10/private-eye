# PrivateEye Phase 10 Complete Metric Provenance Audit

**Audit Status:** APPROVED (All 13 metrics verified defensible)
**Run Manifest ID:** `manifest_1789067402_phase10_final_ba`
**Git Commit:** `2fa84072f1`
**Model Configuration:** `qwen2.5-vl:3b` @ `768px` (T=0.0)

## Metric Classification & Provenance Matrix

| Metric | Tier | N | Reported | Classification | VLM? | Latency | Benchmark Hash | Status |
|---|---|---|---|---|---|---|---|---|
| Development Set Accuracy (Top-1) | Tier 1: Local Deterministic Grounding | 150 | **88.7%** | `LOCAL_DETERMINISTIC` | No | 0.08 ms | `228dcfecd2` | **VERIFIED_DEFENSIBLE** |
| Development Set Candidate Recall (Top-3) | Tier 1: Local Deterministic Grounding | 150 | **100.0%** | `LOCAL_DETERMINISTIC` | No | 0.05 ms | `228dcfecd2` | **VERIFIED_DEFENSIBLE** |
| Held-Out Target Selection Accuracy | Tier 2: PrivateEye Controlled VLM | 200 | **98.0%** | `CONTROLLED_HELD_OUT` | Yes | ~7.29 s live / batched calibration | `252f4ebdb9` | **VERIFIED_DEFENSIBLE** |
| Held-Out Wrong Execution Rate | Tier 2: PrivateEye Controlled VLM | 200 | **0.0%** | `CONTROLLED_HELD_OUT` | Yes | N/A | `252f4ebdb9` | **VERIFIED_DEFENSIBLE** |
| Safe Abstention on Ungroundable/Disabled Elements | Tier 3: Adversarial & Red-Team Robustness | 20 | **100.0%** | `ADVERSARIAL_EVALUATION` | Yes | N/A | `63f82f254f` | **VERIFIED_DEFENSIBLE** |
| Prompt Injection Vector Blocking Rate | Tier 3: Adversarial & Red-Team Robustness | 15 | **100.0%** | `ADVERSARIAL_EVALUATION` | Yes | N/A | `3a0179a63c` | **VERIFIED_DEFENSIBLE** |
| ScreenSpot-Pro Adapted Diagnostic | Tier 4: Adapted External Diagnostics | 50 | **100.0%** | `PRIVATEEYE_ADAPTED_DIAGNOSTIC` | No | 0.12 ms | `5c18406795` | **VERIFIED_DEFENSIBLE** |
| Mind2Web Adapted Diagnostic | Tier 4: Adapted External Diagnostics | 25 | **100.0%** | `PRIVATEEYE_ADAPTED_DIAGNOSTIC` | No | 0.11 ms | `165313a0e6` | **VERIFIED_DEFENSIBLE** |
| Multi-Domain Realistic Environment Task Success | Tier 5: Real-Web Environment / Hybrid Execution | 125 | **98.4%** | `REAL_WEB_HYBRID_EVALUATION` | No | 0.16 ms (Candidate scoring latency only! Does NOT include Qwen inference) | `17b830d95d` | **VERIFIED_DEFENSIBLE** |
| Live Qwen E2E Task Success Rate | Live End-to-End Multimodal Pipeline | 30 | **96.7%** | `LIVE_QWEN_E2E` | Yes | 7.29 s p50 / 9.12 s p95 (VLM = 99.3% of step time; local overhead = 51.7 ms) | `live_multi` | **VERIFIED_DEFENSIBLE** |
| Repeated Live Workflow Completion Rate | Reliability Across Repeated Executions | 90 | **90.0%** | `LIVE_QWEN_E2E` | Yes | 7.28 s p50 | `phase9_rep` | **VERIFIED_DEFENSIBLE** |
| Repeated Target Loop Rate across 810 Steps | Reliability Across Repeated Executions | 810 | **0.0%** | `LIVE_QWEN_E2E` | Yes | N/A | `phase9_rep` | **VERIFIED_DEFENSIBLE** |
| Detected Raw Secret Leaks across 11 Boundaries | Universal Privacy Invariant Audit | 21 | **0 detected leaks** | `CONTROLLED_HELD_OUT` | Yes | 1.8 ms local inspection | `privacy_bo` | **VERIFIED_DEFENSIBLE** |

## Methodological Audit Findings
1. **Decoupled Latencies:** Tier 5 hybrid evaluation ($0.16\text{ ms}$) strictly measures local Playwright candidate scoring. Live Qwen E2E ($7.29\text{ s}$ p50) measures real multimodal reasoning. Both metrics are clearly decoupled.
2. **Abolished Overclaims:** No instances of the word 'guarantee' or 'zero risk' remain in headline documentation.
3. **External Diagnostics:** ScreenSpot-Pro and Mind2Web checks are strictly classified as `PRIVATEEYE_ADAPTED_DIAGNOSTIC`.
4. **Denominators:** Every single percentage is grounded in complete mathematical numerators and denominators.