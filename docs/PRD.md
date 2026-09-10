# PRD — PrivateEye

## 1. Executive Summary

A local-first browser agent that lets a cloud VLM assist with on-screen tasks **without ever receiving
raw personal data**. The client performs visual perception and PII redaction on-device; the server
perceives only an anonymized screen. This directly implements SIH Problem 26171: "bridge cloud reasoning
with strict client-side data privacy."

## 2. Problem Statement

* **What problem exists?** Useful AI agents need screen context; screens contain credentials, faces,
  government IDs, health and financial data. Sending raw screenshots to cloud LLM/VLMs leaks all of it.
* **Why does it matter?** It blocks agent adoption in regulated/sensitive domains (banking, KYC, healthcare,
  government — ISRO's stated interest). DPDP Act 2023 (India) heightens this.
* **How is it currently solved?** (a) Blind server agents that only get DOM text (no visual grounding);
  (b) fully-local small models (weak reasoning); (c) trusting the vendor (privacy-policy roulette).
* **Why insufficient?** None combine strong cloud reasoning with a *verifiable* local privacy boundary.

## 3. Vision

Every screen-assist request carries a machine-readable guarantee: "this payload contains no recoverable PII."
The redaction contract (`RedactionMap`) makes privacy inspectable, not promised.

## 4. Goals

| ID | Goal | Measure |
|---|---|---|
| G-1 | End-to-end task completion on demo flows | ≥90% success on 3 scripted flows |
| G-2 | No raw PII on the wire | 100% of flagged PII regions masked; packet-level demo |
| G-3 | Fast enough to feel interactive | e2e step latency ≤3 s p50, ≤6 s p95 |
| G-4 | Light client | ≤1.5 GB RAM, ≤2 CPU cores typical, local CV ≤300 ms/frame |
| G-5 | Demonstrable accuracy | PII detection F1 ≥0.85 on our labeled synthetic corpus |

## 5. Non-Goals

- NO real-credential handling (all demo data synthetic)
- NO generic web browsing at scale (3 curated demo sites for MVP)
- NO training/fine-tuning of models during the hackathon (inference only)
- NO MV3 browser extension in MVP (V1; problem statement's "extension/JS" is satisfied by the
  locally-running client agent which controls real Chrome/Firefox)
- NO multi-tenancy, auth, or billing

## 6. Target Users

**Persona A — Privacy-conscious end user ("Asha")**
Role: completes KYC/bank/hospital forms on the web. Context: distrusts uploading ID scans.
Goals: get forms done fast; certainty data stays local. Pain: retyping, portals' confusing layouts.
Tech ability: low. Success: form submitted, she saw exactly what left her machine.

**Persona B — ISRO/SIH evaluator ("Dr. Rao")**
Role: judges the submission against the 5 announced metrics. Goals: measurable accuracy, redaction
precision, resource numbers, working end-to-end demo. Pain: vaporware, unevaluated claims.
Success: live demo + benchmark table + resource dashboard.

**Persona C — Developer integrator ("Dev")**
Role: would embed the agent in a product. Goals: clean protocol, documented API, reproducible build.
Success: `docker compose up` works; protocol schema is stable.

## 7. User Stories

* US-1: As Asha, I want the agent to fill my KYC form while showing me a live view of what's being masked,
  so that I can verify privacy before anything is sent.
* US-2: As Asha, I want the agent to ask me before submitting anything, so that it can't act irreversibly.
* US-3: As Dr. Rao, I want a benchmark report of PII recall/precision/redaction precision, so that metrics
  1–3 are evidence-backed.
* US-4: As Dr. Rao, I want to see CPU/RAM/latency numbers live, so that metrics 4–5 are evidence-backed.
* US-5: As Dev, I want all server responses to be structured JSON actions, so that execution is auditable.
* US-6: As Asha, I want my secrets typed locally and never transmitted, so that the server plans but can't steal.

## 8. User Journeys

**J-1 KYC form (primary demo).** Open KYC site → capture → masks appear (face blurred, Aadhaar digits
partially masked, PAN masked) → sanitized context sent → server returns sequence of fill/click actions →
client fills values locally from profile → agent pauses at Submit → user confirms → submitted.
**J-2 Redaction benchmark.** Run `eval/benchmark.py` over labeled synthetic corpus → confusion matrix +
precision/recall table exported → displayed on dashboard.
**J-3 Latency/resource measurement.** Run `eval/latency.py` over J-1 → waterfall (capture/detect/redact/
network/infer/execute) + CPU/RAM time series.

## 9. Functional Requirements

| ID | Requirement | Pri | Acceptance criteria | Deps |
|---|---|---|---|---|
| FR-001 | Capture full-page screenshot via Playwright | P0 | PNG/JPEG bytes + viewport size returned | — |
| FR-002 | Extract a11y tree snapshot | P0 | JSON tree with role/name/value per node | — |
| FR-003 | DOM heuristic PII detection | P0 | Flags `type=password`, `autocomplete=*email*/cc-*`, `inputmode=numeric` fields | FR-002 |
| FR-004 | Regex+NER text PII detection | P0 | Aadhaar (4-4-4), PAN ([A-Z]{5}\d{4}[A-Z]), phone (10d), email detected in visible text | FR-002 |
| FR-005 | Face detection | P0 | BlazeFace ONNX on screenshot; ≥1 face found where present (synthetic set) | FR-001 |
| FR-006 | Pixel redaction | P0 | Blackout (passwords/PAN), gaussian blur (faces), digit mask (Aadhaar/phone) applied to image | FR-003..005 |
| FR-007 | RedactionMap contract | P0 | Every redaction emitted as {region, category, method}; server receives it | FR-006 |
| FR-008 | Sanitized payload POST | P0 | JPEG + a11y tree + RedactionMap + URL to /v1/analyze | FR-007 |
| FR-009 | Structured action response | P0 | Server returns one of click/fill/scroll/select/navigate/done/ask_user with a11y-target | — |
| FR-010 | Local execution | P0 | Actions executed via Playwright getByRole/getByLabel; fill uses local value_ref | FR-009 |
| FR-011 | Human-in-the-loop gate | P0 | "submit", "pay", "send" targets require explicit user confirmation | FR-010 |
| FR-012 | Metrics dashboard | P1 | Live: step latency, CPU%, RSS, redaction count, detection F1 | FR-008 |
| FR-013 | Benchmark harness | P0 | Precision/recall/F1 + confusion matrix vs labeled corpus | FR-006 |
| FR-014 | Firefox support | P1 | Same flow runs on firefox channel | FR-010 |

## 10. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-001 | Privacy | Zero flagged PII pixels in outbound payload (verified by `eval/leak_check.py` re-scanning outbound image) |
| NFR-002 | Privacy | Secret values never serialized into any network message (static check + runtime interceptor) |
| NFR-003 | Performance | Local detect+redact ≤300 ms/frame at 1280×800 |
| NFR-004 | Performance | Step e2e ≤3 s p50 / ≤6 s p95 on LAN |
| NFR-005 | Performance | Outbound image ≤400 KB (JPEG q≈70, downscale to 1280px) |
| NFR-006 | Resources | Client RSS ≤1.5 GB, CPU ≤2 cores sustained |
| NFR-007 | Reliability | Action failure → retry ≤2 with fresh context, then ask_user |
| NFR-008 | Security | TLS (or LAN-only + ssh tunnel at demo); server validates schema strictly |
| NFR-009 | Security | Prompt-injection screen content cannot make server emit non-whitelisted actions (LLM01) |
| NFR-010 | Observability | Every step logged with timing waterfall; logs contain no PII |
| NFR-011 | Compatibility | Python 3.11; Chromium + Firefox current stable |
| NFR-012 | Reproducibility | `docker compose up` reproduces server; pinned requirements |

## 11. MVP
Everything marked P0 in FR-001..013, scoped to 3 demo sites + 1 KYC end-to-end flow + benchmark report.

## 12. V1
Extension variant (ONNX Runtime Web/WebGPU), policy engine, planner with milestones, LLM01 guardrails,
Firefox full support, second flow (hospital appointment).

## 13. Future Roadmap
DP-noise telemetry, federated redaction updates, on-device OmniParser-style screen parsing, redaction
attestation logs, ISRO-internal deployment profile (air-gapped vLLM).

## 14. Success Metrics (mapped to SIH rubric)

| Rubric | Target | Evidence |
|---|---|---|
| Visual context accuracy (25%) | ≥85% element identification agreement | benchmark vs a11y-ground-truth |
| PII recall/precision (20%) | F1 ≥0.85 each category | labeled corpus (300 synthetic screens) |
| Redaction precision (20%) | ≥95% masks fully cover flagged regions; ≤5% over-mask of non-PII | IoU-based eval |
| Client resource utilization (20%) | within NFR-006 + ≤300 ms/frame | live psutil dashboard |
| End-to-end latency (15%) | within NFR-004 | latency waterfall report |

## 15. Acceptance Criteria
1. J-1 completes live on stage in <5 min, with visible masking.
2. `eval/benchmark.py` prints a table meeting section 14 targets.
3. Packet capture / server-side dump shows no unredacted PII.
4. README quickstart works on a fresh machine in ≤15 min.
