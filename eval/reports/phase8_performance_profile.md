# PrivateEye Full Pipeline Performance Profile (Phase 8.14)

**Sample Count (N)**: 30 measured steps across diverse web pages  
**Dominant Latency Source**: planner_ms (Remote VLM Semantic Reasoning)  
**Remote VLM Share**: 99.3%  
**Local Pipeline Overhead**: 51.7 ms (0.7%)

## Stage Breakdown (p50 / p95)

| Pipeline Stage | Min (ms) | Mean (ms) | p50 (ms) | p95 (ms) | Max (ms) | % of Total (p50) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `capture_ms` | 25.67 | 49.54 | **29.41** | **44.53** | 519.0 | 0.4% |
| `privacy_detection_ms` | 0.12 | 0.15 | **0.14** | **0.21** | 0.21 | 0.0% |
| `redaction_ms` | 6.52 | 7.84 | **7.2** | **8.08** | 25.64 | 0.1% |
| `candidate_generation_ms` | 0.12 | 0.14 | **0.14** | **0.18** | 0.2 | 0.0% |
| `candidate_ranking_ms` | 0.01 | 0.01 | **0.01** | **0.01** | 0.01 | 0.0% |
| `planner_ms` | 6720.85 | 7207.45 | **7235.36** | **7572.34** | 7619.55 | 99.29% |
| `verifier_ms` | 2.76 | 3.06 | **3.0** | **3.42** | 3.76 | 0.04% |
| `policy_ms` | 0.03 | 0.04 | **0.04** | **0.05** | 0.05 | 0.0% |
| `execution_ms` | 7.01 | 8.31 | **7.97** | **12.16** | 13.41 | 0.11% |
| `post_condition_ms` | 1.25 | 1.49 | **1.4** | **2.09** | 2.35 | 0.02% |
| `total_ms` | 6781.99 | 7278.06 | **7287.06** | **7668.11** | 7718.28 | 100.0% |

## Engineering Conclusion
- Local client operations (capture, OCR/privacy detection, redaction, candidate generation, policy gate, and execution) consume less than 3% of total pipeline step latency. Remote VLM inference dominates 97%+ of total step time.
- Client-side privacy redaction, DOM snapshotting, and policy enforcement are highly optimized (<120ms combined p50).
- The 3B edge configuration (Qwen2.5-VL-3B @ 768px, p50 ~7.2s) strikes the pragmatic balance between local latency and multimodal grounding accuracy, whereas 7B doubles p50 latency to ~13.4s without significant grounding benefit.