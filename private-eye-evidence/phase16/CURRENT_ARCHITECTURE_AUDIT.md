# Phase 16: Complete Codebase Architecture Audit

## Executive Summary
This document provides an exhaustive, code-verified audit of PrivateEye's current production execution path on branch `phase16-real-world-validation`. It establishes exact locations for screenshot capture, privacy boundaries, network egress, policy authorization, Playwright execution, value_ref resolution, and kill-switch checks.

---

## 1. End-to-End Runtime Execution Path

The authoritative execution loop is anchored in [`client/agent.py: PrivateEyeAgent.run()`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/agent.py):

```
                        [ Browser Page ]
                               │
                               ▼ (Playwright CDP)
                     capture_page(page) ────────► Returns Screenshot Bytes & DOM Elements
                               │
                               ▼
            ┌─────────────────────────────────────────┐
            │       LOCAL PRIVACY BOUNDARY            │
            │                                         │
            │  1. PrivacyPipeline.detect()            │
            │     - RegexDetector (Unicode normalized)│
            │     - DOMDetector (placeholder/aria)    │
            │  2. RedactionEngine.redact()            │
            │     - Pixel Masking (Blackout/Dark Pill)│
            │     - Sanitized ScreenGraph (no values) │
            │  3. FailClosedPolicy.evaluate_privacy() │
            └────────────────────┬────────────────────┘
                                 │ Sanitized ScreenContext only
                                 ▼
                   OutboundLeakInterceptor.assert_safe()
                                 │
                                 ▼ (HTTP POST to /v1/analyze)
                       [ VLM Reasoning Layer ]
                       (Local Ollama / Mock)
                                 │
                                 ▼ AgentAction (action, target, value_ref)
            ┌─────────────────────────────────────────┐
            │     AUTHORITATIVE EXECUTION GATE        │
            │                                         │
            │  1. Schema Validation (no raw 'value')  │
            │  2. FailClosedPolicy.evaluate_candidate()│
            │  3. LocalPolicyEngine.evaluate_policy() │
            │     - Risk Tiering (Low/Medium/High)    │
            │     - Confidence Threshold Gating       │
            │     - Irreversible Action Block         │
            │     - Symbolic Namespace Verification   │
            └────────────────────┬────────────────────┘
                                 │ Authorized action
                                 ▼
                     ActionExecutor.execute()
                                 │
                                 ▼ (Local Value Resolution via LocalVault)
                    Playwright Semantic Dispatch
                                 │
                                 ▼
                     _verify_post_condition()
                                 │
                                 ▼
                    State Transition / Recovery
```

---

## 2. Exhaustive Subsystem Mapping

### A. Screenshot Capture Points
* [`client/capture.py: capture_page()`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/capture.py):
  Captures raw PNG screenshot via `page.screenshot()` and extracts DOM elements with bounding boxes.
* **Storage Invariant**: Raw screenshot bytes exist strictly in local memory and are never written to disk or transmitted over the wire.

### B. Network Egress Points
* [`client/agent.py: line 160`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/agent.py#L160):
  Outbound `httpx.post(f"{self.server_url}/v1/analyze", content=payload)`.
  **Enforcement**: Guarded by `OutboundLeakInterceptor.assert_safe(payload)`. Payload contains base64-encoded *redacted* image bytes and sanitized `ScreenGraph` without values.
* **Audit Confirmation**: No other outbound HTTP/WebSocket network connections exist in `client/`.

### C. Policy Engine Authorization Boundary
* [`client/agent.py: lines 197–215`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/agent.py#L197-L215):
  ```python
  policy_decision = self.policy_engine.evaluate_policy(
      action=action.action,
      confidence=confidence_to_eval,
      candidate=selected_candidate,
      task=self.task,
      value_ref=action.value_ref,
      verifier_passed=not candidate_decision.ambiguous,
  )
  if not policy_decision.action_permitted:
      errors.append(f"Fail-closed policy engine blocked action: {policy_decision.reason}")
      await browser.close()
      return AgentRunResult(run_id, False, page.url, step, telemetry, errors)
  ```
* **Authorization Invariant**: Exactly one authoritative decision point exists prior to Playwright action dispatch.

### D. Sensitive Credential Isolation (`value_ref`)
* [`client/vault.py: LocalVault.resolve()`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/vault.py):
  Resolves symbolic reference tokens (`user_profile.pan`, `user_profile.password`) strictly at the client executor boundary immediately before invoking Playwright typing.
* **Network Invariant**: Server never receives or emits raw secrets; model receives only symbolic strings.

### E. Kill-Switch Mechanism
* [`client/kill_switch.py: GLOBAL_KILL_SWITCH`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/kill_switch.py):
  Evaluated at every loop turn in `client/agent.py: line 92`. If engaged, throws `KillSwitchTriggeredError`, immediately closes Playwright browser instance, and halts execution cleanly.

### F. Fast Local Perception Path
* [`client/fast_perception.py: FastPerceptionEngine`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/client/fast_perception.py):
  Two-tier architecture:
  - **Tier 1**: Deterministic DOM, ARIA, geometry bounding, privacy masking, candidate scoring (<15 ms latency).
  - **Tier 2**: Invokes Qwen2.5-VL-3B only on ambiguity, low confidence, or unanchored canvas elements.
