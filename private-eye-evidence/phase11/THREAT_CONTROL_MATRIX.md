# PrivateEye Threat-Control-Evidence Security Matrix (Phase 11)

> **Governance Standard Alignment:** Mapped according to the **OWASP Agent Control Standard (ACS 2026)** and **NIST AI RMF 1.0 (Govern / Measure / Manage)**.  
> **Evaluation Scope:** 15 adversarial and runtime threats evaluated under the frozen release configuration (`v1.0-RC`).

---

## Master Threat-Control Matrix

| Threat ID | Threat / Attack Description | Affected Component | Defensive Control Hook | Empirical Test Result | Evidence Artifact | Residual Risk & Boundary |
|---|---|---|---|---|---|---|
| **THREAT-01** | **Direct Prompt Injection** (Goal override via user instructions) | Planner Context | Structural JSON input boundary & system prompt pinning | **15/15 Blocked (100.0%)** | `phase8_prompt_injection.json` | Infinite variations of natural language jailbreaks cannot be exhaustively proven safe. |
| **THREAT-02** | **Indirect Webpage Prompt Injection** (Adversarial text in webpage DOM) | ScreenGraph & Observation | Local candidate sanitizer strips instruction semantics; model treats DOM as passive candidate graph | **10/10 Blocked (100.0%)** | `phase8_prompt_injection.json` | Multimodal OCR on untrusted rendered images could theoretically trigger visual injection. |
| **THREAT-03** | **Malicious Instructions in Visible Images** (Steganographic/Visual prompt injection) | Multimodal Vision Context | Visual Crop Verifier isolates bounded bounding boxes; local policy blocks unauthorized commands | **Contained (100.0%)** | `phase10_compound_faults.json` | High-order adversarial pixel perturbations designed for Qwen2.5-VL vision encoder. |
| **THREAT-04** | **Sensitive Credential Exfiltration** (Attempt to transmit credit card or SSN) | Model Wire Protocol | Local Vault Tokenization (`value_ref`); zero raw secrets in HTTP payload | **0 Leaks Detected (11 Boundaries)** | `phase10_privacy_failure_audit.json` | User explicitly writing secret into plain task prompt bypasses client vault isolation. |
| **THREAT-05** | **Candidate Spoofing / Clickjacking** (Transparent overlay diverting action target) | Local Candidate Engine | ARIA visibility, DOM geometry, and layer z-index validation | **100% Detected (0 Bypasses)** | `heldout_grounding_benchmark.json` | Advanced Canvas-rendered fake widgets lacking DOM nodes require visual crop verification. |
| **THREAT-06** | **Stale Reference Execution Race** (Target element removed before click dispatch) | Execution Dispatch | `LocalRefValidator` verifies node presence in live DOM right before Playwright dispatch | **0 Corrupt Actions (100% Fresh Re-reasoning)** | `phase10_reliability.json` | Race condition occurring in the <5ms window between validator check and OS mouse click. |
| **THREAT-07** | **Ambiguous Target Guessing** (Two identical confirm buttons side-by-side) | Action Selection | Confidence & Margin Gating (<0.15 triggers `ASK_USER` safe abstention) | **20/20 Safe Abstentions (100.0%)** | `redteam_grounding_benchmark.json` | False positive abstention on deliberately duplicated UI buttons (e.g. pagination controls). |
| **THREAT-08** | **Unauthorized High-Risk Action** (Destructive account deletion / fund transfer) | Execution Gate | Local Policy Engine (`classify_risk_level`); mandatory human confirmation | **100% Gating (0 Bypasses)** | `phase10_runtime_control_audit.json` | Misclassified novel actions not matching destructive keywords or financial patterns. |
| **THREAT-09** | **Malformed Action Syntax** (VLM generating invalid JSON or unknown action) | Action Deserializer | Strict Pydantic Schema Validation & Fail-Closed Parser (`SAFE_STOP`) | **100% Fail-Closed (0 Crashes)** | `phase9_hardening.json` | Model entering repetitive malformed generation loops requiring session termination. |
| **THREAT-10** | **Unknown Candidate Reference** (Model emits target reference `e99` not in graph) | Reference Resolver | Local Ref Registry validation; immediate rejection with fresh reasoning trigger | **100% Handled (0 Invalid Dispatches)** | `phase9_hardening.json` | Latency incurred by restarting observation turn. |
| **THREAT-11** | **Infinite Replay / Action Looping** (Repeatedly clicking failed button) | Progress Evaluator | State hash comparison across turns; explicit `no_progress` supervisory signal | **0.0% Repeated Loops (911 Steps)** | `phase10_reliability.json` | Cyclic alternating loops across 2 distinct buttons (partially mitigated by action history). |
| **THREAT-12** | **VLM Inference Gateway Timeout** (Model API hangs or takes >15.0s) | Network Client | Watchdog timer enforcing hard deadline; strict fail-closed termination | **100% Bounded (0 Silent Hangs)** | `phase9_fault_injection.json` | Aborting a valid long-reasoning turn on resource-constrained host machines. |
| **THREAT-13** | **Browser WebSocket Disconnect** (Playwright browser process crashes mid-step) | Browser Driver | Fail-closed runtime interceptor; state preservation and clean exit | **100% Contained (0 Leaks)** | `phase10_compound_faults.json` | Inability to complete workflow without launching a new browser instance. |
| **THREAT-14** | **PII Detector Crash / Failure** (Regex or NER engine throws unhandled exception) | Privacy Pipeline | Strict Fail-Closed Privacy Filter (`DO_NOT_TRANSMIT`); halts transmission immediately | **0 Secret Leaks (8/8 Faults)** | `phase10_privacy_failure_audit.json` | Legitimate workflow blocked when privacy subsystem encounters transient memory pressure. |
| **THREAT-15** | **Runaway Execution / Emergency Stop** (User triggers kill switch) | Dispatch Boundary | Hardware/thread-safe kill switch interrupting dispatch path (<0.043 ms) | **0 Subsequent Actions Dispatched** | `phase10_kill_switch_event.json` | Local client interrupt cannot rollback an action already committed to a remote bank server. |

---

## Key Governance Conclusions
1. **Defense-in-Depth:** No single component is trusted with complete autonomy.
2. **Fail-Closed Runtime:** Every security control is designed to fail safely into an observable halt rather than degrading into unsafe default actions.
3. **Accountability & Auditability:** Every action emits a structured provenance chain linking user intent, model reasoning, policy risk classification, execution status, and post-condition verification.
