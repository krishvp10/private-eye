# AI_ML.md

## Models (verified licenses, Sept 2026)

| Role | Model | Size | License | Hosting |
|---|---|---|---|---|
| Server reasoning | Qwen2.5-VL-7B-Instruct | 7B (AWQ 4-bit ≈ 5.5 GB) | Apache-2.0 | vLLM ≥0.7.2 + transformers ≥4.49 (pinned) |
| Server fallback | qwen2.5vl:7b via Ollama | 7B q4 | Apache-2.0 | single GPU/laptop |
| V1 server upgrade (experiment) | UI-TARS-1.5-7B | 7B | Apache-2.0 | same stack |
| Client face channel | BlazeFace (ONNX port) | <1 MB | Apache-2.0 | ONNX Runtime CPU, ≤30 ms/img |
| Client text channel | spaCy en_core_web_sm + regex | 12 MB | MIT | local |
| V1 screen parsing (optional) | OmniParser icon_detect_v3 + Florence-2 caption | 1–2 GB | MIT (v3 only; older weights AGPL) | local, if time |

## Why not bigger / hosted
Rubric caps server flexibility ("offline deployable, cloud allowed during SIH") — 7B AWQ fits a 12 GB
GPU at ≤2 s/token-batch latency for our ≤1.5k-token prompts; hosted GPT-4o-class would violate the
open-weights requirement and the privacy story (third-party processor).

## Prompt architecture
- **System (fixed)**: role, action enum, target-must-exist rule, "you are seeing a sanitized screen;
  RedactionMap tells you what was hidden — never request hidden values, use value_ref", JSON-only output.
- **User**: task + last-action result + screen_graph (textualized, capped 400 nodes, priority: interactive
  elements) + redaction legend + sanitized image.
- Temperature 0; JSON-mode; one repair pass on schema failure; deterministic seeds for eval reruns.

## Hallucination & guardrail design
Grounding never delegated to the VLM (client a11y does it) → the classic SeeAct 20–25 pt grounding gap
doesn't apply to *finding* elements, only to *choosing* among them. Residual risk: wrong choice →
caught by post-condition checks (e.g., expected URL/field state) → retry/escalate (NFR-007).

## Prompt-injection handling
Page text is data, not instructions: system prompt forbids following embedded commands; guard validates
action enum + target existence; destructive actions need human approval (SECURITY.md TB-3).

## Evaluation framework
- Offline: action-choice accuracy on 60 labeled step-decisions from our demo flows (human-judged).
- Online: J-1/J-V1 flow success rate over 20 trials; steps-to-complete; escalation rate.
- Redaction/detection: see TESTING.md benchmark (this is where AI meets the 40% PII/redaction rubric).

## Privacy-by-design for ML
No fine-tuning on user data (MVP). No embeddings stored. Model inputs/logs scanned by leak-check.
