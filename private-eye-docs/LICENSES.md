# LICENSES.md — Dependency License Register

| Component | License | Usage | Redistribution/attribution notes | Concern |
|---|---|---|---|---|
| Playwright (incl. browsers) | Apache-2.0 | client automation | notice file in repo | None |
| ONNX Runtime | MIT | local inference | include license | None |
| MediaPipe (BlazeFace weights) | Apache-2.0 | face detection | include license; model card | None |
| spaCy + en_core_web_sm | MIT / CC BY-SA 4.0 (model) | NER | model credit line in README | Low — check model card wording |
| Qwen2.5-VL-7B-Instruct | Apache-2.0 | server VLM | include LICENSE from HF repo | None |
| vLLM | Apache-2.0 | inference server | include license | None |
| transformers | Apache-2.0 | model glue | pin version | None |
| FastAPI, Uvicorn, pydantic | MIT | server | — | None |
| Ollama | MIT | fallback runtime | — | None |
| **Ultralytics (YOLOv8/11)** | **AGPL-3.0** | **NOT USED** | copyleft triggers on network use; enterprise license paid | **FLAGGED — banned from repo (CI check)** |
| OmniParser | MIT (icon_detect_v3, caption models); AGPL (older icon_detect) | V1 optional | download only v3 weights; verify LICENSE file at fetch | Flagged — gate at download |
| MIDV-500/2020 | Research use; source docs public-domain/Wikimedia | eval only, local | do not redistribute; attribution per documents.pdf | Medium — keep out of repo, gitignored |
| WIDER FACE | Research-only | eval only, local | no redistribution | Medium |
| browser-use, SeeAct repos | MIT / verify SeeAct | study only | — | Low |
| OpenImages annotations | CC BY 4.0 | optional eval | attribution | Low |
| Demo site assets (faces) | Generated/synthetic (This Person Does Not Exist-style or generated.photos-style) | demo | synthetic only, no real persons | None |

**Compatibility verdict**: MVP stack is clean Apache/MIT. Only exposure = AGPL if someone sneaks
Ultralytics in → CI import check rejects `ultralytics`, `yolo` imports.
