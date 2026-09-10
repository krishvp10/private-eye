# PrivateEye Frozen System Architecture (v1.0-RC)

```
                         ┌───────────────┐
                         │   USER GOAL   │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │ LOCAL OBSERVATION   │
                    │ Screenshot + ARIA   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ LOCAL PRIVACY GATE   │
                    │ Regex + NER + Mask   │
                    └──────────┬───────────┘
                               │
                     sanitized context only
                     (Zero Raw Secrets)
                               │
                               ▼
                       ┌──────────────┐
                       │ QWEN 2.5-VL  │ (3B @ 768px, T=0.0)
                       └──────┬───────┘
                              │
                      semantic decision
                              │
                              ▼
                 ┌────────────────────────┐
                 │ LOCAL CANDIDATE ENGINE │
                 │ ARIA roles, names, DOM │
                 └───────────┬────────────┘
                             │
                           TOP-K (k=5)
                             │
                             ▼
                 ┌────────────────────────┐
                 │ SELECTIVE VERIFIER     │ (Triggered on small/ambiguous)
                 └───────────┬────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │ LOCAL POLICY ENGINE    │ (OWASP ACS 2026 Gating)
                 └───────────┬────────────┘
                             │
                             ▼
                        PLAYWRIGHT (Local Execution, Vault Dereference)
                             │
                             ▼
                      POST-CONDITION (DOM / URL Mutation Check)
                             │
                             ▼
                     PROGRESS EVALUATOR
                        ↙           ↘
                     PASS          FAIL
                                    │
                             FRESH REASONING
```

### Cross-Cutting Controls
1. **Fail-Closed Runtime:** Any component failure halts execution safely (`DO_NOT_TRANSMIT`, `SAFE_STOP`).
2. **Emergency Kill Switch:** Thread-safe, microsecond interrupt (<5ms) blocking all subsequent actions.
3. **Action Provenance:** Auditable record answering 'Why did PrivateEye perform this action?'
4. **Local Vault Dereference:** Sensitive form fills pass `value_ref` tokens over the wire; raw secret dereference is local.
