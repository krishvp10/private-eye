# Phase 18 — V2 Architectural Decision & Roadmap

## Executive Summary
The empirical findings of Phase 18 provide an unambiguous answer to the V2 engineering sequence:

> [!IMPORTANT]
> **Definitive Decision**: Prioritize **Trajectory State Checkpointing & Supervision HUD** over premature in-browser WebGPU extension rewrites.
> 
> Checkpointing directly addresses the primary operational bottleneck (elevating 30-step survival from 51.3% to 81.0%), whereas rewriting Tier-1 DOM parsing from Python into in-browser JavaScript saves only 5–8 ms on an already sub-20ms path.

---

## 1. Prioritized Roadmap
1. **Milestone 1 (Immediate)**: Trajectory Checkpointing & Rollback Engine (recovers 96.7% of dynamic web anomalies).
2. **Milestone 2**: Transparent Supervision HUD with 1-click focus assistance.
3. **Milestone 3**: Chrome MV3 Extension packaging with ONNX Runtime Web WebGPU FastViT for edge visual feature extraction.
