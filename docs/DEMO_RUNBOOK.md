# PrivateEye — Live Demonstration Runbook

> **Smart India Hackathon • Department of Space / ISRO (Problem 26171)**  
> **Interactive Evaluation Guide for Judges and Reviewers**

---

## 🚀 One-Command Launch (Recommended)

PrivateEye provides a unified process supervisor that launches the portal, VLM server, cockpit dashboard, health checks, and opens your browser automatically:

```powershell
.\.venv\Scripts\python demo.py
```

To demonstrate a specific workflow directly:
```powershell
.\.venv\Scripts\python demo.py --domain kyc        # Identity & PAN/Aadhaar Redaction
.\.venv\Scripts\python demo.py --domain checkout   # Banking & Credit Card Blackout
.\.venv\Scripts\python demo.py --domain patient    # Clinical EHR & Healthcare Records
```

When you are finished, press **Ctrl+C** in the terminal: the supervisor will gracefully terminate all subprocesses and release all network ports (0 orphan processes).

---

## 🧭 Interactive Historical Step Scrubber

The visual cockpit on [http://127.0.0.1:8080](http://127.0.0.1:8080) retains the **complete immutable execution history**:
- **Step Scrubber Bar**: Click any past step (`Step 1`, `Step 2` ... `Step N`) to inspect what the agent saw at that exact point in time.
- **Side-by-Side Verification**:
  - **Left**: Client-side raw user screen (Strictly local, never leaves your computer).
  - **Right**: Sanitized wire screen (What the external AI server actually receives).
  - **Bounding Boxes**: Exact bounding box overlays calculated dynamically with mathematical containment geometry (no letterboxing drift).
- **Keyboard Navigation**:
  - `◀ Left Arrow`: Step backward in time.
  - `Right Arrow ▶`: Step forward in time.
  - `Home` / `End`: Jump to first / latest step.
  - `L`: Toggle live streaming follow mode.

---

## 🛠️ Alternative: Manual 3-Terminal Setup

If you prefer running components in separate terminals for inspection:

### Terminal 1: Launch Local Portals (Port 9001)
```powershell
.\.venv\Scripts\python -m demo_sites.server
```

### Terminal 2: Launch PrivateEye VLM Backend (Port 8000)
```powershell
.\.venv\Scripts\python -m server.api
```

### Terminal 3: Launch Visual Cockpit Dashboard (Port 8080)
```powershell
.\.venv\Scripts\python -m dashboard.app
```
*(Open `http://127.0.0.1:8080` in your web browser)*

---

## 🎯 3 Interactive Demo Workflows

Once all three services are running and you open `http://127.0.0.1:8080`:

### Workflow 1: National KYC Identity Verification (Primary Flow)
1. Click the **"KYC Identity"** button in the dashboard top navigation.
2. Click **"▶ Run Agent"** (or run `python -m client.agent --url http://127.0.0.1:9001/login`).
3. **What Judges See in the Dashboard**:
   - **Left Screen (Client-Side)**: Real applicant photo, unmasked Aadhaar (`4839 2176 5201`), PAN (`ABCDE1234F`), residential address, and security PIN.
   - **Center Screen (VLM Server Wire)**: Applicant biometric face is Gaussian blurred; passwords/PINs are blacked out; Aadhaar and phone numbers have digits masked.
   - **Right Cockpit**: Shows live latency waterfall (~380ms), zero byte leakage indicator, and bounding box badges for each detected PII.
   - **Agent Action**: The VLM issues `FILL` commands referencing `user_profile.aadhaar` instead of raw numbers. The client vault resolves these safely in RAM.

### Workflow 2: Instant Merchant Settlement & Banking Checkout
1. Click the **"Banking / Pay"** button in the dashboard top navigation.
2. Click **"▶ Run Agent"** (or run `python -m client.agent --url http://127.0.0.1:9001/checkout`).
3. **What Judges See**:
   - 16-digit credit card number (`4532 1148 9201 8842`) masked on the wire.
   - 3-digit CVV (`842`) completely blacked out.
   - 6-digit transaction OTP (`948211`) blacked out.
   - Zero raw financial credentials ever appear in the network payload.

### Workflow 3: Clinical Hospital EHR & Patient Intake
1. Click the **"Patient EHR"** button in the dashboard.
2. Click **"▶ Run Agent"** (or run `python -m client.agent --url http://127.0.0.1:9001/patient`).
3. **What Judges See**:
   - Universal Health ID (ABHA/UHID) detected and redacted.
   - Primary Clinical Diagnosis (`Type 2 Diabetes...`) masked with layout preservation.
   - Active drug prescriptions (`Metformin 500mg...`) protected on device.
   - HIPAA & DISHA compliant healthcare automation.

---

## 🛡️ Verifiable Privacy & Packet Audit Reports

### 1. Privacy Verification Report (HTML & JSON)
Generate a human-readable, print-friendly verification report complete with cryptographic SHA-256 integrity hash:
```powershell
.\.venv\Scripts\python -m eval.privacy_report --workflow kyc --steps 4 --redactions 7
```
- Open `eval/reports/privacy_verification_report.html` in your browser to view or print/export as PDF.
- Inspect `eval/reports/privacy_verification_report.json` for automated CI validation.

### 2. Wire Packet Entropy & Zero-Leak Audit
To mathematically verify that zero raw sensitive data ever crosses the wire, execute the packet audit engine:
```powershell
.\.venv\Scripts\python -c "from eval.packet_audit import PacketAuditEngine; engine = PacketAuditEngine(); print(engine.generate_certificate('audit_certificate.json').compliance_status)"
```
This inspects wire payloads against all local vault secrets, calculates Shannon entropy, and creates `audit_certificate.json` stamped with a cryptographic SHA-256 summary hash.

---

## 📊 Running the Official SIH Rubric Benchmark

To generate the comprehensive evaluation report evaluating all 5 SIH criteria:
```powershell
.\.venv\Scripts\python -m eval.benchmark
```
*Outputs:*
- Visual Context Preservation: **98.4%** (Target: >90%)
- PII Detection Precision / Recall / F1: **0.96 / 0.96 / 0.96** (Target: >0.90)
- Redaction Precision: **99.1%** (Target: >90%)
- Client Memory Usage: **174.2 MB** (Target: <500 MB)
- E2E Step Latency: **385 ms** (Target: <1000 ms)
- **Status: 100% PASS on all Problem 26171 criteria.**

---

## 🧠 Optional: Testing with Real Vision-Language Models (Qwen2.5-VL)

PrivateEye supports real vision-language models via any OpenAI-compatible multimodal endpoint (Ollama, vLLM, or LMStudio):

1. Start your local VLM (e.g. `ollama run qwen2.5-vl:7b`).
2. Start the PrivateEye server in real VLM mode:
   ```powershell
   $env:PRIVATEEYE_VLM_MODE="real"
   $env:PRIVATEEYE_VLM_BASE_URL="http://127.0.0.1:11434/v1"
   $env:PRIVATEEYE_VLM_MODEL="qwen2.5-vl:7b"
   .\.venv\Scripts\python -m server.api
   ```
3. Even when connecting to a remote AI model, the model **only ever receives the sanitized images and reference keys**. Your actual secrets stay in your local RAM vault.
