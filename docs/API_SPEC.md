# API_SPEC.md

Base: `http://server:8000` · Versioning: path `/v1` · Auth: none at MVP (LAN demo); add shared-secret
header `X-PE-Key` in production profile · Format: JSON over HTTPS (or ssh-tunneled HTTP at demo).

## POST /v1/analyze

```text
Method: POST
Path: /v1/analyze
Purpose: Submit sanitized screen context; receive next agent action
Authentication: none (MVP) / X-PE-Key (prod profile)
Request: ScreenContext (see schema)
Response: 200 → AgentAction | 422 → SchemaError | 429 → rate limited (demo: 10 rps/IP)
Errors: {"error": {"code": "SCHEMA_INVALID"|"IMAGE_TOO_LARGE"|"UNSUPPORTED_ACTION", "detail": "..."}}
Rate limits: 10 rps/IP (token bucket, in-memory)
Idempotency: analyze is read-only w.r.t. world; client retries are safe; header Idempotency-Key logged
Caching: none (screens differ per step)
Validation: pydantic strict; image ≤600 KB; URL scheme http/https only
```

```json
// ScreenContext
{
  "version": "1.0",
  "run_id": "uuid",
  "step": 3,
  "url": "http://demo.local/kyc",
  "image_b64": "<jpeg>",
  "image_meta": {"w": 1280, "h": 800, "fmt": "jpeg", "quality": 70},
  "screen_graph": {"root": {"role": "WebArea", "name": "KYC", "children": [
    {"role": "textbox", "name": "Full name", "id": "el_12", "bbox": [120, 300, 260, 24]},
    {"role": "button", "name": "Submit", "id": "el_18", "bbox": [120, 600, 90, 30]}]}},
  "redactions": [
    {"region": [400, 150, 220, 60], "category": "aadhaar", "method": "mask_digits"},
    {"region": [700, 140, 80, 80], "category": "face", "method": "blur"}
  ],
  "task": "Complete the KYC form and stop before final submit"
}

// AgentAction (response)
{"action": "fill", "target": {"kind": "a11y", "role": "textbox", "name": "Full name"},
 "value_ref": "profile.full_name", "reason": "Name field is empty; form requires it."}
{"action": "click", "target": {"kind": "a11y", "role": "button", "name": "Next"}}
{"action": "scroll", "dy": 640}
{"action": "done", "summary": "All fields filled; awaiting user submit."}
{"action": "ask_user", "question": "Which plan tier should I select?"}
```

**Forbidden in responses (server-side enforced):** raw `value` fields on fill (client must resolve
`value_ref`); targets not present in `screen_graph`; actions outside the enum.

## GET /v1/health
`{"status":"ok","model":"Qwen/Qwen2.5-VL-7B-Instruct","vllm":"0.7.x","gpu":"..."}`

## GET /v1/runs/{run_id}
Read-only audit view of logged steps (no PII). Powers dashboard report.

## Webhooks / events
Not in MVP. V1: server-sent events for multi-step planning streams.

## Server → VLM prompt contract (internal)
Rendered from ScreenContext: system prompt (fixed), user message = [sanitized image + textual screen
graph + redaction legend + task + last action result]. Temperature 0 for determinism. JSON-mode output
parsed to AgentAction; parse failure → one repair pass.
