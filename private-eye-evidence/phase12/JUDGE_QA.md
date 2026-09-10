# PrivateEye Phase 12 — Hostile Reviewer & Judge Q&A Defense Guide

This document prepares the engineering team to address technical, methodological, and adversarial questions during hackathon judging and security review.

---

### 1. Why not just send the entire raw screen to GPT-4o or a cloud Vision model?
**Answer:** Because the security and privacy boundary is intentionally client-local. Sending raw screen pixels to a remote cloud API violates zero-trust data protection principles: raw screens expose banking credentials, government IDs (PAN, Aadhaar), health records, and private chat feeds to external servers, training pipelines, and third-party data retention. PrivateEye's architecture redacts visual PII client-side and represents sensitive inputs via symbolic `value_ref` tokens, ensuring sensitive secrets never cross the network.

### 2. Why use a relatively small 3B model (Qwen2.5-VL-3B)?
**Answer:** The objective of PrivateEye is not to rely on an unconstrained, compute-heavy 70B+ model to guess user intentions. Instead, our architecture moves visual grounding (local candidate engine with $k=5$), sensitive value resolution (client vault), policy verification (local policy engine), and recovery logic into deterministic local layers. A local 3B model runs entirely on-device (e.g. via Ollama) without GPU cluster costs, preserving local execution boundaries while achieving **98.46% step accuracy** on held-out tasks.

### 3. Why is overall task completion (86.0% / 89.0%) lower than step accuracy (98.46% / 98.79%)?
**Answer:** Because multi-step workflow completion is an accumulated risk problem. In a 20-step workflow, completing the task requires succeeding on every critical state transition ($0.9879^{20} \approx 78.36\%$, matching empirical $78.12\%$). A single failed action (e.g., dynamic DOM race, timing debounce) terminates or stalls the workflow if unrecovered. Long-horizon task completion is fundamentally harder than single-step action selection.

### 4. What happens when the local PII detector misses a secret (e.g., false negative)?
**Answer:** PrivateEye does not rely exclusively on the PII detector. Our defense-in-depth design decouples detection from execution:
1. **Visual Sanitization:** Multi-signal detector (DOM + Regex + NER + Face) catches 94.0% of PII in raw text/pixels.
2. **Local `value_ref` Resolution:** Protected fields (passwords, payment cards, national IDs) are filled via symbolic tokens (`user_profile.pan`). The model never handles the raw secret string.
3. **Outbound Packet Leak Interception:** All outbound network payloads are inspected before transmission against vault secret hashes; if any secret is detected, transmission is immediately blocked.

### 5. What happens under a prompt injection attack from untrusted webpage content?
**Answer:** Untrusted webpage content is ingested into the local `ScreenGraph` with an explicit provenance flag (`untrusted_source=True`). Actions proposed by the model that originate from or redirect to untrusted external URLs are intercepted at the **Local Policy Engine boundary**. The engine classifies unauthorized external exfiltration or destructive clicks as `HIGH RISK / DENIED` and halts execution fail-closed, preventing unauthorized actions (15/15 injection attacks blocked in tests).

### 6. What happens when the DOM mutates between candidate generation and action dispatch?
**Answer:** PrivateEye enforces **Local Reference Validation**. Every generated candidate has a cryptographic element hash and bounding geometry. Before dispatching Playwright actions, the client verifies that the target node is still attached, visible, and matches expected semantics. If the element is stale, the engine halts dispatch, triggers local refetching, and uses selective crop verification rather than blind clicking.

### 7. What happens when the model outputs an invalid or fabricated reference?
**Answer:** PrivateEye is fail-closed. If the model returns an invalid candidate ref or a non-existent `value_ref`, the action is rejected before dispatch. The system does not attempt random clicks; it triggers fresh reasoning with localized state memory or halts cleanly via safe abstention.

### 8. What happens if the browser crashes or disconnects mid-workflow?
**Answer:** The execution runtime intercepts connection dropouts and immediately logs a `browser_disconnected` failure event. It releases vault locks, writes a structured provenance log, and transitions to safe abstention without leaving zombie browser processes running.

### 9. What happens when the local VLM server times out or hangs?
**Answer:** The client enforces an explicit timeout (configurable, default 15s). If the VLM fails to respond, the request is aborted, the failure is categorized as `model_timeout`, and the fail-closed policy halts execution to prevent partial or unverified state mutations.

### 10. What does "fail-closed" mean in this system?
**Answer:** "Fail-closed" means that in the presence of uncertainty, low confidence, policy ambiguity, unmapped references, or component errors, the system defaults to **blocking execution and abstaining**, rather than attempting an unverified action. The agent never executes an action unless policy, confidence, and grounding verifiers explicitly pass.

### 11. What exactly does the emergency kill switch stop?
**Answer:** The kill switch engages an atomic runtime flag that immediately closes the execution dispatch gate. It blocks any pending or subsequent Playwright dispatches, cancels active model inference, releases vault locks, and writes an immutable audit record conforming to OWASP Agent Control Standards. Controlled dispatch-path latency is measured at **0.031–0.043 ms**.

### 12. Is your 20/20 OSWorld benchmark result official?
**Answer:** **No.** PrivateEye achieved 20/20 on a **20-task OSWorld-derived diagnostic subset under our documented adapted protocol**. We do not claim an official OSWorld benchmark ranking or official leaderboard submission; the evaluation serves as an external architectural diagnostic verifying multi-step desktop/browser workflow capabilities.

### 13. Does "0 detected secret leaks" mathematically guarantee absolute privacy?
**Answer:** **No.** We state: *"0 detected secret leaks across tested boundaries, synthetic credentials, and adversarial failure conditions."* This is an empirical measurement across our extensive invariant test suite, not a formal mathematical proof of zero risk across all arbitrary web pages.

### 14. Why does performance degrade on long-horizon tasks (63.33% vs 100% short)?
**Answer:** Our hazard rate sensitivity analysis shows that per-step hazard remains approximately stationary between steps 6 and 20 (~1.42% per step). Degradation is governed by compounding step risk over 20 consecutive operations ($0.9879^{20} \approx 78.36\%$) and environmental friction (asynchronous DOM delays, complex modal cascades) rather than sudden memory collapse.

### 15. What is the single biggest remaining limitation of PrivateEye?
**Answer:** Long-horizon multi-step resilience on unstructured, dynamic single-page applications with unpredictable asynchronous state delays. While step accuracy is 98.46%, compounding step risks reduce long-horizon completion to 63.33% on held-out tasks.

### 16. What would you build or improve next with 3 more months of research?
**Answer:** 
1. **Dynamic Checkpoint Rollback:** Implement Playwright session snapshotting to rewind state upon post-condition failure rather than aborting.
2. **Specialized Compact Grounding Heads:** Fine-tune a dedicated 0.5B vision grounding head to eliminate visual crop latency.
3. **Formal Verification of Policy Gates:** Mechanically verify policy invariant predicates using SMT solvers.

### 17. How does this architecture scale beyond a single local laptop?
**Answer:** The architecture naturally separates into a client-side execution container (holding user credentials and Playwright) and a private enterprise model inference cluster. The network payload between them contains only sanitized screenshots and symbolic tokens—guaranteeing enterprise data privacy even across shared infrastructure.

### 18. What makes PrivateEye fundamentally different from typical browser agents (e.g. standard LangChain/Playwright wrappers)?
**Answer:** Standard browser agents treat the VLM as an **unrestricted autonomous agent** that receives raw screen data and directly issues browser clicks. PrivateEye treats the VLM as an **untrusted reasoning advisor**:
- Observations are redacted before reaching the model.
- Candidate actions are restricted to locally verified DOM targets ($k=5$).
- Protected credentials are resolved exclusively on the client via `LocalVault`.
- Actions must pass through an authoritative `LocalPolicyEngine` and `KillSwitch`.
- Execution is strictly verified by post-condition checks and fails closed.
