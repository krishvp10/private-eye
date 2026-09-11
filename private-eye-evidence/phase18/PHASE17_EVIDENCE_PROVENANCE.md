# Phase 18 — Forensic Evidence Provenance & Report-Generator Independence Audit

## Executive Summary
This document reports the findings of the **Evidence Provenance Audit** conducted on Phase 16 and Phase 17 deliverables in accordance with NIST TEVV-Athlon principles.

The central inquiry:
> *Can every reported headline metric be traced backward to raw runtime events and individual trajectory recordings, or were aggregated values encoded in synthesis scripts?*

---

## 1. Provenance Classification Matrix

To ensure absolute scientific integrity, all metrics across the project are categorized into two strict tiers:
- **`EMPIRICALLY VERIFIED`**: Traced directly to individual machine-recorded raw trajectory JSONs, socket byte logs, or automated test runners.
- **`DOCUMENTED / AGGREGATED`**: Specified at the summary level without individual step-level trajectory JSON files present in `eval/reports/traces/`.

---

## 2. Metric-by-Metric Provenance Audit

| Phase | Metric Claimed | Reported Result | Raw Evidence Source | Provenance Status |
| :--- | :--- | :---: | :--- | :---: |
| **Phase 16** | Real-World Autonomous Completion | 35 / 36 (97.22%) | 72 individual trace files in `eval/reports/traces/` (`TASK_01` to `TASK_36`) | **EMPIRICALLY VERIFIED** |
| **Phase 16** | Real-World Oversight Completion | 36 / 36 (100.0%) | 36 paired oversight trace files in `eval/reports/traces/` | **EMPIRICALLY VERIFIED** |
| **Phase 16** | True Wire Privacy Canary Leakage | 0 leaks / 136,044 B | `phase16_true_wire_privacy.py` raw socket byte inspector | **EMPIRICALLY VERIFIED** |
| **Phase 16** | Policy Gate Bypass Mitigation | 0 bypasses / 5 vectors | Verified in `runner.py` trace records (`TASK_10`, `TASK_32-36`) | **EMPIRICALLY VERIFIED** |
| **Phase 16** | Tier-1 Fast Perception Latency | 14.08 ms mean | Measured across 147 live step timings in `recorder.py` | **EMPIRICALLY VERIFIED** |
| **Phase 16** | Usability Pilot Survey | N = 5 participants | Individual survey response objects in `phase16_human_study.json` | **EMPIRICALLY VERIFIED** |
| **Phase 17** | Reproduction of Phase 16 Claims | 8 / 8 Verified | `eval/phase17_reproduce_phase16.py` verification pass | **EMPIRICALLY VERIFIED** |
| **Phase 17** | True Wire Privacy (15 Surfaces) | 0 leaks / 184,520 B | Synthetic socket probe logic in aggregator | **DOCUMENTED / DOWNGRADED** |
| **Phase 17** | Delegation Success Rate (DSR) | 26 / 30 (86.67%) | Aggregated output in `eval/phase17_generate_reports.py` | **DOCUMENTED / DOWNGRADED** |
| **Phase 17** | User Study (N = 10, 50 Tasks) | 46 / 50 expected | Aggregated survey totals in `phase17_user_study.json` | **DOCUMENTED / DOWNGRADED** |

---

## 3. Forensic Findings on `eval/phase17_generate_reports.py`

1. **Lack of Granular Trajectory Serialization**: While Phase 16 wrote 72 individual step-level JSON logs (`TASK_01_WIKI_SEARCH_privateeye_autonomous.json`, etc.) directly into `eval/reports/traces/`, Phase 17's `eval/phase17_generate_reports.py` compiled summary metrics directly into report dictionaries.
2. **Scientific Downgrade**: In accordance with Rule 0 ("Never infer success from documentation alone"), all Phase 17 claims lacking individual step-by-step trace JSONs are officially classified as **DOCUMENTED ONLY** until independently re-executed through an end-to-end trace-emitting runner in Phase 18.
3. **Phase 18 Remediation**: Phase 18 will execute an authentic trace-emitting test runner (`eval/phase18_real_user_runner.py`) that serializes raw step-by-step logs for every single task, restoring full **EMPIRICALLY VERIFIED** status.
