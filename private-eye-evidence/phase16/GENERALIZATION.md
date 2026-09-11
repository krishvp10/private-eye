# Phase 16 — Seen vs. Held-Out Generalization Analysis

## 1. Context & Motivation
As established in recent web-agent literature (e.g., WebLINX, WebArena), browser agents frequently demonstrate high success on websites they were tuned or tested against, but degrade severely on unseen, dynamic real-world sites.

To prevent benchmark overfitting, Phase 16 established an explicit 20/16 split between Development (Seen) sites and Held-Out Real sites.

---

## 2. Generalization Split Breakdown

| Corpus Partition | Task Count | Completed | Failed | Success Rate | Fast-Path Rate | VLM Fallback Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seen Development Sites** | 20 | 20 | 0 | **100.0%** (20/20) | 85.2% | 14.8% |
| **Held-Out Real Sites** | 16 | 15 | 1 | **93.75%** (15/16) | 78.4% | 21.6% |
| **Generalization Delta** | — | — | — | **-6.25%** | -6.8% | +6.8% |

---

## 3. Analysis of Held-Out Degradation
- **Generalization Gap**: The agent exhibited a minor **6.25% drop** in task completion on completely un-tuned domains.
- **Increased Reliance on Tier-2 Fallback**: On held-out sites, the VLM fallback rate rose from 14.8% to 21.6%, demonstrating that novel visual layouts trigger PrivateEye's uncertainty threshold, appropriately invoking the deeper vision-language model.
- **Graceful Failure**: The single failed task (`TASK_25`) resulted in an explicit, policy-compliant abstention rather than an incorrect or destructive click. Under Condition C (Human Oversight), a single human click resolved the unlabelled element, restoring 100% downstream completion.
