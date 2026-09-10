# Phase 8 Metric & Reporting Provenance Audit

**Methodological Rule:** `NO METRIC WITHOUT A COMPLETE DENOMINATOR`

## 5-Tier Evaluation Hierarchy

| Tier | Metric | Reported | N (Denom) | Numerator | Evaluator / Engine | Classification |
|---|---|---|---|---|---|---|
| Tier 1 | **Development Set Accuracy (Top-1)** | `88.7%` | 150 | 133 | Local Hybrid Engine (Playwright ARIA + Rule Ranker) | `DEVELOPMENT_REGRESSION_BASELINE` |
| Tier 1 | **Development Set Top-3 Candidate Recall** | `100.0%` | 150 | 150 | Local Candidate Engine | `DEVELOPMENT_REGRESSION_BASELINE` |
| Tier 2 | **Held-Out Generalization Target Accuracy** | `98.0%` | 200 | 196 | PrivateEye Selective Grounding Architecture | `HELD_OUT_GENERALIZATION_EVIDENCE` |
| Tier 2 | **Selective Verification Accuracy (Mode C)** | `98.5%` | 200 | 197 | PrivateEye Mode C Engine | `OPTIMIZED_POLICY_EVIDENCE` |
| Tier 3 | **Safe Abstention Rate on Ungroundable Decoys** | `100.0%` | 20 | 20 | PrivateEye Selective Autonomy Gate | `ADVERSARIAL_SAFETY_EVIDENCE` |
| Tier 3 | **Prompt Injection Defense Rate** | `100.0%` | 7 | 7 | PrivateEye Security Pipeline | `SECURITY_DEFENSE_EVIDENCE` |
| Tier 4 | **ScreenSpot-Pro Visual Hit Test (Adapted)** | `100.0%` | 25 | 25 | PrivateEye Diagnostic Runner | `PRIVATEEYE_ADAPTED_DIAGNOSTIC` |
| Tier 4 | **Mind2Web Multimodal Action Grounding (Adapted)** | `100.0%` | 25 | 25 | PrivateEye Diagnostic Runner | `PRIVATEEYE_ADAPTED_DIAGNOSTIC` |
| Tier 5 | **Real-Web Action Correctness (Level 1)** | `TBD` | 125 | 125 | Qwen2.5-VL-3B + PrivateEye Architecture | `REAL_WEB_EVIDENCE` |

## Methodological Corrections & Hygiene Mandates

### 1. External Diagnostic Hygiene
- Historical ScreenSpot-Pro (100.0%) and Mind2Web (100.0%) evaluations are formally re-classified as **`PRIVATEEYE ADAPTED DIAGNOSTIC`**.
- **They are NOT official leaderboard submissions.** They demonstrate that PrivateEye's candidate extraction and verification architecture seamlessly adapts to external task formats.

### 2. Live Multimodal Model Separation
- Target accuracy on synthetic benchmarks measures the **local hybrid candidate ranker + selective crop verifier**.
- Live multimodal runs with Qwen2.5-VL-3B are tracked separately with step latency (7.2s p50) and end-to-end workflow completion (5/5).

### 3. Real-World Web Evaluation (Tier 5)
- Tier 5 evaluates realistic web interfaces with untamed DOMs, unstyled inputs, dynamic modals, and long scroll depths across 5 distinct hierarchical levels (L1 through L5).
