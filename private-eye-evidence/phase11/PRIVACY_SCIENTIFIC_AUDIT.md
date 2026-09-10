# PrivateEye Scientific Privacy & PII Detection Audit (Phase 11)

> **Methodological Principle:** We explicitly separate **End-to-End Leak Prevention** (a systems-level architectural property) from **Local PII Detector Quality** (a statistical classification task). A critical insight of PrivateEye is that client privacy does **not** rely solely on an infallible classifier: the **local vault tokenization boundary** (`value_ref`) guarantees that credentials never touch the remote model context.

## 1. Dimension A: End-to-End Privacy Boundary Invariant
- **Evaluated Surfaces:** 11 Representation Boundaries
- **Synthetic Credentials:** 21 Active Vault Secrets
- **Active Failure Modes:** 8 Stress Scenarios (detector crash, redaction timeout, network drop)
- **Detected Raw Secret Leaks:** **0 Leaks** (`100% leak-free within tested scope`)

| Boundary Surface | Scanned Artifacts | Detected Leaks | Status |
|---|---|---|---|
| 1. Raw Screenshot | 100 | **0** | `PASS` |
| 2. Redacted Image | 100 | **0** | `PASS` |
| 3. ScreenGraph Export | 100 | **0** | `PASS` |
| 4. Candidate Metadata | 500 | **0** | `PASS` |
| 5. Marked Candidate Image | 100 | **0** | `PASS` |
| 6. Selective Visual Crops | 150 | **0** | `PASS` |
| 7. Planner Model Prompt | 100 | **0** | `PASS` |
| 8. Verifier Model Prompt | 100 | **0** | `PASS` |
| 9. Model Raw Response | 100 | **0** | `PASS` |
| 10. Telemetry & Audit Logs | 578 | **0** | `PASS` |
| 11. Action Provenance Chain | 100 | **0** | `PASS` |

## 2. Dimension B: Local PII Detector Quality
- **Diagnostic Corpus:** 400 Annotated Form Fields
- **Precision:** **95.92%** (188/196)
- **Recall:** **94.0%** (188/200)
- **F1 Score:** **94.95%**
- **False Positive Rate (Overmasking):** **4.0%** (8/200)
- **False Negative Rate (Undermasking):** **6.0%** (12/200)

### Architectural Implication: Defense-in-Depth
- A conventional agent streaming raw DOM to a cloud LLM depends 100% on detector recall ($FNR = 0\%$).
- PrivateEye decouples this: even if a visual detector misses an input field (6.0% FNR), the local Playwright execution engine **refuses to dispatch raw string literals without a registered vault token**.
- Result: 0 detected secret leaks across all live runs and failure scenarios.
