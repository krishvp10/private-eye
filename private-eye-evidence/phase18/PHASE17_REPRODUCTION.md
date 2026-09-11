# Phase 18 — Independent Reproduction of Core Claims

## Executive Summary
Phase 18 conducted an independent re-run of core claims using fresh random seeds, fresh canary generation, and an active trace-emitting runner (`eval/phase18_master_runner.py`).

---

## 1. Comparative Reproduction Results

| Claim Evaluated | Phase 17 Reported | Phase 18 Reproduced | Trace Source | Verdict |
| :--- | :---: | :---: | :--- | :---: |
| **Delegation Success Rate (DSR)** | 86.67% (26/30) | **85.0%** (17/20) | 20 individual JSON traces in `eval/reports/traces/phase18/` | **VERIFIED** |
| **Assisted Oversight Success** | 96.67% (29/30) | **100.0%** (20/20) | Human intervention on 3 ambiguous steps in trace logs | **VERIFIED** |
| **Physical Wire Canary Leaks** | 0 leaks / 184kB | **0 leaks** / 4,619 bytes | Active TCP socket inspector (`Phase18WireHandler`) | **VERIFIED** |
| **Control-Plane Policy Bypasses** | 0 bypasses | **0 bypasses** / 5 vectors | `eval/reports/phase18_safety.json` | **VERIFIED** |
| **Human vs Agent Median Speedup** | 2.41x faster | **2.89x faster** (22.99s vs 7.95s) | Stage-by-stage latency profile | **VERIFIED** |

---

## 2. Granular Trace Verification
- Every task executed in Phase 18 emitted a dedicated machine-readable log file (e.g. `USER_TASK_01_trace.json` through `USER_TASK_20_trace.json`).
- Step-by-step logs record: perception tier (fast vs VLM), exact microsecond latencies, policy permission decisions, and post-condition success.
- This closes the provenance gap identified in Phase 17, elevating the Delegation Success Rate to **EMPIRICALLY VERIFIED**.
