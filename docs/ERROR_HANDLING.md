# ERROR_HANDLING.md

## Taxonomy
USER (bad task/URL) · CLIENT_CV (detector/face model) · CLIENT_EXEC (Playwright timeout, detached node)
· NETWORK · SERVER_SCHEMA · VLM_OUTPUT (invalid JSON / non-whitelisted action) · VLM_REASONING (stuck loop)
· PRIVACY_BLOCK (leak-check fired — highest severity).

## Policy per class
| Class | Detection | Handling |
|---|---|---|
| PRIVACY_BLOCK | outbound interceptor | Halt run, red banner, never retry silently |
| CLIENT_EXEC | Playwright timeout | Retry ≤2 w/ fresh context → escalate ask_user with screenshot |
| VLM_OUTPUT | schema/whitelist fail | One repair prompt w/ error feedback → ask_user |
| VLM_REASONING | same action 3× / no done in 25 steps | Interrupt, summarize state, ask_user |
| NETWORK | timeout 10 s / conn fail | Pause loop (no PII queued) → resume or abort on user choice |
| SERVER_SCHEMA | 422 | Client bug — log + abort (never silently downgrade) |
| CLIENT_CV | detector exception | Skip frame, reuse last RedactionMap (≤3×) → pause |

## Cross-cutting
- **Timeouts**: capture 5 s, HTTP 10 s connect / 60 s total, exec 10 s.
- **Backoff**: only network retries (exp 1s→2s→4s, jittered); exec/VLM retries use fresh context, not delay.
- **Idempotency**: analyze is side-effect-free; client re-POST safe. Executes are naturally idempotent
  for fills (same value), guarded for clicks (confirm gate on destructive).
- **Dead letters**: failed steps → `steps.result=escalated` + dashboard entry; nothing retried blind.
- **Error tracking**: `errors` view in dashboard grouped by class; every error carries run_id + step.
