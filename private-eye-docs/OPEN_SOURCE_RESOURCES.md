# OPEN_SOURCE_RESOURCES.md (master matrix at bottom)

## Tier-1 verified resources

### Playwright — client browser control
Repo: github.com/microsoft/playwright · License: Apache-2.0 · Language: TS core, Python binding
Purpose: browser automation — capture, a11y snapshot, action execution.
Maturity: industry standard; used by SeeAct's own online-eval harness (verified).
Use directly: **YES** (primary dependency). Risk: low. Alternative: Selenium (rejected: a11y API weaker),
Puppeteer (rejected: Firefox support inferior).

### Qwen2.5-VL-7B-Instruct — server VLM
Repo: github.com/QwenLM/Qwen2.5-VL · HF: Qwen/Qwen2.5-VL-7B-Instruct · License: Apache-2.0 (verified:
Qwen2.5 family Apache-2.0 except 3B/72B).
Purpose: perceives sanitized screenshot + screen graph; emits AgentAction JSON.
Maturity: SOTA-class open VLM; vLLM-supported (requires vLLM ≥0.7.2, transformers ≥4.49 — pin both).
Use directly: YES via vLLM. Alternatives: Qwen3-VL (Apache-2.0, newer — EXPERIMENT: check vLLM support
matrix before committing), UI-TARS-1.5-7B (Apache-2.0, GUI-tuned — stronger grounding but worse
general chat), InternVL2.5-8B (MIT — heavier). Recommendation: start Qwen2.5-VL-7B (best docs).

### vLLM — server inference
Repo: github.com/vllm-project/vllm · License: Apache-2.0. Purpose: OpenAI-compatible serving, AWQ quants.
Use: YES. Fallback: Ollama (MIT) for laptop-GPU demos.

### MediaPipe BlazeFace — local face detection
Repo: github.com/google-ai-edge/mediapipe · License: Apache-2.0. Purpose: lightweight face boxes on device.
Use: YES (or ONNX port). Alternative: YuNet (OpenCV, Apache-2.0) — good swap if MediaPipe packaging stalls.

### ONNX Runtime — local inference
Repo: github.com/microsoft/onnxruntime · License: MIT. Use: YES (detectors exported to ONNX INT8).

### spaCy + regex — text PII
Repo: github.com/explosion/spaCy · License: MIT. Use: YES (NER for person names; regexes for
Aadhaar/PAN/phone/email). Alternative: Presidio (MIT, Microsoft) — actually recommended wrapper:
github.com/microsoft/presidio gives analyzer+anonymizer architecture we can borrow. **Recommendation:
adopt Presidio's RecognizerResult model; implement recognizers ourselves to avoid heavy deps.**

### FastAPI / Uvicorn — server framework. MIT. Use: YES.
### fcakyon/midv500 — MIDV-500→COCO converter. Use: YES for eval data (verify license of repo before
redistribution; dataset itself is research-use, docs public-domain).

## Flagged resources (license risk)

| Resource | Issue | Decision |
|---|---|---|
| Ultralytics YOLOv8/11 | AGPL-3.0 — copyleft triggers on network use if unmodified; enterprise license exists | **Avoid training/inference via ultralytics package**; use ONNX exports w/ non-AGPL runtimes, or pick YOLOX/PP-YOLOE+ (Apache-2.0). MVP doesn't need YOLO at all (a11y tree covers elements) |
| OmniParser icon_detect (v1/v2) | Ultralytics-based weights = AGPL | Only icon_detect_v3 (MIT, YOLOv9-based) + MIT caption models are usable; verify at download time |
| WIDER FACE | Research-only, no redistribution | Use locally for eval only; never ship images |
| SeeAct repo | Verify license before forking (research code) | Learn from, don't fork |

## Master resource matrix

| Resource | Type | URL | Purpose | License | Recommended? | Priority |
|---|---|---|---|---|---|---|
| Playwright | Browser automation | github.com/microsoft/playwright | Client capture+execution | Apache-2.0 | YES | P0 |
| Qwen2.5-VL-7B-Instruct | VLM weights | huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct | Server reasoning | Apache-2.0 | YES | P0 |
| vLLM | Inference server | github.com/vllm-project/vllm | Serve VLM | Apache-2.0 | YES | P0 |
| Ollama | Inference (fallback) | ollama.com | Laptop demo | MIT | YES (fallback) | P1 |
| ONNX Runtime | Local inference | github.com/microsoft/onnxruntime | Client CV | MIT | YES | P0 |
| MediaPipe BlazeFace | Face detector | github.com/google-ai-edge/mediapipe | Redaction channel | Apache-2.0 | YES | P0 |
| spaCy | NER | github.com/explosion/spaCy | Text PII | MIT | YES | P0 |
| Presidio (architecture ref) | PII framework | github.com/microsoft/presidio | Design reference | MIT | Partial | P1 |
| MIDV-500 (+fcakyon/midv500) | Eval dataset | arxiv.org/abs/1807.05786 | Doc/face eval | Research | YES (eval only) | P0 |
| WIDER FACE | Eval dataset | mmlab.ie.cuhk.edu.hk/projects/WIDERFace | Face recall | Research-only | YES (eval only) | P1 |
| OmniParser v3 | Screen parsing | github.com/microsoft/OmniParser | V1 on-device parsing | MIT (v3 only) | V1 | P2 |
| UI-TARS-1.5-7B | GUI VLM | huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B | V1 server upgrade | Apache-2.0 | V1 | P2 |
| browser-use | Reference agent | github.com/browser-use/browser-use | Competitive study | MIT | Study only | P2 |
| OpenImages | Detection data | storage.googleapis.com/openimages | Eval negatives | CC BY 4.0 | Optional | P3 |
