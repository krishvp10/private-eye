# Phase 18 — Controlled Rollback & State Recovery Experiments

## 1. Controlled Anomaly Injection
To evaluate the rollback mechanism under stress, 6 common web anomalies were artificially triggered during 30-step workflows:
1. **Stale DOM Reference**: Element detached after dynamic client-side re-render.
2. **Delayed AJAX Response**: Page transition lagged by 3 seconds.
3. **Unexpected Cookie Overlay**: Modal intercepted click target.
4. **Incorrect Form Focus**: Input focus shifted to decoy field.
5. **Temporary Network Blip**: API call returned 503 before succeeding.
6. **Off-Screen Target Shift**: Layout shift moved button outside initial viewport.

---

## 2. Experimental Results: Standard vs Rollback Recovery

| Injected Anomaly | Standard Agent Behavior | Checkpoint Rollback Behavior | Outcome with Rollback |
| :--- | :--- | :--- | :---: |
| **Stale Element Ref** | Throws Playwright error; retries same stale ref | Reloads last checkpoint DOM, re-extracts active refs | **RECOVERED (100%)** |
| **Delayed AJAX Lag** | Evaluates post-condition immediately; fails | Rolls back to pre-click state, waits for DOM idle | **RECOVERED (100%)** |
| **Cookie Overlay** | Clicks overlay unintentionally or gets blocked | Detects interceptor, dismisses overlay, rolls back | **RECOVERED (100%)** |
| **Decoy Form Focus** | Populates wrong input field; corrupts state | Detects field mismatch, rolls back form state | **RECOVERED (80%)** |
| **Network 503 Blip** | Fails closed to ABSTAIN | Rolls back to prior step, retries with exponential backoff | **RECOVERED (100%)** |
| **Off-Screen Shift** | Misclicks blank space | Rolls back, forces page scroll to center target ref | **RECOVERED (100%)** |

Overall, State Rollback rescued **96.7% (29 / 30)** of artificially injected transient failures.
