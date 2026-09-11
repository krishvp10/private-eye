# Phase 17 — Architectural Decision: Prioritizing Real Workloads Over Premature Extension Engineering

## Executive Summary
Based on the empirical evidence gathered across Phases 16 and 17, this document establishes the engineering decision regarding **PrivateEye V2**:

> [!IMPORTANT]
> **Decision Rule**: Do NOT begin rewriting PrivateEye into a full Chrome MV3 extension before resolving long-horizon environmental desynchronization and user explainability.
> 
> The primary bottleneck to real-world user adoption is **long-horizon compounding stability and policy explainability**, NOT in-browser WebGPU execution.

---

## 1. Evidence-Driven Architectural Analysis

### A. What consumes the most user latency?
- **Perception turns**: 75.7% of turns use Tier-1 Fast Local Perception, executing in **14.1 ms**.
- Moving 14 ms host DOM parsing into in-browser JavaScript would save at most **5–8 ms**, which is perceptually imperceptible to the user.
- The dominant latency contributor is the **24.3% of turns requiring Tier-2 Qwen fallback (~7.26 s)**. Since 3B+ parameter VLMs cannot run stably inside a Chrome tab without triggering OOM crashes (requiring 3.6 GB memory), the heavy fallback model *must remain on the host* regardless of extension architecture.

### B. What causes actual agent failures?
- In unconstrained evaluations, failures do not stem from DOM parsing speed.
- Failures stem from:
  1. **Dynamic DOM desynchronization** on infinite scroll or delayed AJAX (compounding over 20+ steps).
  2. **Unlabelled custom UI components** lacking ARIA accessibility trees.
  3. **Adversarial duplicate buttons** requiring user disambiguation.

---

## 2. Definitive V2 Engineering Roadmap
1. **Milestone 1: State Checkpointing & Deep Trajectory Stabilization**:
   - Implement DOM snapshot rollback and automatic session state recovery to increase 30-step survival from 50% to 80%+.
2. **Milestone 2: Explainable User Supervision HUD**:
   - Enhance the control plane with step-by-step progress tracking and interactive 1-click focus helpers.
3. **Milestone 3: Chrome MV3 Offscreen WebGPU Bridge**:
   - Only after stabilizing deep trajectories, package Tier-1 Fast Perception and the Canary Redaction Masker into a Chrome MV3 Extension using ONNX Runtime Web FastViT for local coordinate refinement.
