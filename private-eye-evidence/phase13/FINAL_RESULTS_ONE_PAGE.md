# PrivateEye: One-Page Executive Judge & Reviewer Summary

---

### Project Profile
* **Project Name:** PrivateEye — Privacy-Preserving On-Device Visual Browser Agent
* **Version:** v1.0-RC (`FROZEN BASELINE: 5d697dc`, `RELEASE COMMIT: bfc9d23`)
* **Core Model:** Qwen2.5-VL-3B running strictly locally via Ollama (768px default, adaptive 1024px crop)
* **Standards Alignment:** NIST AI RMF 1.0 (TEVV-Athlon) & OWASP Agent Control Standard (ACS 2026)

---

### Execution Architecture
```text
Observe → Sanitize → Reason → Ground → Gate → Execute → Verify
   │          │          │        │       │       │        │
Screen     Privacy    Local 3B   k=5    Policy  Local   Fail-Closed
Capture   Redaction     VLM    Verifier  Gate   Vault   Telemetry
```

---

### Headline Authoritative Results

| Dimension | Primary Metric | Scope / Dataset | 95% Confidence Interval | Source Artifact |
|---|---|---|---|---|
| **Development Autonomy** | **89.00%** Task Success (89/100) | Live 25 workflows × 4 reps (911 steps) | Wilson: `[81.36%, 93.84%]` | `phase10_reliability.json` |
| **Development Accuracy** | **98.79%** Step Accuracy (900/911)| 911 executed live turns | Wilson: `[97.83%, 99.33%]` | `phase10_reliability.json` |
| **Held-Out Validation** | **86.00%** Task Success (86/100) | 50 unseen workflows × 2 reps (912 steps)| Cluster Bootstrap: `[77.00%, 93.00%]` | `phase11_independent_validation.json` |
| **Held-Out Accuracy** | **98.46%** Step Accuracy (898/912)| 912 blind evaluated steps | Cluster Bootstrap: `[97.72%, 99.22%]` | `phase11_independent_validation.json` |
| **Trajectory Efficiency** | **1.000 Actions-to-Completion** | Completed runs (793/793 actions) | Exactly 1.000x (0 path wandering) | `phase12_trajectory_efficiency.json` |
| **Privacy Invariant** | **0 Detected Secret Leaks** | 11 representation boundaries, 21 secrets | Wilson: `[0.00%, 25.88%]` | `phase10_privacy_failure_audit.json` |
| **PII Detection** | **95.92% Precision / 94.00% Recall**| Multi-signal detection corpus | Wilson: `[86.29%, 98.92%]` | `phase11_privacy_scientific_audit.json` |
| **Prompt Injection** | **15 / 15 Vectors Blocked** | Direct & indirect prompt injection suite | Wilson: `[79.62%, 100.00%]` | `phase8_prompt_injection.json` |
| **Single Fault Resilience**| **20 / 20 Contained** | Deterministic single fault injections | Wilson: `[83.89%, 100.00%]` | `phase9_fault_injection.json` |
| **Compound Fault Chaos** | **10 / 10 Contained** | Multi-layered compound failure suite | Wilson: `[72.25%, 100.00%]` | `phase10_compound_faults.json` |
| **External Diagnostic** | **20 / 20 Adapted Tasks** | 20-task OSWorld-derived diagnostic subset | Wilson: `[83.89%, 100.00%]` | `phase10_osworld_diagnostic.json` |
| **Kill Switch Latency** | **0.031–0.043 ms** | Local software dispatch interrupt gate | Controlled benchmark measurement | `phase10_kill_switch_event.json` |

---

### Core Technical Differentiators
1. **Zero Secret Cloud Transmission:** Sensitive form fields are represented as abstract `value_ref` tokens; raw credentials reside strictly in local memory and are resolved on the client machine.
2. **Local Bounded Grounding ($k=5$):** The model cannot click arbitrary hallucinated pixels. The local candidate engine and selective visual crop verifier restrict actions to verified, visible elements.
3. **Fail-Closed Runtime:** When faced with ambiguous targets, low confidence, or untrusted webpage commands, the system halts safely (`ASK_USER`), preventing catastrophic state mutations.

---

### Primary Documented Limitation
* **Long-Horizon Workflow Risk:** While step accuracy remains high (98.46%), multi-step cumulative compounding reduces task completion on deep horizons (63.33% held-out / 78.12% dev on 11–20 steps). Per-step hazard remains stable (~1.42%), showing that failure is driven by steady environmental friction rather than cognitive memory decay.
