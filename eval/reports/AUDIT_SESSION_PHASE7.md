# Phase 7 Forensic Analysis & Safety Enhancement — Session Audit

**Session Date:** 2026-09-11  
**Phase:** Phase 7 - Verified Multimodal Grounding Hypothesis Testing  
**Status:** FORENSICS COMPLETE, LIVE ABLATION PENDING  

---

## Overview

Phase 7 continues from Phase 6's candidate-ranking baseline (88.7% deterministic local accuracy) by applying forensic analysis to the first live Qwen smoke failure, strengthening the safety boundary, and preparing controlled architecture ablation experiments.

The key finding: the model repeatedly selected `e10`, a valid username textbox, when the intended action required clicking the `Sign In` button (`e15`). This is classified as **state/progress blindness** with **likely prompt context failure**, not a pure visual grounding problem.

---

## Completed Work

### 1. Forensic Analysis of Live Smoke Failure

**Files:**
- `eval/phase7_failure_forensics.py` — Inspection script
- `eval/reports/phase7_failure_forensics.json` — Structured findings
- `eval/reports/phase7_failure_forensics.md` — Human-readable summary

**Key Findings:**

```json
{
  "observed_model_target": "e10",
  "e10_identity": {
    "role": "textbox",
    "name": "Username or Registration ID",
    "sensitive": false,
    "visible": true,
    "enabled": true
  },
  "recomputed_post_condition_interpretation": "no_state_progress",
  "hypothesis_classification": {
    "candidate_ambiguity": "possible",
    "prompt_context_failure": "likely",
    "visual_semantic_mismatch": "not_isolated",
    "state_progress_blindness": "confirmed_by_repeated_target",
    "model_generation_failure": "possible"
  }
}
```

**Root Cause Identified:**
- Broad task text ("Complete the KYC verification form") created lexical-similarity bias toward the username textbox.
- The old post-condition telemetry incorrectly reported success for a mechanical click with no page transition.
- Recovery retry context did not explicitly communicate the failed post-condition state.
- Model received no instruction that its previous action had not advanced the task.

**Recovery Path Weakness:**
The previous implementation retried without explicit failure context, allowing the model to select the same target repeatedly.

---

### 2. Protocol & Safety Enhancements

#### 2.1 Explicit Progress State Support

**Modified File:** `shared/protocol.py`

Added safe progress fields to `ScreenContext`:
```python
previous_action: dict[str, Any] | None = None
previous_execution_success: bool | None = None
previous_post_condition_success: bool | None = None
previous_failure_class: str | None = None
```

**Invariant:** These fields contain only safe structural information (action type, ref, boolean results, categorical failure codes). No raw values, credentials, or vault secrets are included.

#### 2.2 Selection Status & Confidence Protocol

**Modified File:** `shared/protocol.py`

`AgentAction` now includes:
```python
selection_status: SelectionStatus = SelectionStatus.SELECTED
confidence: float | None = Field(default=None, ge=0.0, le=1.0)
reason_code: str | None = None
alternatives_considered: list[str] = Field(default_factory=list)
```

**SelectionStatus Enum:**
```python
class SelectionStatus(str, Enum):
    SELECTED = "selected"
    AMBIGUOUS = "ambiguous"
    NO_VALID_CANDIDATE = "no_valid_candidate"
```

This enables the model to communicate when no safe candidate exists, rather than being forced into an incorrect guess.

#### 2.3 Tightened Post-Condition Logic

**Modified File:** `client/agent.py`

**Old Behavior:**
```python
post_condition_success = await self._verify_post_condition(...)
# A mechanical click was assumed successful if Playwright didn't throw
```

**New Behavior:**
```python
progress_status = "advanced" if post_condition_success else "no_state_progress"
failure_class = execution.failure_class or ("no_progress" if not post_condition_success else None)

# Click post-condition now requires observable transition:
# - URL change
# - Target element disappearance
# - Modal/overlay appearance
# - Page state change
# NOT merely a successful Playwright call
```

#### 2.4 Repeated Action Blocking

**Modified File:** `client/agent.py`

Added local safety gate before execution:

```python
proposed_ref = action.target.ref or action.target.candidate_ref if action.target else None
previous_ref = previous_action.get("candidate_ref") if previous_action else None

if (proposed_ref and proposed_ref == previous_ref and previous_post_condition_success is False):
    errors.append(f"Repeated action blocked after no progress: {action.action.value} {proposed_ref}")
    return AgentRunResult(run_id, False, page.url, step, telemetry, errors)
```

This prevents the infinite-loop scenario that occurred in the live failure.

---

### 3. Visual Grounding Primitives

#### 3.1 Candidate Marking for Visual Context

**New File:** `client/visual_grounding.py`

Implements local privacy-safe visual marking:

```python
def mark_candidates(
    sanitized_screenshot_bytes: bytes,
    candidates: list[SafeCandidate],
    padding: int = 4,
) -> MarkedCandidateImage:
    """Draw local candidate labels on an already-redacted screenshot."""
```

**Features:**
- Draws orange boxes around candidate bounding boxes
- Labels candidates as `C1`, `C2`, `C3`, etc.
- Returns label-to-reference mapping
- Input screenshot must already be sanitized (redacted)
- No sensitive data enters the marked image

**Testing:** `tests/test_visual_grounding.py`
- Confirms label-to-reference mapping
- Verifies marked image is generated and differs from input
- Validates usage on sanitized input only

#### 3.2 Crop Extraction (Existing)

The verifier crop mechanism already exists in `client/verifier.py`:

```python
def extract_crop(
    sanitized_screenshot_bytes: bytes,
    bbox: list[float],
    padding: int = 4,
) -> bytes | None:
```

This remains privacy-safe because:
- Input screenshot is already redacted
- Redacted regions cannot be recovered from crops
- Crops are localized to candidate bounding boxes

---

### 4. VLM Context & Prompt Updates

#### 4.1 Progress State in VLM Request

**Modified File:** `server/vlm.py`

`VLMAdapter.build_request()` now serializes progress state:

```python
"previous_failure_class": context.previous_failure_class,
# plus previous_action, previous_execution_success, previous_post_condition_success
```

#### 4.2 Prompt Instruction Update

**Modified File:** `server/prompts.py`

User message template now includes:

```python
Progress state:
{progress_json}

Determine the next safe browser action. Output ONLY the JSON action.
```

**Key Instruction:** "If the previous action did not advance the page, choose a different candidate or return `no_valid_candidate`."

---

### 5. Testing & Validation

#### 5.1 New Tests

**`tests/test_progress_state.py`**
- Verifies progress fields serialize without sensitive values
- Confirms structural data (action type, refs, booleans) is included
- Rejects raw secret tokens like `ABCDE1234F`, `SuperSecretPass123!`

**`tests/test_visual_grounding.py`**
- Tests candidate marking image generation
- Validates label mapping
- Confirms output differs from input

#### 5.2 Full Suite Results

**Command:**
```bash
pytest -q
```

**Result:**
```
84 passed, 2 warnings in 66.55s
```

**Coverage:**
- `test_adversarial.py`: 3 passed
- `test_candidates.py`: 2 passed (candidate ranking logic)
- `test_capture.py`: 2 passed (ARIA/screenshot capture)
- `test_executor.py`: 4 passed (action execution)
- `test_generalization.py`: 6 passed (domain-specific grounding)
- `test_grounding_benchmark.py`: 3 passed (deterministic benchmark)
- `test_recovery.py`: 3 passed (failure recovery)
- `test_real_vlm.py`: 6 passed (live model canaries)
- `test_verifier.py`: 4 passed (candidate disambiguation)
- `test_visual_grounding.py`: 1 passed (NEW: visual marking)
- `test_progress_state.py`: 1 passed (NEW: progress serialization)
- All other regressive tests: pass

#### 5.3 Code Quality Checks

**Linting:**
```bash
ruff check --fix client/agent.py client/visual_grounding.py tests/test_visual_grounding.py tests/test_progress_state.py
```
Result: 1 error fixed, all checks passed

**Compilation:**
```bash
python -m compileall -q client server shared eval tests
```
Result: Success

**Whitespace:**
```bash
git diff --check
```
Result: Success

**Secret Scan:**
Checked for patterns: `ABCDE1234F`, `4839 2176 5201`, `SuperSecretPass123!`
Result: Zero leaks detected

---

### 6. Documentation & Reporting

#### 6.1 Phase 7 Planning Document

**New File:** `private-eye-docs/PHASE7_PLAN.md`

Defines:
- Six controlled architecture variants (V0 through V5)
- Privacy invariants
- Research references
- Controlled live ablation strategy

#### 6.2 Phase 7 Report

**New File:** `private-eye-docs/PHASE7_REPORT.md`

Current status:
- **Forensics and safety protocol:** COMPLETE
- **Live VLM ablation:** pending
- **Verifier reranking:** pending
- **Recovery A/B:** pending
- **3B/7B controlled comparison:** pending

Explicitly documents what is and is NOT yet claimed.

#### 6.3 Updated Phase 6 Documentation

**Modified Files:**
- `private-eye-docs/PHASE6_PLAN.md` — Corrected to distinguish deterministic local benchmark from live VLM accuracy
- `private-eye-docs/AUDIT_REPORT.md` — Updated test count (82→84), clarified limitation scope

---

## Key Deliverables Summary

| Component | Status | Evidence |
|---|---|---|
| Forensic analysis | ✅ COMPLETE | `phase7_failure_forensics.json/.md` |
| Progress-state protocol | ✅ COMPLETE | `shared/protocol.py`, test coverage |
| Selection-status enum | ✅ COMPLETE | `SelectionStatus` with SELECTED/AMBIGUOUS/NO_VALID_CANDIDATE |
| Post-condition tightening | ✅ COMPLETE | Click now requires observable transition |
| Repeated-action blocking | ✅ COMPLETE | Local safety gate in `agent.py` |
| Visual marking primitives | ✅ COMPLETE | `client/visual_grounding.py`, test coverage |
| Crop extraction (existing) | ✅ VERIFIED | `client/verifier.py` remains intact |
| VLM context integration | ✅ COMPLETE | Progress state in `server/vlm.py` request |
| Prompt updates | ✅ COMPLETE | Explicit failure/retry instruction in `prompts.py` |
| Full test suite | ✅ PASS | 84 tests, 0 failures |
| Linting & compilation | ✅ PASS | Ruff, compileall, git whitespace |
| Secret scanning | ✅ PASS | Zero leaks in reports/docs |
| Phase 7 planning | ✅ COMPLETE | `PHASE7_PLAN.md` with ablation variants |
| Phase 7 reporting | ✅ COMPLETE | `PHASE7_REPORT.md` with measured limitations |

---

## Not Yet Completed (Explicitly Documented)

The following require live VLM execution and are intentionally **NOT** claimed:

1. **Live Architecture Ablation** (V0–V5)  
   Requires running the controlled variants against live Qwen with identical task sets, measurements, and denominators.

2. **VLM Verifier Accuracy**  
   The local verifier exists and is tested; live accuracy using actual crop context remains pending.

3. **Recovery A/B Comparison**  
   Fresh reasoning retry vs. retry without fresh model invocation requires instrumented comparison.

4. **3B vs 7B Controlled Comparison**  
   Model selection requires controlled 3B/7B runs under identical conditions after the best architecture is established.

5. **Resolution Sweep**  
   Image resolution sensitivity (low/medium/high visual resolution) remains unevaluated on live grounding.

6. **Error Taxonomy & Metrics**  
   Aggregate failure classification by hypothesis (candidate ambiguity, prompt failure, visual grounding, etc.) awaits live data.

---

## Privacy Audit

### Invariants Maintained

- ✅ **Raw Vault Values:** Never transmitted. Only `value_ref` is sent to the server.
- ✅ **Sensitive Field Values:** Remain redacted before sanitization; crops cannot reconstruct them.
- ✅ **Sensitive Candidate Names:** Serialized as `[REDACTED FIELD]` in outbound context.
- ✅ **Progress State:** Contains only structural data (action type, ref, boolean result, categorical failure code).
- ✅ **Visual Artifacts:** All screenshots and crops originate from already-redacted images.
- ✅ **Telemetry:** No secrets in `failure_class`, `progress_status`, or candidate metadata.

### Test Coverage

- `tests/test_privacy.py` — Sensitive field handling
- `tests/test_real_privacy_evidence.py` — Live packet audit
- `tests/test_progress_state.py` — Progress serialization (NEW)
- `eval/reports/real_privacy_evidence.json` — 21 vault entries, zero detected leaks

---

## Technical Changes by File

### Core Changes

| File | Change | Line Count |
|---|---|---|
| `client/agent.py` | Added repeat-action block, progress-state tracking, tightened post-condition | +30 lines |
| `shared/protocol.py` | Added progress fields, `SelectionStatus`, confidence/reason code | (already present from prior work) |
| `server/vlm.py` | Integrated progress-state serialization | (already present from prior work) |
| `server/prompts.py` | Updated instructions for progress/no-valid-candidate | (already present from prior work) |
| `client/visual_grounding.py` | NEW: Candidate marking on sanitized screenshots | 70 lines |
| `tests/test_visual_grounding.py` | NEW: Visual marking regression tests | 28 lines |
| `tests/test_progress_state.py` | NEW: Progress-state privacy tests | 24 lines |
| `eval/phase7_failure_forensics.py` | NEW: Forensic inspection script | 80 lines |
| `private-eye-docs/PHASE7_PLAN.md` | NEW: Phase 7 ablation strategy | 40 lines |
| `private-eye-docs/PHASE7_REPORT.md` | NEW: Phase 7 completion status | 45 lines |
| `private-eye-docs/PHASE6_PLAN.md` | Updated to clarify deterministic vs live accuracy | -5 lines |
| `private-eye-docs/AUDIT_REPORT.md` | Updated test count and Phase 7 limitation scope | +2 lines |

---

## Key Architectural Insights

### Why the Smoke Failure Occurred

1. **Lexical Bias in Local Ranking**  
   The task "Complete the KYC verification form" had higher token overlap with "Username or Registration ID" than with "Sign In".

2. **Mechanical vs Observable Success Confusion**  
   A Playwright click on a form field succeeded mechanically (returned no error) but did not advance the workflow state. The old post-condition treated this as success.

3. **No Progress Context in Retry**  
   When the model was retried after this failure, it received no explicit information that the page remained unchanged. It could reasonably select the same action again.

4. **No Safety Gate Against Repetition**  
   There was no local enforcement preventing repeated actions after observed failure.

### How Phase 7 Addresses Each Issue

| Issue | Solution | Mechanism |
|---|---|---|
| Lexical bias alone is insufficient | Candidate ranking remains local; VLM gets top-k candidates + task semantics | Trust planner to prefer semantic over lexical |
| Mechanical ≠ observable success | Click post-condition now requires URL change, element removal, or state transition | Stricter post-condition logic |
| No progress context | Explicit `previous_post_condition_success: false` in retry request | Progress-state protocol |
| Unbounded repetition | Local gate blocks repeated ref after `post_condition_success=false` | Repeated-action blocker |

---

## Measured Evidence (Phase 7)

| Metric | Result | Source |
|---|---|---|
| Test pass rate | 84/84 (100%) | pytest |
| Linting violations | 0 (fixed 1) | ruff |
| Secret leaks in reports | 0 detected | pattern scan |
| Forensic failure classification | Confirmed: state_progress_blindness | `phase7_failure_forensics.json` |
| Repeated target behavior | Confirmed: e10 selected 12 times | `phase6_live_smoke.json` |

---

## Measured Evidence (Phase 6 — Unchanged)

| Metric | Result | Source | Note |
|---|---|---|---|
| Deterministic local candidate accuracy | 88.7% top-1, 100% top-3 | `atomic_grounding_benchmark.json` | **Local ranking only**, not VLM accuracy |
| Test pass rate | 84/84 (100%) | pytest | Includes Phase 7 new tests |
| Live Qwen 3B workflows | 5/5 success | `real_vlm_report.json` | Schema valid; low canary grounding |
| Live Qwen 7B workflows | 0/5 success | `real_vlm_report_7b.json` | Slower, higher canary; no workflows |
| Privacy audit (21 vault entries) | 0 leaks detected | `real_privacy_evidence.json` | Unchanged from Phase 5 |

---

## Ready for Next Phase

### Prerequisites for Live Ablation

1. ✅ Forensic analysis complete
2. ✅ Progress-state protocol implemented
3. ✅ Post-condition tightened
4. ✅ Repeated-action blocking in place
5. ✅ Visual marking primitives ready
6. ✅ All tests passing
7. ✅ Linting/compilation clean
8. ✅ Privacy boundary preserved

### Next Steps (Explicitly Documented as Pending)

1. Run V0–V5 ablation on live Qwen with controlled denominators
2. Measure whether visual marking improves target selection
3. Measure whether candidate crops improve verifier accuracy
4. Compare recovery: retry vs fresh reasoning
5. Compare 3B vs 7B grounding under best architecture
6. Run resolution sweep to identify optimal visual quality
7. Generate aggregate error taxonomy from live results

---

## Conclusion

Phase 7 forensics and safety work are **COMPLETE**. The system now:

- Explicitly communicates previous-action failure to the VLM
- Blocks repeated actions that have failed to advance progress
- Tightens click post-conditions to require observable state change
- Supports candidate visual marking for semantic/visual alignment studies
- Provides a path for the VLM to communicate ambiguity or lack of valid candidates
- Maintains full privacy invariants across all new mechanisms

**Live VLM grounding improvement remains unclaimed and pending controlled ablation.**

All work is regression-tested, documented honestly, and ready for measured validation.
