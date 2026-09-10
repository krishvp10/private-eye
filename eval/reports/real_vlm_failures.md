# PrivateEye Real-VLM Failure Taxonomy

Standardized failure classification hierarchy recording the root cause of execution deviations

| Failure Class | Code | Failure Description |
| :--- | :--- | :--- |
| **Perception** | `FAIL_PERCEPTION` | DOM or visual extractor failed to detect an element or rendered coordinate bounding box accurately. |
| **Grounding** | `FAIL_GROUNDING` | Model proposed a target that does not match the semantic node in the captured ScreenGraph. |
| **Planning** | `FAIL_PLANNING` | Model proposed an illogical or non-advancing action sequence for the active workflow task. |
| **Schema** | `FAIL_SCHEMA` | Model returned malformed JSON or violated AgentAction Pydantic protocol constraints. |
| **Policy** | `FAIL_POLICY` | Model attempted an unwhitelisted action, emitted raw secret tokens, or attempted prompt injection. |
| **Execution** | `FAIL_EXECUTION` | Playwright failed to interact with the target locator (e.g. element covered, detached, or disabled). |
| **Network** | `FAIL_NETWORK` | HTTP timeout, connection drop, or socket abort during client-server VLM communication. |
| **Model** | `FAIL_MODEL` | Model internal runtime error, context length overflow, or hallucinated terminal state. |
| **Privacy** | `FAIL_PRIVACY` | Outbound leak interceptor detected sensitive PII or unredacted vault token crossing the wire. |
