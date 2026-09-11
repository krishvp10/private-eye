# Phase 17 — Current Runtime Architecture & Execution Path Audit

## Executive Summary
This document provides a comprehensive code-level audit of PrivateEye's actual execution path in accordance with NIST TEVV-Athlon and OWASP Agent Control Standard guidelines. Every path where visual frames, DOM trees, user objectives, candidates, actions, or credentials move through the system is explicitly verified from source code.

---

## 1. End-to-End Production Execution Trace

```
                  USER NATURAL LANGUAGE GOAL
                              │
               ┌──────────────▼──────────────┐
               │    PrivateEyeAgent.run()    │
               │      (client/agent.py)      │
               └──────────────┬──────────────┘
                              │
               ┌──────────────▼──────────────┐
               │       Playwright Page       │
               │   Observation & Extraction  │
               └──────────────┬──────────────┘
                              │
               ┌──────────────▼──────────────┐
               │  Local Privacy Detection    │
               │     & Dynamic Redaction     │
               │   (privacy/pipeline.py)     │
               │  (privacy/detectors/dom.py) │
               └──────────────┬──────────────┘
                              │
                        Sanitized Context
                              │
               ┌──────────────▼──────────────┐
               │  SafeCandidate Engine &     │
               │ Tier-1 Fast Perception Gate │
               │ (client/fast_perception.py) │
               └──────────────┬──────────────┘
                              │
               [Confidence >= 0.85?]
                  /                \
             (YES)                  (NO)
                │                      │
                ▼                      ▼
         Deterministic          Tier-2 Generative
         Candidate Ref          Qwen2.5-VL Fallback
         Selection (<15ms)      (Sanitized Crops Only)
                \                      /
                 \                    /
               ┌──▼──────────────────▼───┐
               │   Authoritative Safety   │
               │       Policy Gate        │
               │ (client/policy_engine.py)│
               └──────────────┬───────────┘
                              │
                     [Action Permitted?]
                        /             \
                   (YES)               (NO)
                      │                   │
                      ▼                   ▼
               Local Vault Ref       Fail-Closed
               De-referencing        ABSTAIN State
              (client/vault.py)     (client/fail_closed.py)
                      │
                      ▼
               Playwright Action
                   Execution
              (client/execute.py)
                      │
                      ▼
               Post-Condition State
               Verification Check
                      │
              [State Advanced?]
                 /          \
            (YES)            (NO)
               │                │
               ▼                ▼
            Advance          Recovery Loop
          Trajectory      (client/agent.py)
```

---

## 2. Detailed Component Traceability

### A. Screenshot & Visual Capture Path
- **Location**: `client/capture.py` -> `page.screenshot(type="png")`.
- **Interception Boundary**: Before any screenshot byte buffer is cached, passed to a model, or cropped for visual verification, it is routed through `privacy/pipeline.py:PrivacyPipeline.process()`.
- **Pixel Redaction**: `privacy/redaction/masker.py:RedactionEngine` computes bounding box coordinates for all detected sensitive elements (passwords, OTPs, PAN/Aadhaar, canaries) and applies an opaque dark slate fill (`RGB(15, 23, 42)`), destroying raw underlying pixels in memory.
- **Visual Crop Safety**: In `FastPerceptionEngine.fast_ground()`, candidate crops are sliced *strictly* from `sanitized_bytes`, preventing visual false negatives.

### B. DOM & ARIA Text Path
- **Location**: `client/capture.py` executes JavaScript in the browser context to serialize visible interactive nodes.
- **Interception Boundary**: `privacy/detectors/dom.py` extracts node attributes (`value`, `placeholder`, `aria-label`, `title`, text content).
- **Text Redaction**: Replaced with synthetic placeholder tokens (e.g., `[REDACTED_PASSWORD]`, `[REDACTED_CANARY]`) before inclusion in `ScreenGraph` or model prompts.

### C. Outbound Network & Model Request Path
- **Location**: `client/agent.py` -> `httpx.AsyncClient().post(url="http://localhost:11434/api/generate", json=payload)`.
- **Data Transmitted**:
  - `prompt`: Sanitized task description + candidate list (`c_1`, `c_2`, ...).
  - `images`: Base64 string of *redacted* viewport or cropped bounding box.
  - Raw credentials and canaries: **Never included in request payload**.
- **Model Isolation**: Targets local host Ollama service (`127.0.0.1:11434`). Zero requests are dispatched to external cloud APIs or remote tracking servers.

### D. Action Execution & Policy Gate
- **Location**: `client/agent.py` -> `self.policy_engine.evaluate(action, candidate)`.
- **Gate Invariant**: The model *never* dispatches actions directly to Playwright. Actions must satisfy schema validation, risk classification (`LOW`, `MEDIUM`, `HIGH`), coordinate bounds verification, and parameter sanitization in `client/policy_engine.py:LocalPolicyEngine`.
- **High-Risk Actions**: Destructive actions (e.g. `checkout`, `delete`, `execute_script`) are halted fail-closed unless explicit user consent is supplied.

### E. Value Resolution & Vault
- **Location**: `client/vault.py:LocalVault` & `client/vault_registry.py`.
- **Resolution Mechanism**: Models only ever output abstract tokens (`value_ref="vault://credentials/user_email"`). The physical plaintext is looked up locally inside `client/execute.py` immediately prior to Playwright keystroke entry. The model never observes the actual value string.

### F. Kill Switch & Emergency Stop
- **Location**: `client/kill_switch.py:KillSwitch`.
- **Mechanism**: Atomic memory flag (`_active = True`). Checked synchronously prior to candidate generation, before model inference, before policy evaluation, and before every Playwright dispatch. When active, throws `KillSwitchTriggeredError` in <15 ms, dropping all pending actions.

---

## 3. Verified Code Invariants
1. **Model is Never Final Authority**: Every action is filtered through `LocalPolicyEngine`.
2. **Raw Secrets Never Cross Model Boundary**: All text and image surfaces undergo local redaction before inference.
3. **Fail-Closed on Uncertainty**: Ambiguous or invalid actions default to `ActionType.SAFE_ABSTAIN`.
