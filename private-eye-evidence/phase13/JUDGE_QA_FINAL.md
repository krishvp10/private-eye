# PrivateEye v1.0-RC: Authoritative Judge Q&A & Technical Defense Guide (Phase 13)

This document provides concise, evidence-backed, technically precise answers to the 24 critical questions asked by technical reviewers, hackathon judges, and security evaluators.

---

### 1. What problem does PrivateEye solve?
**Answer:** Traditional browser agents stream raw screen pixels to remote frontier VLMs and grant them unrestricted execution authority. This leaks sensitive personal and financial PII (PAN, passwords, healthcare records) across the network and exposes user browsers to prompt injection and irreversible state corruption. PrivateEye solves this by enforcing an authoritative client-side privacy, grounding, and policy boundary that keeps sensitive data local and bounds model authority.

### 2. Why can't you just use GPT-4o or Claude 3.5 Sonnet with browser access?
**Answer:** Sending user browser sessions to remote commercial APIs violates zero-trust enterprise security:
1. **Privacy Exposure:** Unredacted bank statements, tax IDs, and confidential internal portals cross external boundaries.
2. **Unrestricted Authority:** If a webpage injects a command instructing the model to transfer funds or delete data, a raw cloud VLM will attempt to execute it directly.
3. **Bandwidth & Latency:** Uploading multi-megabyte high-resolution screenshots on every turn creates substantial network latency and token costs.

### 3. Why use Qwen2.5-VL-3B instead of a larger 70B model?
**Answer:** PrivateEye demonstrates that you do not need an unconstrained 70B+ cloud model to achieve high web-agent reliability. By moving candidate generation, visual crop verification, policy gating, and sensitive credential resolution into deterministic local layers, an on-device 3B model achieves **98.46% step accuracy** on held-out workflows while running completely offline without cloud API fees or data leakage.

### 4. Why must privacy enforcement remain local on the client device?
**Answer:** Because once sensitive pixels or strings cross the network interface card (NIC), the user has lost control over data retention, provider logging, model retraining, and upstream intercept. Processing PII detection, redaction, and secret vault storage entirely on-device is the only way to satisfy zero-trust data sovereignty.

### 5. What happens if the PII detector misses something (false negative)?
**Answer:** PrivateEye employs **defense-in-depth**:
1. The multi-signal detector (DOM + Regex + NER + Face) achieves **94.00% recall** and **95.92% precision**.
2. For sensitive fields (e.g. passwords, payment cards, national IDs), the system requires **symbolic `value_ref` resolution**: the agent never operates on raw text.
3. All outbound network packets pass through an **Outbound Leak Interceptor** that inspects payloads against vault secret hashes before transmission. Across 11 representation boundaries under 8 failure modes, **0 raw secrets leaked**.

### 6. What is `value_ref`?
**Answer:** `value_ref` is an indirection token (e.g. `"user_profile.pan"` or `"user_profile.password"`). The remote model is only allowed to return the symbolic reference key. The client-side `LocalVault` securely resolves this key to the actual string in local memory and types it directly into the local browser DOM via Playwright. The raw secret never enters the model context or prompt payload.

### 7. What if a malicious webpage injects adversarial instructions?
**Answer:** The local `ScreenGraph` parses webpage content and tags untrusted DOM nodes (`untrusted_source=True`). Actions originating from or redirecting to untrusted external URLs are intercepted at the **Local Policy Engine boundary**. The policy engine classifies unauthorized exfiltration or destructive clicks as `HIGH RISK / DENIED` and halts execution fail-closed (15/15 injection attacks blocked in tests).

### 8. What happens if the model chooses the wrong element?
**Answer:** First, the action space is constrained to $k=5$ locally verified candidates, preventing random out-of-bounds clicks. Second, the **Selective Visual Crop Verifier** cross-examines ambiguous targets before dispatch. Third, if an action fails post-condition verification, the agent captures a fresh DOM snapshot, re-indexes candidates, and triggers fresh reasoning rather than looping blindly (0% repeated-target loops).

### 9. What happens if the DOM mutates between candidate generation and execution?
**Answer:** PrivateEye enforces **Local Reference Validation**. Every candidate maintains a cryptographic element hash and geometric bounding box. Before Playwright dispatches an action, the client verifies that the element is still attached, visible, and semantically consistent. If the element is stale, dispatch halts, triggering a fresh DOM snapshot.

### 10. What happens when Playwright execution fails or throws a browser error?
**Answer:** Execution errors are caught by the runtime and classified (e.g. `stale_ref`, `network_delay`, `no_progress`). Non-destructive transient errors trigger local recovery routines (refetching, spinner debounce). Unrecoverable errors trigger safe abstention (`ASK_USER`) without corrupting application state.

### 11. What happens when the local VLM server times out or hangs?
**Answer:** The client enforces an explicit 15-second request timeout. If Ollama fails to respond within this deadline, the request is aborted, categorized as `model_timeout`, and the fail-closed policy immediately aborts the turn to prevent partial or unverified state mutations.

### 12. What exactly does "fail-closed" mean in PrivateEye?
**Answer:** "Fail-closed" means that in the presence of uncertainty, low confidence, policy ambiguity, unmapped references, or component errors, the system defaults to **halting and abstaining**, rather than attempting an unverified action. The agent never executes an action unless policy, confidence, and grounding verifiers explicitly pass.

### 13. What exactly does the emergency kill switch stop?
**Answer:** The kill switch engages an atomic runtime flag that immediately closes the execution dispatch gate. It blocks any pending or subsequent Playwright dispatches, cancels active model inference, releases vault locks, and writes an immutable audit record conforming to OWASP Agent Control Standards. Controlled dispatch-path latency is measured at **0.031–0.043 ms**.

### 14. Why is step accuracy (98.46%–98.79%) higher than task completion (86.0%–89.0%)?
**Answer:** Because end-to-end task completion is governed by compounding multi-step survival. A single failed critical transition terminates the entire workflow. In an independent 20-step workflow, $(0.9879)^{20} \approx 78.36\%$, closely matching empirical survival (78.12%). Action accuracy measures single-turn precision; task completion measures full-trajectory integrity.

### 15. Why does performance degrade on long-horizon workflows (63.33% held-out vs 100% short)?
**Answer:** Our hazard rate sensitivity analysis reveals that the per-step hazard rate remains stationary at **~1.42%** across steps 6–20. Degradation is driven by accumulated risk across 20 consecutive state transitions and real-world environmental friction (asynchronous DOM delays, complex modal cascades) rather than cognitive memory amnesia or hallucination.

### 16. Is the 20/20 OSWorld benchmark result official?
**Answer:** **No.** PrivateEye achieved 20/20 on a **20-task OSWorld-derived diagnostic subset under our documented adapted protocol**. We do not claim an official OSWorld benchmark ranking or official leaderboard submission; the evaluation serves as an external architectural diagnostic verifying multi-step desktop/browser workflow capabilities.

### 17. Does "0 detected secret leaks" mean mathematically guaranteed privacy?
**Answer:** **No.** We state: *"0 detected secret leaks across tested boundaries, synthetic credentials, and adversarial failure conditions."* This is an empirical measurement across our extensive invariant test suite, not a formal mathematical proof of zero risk across all arbitrary web pages.

### 18. How many distinct websites and workflows were evaluated?
**Answer:** 
- Development Suite: 25 distinct workflows across 25 multi-domain web applications × 4 repetitions = **100 runs** (911 steps).
- Held-Out Validation: 50 frozen workflow patterns across 8 unseen domains × 2 repetitions = **100 runs** (912 steps).
- Total evaluated: **200 full end-to-end workflow executions** encompassing 1,823 action steps.

### 19. Why should judges trust this benchmark data?
**Answer:** Because every figure is backed by reproducible, frozen JSON artifacts that are verified mechanically by [`eval/final_metric_validator.py`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/eval/final_metric_validator.py) (23/23 checks pass). All evaluation scripts, manifests, and raw run records are included in the repository and reproduce with a single command.

### 20. What fundamentally makes PrivateEye different from other browser agents?
**Answer:** Standard browser agents treat the VLM as an **unrestricted autonomous actor** that receives raw screens and directly controls the mouse and keyboard. PrivateEye treats the VLM as an **untrusted reasoning advisor**:
1. Visual context is sanitized before reaching the model.
2. Candidate choices are constrained locally to $k=5$ verified DOM nodes.
3. Protected credentials remain in a client vault and are referenced symbolically.
4. An authoritative policy gate and hardware-independent kill switch stand between model output and browser execution.

### 21. How could this architecture scale to enterprise deployments?
**Answer:** The architecture naturally separates into a client-side execution container (holding user credentials and Playwright) and a private enterprise model inference cluster. The network payload between them contains only sanitized screenshots and symbolic tokens—guaranteeing enterprise data privacy even across shared infrastructure.

### 22. What would you build or improve with six more months of research?
**Answer:** 
1. **Dynamic Checkpoint Rollback:** Implement browser session snapshotting to rewind DOM state upon post-condition failure rather than aborting.
2. **Compact Specialized Grounding Heads:** Train a dedicated 0.5B vision grounding head to eliminate visual crop latency.
3. **Formal Verification of Policy Gates:** Mechanically verify policy invariant predicates using SMT solvers.

### 23. What is the single biggest remaining technical risk?
**Answer:** Multi-step resilience on unstructured, dynamic single-page applications with unpredictable asynchronous state delays. While step accuracy is 98.46%, compounding step risks reduce long-horizon completion to 63.33% on held-out tasks.

### 24. What is the strongest piece of evidence that your architecture works?
**Answer:** **Generalization under independent held-out evaluation.** When evaluated on 50 completely unseen workflow patterns across 8 new domains, PrivateEye maintained **98.46% step accuracy** (matching the 98.79% development score within 0.33 pp), achieved an **actions-to-completion ratio of 1.000**, and maintained **0 detected secret leaks** and **0 repeated loops**.
