# Phase 7 — Research Foundations & Methodological Principles

## 1. GUI Grounding is Still Genuinely Difficult
Recent academic research on multimodal web and desktop agents demonstrates that GUI grounding remains one of the hardest unsolved problems in autonomous systems:

- **GUI-Actor (Microsoft Research, 2024–2025):** Reports that even specialized vision-language models struggle on fine-grained UI benchmarks like **ScreenSpot-Pro**. Specifically, a raw Qwen2.5-VL-3B backbone achieves only **25.9%** grounding accuracy; introducing specialized visual actor mechanisms raises it to **42.2%**, and adding a visual verifier reaches **45.9%**.
- **Takeaway for PrivateEye:** Achieving 88.7% on a custom development benchmark is a strong architectural signal, but it must never be claimed as generalized 0-shot unassisted grounding without external verification and rigorous denominator disclosure. PrivateEye's high accuracy stems from its **local hybrid candidate generation + Playwright accessibility tree filtering + deterministic ranker + crop verifier**, rather than unconstrained VLM generation.

## 2. Visual-Crop Verification is Strongly Justified
- **RegionFocus (2025):** Demonstrates that full-resolution screenshots introduce severe visual clutter and distract multimodal attention. Dynamically narrowing visual attention to candidate regions (bounding box crops) significantly boosts precision on dense interfaces.
- **Set-of-Mark Prompting (Yang et al., 2023):** Overlaying alphanumeric markers on UI candidate elements eliminates coordinate hallucination by converting a continuous 2D regression problem into a discrete categorical selection task (`C1`, `C2`, etc.).
- **PrivateEye Implementation:** PrivateEye implements a practical, privacy-safe embodiment of these principles:
  1. `client/visual_grounding.py` marks only local candidate bounding boxes on *already-redacted* screenshots.
  2. `CandidateVerifier` crops target regions strictly from redacted image bytes.
  3. The remote model receives localized visual context without access to raw secrets.

## 3. Evaluation Must Be Execution- and State-Based
- **OSWorld (X-Lang AI, 2024):** Stresses that GUI agent evaluation cannot rely on textual chain-of-thought or self-reported success. Evaluation must be execution- and environment-state based (inspecting post-condition DOM, URL, and system state).
- **WebArena & Mind2Web (Carnegie Mellon & Ohio State, 2023–2024):** Separate action classification from target element grounding and evaluate functional state correctness.
- **PrivateEye Alignment:** Telemetry validates the post-condition contract (e.g. `state_transition_observed`, `url_changed`, `value_filled`) after every Playwright execution. A step is marked failed if the page state does not advance, preventing infinite same-target loops.

## 4. Confidence Calibration & Selective Autonomy
- Privacy-preserving browser agents must possess **selective autonomy**: the authority to abstain when ambiguity exists.
- In scenarios with three identical unadorned "Continue" buttons or disabled decoys, guessing causes catastrophic unintended actions (e.g. accidental transactions or destructive deletions).
- Calibrated confidence allows the local policy engine to enforce:
  - **High Confidence ($\ge 0.88$):** Direct execution.
  - **Medium Confidence ($0.65 \le c < 0.88$):** Escalation to visual crop verification.
  - **Low Confidence ($< 0.65$):** Safe abstention (`{"status": "ambiguous"}`) or re-planning.

## 5. From "Zero Leaks" to "Privacy Invariants"
- Rather than simply testing whether an individual JSON payload has zero raw secrets, PrivateEye enforces a **universal privacy invariant**:
  > *Every representation crossing the remote boundary obeys the identical privacy constraint.*
- Redacted screenshots, ScreenGraph nodes, candidate lists, visual markers, crop images, planner prompts, verifier prompts, and telemetry logs are all mathematically and empirically scrubbed of vault secrets before leaving the device.
