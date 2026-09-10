# PrivateEye Demo & Benchmark Runbook

## One-command launch

```powershell
python demo.py
```

Select a configured fixture with:

```powershell
python demo.py --domain kyc
python demo.py --domain checkout
python demo.py --domain patient
python demo.py --domain sample_fixture
```

Use `--no-browser` for CI or a headless smoke check.

---

## Configuration

The supervisor reads safe local defaults from `shared/config.py`. Override
without source edits:

```powershell
$env:PRIVATEEYE_HOST="127.0.0.1"
$env:PRIVATEEYE_DEMO_PORT="9001"
$env:PRIVATEEYE_SERVER_PORT="8000"
$env:PRIVATEEYE_DASHBOARD_PORT="8080"
```

The VLM boundary remains explicit:

```powershell
$env:PRIVATEEYE_VLM_MODE="mock"
# or PRIVATEEYE_VLM_MODE=real when a reachable endpoint exists
```

---

## Phase 7 Evaluation & Security Benchmarks

To reproduce all Phase 7 generalization, reliability, calibration, and privacy evaluations:

### 1. Metric Provenance Audit & Development Set Freeze
```powershell
python eval/freeze_and_audit.py
```
- Freezes `eval/data/development_set.json` (SHA256: `228dcfecd20a56f531f3eb45f915cf54e430b5741b08d5e11ac940757dbf8cd0`).
- Generates `eval/reports/phase7_metric_audit.json` and `.md`.

### 2. Held-Out Generalization Benchmark (200 cases)
```powershell
python eval/heldout_benchmark.py
```
- Evaluates 200 unseen cases across 7 fresh domains and responsive layouts.
- Output: `eval/reports/heldout_grounding_benchmark.json` and `.md`.

### 3. Red-Team Adversarial Grounding Benchmark (75 cases)
```powershell
python eval/redteam_benchmark.py
```
- Evaluates 75 adversarial scenarios: identical unadorned labels, hidden decoys, prompt injection.
- Evaluates selective autonomy and safe abstention (`AMBIGUOUS`, `NO_VALID_CANDIDATE`).
- Output: `eval/reports/redteam_grounding_benchmark.json` and `.md`.

### 4. Confidence Calibration & Selective Verification
```powershell
python eval/confidence_calibration.py
```
- Measures accuracy across 6 confidence buckets (`0.50-0.59` through `0.95-1.00`).
- Compares Mode A (Direct), Mode B (Always Verifier), and Mode C (Selective Verifier).
- Output: `eval/reports/confidence_calibration.json` and `.md`.

### 5. Adaptive Resolution Benchmark
```powershell
python eval/resolution_adaptive_benchmark.py
```
- Compares Fixed 448px vs 768px vs 1024px vs Adaptive Resolution.
- Output: `eval/reports/phase7_adaptive_resolution.json` and `.md`.

### 6. Failure Recovery Benchmark & Error Taxonomy
```powershell
python eval/recovery_benchmark.py
```
- Compares R0 (Blind Retry: 0%) vs R1 (Fresh Reasoning: 100%) vs R2 (+ Verifier: 100%).
- Categorizes failures according to the 19-class error taxonomy.
- Output: `eval/reports/phase7_recovery_benchmark.json` and `.md`.

### 7. Universal Privacy Invariant Audit
```powershell
python eval/privacy_invariant_audit.py
```
- Deep audit of all 11 remote-bound boundaries and 57 report files against 21 vault secrets.
- Output: `eval/reports/phase7_privacy_invariant.json` and `.md`.

### 8. Controlled Model Comparison (3B vs 7B)
```powershell
python eval/model_comparison_benchmark.py
```
- Evaluates Qwen2.5-VL-3B vs 7B across 275 evaluation cases under identical conditions.
- Documents the Pareto trade-off and deployment decision.
- Output: `eval/reports/phase7_model_comparison.json` and `.md`.

### 9. External Diagnostic Check
```powershell
python eval/external_diagnostic.py
```
- Evaluates 50 ScreenSpot-Pro and Mind2Web diagnostic cases.
- Output: `eval/reports/phase7_external_diagnostic.json` and `.md`.

---

## What to Inspect in the Interactive Demo

1. Open the dashboard shown by the supervisor (`http://127.0.0.1:8080`).
2. Click **Run Agent**.
3. Use the timeline chips or Previous/Next controls to replay a step.
4. Compare local raw imagery with the sanitized wire image.
5. Inspect detections, redactions, action target, validation, execution, and latency metadata.
6. Open the generated privacy report under `eval/reports/`.

Raw screenshots are retained only in local dashboard memory. They are never transmitted to the reasoning server. Reports contain zero raw secrets.

---

## Shutdown

Press Ctrl+C in the supervisor terminal. It terminates the supervised process tree cleanly.
