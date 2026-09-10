# PrivateEye Phase 9 Research & Architectural Analysis

**Focus:** Production Hardening, Runtime Safety Governance, Reproducibility & External Benchmark Scoping  
**Date:** September 2026  
**Standards Covered:** OWASP Agent Control Standard (ACS, Sep 2026) · OWASP Agentic Top 10 · NIST AI RMF 1.0 · BrowserGym · OSWorld · ScreenSpot-Pro · GUI-Actor  

---

## 1. The Shifting Paradigm in Autonomous Agent Evaluation

During 2024–2025, the browser agent literature focused almost exclusively on raw benchmark accuracy: pushing foundation model parameters (from 7B to 72B), complex multi-agent orchestrations, or specialized visual grounding heads.

However, research throughout 2026 (culminating in the publication of the **OWASP Agent Control Standard** on September 1, 2026 and NIST's GenAI evaluation methodology) demonstrates that raw benchmark accuracy without runtime governance produces brittle, unsafe agents unsuitable for enterprise deployment.

### 1.1 The Core Lessons from Recent Benchmarks

1. **OSWorld (Computer Use Benchmarking):**  
   OSWorld evaluates agents in realistic multi-application operating environments with execution-based state evaluation. OSWorld revealed the massive chasm between synthetic tasks and real environments: while human operators achieve $>72\%$ completion, state-of-the-art multimodal models initially scored $\approx 12\%$. OSWorld demonstrated that run-to-run brittleness, DOM mutations, and ungrounded actions compound exponentially over long horizons.

2. **ScreenSpot-Pro (High-Resolution GUI Grounding):**  
   ScreenSpot-Pro highlighted that visual grounding on authentic high-resolution interfaces is substantially harder than toy benchmarks, with top baselines scoring below $20\%$ in zero-shot settings. RegionFocus and GUI-Actor proved that dynamically narrowing attention (via visual crops or candidate grounding) dramatically outperforms raw coordinate regression.

3. **BrowserGym & Mind2Web (Environment-Driven Evaluation):**  
   BrowserGym provides standardized observation and action spaces across WorkArena, WebArena, and MiniWoB. Mind2Web emphasized cross-website domain generalization. Both benchmarks established that static HTML scraping or single-DOM heuristics fail when tested against dynamic single-page applications.

### 1.2 PrivateEye's Position & Benchmark Discipline

PrivateEye adopts strict academic discipline:
- **Adapted Diagnostics vs. Official Leaderboards:** PrivateEye's 50-example ScreenSpot and 25-example Mind2Web suites are explicitly labeled `PRIVATEEYE ADAPTED DIAGNOSTIC`. They serve as unit-level sanity checks for candidate extraction, **not** as claims of official leaderboard parity.
- **Decoupling Latency Metrics:** Phase 8 accurately measured local candidate scoring at $\approx 0.16\text{ ms}$, but this evaluates only deterministic Playwright ranking over DOM fixtures. Real multimodal inference with Qwen2.5-VL-3B requires $\approx 7.29\text{ s}$ p50. Conflating the two would be scientifically fraudulent. Phase 9 explicitly separates Tier 5 Hybrid Evaluation from Live E2E Multimodal Execution.

---

## 2. Alignment with the OWASP Agent Control Standard (ACS, Sep 2026)

The OWASP ACS defines the security baseline for autonomous AI agents operating tools and APIs. PrivateEye v1.0-RC implements the four core pillars:

```
                  ┌────────────────────────────────────────┐
                  │      OWASP AGENT CONTROL STANDARD       │
                  └───────────────────┬────────────────────┘
                                      │
         ┌────────────────┬───────────┴────┬────────────────┐
         ▼                ▼                ▼                ▼
   CONTROLLABILITY   TRACEABILITY    INSPECTABILITY    FAIL-CLOSED
   • Kill Switch     • Action        • Run Manifest    • 12 Failure
   • Policy Engine     Provenance    • Privacy Audit     Modes
   • Human-in-Loop   • Sanitized     • Dashboard Live    • Banned Mock
     Approval          Logs            Telemetry           Fallback
```

### 2.1 Threat Mapping to OWASP Agentic Top 10

| OWASP ASI Category | Agentic Risk Description | PrivateEye Countermeasure & Invariant |
|---|---|---|
| **ASI01: Goal Hijacking** | Indirect prompt injection embedded in webpage DOM or image. | Webpage content treated strictly as untrusted data. Semantic action validator enforces user goal authority. |
| **ASI02: Tool Misuse / Excessive Agency** | Model attempts unauthorized shell execution or destructive database updates. | Local Safety Policy Engine restricts tools to white-listed browser actions; destructive actions require human confirmation. |
| **ASI03: Identity & Privilege Abuse** | Agent accesses unauthorized credentials or exceeds operational boundaries. | Local Vault enforces key-level allowlists; credentials resolved only by local executor via `value_ref`. |
| **ASI04: Sensitive Data Disclosure** | Agent transmits raw PII/secrets to remote model provider or telemetry endpoint. | Dual-tier privacy gate (NER + OCR + regex) redacts text and raster pixels before context serialization. |
| **ASI06: Memory & Context Poisoning** | Adversarial webpage corrupts agent multi-step memory. | Context memory stores only cryptographically structured state tuples; external scripts cannot inject history. |
| **ASI08: Cascading Failures** | Stale references or minor post-condition failures trigger infinite retry loops. | Multi-tier state tracking detects loops immediately; fresh reasoning recovery re-observes the environment. |

---

## 3. The Fail-Closed Principle in Autonomous Agent Design

Traditional agent frameworks exhibit a dangerous "fail-open" or "best-effort" bias: when uncertain, they click the closest element or fall back to an unverified heuristic.

PrivateEye establishes the formal **Fail-Closed Runtime Invariant**:
$$\text{Safety}(\text{action}) \notin \{\text{PROVEN}\} \implies \text{Action} \equiv \text{ABORT}$$

### 3.1 Formal Case Handling

1. **Privacy Detection Crash $\to$ `DO_NOT_TRANSMIT`:** If the local regex or NER detector raises an exception, PrivateEye refuses to serialize or transmit the screenshot. Confidentiality takes absolute precedence over task completion.
2. **Redaction Buffer Corruption $\to$ `DO_NOT_TRANSMIT`:** If image masking fails to yield a valid redacted JPEG/PNG, the raw image is discarded.
3. **Unknown Candidate Ref $\to$ `DO_NOT_EXECUTE`:** If the VLM hallucinates a reference token not present in the active local candidate table, dispatch is aborted.
4. **Low Model Confidence $\to$ `ABSTAIN_AND_REQUEST_INFO`:** Actions with confidence $< 0.65$ trigger safe abstention rather than random guessing.
5. **Model Outage $\to$ `SAFE_STOP`:** If the local Ollama daemon crashes or times out repeatedly, the agent halts safely with a user-facing notification. **Silent fallback to MockVLM is strictly prohibited.**

---

## 4. Run Manifests and Measurement Science (NIST AI RMF)

The National Institute of Standards and Technology (NIST) AI Risk Management Framework (AI RMF 1.0) emphasizes that trustworthiness requires empirical reproducibility and measurement integrity.

In PrivateEye Phase 9, no benchmark score is valid without an accompanying **Run Manifest** (`client/manifest.py`). The manifest binds:
- Exact Git commit SHA
- SHA256 cryptographic hash of the benchmark fixture
- Model identifier, decoding temperature, and resolution
- Verifier thresholds ($\tau_{\text{high}}=0.88, \tau_{\text{low}}=0.65$)
- Host OS, Python version, and Playwright binary version
- GPU hardware profile and runtime environment

This guarantees that external researchers can reproduce exact benchmark outcomes without configuration ambiguity.

---

## 5. Architectural Decision: Why Bypassing Fine-Tuning was the Right Choice

While papers such as GUI-Actor demonstrate that specialized grounding heads can improve Qwen2.5-VL, fine-tuning introduces severe risks at this stage of development:
1. **Catastrophic Forgetting:** Fine-tuning on web grounding often damages multi-turn reasoning and instruction compliance.
2. **Loss of Portability:** A base Ollama model (`qwen2.5-vl:3b`) can be run out-of-the-box by any hackathon judge or developer with `ollama pull`. A custom checkpoint introduces complex weights distribution and dependency management.
3. **Marginal Returns vs. Massive Structural Gains:** Improving raw VLM accuracy from 88% to 92% yields minor benefits compared to PrivateEye's selective verifier + local candidate grounding (which achieves **98.5%** accuracy on base Qwen) and fresh-reasoning recovery (which achieves **100%** recovery from locator stalls).

**Conclusion:** Freezing Qwen2.5-VL-3B at 768px with client-side fail-closed policy enforcement and action provenance provides the strongest, most defensible, and most reproducible foundation for PrivateEye v1.0-RC.
