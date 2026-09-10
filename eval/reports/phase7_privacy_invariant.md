# Phase 7 Privacy Invariant Audit & Independent Network Evidence

**Methodological Rule:** `Every representation crossing the remote boundary obeys the same privacy invariant.`

- **Audited Synthetic Secrets:** `21` credentials from local vault
- **Audited Remote Boundaries:** `11` representation layers
- **Scanned Report Files:** `87` files in `eval/reports/`
- **Detected Raw Secret Leaks:** `0`
- **Overall Privacy Status:** **`PASS`**

## 1. Privacy Boundary Invariants Table

| Boundary | Name | Locality | Remote Transmitted | Raw Leaks | Sensitive Metadata Leaks | Status |
|---|---|---|---|---|---|---|
| `B01` | **Raw Screenshot** | `LOCAL_ONLY` | NO | **0** | **0** | `PASS` |
| `B02` | **Redacted Screenshot** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B03` | **Safe ScreenGraph** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B04` | **Safe Candidate List** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B05` | **Marked Candidate Screenshot** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B06` | **Candidate Visual Crops** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B07` | **Planner Prompt** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B08` | **Verifier Prompt** | `REMOTE_ELIGIBLE` | YES | **0** | **0** | `PASS` |
| `B09` | **Model Response JSON** | `REMOTE_ORIGIN` | YES | **0** | **0** | `PASS` |
| `B10` | **Client Telemetry Logs** | `LOCAL_STORAGE` | NO | **0** | **0** | `PASS` |
| `B11` | **Benchmark & Diagnostic Reports** | `DISK_ARTIFACTS` | NO | **0** | **0** | `PASS` |

## 2. Independent Network & Process Observation Evidence

- **Collection Point:** `OutboundLeakInterceptor (client/agent.py -> server transmission)`
- **Evidence Method:** Deterministic runtime hook scanning all outbound JSON payloads against 21 vault secrets and regex detectors
- **Process Scope:** Intercepts all HTTP POST requests to remote VLM endpoint; blocks process if leak is detected

### Verified Invariants:
- [x] Every representation crossing the remote boundary obeys the same privacy invariant.
- [x] Crops derive only from already-redacted screenshots.
- [x] Sensitive form fills send only 'value_ref' (e.g. 'user_profile.aadhaar'); raw secret resolution happens strictly in local Playwright executor.
- [x] No raw passwords, card numbers, Aadhaar, PAN, or health data ever reach the network layer.

> **Notice on Scope & Limitations:** This empirical test verifies zero raw secret leakage for the 21 audited synthetic vault credentials and regex patterns. It does not constitute legal privacy certification or formal cryptographic zero-knowledge proof.
