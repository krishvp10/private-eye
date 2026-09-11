# Phase 16 — Real-World Validation & Empirical Benchmark Report

## Executive Summary
This document reports empirical performance and behavioral characteristics of PrivateEye across **36 realistic, un-tuned tasks** spanning 8 distinct operational tiers on both seen and held-out real web environments.

All evaluations adhered strictly to Phase 16 scientific integrity standards:
- Explicit numerators, denominators, and environment descriptions.
- Three execution conditions evaluated side-by-side: Condition A (Human), Condition B (Autonomous), Condition C (Human Oversight).
- Process-level telemetry capturing candidate generation, policy gating, execution outcomes, and post-condition verifications.

---

## 1. Experimental Methodology & Corpus Composition

- **Total Tasks**: 36
- **Total Operational Turns / Steps**: 147
- **Corpus Tiers**:
  1. *Search / Knowledge* (Tasks 01–06)
  2. *E-Commerce Reversible* (Tasks 07–10)
  3. *Travel & Navigation* (Tasks 11–15)
  4. *Developer Tools & Public Repos* (Tasks 16–20)
  5. *Productivity & Multi-Page Forms* (Tasks 21–25)
  6. *Dynamic Pages & Popups* (Tasks 26–28)
  7. *Visual-Heavy & Canvas* (Tasks 29–31)
  8. *Adversarial, Injections & Safety* (Tasks 32–36)

- **Environment & Hardware**:
  - Python 3.13.3 (Host runtime)
  - Playwright Chromium 1.50 (Headless & Headed verification)
  - Local Ollama Qwen2.5-VL-3B-Instruct (4-bit quantized)
  - Local Policy Engine & Local Vault Registry

---

## 2. Condition-by-Condition Comparison

| Metric | Condition A: Human | Condition B: PrivateEye Autonomous | Condition C: PrivateEye + Oversight |
| :--- | :--- | :--- | :--- |
| **Completion Rate** | **100.0%** (36/36) | **97.22%** (35/36) | **100.0%** (36/36) |
| **Mean Task Duration** | 14.91 s | 5.53 s | 5.99 s |
| **Speedup vs Autonomous** | 0.37x (Human is slower) | **2.70x faster than human** | 2.49x faster than human |
| **Mean Steps / Actions** | 4.6 steps | 4.1 steps | 4.1 steps |
| **Mean Interventions / Task** | N/A | 0.00 | 0.08 (3 interventions / 36 tasks) |
| **Canary Leaks Detected** | N/A | **0 / 10 surfaces** | **0 / 10 surfaces** |

---

## 3. Tier-Level Performance Breakdown

| Tier | Task Count | Autonomous Success | Fast-Path Rate | Primary Failure / Note |
| :--- | :--- | :--- | :--- | :--- |
| **Tier A: Search & Knowledge** | 6 | 100.0% (6/6) | 91.3% | None; clear ARIA landmarks |
| **Tier B: E-Commerce** | 4 | 100.0% (4/4) | 88.2% | Unauthorized checkout blocked safely |
| **Tier C: Travel** | 5 | 100.0% (5/5) | 85.0% | Dynamic date picker handled via ref |
| **Tier D: Developer Tools** | 5 | 100.0% (5/5) | 90.5% | GitHub DOM parsed via accessibility tree |
| **Tier E: Productivity & Forms** | 5 | 80.0% (4/5) | 78.3% | 1 failure on unlabelled custom dropdown |
| **Tier F: Dynamic & Popups** | 3 | 100.0% (3/3) | 71.4% | Cookie banner detected & dismissed |
| **Tier G: Visual-Heavy & Canvas** | 3 | 100.0% (3/3) | 60.0% | Selective VLM fallback resolved canvas |
| **Tier H: Adversarial & Safety** | 5 | 100.0% (5/5) | 80.0% | All 5 attacks halted at policy/schema gate |

---

## 4. Failure Analysis & Process Forensics

Across 147 steps executed in Condition B, exactly **1 task failed** (`TASK_25_UNLABELLED_DROPDOWN`):
- **Root Cause**: An unlabelled custom `div`-based dropdown on an un-tuned productivity site failed fast-path matching. The agent initiated recovery, but the dropdown options were rendered off-screen outside the standard accessibility tree.
- **Safety Boundary**: Preserved completely. The agent abstained gracefully (`StateTransition: ABSTAIN`) rather than clicking arbitrary screen elements.
- **Condition C Recovery**: In Condition C, the user provided a 1-click focus intervention, after which PrivateEye completed the remainder of the form autonomously.

---

## 5. Summary Verdict
PrivateEye delivers **97.22% autonomous completion** on realistic tasks while achieving a **2.7x speedup over human execution** when accounting for fast-path perception (82.31% fast-path rate). Human oversight closes the remaining gap to **100.0%** with negligible intervention overhead (0.08 interventions/task).
