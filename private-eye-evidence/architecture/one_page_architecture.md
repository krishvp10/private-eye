# PrivateEye One-Page Architecture

```
                    USER GOAL
                        ↓
             LOCAL PRIVACY BOUNDARY
          (PII detection, NER, redaction)
                        ↓
           SAFE VISUAL/SEMANTIC CONTEXT
       (Redacted screenshot, safe screen graph)
                        ↓
                 QWEN 2.5-VL 3B
           (Semantic decision: action, ref)
                        ↓
        LOCAL CANDIDATE/POLICY VALIDATION
   (Top-k candidate grounding, local policy gate,
      human confirmation for high-risk actions)
                        ↓
                    PLAYWRIGHT
     (Local execution, vault value_ref dereference)
                        ↓
                  POST-CONDITION
           (DOM/URL state mutation check)
                        ↓
               RECOVERY / ABSTENTION
   (Fresh reasoning on fault, safe stop on ungroundable)
```

---

## Architectural Principles & Boundaries

1. **Remote Multimodal Reasoning Constrained Locally:**
   The remote/local vision-language model (Qwen2.5-VL-3B) provides semantic high-level intent, but **cannot directly click or type raw values**. Every action must bind to an executable local candidate identified by Playwright and vetted by the deterministic local policy engine.

2. **Zero Raw Secret Transmission:**
   Sensitive form credentials reside entirely in the local vault. Models receive symbolic tokens (`value_ref="vault:stripe_key"`). Raw secret values are resolved locally in memory by Playwright right before dispatch.

3. **Deterministic Fail-Closed Policy:**
   Any unhandled exception, missing reference, policy violation, or ambiguous target fails closed (`SAFE_STOP`). Silent mock fallbacks are strictly banned.

4. **Microsecond Dispatch-Path Emergency Stop:**
   The kill switch halts execution on the thread-safe dispatch boundary (measured local latency: **0.043 ms** in controlled testing) with 0 subsequent actions recorded.

5. **Fresh Reasoning Recovery vs. Blind Retries:**
   Upon an execution or post-condition failure, PrivateEye captures a fresh DOM state and re-invokes candidate generation rather than looping on stale element handles.
