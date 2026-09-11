# Phase 14 Comprehensive Repository Architecture & Codebase Audit

**Audit Status:** COMPLETE  
**Audited Release:** `v1.0-RC-final` (Commit: `f689654`, Baseline: `5d697dc`)  
**Auditor Role:** Independent External Software & Security Evaluator  
**Audited Scope:** All 26 directories and production modules (`client/`, `server/`, `privacy/`, `shared/`, `eval/`, `demo/`, `tests/`)

---

## 1. End-to-End System Pipeline Mapping

```
                                  [USER GOAL / TASK]
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ CLIENT BROWSER WORKSPACE (LOCAL TRUST BOUNDARY)                                         │
│                                                                                         │
│  1. OBSERVATION:                                                                        │
│     Playwright Page ──► capture_page() ──► Screenshot Bytes + Raw DOM Elements + A11y    │
│                                                                                         │
│  2. PRIVACY PIPELINE (privacy/pipeline.py):                                             │
│     [DOM Detector] + [Regex Detector] + [NER Detector] + [Face Detector]                │
│     └──► Detections (Bounding Boxes + Categories + Text Previews)                       │
│                                                                                         │
│  3. LOCAL REDACTION ENGINE (privacy/redaction/masker.py):                               │
│     Solid Bounding-Box Overlay on Pixels + Node Text Masking on ScreenGraph             │
│     └──► Output: Sanitized Screenshot Bytes + Sanitized ScreenGraph                     │
│                                                                                         │
│  4. LOCAL CANDIDATE ENGINE (client/candidates.py):                                      │
│     Filters Sanitized ScreenGraph ──► Top-K (k=5 or k=8) SafeCandidate set              │
│                                                                                         │
│  5. LOCAL OUTBOUND LEAK INTERCEPTOR (eval/leak_check.py):                               │
│     Inspects outgoing JSON payload for raw strings matching LocalVault secrets          │
│     [AUDIT CAVEAT: Excludes image_b64 from regex scanning]                              │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ Encrypted JSON (POST /v1/analyze)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ REMOTE / HOSTED INFERENCE RUNTIME (UNTRUSTED OR SEMI-TRUSTED BOUNDARY)                  │
│                                                                                         │
│  6. SERVER VALIDATION (server/validation.py):                                           │
│     Validates payload schemas, ensures no raw secrets, parses base64 screenshot         │
│                                                                                         │
│  7. MULTIMODAL REASONING (server/vlm.py / Qwen2.5-VL-3B via local Ollama):              │
│     Input: Task + Sanitized Image (768px/1024px) + ScreenGraph + SafeCandidates         │
│     Output: Action JSON with Target Ref (`e1..ek`) and Symbolic `value_ref`              │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ Structured Action Response
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ CLIENT ACTION DISPATCH & RECOVERY RUNTIME                                               │
│                                                                                         │
│  8. FAIL-CLOSED GATE (client/fail_closed.py):                                           │
│     Validates candidate references against current screen graph candidate set           │
│                                                                                         │
│  9. LOCAL CREDENTIAL VAULT RESOLUTION (client/vault.py):                                │
│     Resolves symbolic `value_ref` ('user_profile.pan') against LocalVault in memory     │
│                                                                                         │
│ 10. ACTION EXECUTION (client/executor/execute.py):                                      │
│     Playwright locator resolution -> Attribute & name matching -> Dispatch click/fill   │
│                                                                                         │
│ 11. POST-CONDITION EVALUATION & RECOVERY (client/agent.py, client/recovery.py):         │
│     Checks URL change / DOM mutation. On failure -> Re-capture -> Fresh reasoning loop  │
│                                                                                         │
│ 12. PROVENANCE & AUDIT LOGGING (client/provenance.py):                                  │
│     Records immutable step trace (goal, candidate, decision, result) without raw secrets│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Exhaustive Component-by-Component Architectural Findings

### A. Observation & Capture Layer (`client/capture.py`)
- **Strengths:** Captures viewport geometry, device scale factor, raw DOM accessibility tree, and screenshot in a synchronized snapshot.
- **Vulnerabilities / Weaknesses Identified:**
  1. *Shadow DOM & Nested Iframes:* Does not recursively penetrate cross-origin or closed Shadow DOM trees. Elements inside complex payment iframes (e.g., Stripe, PayPal frames) are invisible to `capture_page()` unless specifically switched into via Playwright `frame_locator`.
  2. *Offscreen / Virtualized DOM Elements:* Elements outside the 1280x800 viewport or inside virtualized infinite scroll containers are not captured in the candidate graph until scrolled into view.

### B. Privacy & Redaction Subsystem (`privacy/`)
- **Strengths:** Multi-signal ensemble combining heuristic DOM attribute matching (passwords, PINs, card fields), calibrated regex patterns (Aadhaar, PAN, SSN, Phone, Email, DOB, UHID), NER, and OpenCV Haar cascades for facial detection.
- **Critical Architectural Vulnerabilities:**
  1. **Detector False Negative Leaks into `image_b64` (HIGH SEVERITY):**
     - When an adversarial secret (e.g., Unicode zero-width spaced PAN `A\u200bB\u200bC...`, split DOM strings, or novel uncalibrated tax identifiers) bypasses the regex/DOM detectors, the pixel bounding box is NOT generated.
     - The unmasked pixels are base64-encoded into `image_b64`.
     - `OutboundLeakInterceptor.inspect_payload` explicitly strips `image_b64` before regex evaluation to avoid collisions with binary base64 character sequences (`text_for_regex = re.sub(r'"image_b64"\s*:\s*"[^"]*"', '"image_b64": ""', payload_text)`).
     - **Result:** Visual secrets missed by the detector cross the network boundary directly into the VLM payload. The system does not possess mathematical zero-leak guarantees.
  2. **Lexical Regex Brittleness:** Simple character insertions or alternate formatting (`A-B-C-D-E-1-2-3-4-F` or spaces within PAN) cause regex misses.

### C. Candidate Generation & Verification (`client/candidates.py`, `client/verifier.py`)
- **Strengths:** Restricts VLM action space to $k \le 8$ (typically $k=5$) interactive candidates, mitigating arbitrary coordinate hallucination. Verifier performs crop-based visual disambiguation on twin targets.
- **Weaknesses Identified:**
  1. *Icon-Only Controls:* Buttons without text, `aria-label`, or accessible names receive rank scores near 0.0 unless the task explicitly references "icon" or "button".
  2. *Candidate Omission on Long Pages:* If an interface has 40+ interactive elements, the candidate engine truncates to top-k. If the legitimate target is ranked 9th, the VLM cannot select it.

### D. Policy Engine vs. Agent Integration (`client/policy_engine.py` vs `client/agent.py`)
- **CRITICAL ARCHITECTURAL DEFECT (HIGH SEVERITY):**
  - `client/policy_engine.py` contains a well-structured `LocalPolicyEngine` that classifies actions into `LOW`, `MEDIUM`, and `HIGH` risk tiers, enforces minimum confidence thresholds ($0.88$ for high risk), and mandates verifier passes.
  - **However, `LocalPolicyEngine` is NEVER imported or called in `client/agent.py` (`PrivateEyeAgent.run`)!**
  - In production `agent.py`, the agent calls only `FailClosedPolicy.evaluate_candidate` and passes the action directly to `ActionExecutor.execute()`.
  - `ActionExecutor` contains an internal rudimentary method `_is_destructive(action)` which checks for keywords like `["submit", "pay", "delete", "send", "confirm"]`, but its confirmation gate defaults to `require_confirmation = False` unless `PE_CONFIRM_ACTIONS=true` is manually configured.
  - **Result:** The formal `LocalPolicyEngine` risk tiering and confidence thresholds demonstrated in standalone benchmarks (`eval/fault_injection_benchmark.py`, `eval/runtime_control_and_adversarial_audit.py`) are disconnected from the primary agent loop in `client/agent.py`.

### E. Credential Vault & Value_Ref Resolution (`client/vault.py`, `shared/vault_registry.py`)
- **Strengths:** Implements strict namespace validation (`user_profile`, `auth`, `payment`, `health`). Prevents injection of code or path traversal (`../../etc/passwd` or SQL fragments raise `ValueError`).
- **Residual Risk:**
  - **Credential Misattribution:** If a prompt injection or hallucinating model requests `value_ref: "user_profile.card_number"` while targeting a benign search input (`#search_input`), `ActionExecutor` resolves the credit card from `LocalVault` and fills it into the search box.
  - The vault does not enforce semantic type binding (e.g., restricting `card_number` exclusively to fields with role `textbox` and name containing `card` or `payment`).

### F. Emergency Kill Switch (`client/kill_switch.py`)
- **Strengths:** Thread-safe in-memory flag guarded by a mutex, emitting structured JSON events conforming to OWASP ACS runtime override guidelines. Dispatch latency measured at $0.036$–$0.043$ ms.
- **Operational Scope Limitations:**
  - **What It Stops:** Subsequent iterations of `PrivateEyeAgent.run()` loop (via `GLOBAL_KILL_SWITCH.assert_not_engaged()`).
  - **What It Does NOT Stop:**
    1. Does NOT interrupt or cancel in-flight HTTP requests to the VLM server (which can take 5–30 seconds).
    2. Does NOT interrupt an in-flight Playwright browser click or page navigation once dispatched.
    3. Is NOT checked inside `ActionExecutor.execute()` before dispatching to Playwright.

### G. Demonstration Suite Realism (`demo/run_scenarios.py`)
- **Auditor Forensic Finding (MEDIUM SEVERITY):**
  - As established during code inspection of `demo/run_scenarios.py`:
    - **Scenario A:** Candidates are hardcoded python objects (`candidates = [SafeCandidate(...)]`), and Playwright actions are hardcoded script dispatches (`await page.fill(...)`, `await page.click(...)`). Neither `PrivateEyeAgent` nor `Qwen2.5-VL-3B` is invoked.
    - **Scenario B:** Context sanitization is a hardcoded dictionary, and model response is a preseeded dictionary (`model_response = {"action": "FILL", ...}`).
    - **Scenario C:** Adversarial action and policy engine rejection are simulated with synthetic dictionaries.
  - **Verdict on Demo Realism:** `demo/run_scenarios.py` is a **scripted stage simulation** demonstrating architectural invariants, NOT an autonomous agent execution. The actual autonomous agent is driven by `client/agent.py` and `eval/live_privacy_demo.py`.

---

## 3. Code Quality, State Management & Hygiene Audit

| Check Category | Findings | Severity |
|---|---|---|
| **Swallowed Exceptions** | Broad `except Exception:` blocks exist in `client/kill_switch.py` (line 78, listener notifications), `demo.py`, and `eval/trajectory_efficiency.py`. | LOW |
| **Mutable Global State** | `GLOBAL_KILL_SWITCH` in `client/kill_switch.py` is a singleton global instance. While thread-safe via `threading.Lock`, multiple sequential agent runs require manual `.reset()`. | LOW |
| **Resource Leakage** | Child processes in `demo.py` (`uvicorn`, `http.server`) use platform-specific process termination (`taskkill /F /T` on Windows). If killed abruptly via SIGKILL, orphan port bindings can persist. | LOW |
| **Timeout Robustness** | HTTP client timeout in `client/agent.py` is dynamically computed (`max(15.0, VLM_TIMEOUT + 5.0)`) preventing hang states on stalled local Ollama daemon. | PASS |
| **Path Traversal / CLI Injection** | URLs in `ActionExecutor` are strictly validated to begin with `http://` or `https://` (line 99). File paths in `vault.py` use `Path(__file__).resolve()`. | PASS |
| **Bytecode & Formatting** | Repository passes `python -m compileall` with 0 syntax errors, and `ruff check` passes cleanly. | PASS |

---

## 4. Architectural Summary for SIH Technical Defense

The architecture of PrivateEye is genuinely innovative in its **inversion of the traditional computer-use paradigm**: rather than granting an unvetted LLM direct pixel-coordinate mouse control, it bounds the agent through client-side candidate generation, local symbolic value substitution, and post-condition loop verification.

However, the team must honestly defend against the two major architectural discrepancies identified:
1. `LocalPolicyEngine` is decoupled from `client/agent.py` (relies on simpler destructive checks in `ActionExecutor`).
2. `demo/run_scenarios.py` is a scripted deterministic demonstration harness rather than a live VLM invocation.
