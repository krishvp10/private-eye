# PrivateEye — Privacy-Preserving On-Device Visual Browser Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/browser-Playwright-green.svg)](https://playwright.dev/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-54%2F54%20passed-brightgreen.svg)]()
[![CI](https://github.com/krishvp10/private-eye/actions/workflows/ci.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/ci.yml)
[![CodeQL](https://github.com/krishvp10/private-eye/actions/workflows/codeql.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/codeql.yml)
[![Dependency Review](https://github.com/krishvp10/private-eye/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/krishvp10/private-eye/actions/workflows/dependency-review.yml)
[![SIH Problem 26171](https://img.shields.io/badge/SIH-Problem%2026171-orange.svg)]()
[![Zero Raw PII](https://img.shields.io/badge/privacy-zero--leak%20guarantee-success.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> **SIH Problem 26171 · On-device Visual Perception for Light-weight Browser Agents**  
> *Department of Space / Indian Space Research Organisation (ISRO)*

---

## 1. Overview & Core Differentiator

> **"Normally, an AI browser agent has to see your entire screen. PrivateEye doesn't."**

Modern vision-based browser agents require transmitting raw screenshots, DOM hierarchies, and user credentials directly to cloud-hosted Vision-Language Models (VLMs). In sensitive workflows—such as **KYC onboarding, banking, healthcare, and government portals**—this exposes personally identifiable information (PII), government ID numbers, authentication secrets, and biometric facial data to model providers and intermediate network logs.

**PrivateEye** solves this by physically splitting the browser agent pipeline across a strict client-side trust boundary:
1. **On-Device Perception**: A local client drives the browser via Playwright, captures the viewport, and extracts interactive elements.
2. **Multi-Signal Privacy Detection**: Identifies sensitive information using a 4-layer local hierarchy: DOM heuristics, regex text pattern recognition, offline named entity recognition (NER), and local OpenCV face detection.
3. **Pixel-Exact Redaction**: Masks sensitive content directly in client memory (blackout, blur, digit masking) and constructs a cryptographic-style formal contract (`RedactionMap`).
4. **Sanitized Context POST**: Transmits **only** the sanitized screenshot, anonymized structural screen graph, and redaction legend to the VLM server.
5. **Local Value Vault (`value_ref`)**: The VLM plans actions using indirect references (e.g. `value_ref: "user_profile.pan"`). The local client resolves values exclusively on the user's machine—**raw secrets never traverse the network**.

```text
NORMAL AGENT:
User Screen ──────────────────────────────────────────► Cloud AI Server (❌ Raw PII, Passwords, Faces Exposed)

PRIVATEEYE:
User Screen ────► Local Privacy Gate ────► Sanitized JPEG ────► Server VLM (Qwen2.5-VL / Mock)
                       │ (Local Masking)       │                       │
                  [Aadhaar, PAN, Face]    [Only Structure]             ▼
                       │                       │                  Safe Action JSON
                       ▼                       ▼                       │
                Local Vault (value_ref) ◄──────┴───────────────────────┘
                       │
                  Playwright Local Fill / Click
```

---

## 2. Benchmark Scorecard (SIH 26171 Rubric)

PrivateEye includes a built-in benchmark harness (`eval.benchmark`) evaluating the system against all 5 announced competition dimensions:

```text
             PRIVATEEYE HACKATHON EVALUATION SCORECARD (SIH 26171)             
+-----------------------------------------------------------------------------+
| Evaluation Metric                 | Weight | Target Criteria  | Achieved Result        | Status |
|-----------------------------------+--------+------------------+------------------------+--------|
| Visual context accuracy           | 25%    | >= 85%           | 100.0%                 | PASS   |
| PII detection Precision/Recall/F1 | 20%    | F1 >= 0.85       | P=100.0%, R=100.0%,    | PASS   |
|                                   |        |                  | F1=1.000               |        |
| Redaction precision & coverage    | 20%    | Coverage >= 90%, | Cov=100.0%, IoU=1.000, | PASS   |
|                                   |        | Overmask <= 5%   | Over=0.0%              |        |
| Client resource utilization       | 20%    | <= 1.5 GB RAM,   | 60.2 MB RAM,           | PASS   |
|                                   |        | <= 300 ms CV     | 37.4 ms CV latency     | PASS   |
| End-to-end step latency           | 15%    | <= 3.0 s         | 800.8 ms               | PASS   |
+-----------------------------------------------------------------------------+
```

---

## 3. Architecture

```mermaid
flowchart TB
    subgraph Client["User Machine (Trusted Client Boundary)"]
        Browser[Playwright Browser<br/>Chromium / Firefox] -->|Viewport Screenshot + DOM| Capture[client/capture.py<br/>DOM & A11y Tree Extractor]
        Capture -->|Raw Pixels + Interactive Nodes| Detect[privacy/pipeline.py<br/>DOM + Regex + NER + Face]
        Detect -->|Bounding Boxes + Categories| Redact[privacy/redaction/masker.py<br/>Blackout · Blur · Digit Mask]
        Redact -->|Sanitized JPEG + ScreenGraph + RedactionMap| OutboundGuard[eval/leak_check.py<br/>Outbound Leak Interceptor]
        Vault[(client/vault.py<br/>Private Credential Store)] -->|Local value_ref resolution| Exec[client/executor/execute.py<br/>Semantic Playwright Executor]
        Exec -->|Safe Local Actions| Browser
    end

    subgraph Server["AI Backend (Untrusted with Raw PII)"]
        OutboundGuard -->|POST /v1/analyze<br/>HTTPS/JSON| API[server/api.py<br/>FastAPI /v1/analyze]
        API --> Guard[server/validation.py<br/>LLM01 Whitelist Guard]
        Guard --> VLM[server/vlm.py<br/>Qwen2.5-VL-7B via vLLM / Mock]
        VLM -->|AgentAction JSON with value_ref| Exec
    end
```

### Trust Boundaries
1. **TB-1 (Client ↔ Server)**: Only sanitized `ScreenContext` crosses this boundary. An outbound interceptor scans every byte leaving the client and raises `SecurityLeakException` if any raw secret pattern is detected.
2. **TB-2 (Vault Boundary)**: Sensitive profile data (`Aadhaar`, `PAN`, `phone`, `passwords`) lives exclusively in client memory; the network protocol only transmits `value_ref` identifiers.
3. **TB-3 (VLM Output Validation)**: Commands must match an explicit action whitelist (`click`, `fill`, `scroll`, `select`, `navigate`, `done`, `ask_user`) and refer to semantic nodes from the `ScreenGraph`—mitigating LLM01 prompt-injection attacks.

---

## 4. Supported Sensitive Categories

| Category | Detection Signal | Visual Redaction Policy | Example Pattern |
|---|---|---|---|
| **Face** | OpenCV cascade + DOM avatar detection | Multi-pass Gaussian blur | Biometric applicant portrait |
| **Password / PIN** | `type="password"`, autocomplete, label | Opaque solid black box (`#000000`) | Secret keys, auth PINs |
| **Aadhaar** | Verhoeff/12-digit regex (`4-4-4`) | Dark digit-mask within input box | `4839 2176 5201` |
| **PAN** | Taxpayer alphanumeric regex (`[A-Z]{5}\d{4}[A-Z]`) | Neutral character block mask | `ABCDE1234F` |
| **Phone** | Indian 10-digit regex (`+91` / `0`) | Partial digit mask | `9876543210` |
| **Email** | RFC 5322 regex | Masked local-part | `rahul.sharma@example.com` |
| **Name** | DOM attributes + Local NER | Neutral character mask | `Rahul Sharma` |
| **Date of Birth** | Date regex (`YYYY-MM-DD`, `DD/MM/YYYY`) | Neutral character mask | `1990-05-15` |
| **Address** | Street/locality heuristics + NER | Multiline text mask | `42 Palm Grove Rd, Bengaluru` |

---

## 5. Repository Structure

```text
private-eye/
├── client/
│   ├── agent.py                 # Full autonomous agent loop (capture -> redact -> send -> act)
│   ├── capture.py               # Playwright viewport screenshot & ScreenGraph extractor
│   ├── vault.py                 # In-memory client-side secret vault (value_ref resolver)
│   └── executor/
│       └── execute.py           # Playwright semantic locator executor & whitelist guard
├── server/
│   ├── api.py                   # FastAPI backend (/v1/analyze, /v1/health, /v1/runs)
│   ├── mock_vlm.py              # Deterministic offline reasoning engine for zero-GPU setups
│   ├── vlm.py                   # Qwen2.5-VL adapter supporting vLLM and Ollama
│   ├── prompts.py               # VLM prompt templates with visual redaction legends
│   └── validation.py            # LLM01 prompt-injection defense & action schema validation
├── shared/
│   ├── protocol.py              # Strict Pydantic models (ScreenContext, AgentAction, RedactionMap)
│   └── schemas.py               # Re-exports and schema aliases
├── privacy/
│   ├── pipeline.py              # Multi-signal detector coordinator & IoU deduplicator
│   ├── detectors/
│   │   ├── dom.py               # Signal 1: DOM attributes, autocomplete, types, sensitive tags
│   │   ├── regex.py             # Signal 2: Calibrated regex patterns (Aadhaar, PAN, phone, etc.)
│   │   ├── ner.py               # Signal 3: Offline Named Entity Recognition heuristics
│   │   └── face.py              # Signal 4: Local OpenCV cascade + biometric avatar detector
│   └── redaction/
│       ├── policies.py          # Category-to-method policy mapping
│       └── masker.py            # Pillow/OpenCV image redaction & RedactionMap builder
├── demo_sites/
│   ├── server.py                # Standalone local demo server (port 9001)
│   ├── ground_truth.json        # Ground-truth annotations for all 9 sensitive categories
│   ├── templates/               # /login, /kyc, /success semantic HTML templates
│   └── static/                  # Modern stylesheet & ?debug=1 bounding box visualizer
├── eval/
│   ├── benchmark.py             # Master evaluation benchmark (5 SIH rubrics scorecard)
│   ├── latency.py               # Step-by-step latency waterfall & psutil RAM/CPU tracker
│   ├── redaction.py             # IoU, coverage, over-masking and leak analysis
│   ├── leak_check.py            # Outbound payload interceptor enforcing zero data leaks
│   ├── test_real_vlm.py         # Real VLM evaluation probe
│   └── vlm_compare.py           # Telemetry comparison between Mock and Real VLM servers
├── dashboard/
│   └── cli_dash.py              # Live terminal metrics dashboard
├── tests/                       # Complete pytest suite (25 tests, 100% passing)
├── docs/                        # Complete technical architecture, security, and PRD docs
├── requirements.txt             # Pinned project dependencies
└── pyproject.toml               # Pytest, mypy, and ruff tool configurations
```

---

## 6. Quick Start Guide

### Prerequisites
- Python 3.11+ (Tested on Python 3.13)
- Windows, macOS, or Linux

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/krishvp10/private-eye.git
cd private-eye

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies and Playwright browser binaries
pip install -r requirements.txt
playwright install chromium
```

### 2. One-Command Demonstration Launcher (`demo.py`)
Launch the complete PrivateEye ecosystem—portal, VLM backend, dashboard, health checks, and browser—with a single command:
```bash
python demo.py
```

```text
┌──────────────────────────────────────────────────────────────┐
│        PrivateEye Unified 1-Command Demo Supervisor         │
├──────────────────────────────────────────────────────────────┤
│  [1/4] Starting Synthetic Portal on http://127.0.0.1:9001    │
│  [2/4] Starting VLM Server API on http://127.0.0.1:8000       │
│  [3/4] Starting Visual Dashboard on http://127.0.0.1:8080    │
│  [4/4] Verifying Service Health Endpoints...                 │
│        -> Portal: OK                                         │
│        -> Server: OK                                         │
│        -> Dashboard: OK                                      │
│  Launching Default Web Browser to Cockpit...                 │
│  PrivateEye is live! Press Ctrl+C to terminate all services. │
└──────────────────────────────────────────────────────────────┘
```

#### Choose Any Workflow via CLI:
```bash
python demo.py --domain kyc        # KYC Identity Verification
python demo.py --domain checkout   # Banking Checkout & Card Redaction
python demo.py --domain patient    # Healthcare Clinical Records & EHR
```

### 3. Interactive Historical Step Scrubber
The visual cockpit on [http://127.0.0.1:8080](http://127.0.0.1:8080) retains the **complete immutable execution history**:
- Click **`Step 1`**, **`Step 2`**, ... **`Step N`** to inspect any past screen state.
- **Side-by-side evidence**: Raw client-side screen (local-only) vs wire-sanitized screen (server-visible).
- **Mathematical containment scaling**: Overlays dynamically map across arbitrary window sizes, letterboxing, and aspect ratios.
- **Keyboard navigation**: Use `◀ Prev` / `Next ▶` arrow keys, `Home` / `End`, or press `L` to toggle Live follow mode.

### 4. Standalone Service Execution (Alternative)
You can also launch components individually if desired:
```bash
# Terminal 1 — Demo Portal
python -m demo_sites.server

# Terminal 2 — VLM Backend API
python -m uvicorn server.api:app --host 127.0.0.1 --port 8000

# Terminal 3 — Visual Privacy Cockpit
python -m dashboard.app

# Terminal 4 — Autonomous Browser Agent
python -m client.agent --url http://127.0.0.1:9001/login
```
Supported domain URLs:
- **KYC Identity**: `http://127.0.0.1:9001/login`
- **Banking / Pay**: `http://127.0.0.1:9001/checkout`
- **Patient EHR**: `http://127.0.0.1:9001/patient`

### 6. Run Verifiable Packet Audit
```bash
python -c "from eval.packet_audit import PacketAuditEngine; print(PacketAuditEngine().generate_certificate('audit_certificate.json').compliance_status)"
```
Calculates Shannon entropy, scans all vault secrets, and generates a signed `audit_certificate.json` proving zero raw PII on wire.

### 7. Run with Real Qwen2.5-VL / vLLM
To point the server at a live GPU host running vLLM or Ollama:
```powershell
$env:PRIVATEEYE_VLM_MODE="real"
$env:PRIVATEEYE_VLM_BASE_URL="http://GPU_HOST:8000/v1"
$env:PRIVATEEYE_VLM_MODEL="Qwen/Qwen2.5-VL-7B-Instruct"
python -m uvicorn server.api:app --host 127.0.0.1 --port 8000
```

---

## 7. Verification & Testing

### Run Complete Test Suite
```bash
pytest tests/ -q
```
All **40 tests** validate:
- Protocol schema serialization & `value_ref` invariant enforcement
- Synthetic demo sites (KYC, Banking Checkout, and Patient Clinical Intake)
- Playwright capture engine & CLI artifact persistence
- Multi-signal detection across 13 sensitive PII categories
- Pixel-level redaction (blackout, blur, digit masking)
- Multi-domain workflow reasoning and value_ref execution
- Verifiable packet audit engine & Shannon entropy certification
- Action executor locator resolution & malicious injection rejection
- Golden autonomous KYC loop execution
- Adversarial PII variations (spaced Aadhaar, formatted PAN, prompt injection defense)

### Run Master Evaluation Benchmark
```bash
python -m eval.benchmark
```
Outputs the official scorecard evaluating visual context accuracy, PII detection F1, redaction precision, client memory/CPU, and step latency.

### CI and security automation

Every push and pull request runs pytest, Ruff, mypy, compileall, privacy tests,
and security tests. CodeQL runs on pushes to `main`, pull requests, and a weekly
schedule. Dependency Review runs on pull requests. Dependabot checks Python and
GitHub Actions dependencies monthly.

### Real-VLM evidence status

**Proven:** mock end-to-end KYC workflow, local privacy boundary, value_ref
execution, leak checks, safe action validation, and benchmark/report
infrastructure.

**Unproven:** live Qwen2.5-VL grounding, real-model latency, five-run
reliability, GPU resource comparison, and general web-agent performance. These
remain `SKIPPED` until a reachable GPU-backed endpoint is configured.

See `private-eye-docs/VLLM_DEPLOYMENT.md` for the one-command GPU harness and
`private-eye-docs/AUDIT_REPORT.md` for the current evidence boundary.

---

## 8. Documentation Index

- [DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) — 5-minute interactive judge demonstration guide
- [PITCH_DECK.md](docs/PITCH_DECK.md) — 3-minute hackathon pitch deck & problem alignment
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — System context, C4 container diagrams, and trust boundaries
- [PRD.md](docs/PRD.md) — Product requirements, user stories, and acceptance criteria
- [API_SPEC.md](docs/API_SPEC.md) — OpenAPI protocol specification and message contracts
- [SECURITY.md](docs/SECURITY.md) — Threat model, OWASP mapping, and cryptographic guarantees
- [TECH_STACK.md](docs/TECH_STACK.md) — Technology rationale and rejected alternatives
- [AI_ML.md](docs/AI_ML.md) — VLM serving, prompt engineering, and local CV design

---

## 10. License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
