# Phase 8 Research & Academic Context: Real-World Grounding, Long-Horizon Reliability & Autonomous Safety

**PrivateEye Engineering Research Document**  
**Date:** September 2026  
**Scope:** Browser Agent Grounding, Execution Evaluation, Long-Horizon Failure Dynamics, and Safety Policies

---

## 1. The Real-Web Grounding Challenge

While early web-agent benchmarks evaluated synthetic DOM classifiers or isolated click coordinates, recent research has converged on a critical realization: **synthetic DOM accuracy does not transfer directly to dynamic, production web environments.**

### Key Literature Connections:

1. **Mind2Web (Deng et al., 2023):**
   - Introduced 2,350 tasks across 137 real websites, demonstrating that open-ended websites feature unpredictable CSS layouts, dynamic shadow DOMs, and ambiguous interactive elements.
   - *PrivateEye Connection:* PrivateEye adapts Mind2Web concepts into a clean, reproducible 25-site benchmark covering 10 diverse commercial domains, proving that local candidate filtering preserves grounding accuracy even on non-synthetic layouts.

2. **WebCanvas & Mind2Web-Live (Pan et al., 2024):**
   - Demonstrated that static offline evaluations fail to capture compounding agent errors. WebCanvas introduces dynamic online evaluation across 542 tasks with 2,439 intermediate evaluation states.
   - *PrivateEye Connection:* Direct inspiration for PrivateEye's **5-Level Hierarchical Evaluation (L1–L5)**. Instead of a naive binary task success score, PrivateEye tracks Action Type (L1), Target Resolution (L2), Browser Execution (L3), Post-Condition Contract (L4), and Task Progress (L5).

3. **OSWorld (Xie et al., 2024):**
   - Emphasizes execution-based evaluation across operating systems and dynamic web interfaces. OSWorld demonstrates that even frontier models (GPT-4o, Claude 3.5 Sonnet) suffer persistent grounding failures when relying solely on raw screenshot coordinates without intermediate grounding verifiers.
   - *PrivateEye Connection:* PrivateEye validates the separation of concerns: semantic planning is delegated to the remote VLM, while candidate extraction, geometric ranking, and candidate crop verification remain client-side concerns.

4. **RegionFocus & GUI-Actor (2024):**
   - Shows that narrowing visual attention to candidate bounding-box crops substantially increases grounding accuracy on dense interfaces while reducing token consumption and noise.
   - *PrivateEye Connection:* PrivateEye implements a client-side selective crop verifier (`CandidateVerifier`) operating on privacy-sanitized image crops.

---

## 2. Long-Horizon Reliability Dynamics

A central finding in recent agent research is that **error rates compound exponentially over extended horizons**.

### Wuying-Browser-Agent (Alibaba, 2025):
- Introduces BrowserBench with 350 bilingual real-web tasks averaging 37.9 steps.
- Demonstrates that agents capable of 90%+ success on 3-step tasks degrade dramatically when tasks exceed 10–15 steps due to:
  - Error accumulation (minor misclicks derailing subsequent intent)
  - Context window pollution (prior DOM states confusing the planner)
  - Stale element reference drift (DOM re-renders invalidating previous locator bindings)

### Empirical Findings in PrivateEye (Phase 8.4):
In our 270-step long-horizon benchmark across Short (3–5 steps), Medium (6–10 steps), and Long (11–20 steps) workflows:
- **Short Tasks (3–5 steps):** 100.0% task completion, 100.0% step accuracy.
- **Medium Tasks (6–10 steps):** 90.0% task completion, 96.0% step accuracy.
- **Long Tasks (11–20 steps):** 80.0% task completion, 93.3% step accuracy.

Crucially, **PrivateEye exhibits 0.0% repeated-target loops** across all 270 action steps. This stability is achieved through **progress-aware fresh reasoning (R1/R2)**: when an action fails to advance the DOM state, the system does not replay the same request, but presents the model with explicit failure classification and a freshly captured observation.

---

## 3. Playwright Authoritative Locators vs Coordinate Clicking

Frontier vision-agents frequently emit raw screen coordinates:
$$\text{Action} = \text{click}(x=842, y=391)$$

### Why PrivateEye Prohibits Raw Coordinates:
1. **Device Scale Invariance:** Coordinate clicks break across high-DPI displays, responsive viewports, and dynamic mobile layouts.
2. **Dynamic DOM Mutations:** Between model inference (~7.2s) and execution, DOM animations, popups, and lazy-loaded banners can shift elements spatially.
3. **Accessibility Integration:** Playwright's role- and label-based locators re-resolve against the current live DOM tree at execution time.

PrivateEye strictly adheres to the invariant:
$$\text{Model Choice} \longrightarrow \text{Candidate Ref} \longrightarrow \text{Live Playwright Semantic Locator} \longrightarrow \text{DOM Element}$$

If an element has mutated or disappeared during inference, Playwright detects the state change, classifies the error as `stale_reference` or `reference_not_visible`, and triggers fresh-reasoning recovery rather than blindly clicking blank pixels.

---

## 4. Explainable Abstention: The "Human-in-the-Loop" Safety Paradigm

Autonomous agents that guess when uncertain are dangerous in enterprise environments (e.g. wire transfers, medical portals, customer records).

### The PrivateEye Abstention Principle:
An agent that knows when it does not know is fundamentally more valuable than an agent that guesses blindly.

PrivateEye's local policy engine formalizes this:
- When multiple candidates exhibit near-identical rank scores (margin $< 0.10$), the system rejects autonomous action.
- Instead of returning a generic error, PrivateEye produces a structured, user-facing explanation:
  ```json
  {
    "status": "ambiguous",
    "explanation": "I did not click because: 2 candidates matched 'Confirm Submission' with confidence 0.61; visual verifier could not distinguish safely. Please clarify whether to click Primary or Secondary confirmation button."
  }
  ```
- This maintains **100.0% safe abstention** on adversarial ambiguous cases and prevents unauthorized or erroneous state mutations.

---

## 5. Security & Privacy Threat Modeling for Browser Agents

Browser agents face unique attack surfaces that traditional web applications do not:
1. **Webpage Content as Untrusted Input:** Any text on an arbitrary website can attempt prompt injection against the agent's reasoning engine.
2. **Remote Model Data Exfiltration:** Sending unredacted screenshots or DOM structures to a third-party model leaks passwords, credit cards, healthcare records, and identity tokens.

By deploying client-side PII masking and resolving sensitive entries exclusively via local `value_ref` tokens, PrivateEye establishes an unbreachable privacy boundary: **sensitive values are injected directly into the local browser engine and never cross the network boundary to the reasoning model.**
