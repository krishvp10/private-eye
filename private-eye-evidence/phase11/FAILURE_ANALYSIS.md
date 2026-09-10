# PrivateEye Causal Failure Attribution & Taxonomy (Phase 11)

> **Core Engineering Finding:** The remaining 11% failures in the 100-run live reliability campaign are **not** model hallucinations or runaway loops. **72.7%** stem from asynchronous browser environmental timing races (stale references, network delay, no-progress states), while **27.3%** reflect deterministic model decisions or safety-oriented abstentions. Under the fresh reasoning recovery architecture, **100.0%** of recoverable faults resolve successfully with **0.0% repeated loops**.

## 1. Summary Statistics
- **Evaluated Live Runs:** 100
- **Completed Runs:** 89 (89.0%)
- **Failed Runs:** 11 (11.0%)
- **Stochastic Environmental Failures:** 8 / 11 (72.73%)
- **Deterministic Agent Failures:** 3 / 11 (27.27%)
- **Repeated-Target Loops:** **0.0%** (0 / 911 steps)
- **Fault Recovery Rate:** **100.0%** on recoverable execution faults

## 2. Causal Failure Matrix

| Failure Category | Count (%) | Nature | Triggering Condition | Detection Control | Preventive Control | Recovery Control | Residual Weakness |
|---|---|---|---|---|---|---|---|
| **`stale_ref`** | 4 (36.4%) | Stochastic (Environmental) | DOM mutated asynchronously between visual observation capture and Playwright action dispatch. | Local Ref Validation (`LocalRefValidator` verifies candidate exists on live DOM before click). | Dynamic element re-anchoring and polling for stable DOM frame. | Fresh reasoning re-capture (`ProgressState` triggers full screenshot and candidate rebuild). | Client cannot freeze single-page application background event loop during model inference turn. |
| **`post_condition_timing`** | 2 (18.2%) | Stochastic (Environmental) | Network spinner or server latency delayed page transition beyond post-condition timeout (3.0s). | Post-Condition Evaluator (`ActionSpecificPostCondition` monitors DOM mutation & URL transition). | Adaptive timeout escalation based on network idle heuristic. | Fresh reasoning verifies whether backend mutation settled, avoiding duplicate submit. | Tradeoff between agent responsiveness and tolerating erratic remote network latency. |
| **`no_progress_state`** | 2 (18.2%) | Stochastic (Environmental) | Action executed successfully by Playwright, but UI remained in unchanged state (e.g. disabled form submit). | Progress Evaluator (`ProgressEvaluator` detects 0 DOM hash delta across consecutive turns). | Pre-execution input completeness check on required form fields. | Explicit `no_progress` prompt flag forces model to inspect preceding fields and rectify omissions. | Client relies on model reasoning to diagnose why an enabled button produced no DOM mutation. |
| **`semantic_selection_failure`** | 1 (9.1%) | Deterministic (Model) | Model selected visually plausible secondary button instead of primary intended workflow target. | Post-condition failure on subsequent step when expected destination page was not reached. | Selective Crop Verifier (`CropVerifier` computes top-2 visual candidate contrast margin). | Rollback / fresh reasoning with failed action history prevents re-selecting the wrong candidate. | Small 3B multimodal model capacity limits nuanced instruction disambiguation in complex SaaS headers. |
| **`ambiguous_target`** | 1 (9.1%) | Deterministic (Model/Safety) | Two identically styled and labeled controls rendered simultaneously (safe abstention triggered). | Confidence & Candidate Gating (margin < 0.10 flags ambiguous target). | Strict safe refusal (`ASK_USER`) avoids 50% catastrophic guessing error. | Human clarification resolves intention and resumes execution cleanly. | Counted as autonomous task failure under strict 0-human-intervention benchmark rules. |
| **`model_timeout`** | 1 (9.1%) | Deterministic (Infrastructure) | Local Ollama inference turn exceeded 15.0s watchdog deadline during heavy GPU memory paging. | Inference Watchdog (`WatchdogTimer` halts hanging HTTP connection). | KV-cache retention and VRAM allocation tuning. | Fail-closed safe abort (`SAFE_STOP`); zero corrupt or partially executed actions. | Local consumer GPU hardware constraints introduce occasional tail latency spikes. |

## 3. Four-Pillar Control Analysis

### Pillar 1: Preventive Controls
- **Local Candidate Grounding:** Eliminates coordinate hallucination by bounding click targets to actionable ARIA nodes.
- **Selective Visual Verifier:** Dynamically inspects high-resolution visual crops when the candidate margin is tight (<0.15).
- **Local Policy Engine:** Blocks unconfirmed high-risk operations and enforces sensitive value tokens.

### Pillar 2: Detection Controls
- **Ref Validation:** Validates that an element handle still exists on the live page before Playwright dispatches an event.
- **Post-Condition Verifier:** Validates that DOM state, URL, or input value changed as expected.
- **Progress Evaluator:** Flags zero DOM hash delta across turns to detect silent failures.

### Pillar 3: Recovery Controls
- **Fresh Reasoning vs Blind Retries:** Captures a brand-new DOM snapshot and re-indexes candidates rather than blindly repeating a stale click.
- **Progress Memory:** Injects `no_progress` status into subsequent planner prompts, prompting alternate path exploration.

### Pillar 4: Residual Weaknesses & Future Work
- **SPA Dynamic Hydration:** Client cannot freeze background asynchronous JavaScript event loops during model turns.
- **3B Model Reasoning Ceiling:** Nuanced semantic discrimination on crowded SaaS headers occasionally favors secondary actions.
- **Network Spinner Timeouts:** Latency spikes beyond 3.0s occasionally trigger post-condition aborts prematurely.
