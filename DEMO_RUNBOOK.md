# PrivateEye Demo & Benchmark Runbook

## Flagship Live Privacy & Safety Demo (Phase 8 Final)

To run the flagship end-to-end verification demonstrating client-side PII masking, `value_ref` resolution, explainable human-in-the-loop abstention, failure recovery, and an 11-boundary privacy invariant audit:

```powershell
python eval/live_privacy_demo.py
```

Outputs:
- `eval/reports/phase8_live_privacy_demo.json`
- `eval/reports/phase8_live_privacy_demo.md`

---

## Interactive Local Portal & Supervisor Launch

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

Use `--no-browser` for headless CI smoke checks.

---

## Configuration & Environment Overrides

Safe defaults are read from `shared/config.py`. Override via environment variables without source edits:

```powershell
$env:PRIVATEEYE_HOST="127.0.0.1"
$env:PRIVATEEYE_DEMO_PORT="9001"
$env:PRIVATEEYE_SERVER_PORT="8000"
$env:PRIVATEEYE_DASHBOARD_PORT="8080"
```

To configure the multimodal reasoning backend:

```powershell
$env:PRIVATEEYE_VLM_MODE="mock"
# or PRIVATEEYE_VLM_MODE="real" when an Ollama / vLLM endpoint is running
```

---

## Phase 8 Evaluation & Benchmark Suite

To reproduce all Phase 8 evaluations across real-world web benchmarks, long-horizon workflows, safety policies, threat modeling, and performance profiling:

### 1. Metric Provenance Audit & Adapted Diagnostic Relabeling (Phase 8.1 & 8.16)
```powershell
python eval/freeze_and_audit_phase8.py
```
- Audits all headline claims against complete denominators.
- Formally downgrades external diagnostic evaluations to `PRIVATEEYE ADAPTED DIAGNOSTIC`.
- Output: `eval/reports/phase8_metric_audit.json` and `.md`.

### 2. Real-World Multi-Domain Web Benchmark (Tier 5, 125 tasks)
```powershell
python eval/realweb_benchmark.py
```
- Evaluates 125 realistic web tasks across 25 distinct commercial web interfaces.
- Tracks 5 hierarchical success levels (L1 action, L2 target, L3 execution, L4 post-condition, L5 task progress).
- Output: `eval/reports/phase8_realweb_benchmark.json` and `.md`.

### 3. Long-Horizon Reliability Benchmark (270 steps)
```powershell
python eval/long_horizon_benchmark.py
```
- Evaluates Short (3–5 steps), Medium (6–10 steps), and Long (11–20+ steps) workflows.
- Measures step accuracy, task completion, and loop rates.
- Output: `eval/reports/phase8_long_horizon.json` and `.md`.

### 4. State & Memory Ablation Benchmark
```powershell
python eval/state_memory_ablation.py
```
- Compares S0 (Memoryless) vs S1 (No Action History) vs S2 (No Progress State) vs S3 (Full Progress-Aware).
- Output: `eval/reports/phase8_state_memory_ablation.json` and `.md`.

### 5. Explainable Human Abstention Quality Benchmark
```powershell
python eval/abstention_quality_benchmark.py
```
- Evaluates 137 test cases (100 clear, 25 ambiguous, 12 disabled).
- Generates "Why did I refuse?" UX explanations with 0 secret leaks.
- Output: `eval/reports/phase8_abstention_quality.json` and `.md`.

### 6. Expanded Prompt Injection Security Benchmark (15 Vectors)
```powershell
python eval/prompt_injection_expanded.py
```
- Tests 15 diverse webpage prompt injection vectors (hidden text, system prompt spoofing, malicious labels).
- Output: `eval/reports/phase8_prompt_injection.json` and `.md`.

### 7. Full Pipeline Latency Profiler (Phase 8.14)
```powershell
python eval/performance_profile.py
```
- Measures sub-millisecond latencies across 10 distinct pipeline stages (capture, detection, redaction, ranking, planner, verifier, policy, execution, post-condition).
- Calculates p50 and p95 and identifies the dominant latency source.
- Output: `eval/reports/phase8_performance_profile.json` and `.md`.

---

## What to Inspect in the Flagship Demo

1. **Local PII Redaction:** Form inputs containing PAN, passwords, and credit cards are visually masked before screenshot serialization.
2. **Sanitized Remote Wire Context:** Outbound network payloads audited by `OutboundLeakInterceptor` show zero raw secrets.
3. **Local Vault Value Resolution:** Playwright injects secrets from the client-side vault via `value_ref` directly into DOM fields.
4. **Explainable Refusal UX:** Faced with twin identical buttons, the agent safely abstains and prompts the user for clarification.
5. **Fresh-Reasoning Recovery:** Transient stale reference errors trigger recovery with fresh DOM snapshots.
6. **11-Boundary Invariant Audit:** Confirms zero leaked secrets across all application boundaries and reports.

---

## Shutdown

Press `Ctrl+C` in the running terminal. The supervisor terminates all background subprocesses cleanly.
