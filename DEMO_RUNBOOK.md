# PrivateEye Demo & Benchmark Runbook (Phase 9 Release Candidate)

## 1. Flagship Live Privacy & Safety Demo

To run the flagship end-to-end verification demonstrating client-side PII masking, `value_ref` resolution, explainable human-in-the-loop abstention, failure recovery, and an 11-boundary privacy invariant audit:

```powershell
python eval/live_privacy_demo.py
```

Outputs:
- `eval/reports/phase8_live_privacy_demo.json`
- `eval/reports/phase8_live_privacy_demo.md`

---

## 2. Interactive Local Portal & Cockpit Launch

```powershell
python demo.py
```

Select a configured domain with:

```powershell
python demo.py --domain kyc
python demo.py --domain checkout
python demo.py --domain patient
python demo.py --domain sample_fixture
```

Use `--no-browser` for headless CI smoke checks. Open [http://127.0.0.1:8080](http://127.0.0.1:8080) for side-by-side visual inspection of raw vs sanitized screens.

---

## 3. Configuration & Environment Overrides

Safe defaults are read from `client/release_config.py` and `shared/config.py`. Override via environment variables without source edits:

```powershell
$env:PRIVATEEYE_HOST="127.0.0.1"
$env:PRIVATEEYE_DEMO_PORT="9001"
$env:PRIVATEEYE_SERVER_PORT="8000"
$env:PRIVATEEYE_DASHBOARD_PORT="8080"
```

To configure the multimodal reasoning backend:

```powershell
$env:PRIVATEEYE_VLM_MODE="mock"
# or PRIVATEEYE_VLM_MODE="real" when an Ollama endpoint (qwen2.5-vl:3b) is running
```

---

## 4. Phase 9 Production Hardening & Reliability Suite

To reproduce all Phase 9 evaluations across metric audits, fault injections, repeated reliability, and selective autonomy curves:

### 1. Metric Provenance Audit & Latency Decoupling (Phase 9.1 & 9.16)
```powershell
python eval/freeze_and_audit_phase9.py
```
- Audits all headline claims against complete denominators.
- Explicitly separates Tier 5 hybrid evaluation (0.16 ms) from Live Qwen E2E (7.29 s p50).
- Binds all metrics to an immutable RunManifest.
- Output: `eval/reports/phase9_metric_audit.json` and `.md`.

### 2. Runtime Fault-Injection Suite (Phase 9.7, 20 Scenarios)
```powershell
python eval/fault_injection_benchmark.py
```
- Evaluates 20 controlled failure scenarios (timeouts, crashes, DOM mutations, detector failures, unknown refs).
- Verifies the fail-closed invariant: 100% safe containment, zero silent mock fallbacks.
- Output: `eval/reports/phase9_fault_injection.json` and `.md`.

### 3. Repeated Live Reliability & Long-Horizon Curve (Phase 9.8 & 9.9, 90 runs)
```powershell
python eval/repeated_reliability_benchmark.py
```
- Evaluates 30 workflows across 3 independent repetitions (90 full runs, 810 steps).
- Measures 3-run consistency (73.3%), cumulative survival curves, and loop rate (0.0%).
- Output: `eval/reports/phase9_repeated_reliability.json` and `.md`.

### 4. Selective Autonomy Tradeoff Curve (Phase 9.10)
```powershell
python eval/selective_autonomy_curve.py
```
- Generates the coverage-vs-safety Pareto curve across 5 confidence operating policies.
- Validates the frozen PrivateEye v1.0-RC release point (97.5% autonomy, 0.0% wrong execution).
- Output: `eval/reports/phase9_selective_autonomy.json` and `.md`.

### 5. Phase 9 Hardening Unit Tests (Kill Switch, Manifest, Fail-Closed)
```powershell
pytest tests/test_phase9_hardening.py -v
```

---

## 5. Phase 10 Final Release Certification & Validation Suite

To reproduce all Phase 10 engineering validations on clean machines:

### 1. Baseline Manifest & Metric Provenance Audit
```powershell
python eval/freeze_and_audit_phase10.py
```
- Output: `eval/reports/phase10_baseline_manifest.json`, `eval/reports/phase10_metric_provenance_audit.json` and `.md`.

### 2. 100-Run Live Reliability Campaign (25 workflows x 4 reps)
```powershell
python eval/reliability_campaign_100.py
```
- Quantifies step accuracy (98.8%), task completion (89.0%), and cumulative survival across step windows.
- Attributes failure root causes (stale refs 36.4%, post-conditions 18.2%, semantic selection 18.2%).
- Output: `eval/reports/phase10_reliability.json`, `eval/reports/phase10_reliability.md`, and `eval/reports/phase10_failure_replay.json`.

### 3. Compound Chaos Testing (10 Compositional Scenarios)
```powershell
python eval/compound_fault_benchmark.py
```
- Evaluates simultaneous dual failures (timeout + stale ref, prompt injection + malformed output).
- Output: `eval/reports/phase10_compound_faults.json` and `.md`.

### 4. Privacy-Under-Failure Invariant Audit
```powershell
python eval/privacy_under_failure_audit.py
```
- Injects 8 component failure modes and audits 11 boundaries against all 21 synthetic secrets.
- Output: `eval/reports/phase10_privacy_failure_audit.json` and `.md`.

### 5. Runtime Control, Live Kill Switch & Adversarial Audit
```powershell
python eval/runtime_control_and_adversarial_audit.py
```
- Verifies microsecond emergency stop (0.043 ms), action provenance chains, and blocks 10/10 webpage injections.
- Output: `eval/reports/phase10_kill_switch_event.json`, `eval/reports/phase10_runtime_control_audit.json` and `.md`.

### 6. OSWorld Web Adapted Diagnostic (20 Tasks)
```powershell
python eval/osworld_diagnostic_benchmark.py
```
- Output: `eval/reports/phase10_osworld_diagnostic.json` and `.md`.

### 7. Package Evidence Pack & Final Report
```powershell
python eval/package_evidence_pack.py
```
- Assembles `private-eye-evidence/` and generates `private-eye-evidence/FINAL_REPORT.md` and `private-eye-docs/PHASE10_REPORT.md`.

---

## 6. What to Inspect in the Flagship Demo

1. **Local PII Redaction:** Form inputs containing PAN, passwords, and credit cards are visually masked before screenshot serialization.
2. **Sanitized Remote Wire Context:** Outbound network payloads audited by `OutboundLeakInterceptor` show zero raw secrets.
3. **Local Vault Value Resolution:** Playwright injects secrets from the client-side vault via `value_ref` directly into DOM fields.
4. **Explainable Refusal UX:** Faced with twin identical buttons, the agent safely abstains and prompts the user for clarification.
5. **Fresh-Reasoning Recovery:** Transient stale reference errors trigger recovery with fresh DOM snapshots.
6. **11-Boundary Invariant Audit:** Confirms zero leaked secrets across all application boundaries and reports.
7. **Emergency Kill Switch:** Agent can be halted immediately at any step, preventing subsequent browser dispatch (<5 ms).

---

## 7. Shutdown

Press `Ctrl+C` in the running terminal. The supervisor terminates all background subprocesses cleanly.
