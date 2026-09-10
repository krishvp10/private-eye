# Phase 6 Research Notes

## Scope

Phase 6 addresses browser grounding: selecting a correct executable browser
target from sanitized visual and semantic context without sending private field
values to the remote model.

## Primary sources

### Playwright ARIA snapshots

Source: <https://playwright.dev/python/docs/api/class-page#page-aria-snapshot>

Playwright documents ARIA snapshots as accessibility-oriented page state. The
installed runtime also exposes the AI-mode snapshot path used by
`client/capture.py`, including refs and boxes. PrivateEye therefore uses the
browser's semantic representation as the authoritative candidate source rather
than asking the VLM to invent pixel coordinates.

### Ollama structured outputs

Source: <https://docs.ollama.com/capabilities/structured-outputs>

Ollama documents JSON-schema-constrained responses and explicitly includes
vision requests. PrivateEye can therefore require an action schema while still
keeping local policy and candidate validation authoritative. Schema validity is
not treated as grounding correctness.

### Qwen structured tool interaction

Source: <https://qwen.readthedocs.io/en/latest/framework/function_call.html>

Qwen documents application-controlled function/tool interaction: the model
selects a structured operation, while the application executes it and may
provide results for further reasoning. This supports the Phase 6 separation
between remote semantic selection and local Playwright execution.

## Design implications

1. Generate candidates locally from visible, enabled ScreenGraph nodes.
2. Transmit only safe metadata: ref, role, non-sensitive name, state, box, and
   sensitivity marker.
3. Replace sensitive candidate names with `[REDACTED FIELD]` before transmission.
4. Prefer `candidate_ref`/`ref` over arbitrary coordinates.
5. Reject unknown or stale refs locally.
6. Use deterministic local ranking before remote reasoning to reduce ambiguity.
7. Treat low-confidence or near-tied rankings as ambiguous rather than guessing.
8. Measure target accuracy independently from workflow completion.

## Evidence boundary

The new 120-case benchmark measures deterministic local candidate ranking. It
does not measure Qwen's live grounding accuracy, verifier quality, production
privacy, or legal compliance. Those remain separate Phase 6 experiments.
