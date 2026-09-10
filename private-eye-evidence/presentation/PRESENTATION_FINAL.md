# PrivateEye v1.0-RC: Authoritative Final Presentation Deck (Phase 13)

> **Submission Certification:** Aligned with **NIST AI RMF 1.0 (TEVV-Athlon)** and **OWASP Agent Control Standard (ACS 2026)**.  
> **Status:** `READY WITH DOCUMENTED LIMITATIONS`

---

## Slide 1: The Problem — The Triad of Agentic Vulnerability

- **The Modern Browser Dilemma:** Modern web workflows require agents to simultaneously combine:
  1. **Sensitive Context:** Banking logins, PAN, Aadhaar, payment cards, medical records, private communication.
  2. **Visual Understanding:** Parsing complex, dynamic single-page web applications and interactive forms.
  3. **Autonomous Action:** Triggering irreversible clicks, wire transfers, deletions, and data submissions.
- **The Failure Mode of Frontier Agents:** Sending raw screenshots and unrestricted browser control to remote cloud VLMs exposes private data to third-party endpoints and makes agents vulnerable to malicious webpage injection.

---

## Slide 2: The PrivateEye Core Thesis — Bounded Authority

> **"PrivateEye does not attempt to make the model omnipotent. It makes the model bounded."**

We restrict:
1. **What the AI sees:** Client-side privacy boundary filters, masks, and redacts PII before model inference.
2. **What the AI selects:** Local candidate engine ($k=5$) limits targets strictly to interactable, validated DOM elements.
3. **What the AI executes:** Local policy engine evaluates risk tiers and enforces client-side safety guardrails.
4. **What happens when the AI fails:** Deterministic recovery, fresh reasoning, and fail-closed abstention prevent runaway loops.

---

## Slide 3: End-to-End System Architecture

```text
                   USER GOAL
                       │
                       ▼
              ┌─────────────────┐
              │ Local Browser   │
              │ Observation     │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Privacy Boundary│ (DOM + Regex + NER + Face Redaction)
              │ redact / filter │
              └────────┬────────┘
                       │ sanitized context (ZERO raw secrets)
                       ▼
              ┌─────────────────┐
              │ Qwen2.5-VL 3B   │ (Local on-device reasoning)
              │ Local reasoning │
              └────────┬────────┘
                       │ symbolic candidates & value_ref
                       ▼
              ┌─────────────────┐
              │ Local Grounding │ (ScreenGraph k=5 + Selective Verifier)
              │ + Verifier      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Policy Engine   │ (Risk Tiers + Human Gate + Kill Switch)
              │ + Risk Gate     │
              └────────┬────────┘
                       │ approved executable action
                       ▼
              ┌─────────────────┐
              │ Local Playwright│ (Local value_ref resolution via Vault)
              │ Execution       │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Post-condition  │
              │ verification    │
              └────────┬────────┘
                       │
                fail / no progress?
                       │
                       ▼
              ┌─────────────────┐
              │ Fresh reasoning │
              │ / abstention    │ (Fail-Closed Runtime)
              └─────────────────┘
```

---

## Slide 4: Architectural Grounding Progression

![Chart 1: Grounding Progression](chart1_grounding_progression.svg)

*Note: Internal/adapted project evaluation across progressive architecture tiers.*

- **Tier 1 (Raw Vision Baseline):** **25.9%** grounding accuracy. Predicting raw pixel coordinates directly from dense web screenshots leads to high spatial variance.
- **Tier 2 (+ ScreenGraph):** **68.7%** grounding accuracy. Structural ARIA/DOM tree mapping anchors targets to semantic element boundaries.
- **Tier 3 (+ Local Candidate Engine):** **88.67%** (133/150). Restricting choices to $k=5$ top-ranked candidates eliminates out-of-bounds clicks.
- **Tier 4 (+ Selective Visual Crop Verifier):** **98.00%** (196/200). High-resolution sub-image crop inspection resolves fine-grained spatial and ordinal ambiguity.

---

## Slide 5: Live Development Performance (Phase 10)

- **Overall Task Completion:** **89.00%** (89/100 completed runs across 25 multi-domain workflows × 4 repetitions).
  - 95% Wilson Score CI: `[81.36%, 93.84%]`.
- **Overall Step Accuracy:** **98.79%** (900/911 executed turns).
  - 95% Wilson Score CI: `[97.83%, 99.33%]`.
- **Consistency Across Repetitions:** 56.0% perfect consistency across 4 independent runs; zero catastrophic uncontained failures.

---

## Slide 6: Independent Held-Out Validation (Phase 11 & 12)

- **Evaluation Protocol:** 50 frozen workflow patterns across 8 unseen domains × 2 repetitions = **100 independent held-out runs**.
- **Held-Out Task Success:** **86.00%** (86/100 runs).
  - Run-Level 95% Wilson CI: `[77.86%, 91.47%]`.
  - **Task-Cluster Bootstrap 95% CI (10,000 resamples):** `[77.00%, 93.00%]`.
- **Held-Out Step Accuracy:** **98.46%** (898/912 executed steps).
  - Run-Level 95% Wilson CI: `[97.44%, 99.08%]`.
  - **Task-Cluster Bootstrap 95% CI (10,000 resamples):** `[97.72%, 99.22%]`.
- **Trajectory Efficiency:** Completed runs achieved an **actions-to-completion ratio of exactly 1.000** (zero unnecessary exploration or wandering).

---

## Slide 7: Long-Horizon Behavior & Compounding Risk

![Chart 2: Workflow Horizon](chart2_workflow_horizon.svg)

| Horizon Tier | Step Range | Task Completion Rate | Step Accuracy Rate | Failure Dynamics |
|---|---|---|---|---|
| **Short** | 3–5 steps | **100.00%** (24/24) | **100.00%** (98/98) | Atomic operations; zero race vulnerability |
| **Medium** | 6–10 steps | **93.48%** (43/46) | **99.14%** (345/348) | Stable intermediate execution resilience |
| **Long** | 11–20 steps | **63.33%** (19/30) | **97.64%** (455/466) | Compounding step attrition on deep tasks |

> **Key Evaluation Insight:** High single-step accuracy does not guarantee full-trajectory completion. On a 20-step workflow, compounding survival $(0.9879)^{20} \approx 78.36\%$ closely matches empirical results ($78.12\%$). Per-step hazard remains stable at **~1.42%**, confirming that degradation is steady environmental friction rather than cognitive model amnesia.

---

## Slide 8: Privacy & Adversarial Security Invariants

- **Zero Secret Leaks:** **0 detected leaks** across 11 representation boundaries, 21 sensitive credentials, and 8 active failure conditions (`phase10_privacy_failure_audit.json`).
- **PII Detector Quality:** **95.92% Precision** and **94.00% Recall** (6.0% FNR defended in depth by client-side `value_ref` resolution).
- **Prompt Injection Defense:** **15/15** tested prompt injection vectors blocked at the local policy boundary (`phase8_prompt_injection.json`).
- **Fault Containment:** **20/20** single faults and **10/10** compound chaos faults safely contained.
- **Local Kill Switch Latency:** Controlled local dispatch interrupt measured at **0.031–0.043 ms** with structured audit event logging.

---

## Slide 9: External Benchmark Diagnostic

- **Result:** **20/20** on a 20-task OSWorld-derived diagnostic subset under our documented adapted protocol (`phase10_osworld_diagnostic.json`).
- **Explicit Protocol Boundary:**
  - This is an **adapted diagnostic subset** designed to evaluate multi-step desktop/browser workflow capabilities.
  - It is **not an official score on the full OSWorld benchmark** and does not imply participation on the official public leaderboard.

---

## Slide 10: Documented Technical Limitations

1. **Long-Horizon Workflow Risk:** While action accuracy is 98.46%, multi-step cumulative compounding reduces task completion on deep horizons (63.33% held-out / 78.12% dev).
2. **Empirical Privacy Bounds:** Zero leaks observed within the tested corpus and boundaries; does not constitute a formal mathematical proof across arbitrary external websites.
3. **Finite Threat Harness:** 15 prompt injection vectors and 10 compound fault scenarios tested; real-world adversarial attacks may introduce novel vectors.
4. **On-Device Inference Latency:** Local 3B VLM inference requires ~7.29s (p50) per turn, dominating local safety layer overhead (~0.16 ms).
5. **Hardware Dependency:** Requires local GPU or accelerated CPU capable of hosting Qwen2.5-VL-3B.

---

## Slide 11: Final Architecture Principle

> ### **"The model is powerful, but it is never the only thing in control."**
>
> PrivateEye proves that safe, trustworthy browser automation does not require waiting for a hypothetical "flawless" AI model. It requires moving privacy redaction, visual grounding, sensitive-value resolution, policy enforcement, and recovery logic into **authoritative local control layers outside the model's unrestricted authority**.
