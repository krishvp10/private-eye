# PrivateEye v1.0-RC: Offline Demonstration Fallback Protocol (Phase 13)

> **Integrity Principle:** Never simulate or fake live execution as if it were occurring in real time. If an unexpected hardware, daemon, or browser failure occurs during a live presentation, immediately disclose the failure mode to the judges, transition to the documented fallback artifacts, and present the pre-recorded and verified telemetry logs.

---

## 1. Failure Mode Matrix & Contingency Action

| Failure Scenario | Detection Trigger | Fallback Protocol | Fallback Evidence Location |
|---|---|---|---|
| **1. Ollama Daemon Offline** | `demo/preflight.py` returns `[FAIL] Ollama` (connection refused on `localhost:11434`). | 1. Attempt single quick restart: `ollama serve` in background terminal.<br>2. If unavailable within 10s, switch to **Pre-Recorded VLM Telemetry Replay**.<br>3. Walk judges through canonical JSON prompt and response traces. | `eval/reports/real_vlm_report.json`<br>`private-eye-evidence/presentation/chart6_latency_decomposition.svg` |
| **2. GPU / VRAM Exhaustion** | Inference latency exceeds 20s or CUDA Out of Memory error logged. | 1. Fall back to CPU inference or switch immediately to **Offline Static Visual Inspection**.<br>2. Present the 125-task multi-domain trace logs showing verified turn latency distribution. | `eval/reports/phase8_performance_profile.json`<br>`private-eye-evidence/performance/latency_profile.json` |
| **3. Chromium / Playwright Launch Failure** | `demo/preflight.py` reports `Browser DOM probe failed` or driver lock. | 1. Run `python demo/reset_demo.py` to clear dangling processes.<br>2. If OS sandbox blocks browser rendering, present **Static HTML Mock & Inspection Walkthrough** using pre-captured visual screenshots. | `demo/fixtures/demo_portal.html`<br>`private-eye-evidence/presentation/chart1_grounding_progression.svg` |
| **4. Local VLM Timeout** | Inference exceeds 15s deadline during live action generation. | 1. Demonstrate **Fail-Closed Runtime Handling**: show that timeout triggers safe abort, never corrupting state.<br>2. Switch to pre-computed trajectory log of Scenario A. | `eval/reports/phase10_failure_replay.json`<br>`eval/reports/phase12_trajectory_efficiency.json` |
| **5. Host Machine Network Disconnection** | Complete air-gapped / offline conference venue Wi-Fi. | **Zero Impact:** PrivateEye is designed 100% offline. All models, vaults, and synthetic web fixtures run on `localhost`. | Fully self-contained local workspace. |
| **6. Screen Capture / Rendering Glitch** | Playwright screenshot capture returns blank or corrupt buffer. | 1. Present **ScreenGraph Accessibility Tree Representation** directly from CLI stdout.<br>2. Emphasize that PrivateEye uses multi-signal ARIA grounding, meaning the agent can operate even under degraded visual rendering. | `shared/protocol.py` (`ScreenGraph`)<br>`eval/reports/heldout_grounding_benchmark.json` |

---

## 2. Pre-Recorded Demonstration Assets

All fallback demonstrations must be explicitly introduced to judges as pre-recorded artifacts:

1. **Pre-Executed Scenario Logs:**
   - Location: [`demo/logs/demo_events.jsonl`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/demo/logs/demo_events.jsonl)
   - Contains immutable timestamped audit events of Scenarios A, B, and C with zero raw secrets.
2. **Canonical Multi-Domain Execution Traces:**
   - Location: [`eval/reports/phase10_reliability.json`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/eval/reports/phase10_reliability.json)
   - 100 complete E2E workflow runs, covering 911 executed steps, 89 successful workflows, and 11 transparently attributed failures.
3. **Synthetic Banking Portal Fixture:**
   - Location: [`demo/fixtures/demo_portal.html`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/demo/fixtures/demo_portal.html)
   - Operates in any standard web browser by opening the local file URI directly without running web servers.
4. **Adversarial & Fault Injection Verification Suite:**
   - Location: [`eval/reports/phase10_compound_faults.json`](file:///c:/Users/krish/OneDrive/Desktop/BROWSER-AGENT/eval/reports/phase10_compound_faults.json)
   - Proves 10/10 compound fault containment and 15/15 prompt injection containment under reproducible testing.

---

## 3. Fallback Verbal Transition Script

If a live glitch occurs during judging, use this transparent statement:

> *"Judges, our local daemon has encountered an environment timing issue. Rather than stalling the presentation, let us show you our deterministic fallback logs. In PrivateEye, all telemetry is structured and tamper-evident. Here is the exact recorded execution trace from our Phase 12 validation runs, showing the same policy gate and zero-leak invariant verified across 100 live workflows."*
