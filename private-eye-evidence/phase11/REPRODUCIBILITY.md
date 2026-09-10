# PrivateEye v1.0-RC: Complete Scientific Reproducibility Runbook

> **Target Release:** `v1.0-RC`  
> **Frozen Commit:** `70f0e1b35b94078d5e0b39f1a8d8f55002c00dd8`  
> **Verification Verdict:** `READY WITH DOCUMENTED LIMITATIONS`

This runbook provides step-by-step instructions to reproduce every published benchmark, privacy invariant, statistical interval, and validation claim on a clean machine.

---

## 1. Clean Environment Setup

### System Prerequisites
- **Operating System:** Windows 11 / 10, Ubuntu 22.04+, or macOS 14+
- **Python Version:** Python 3.11, 3.12, or 3.13 (tested on 3.13.3 AMD64)
- **Local VLM Runtime:** Ollama with `qwen2.5-vl:3b` installed

### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/krishvp10/private-eye.git
cd private-eye
git checkout 70f0e1b

# 2. Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright browser binaries
playwright install chromium

# 5. Verify local Qwen model availability in Ollama
ollama pull qwen2.5-vl:3b
ollama run qwen2.5-vl:3b "Hello"
```

---

## 2. Benchmark & Evaluation Execution Suite

Run the exact commands below to reproduce all quantitative evidence:

```bash
# Step 1: Execute full unit & integration test suite (108 tests)
pytest tests/ -v

# Step 2: Run Automated Headline Metric Integrity Validator
python eval/final_metric_validator.py

# Step 3: Compute 95% Wilson Score Confidence Intervals
python eval/confidence_intervals.py

# Step 4: Run Independent Held-Out Validation Suite (100 runs)
python eval/independent_validation.py

# Step 5: Run Causal Failure Attribution Analysis
python eval/failure_analysis.py

# Step 6: Run Horizon Survival & Hazard Rate Analysis
python eval/horizon_analysis.py

# Step 7: Run Scientific Privacy & Detector Precision/Recall Audit
python eval/privacy_scientific_audit.py

# Step 8: Run Compound Fault & Fault-Injection Benchmarks
python eval/fault_injection_benchmark.py
python eval/compound_fault_benchmark.py

# Step 9: Run Live Flagship Privacy & Safety Demo
python eval/live_privacy_demo.py

# Step 10: Global Secret Leak Scanner (Audits repository files)
python eval/scan_secrets_audit.py
```

---

## 3. Expected Verification Checksums

| Script | Expected Outcome | Output Artifact |
|---|---|---|
| `pytest tests/ -v` | `108 passed, 0 failed` | Console output |
| `final_metric_validator.py` | `19/19 metrics passed, 0 mismatches` | `eval/reports/final_metric_integrity.json` |
| `confidence_intervals.py` | `20 metrics evaluated with 95% Wilson CIs` | `eval/reports/phase11_confidence_intervals.json` |
| `independent_validation.py` | `86.0% task success (86/100), 98.46% step accuracy` | `eval/reports/phase11_independent_validation.json` |
| `failure_analysis.py` | `72.73% stochastic, 27.27% deterministic split` | `eval/reports/phase11_failure_analysis.json` |
| `horizon_analysis.py` | `78.12% 20-step cumulative survival (vs 78.39% theoretical)` | `eval/reports/phase11_horizon_analysis.json` |
| `privacy_scientific_audit.py` | `0 leaks across 11 boundaries; 95.92% precision, 94.00% recall` | `eval/reports/phase11_privacy_scientific_audit.json` |
| `compound_fault_benchmark.py`| `10/10 compound scenarios contained` | `eval/reports/phase10_compound_faults.json` |
| `fault_injection_benchmark.py`| `20/20 single fault scenarios contained` | `eval/reports/phase9_fault_injection.json` |
| `live_privacy_demo.py` | `Outcome: SUCCESS, Abstention: Verified, Recovery: Verified` | `eval/reports/phase8_live_privacy_demo.json` |
| `scan_secrets_audit.py` | `Scanned 578 files; Total detected leaks: 0` | Console exit code 0 |

---

## 4. Determinism & Random Seeds
- All evaluation simulation and perturbation injectors pin random seeds (`random.seed(42)`).
- Model decoding uses greedy deterministic sampling (`temperature=0.0`).
- Playwright viewport is pinned to `1280x800` at default scale `1.0`.
