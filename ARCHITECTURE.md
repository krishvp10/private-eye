# ARCHITECTURE.md

## System Context

```mermaid
flowchart LR
    U[User] -->|task + confirmation| C[PrivateEye Client<br/>Playwright browser]
    C -->|sanitized JPEG + screen graph + RedactionMap| S[PrivateEye Server<br/>FastAPI + vLLM]
    S -->|AgentAction JSON| C
    C --> D[(Local secret profile<br/>values never sent)]
    E[Eval harness] -->|labeled corpus| C
    C --> M[(Metrics DB<br/>SQLite)]
    S --> M
```

## Container diagram

```mermaid
flowchart TB
    subgraph client[Client machine — local trust boundary]
        A[agent loop] --> CAP[capture.py<br/>screenshot + a11y tree]
        CAP --> DET[detectors:<br/>DOM heuristics / regex+NER / face]
        DET --> MASK[masker.py<br/>blackout · blur · digit-mask]
        MASK --> ENC[payload encoder<br/>JPEG q70 ≤1280px]
        A --> EXEC[execute.py<br/>getByRole/getByLabel]
        EXEC --> VAULT[local value vault]
        A --> LOG[(run log SQLite)]
    end
    subgraph server[Server — cloud/LAN GPU box]
        API[/v1/analyze/] --> GUARD[schema guard + LLM01 filter]
        GUARD --> VLM[[Qwen2.5-VL-7B · vLLM]]
        VLM --> ACT[AgentAction JSON]
        API --> LOG2[(run log SQLite)]
    end
    ENC --HTTPS/LAN--> API
    ACT --JSON--> EXEC
```

## Sequence: one step

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client agent
    participant S as Server
    U->>C: task: "Complete the KYC form"
    loop until done
        C->>C: screenshot + a11y snapshot
        C->>C: detect PII (DOM/regex-NER/face)
        C->>C: redact pixels + build RedactionMap
        C->>S: POST /v1/analyze {image, screen_graph, redactions, url}
        S->>S: validate schema, guard action space
        S->>S: VLM decides next action
        S-->>C: {action: fill, target:{label:"Full name"}, value_ref:"profile.name"}
        alt destructive action (submit/pay/send)
            C->>U: confirmation prompt
            U-->>C: approve
        end
        C->>C: resolve value_ref LOCALLY, Playwright fill
        C->>C: log step timing + redactions
    end
    C-->>U: task complete + report
```

## Trust boundaries

1. **TB-1 Client↔Server**: only `ScreenContext` may cross. Enforced by: outbound interceptor that runs
   detectors on the *encoded* image and REFUSES to send if any unredacted PII match (defense-in-depth
   beyond the redact step) + static ban on serializing vault values.
2. **TB-2 Vault**: secret profile lives in client memory/env only; value_ref indirection everywhere else.
3. **TB-3 VLM output**: commands pass a whitelist filter (action ∈ enum, target must exist in screen_graph)
   before execution — LLM01 prompt-injection mitigation.

## Failure boundaries

- Client CV failure → skip frame, reuse last valid RedactionMap, alert user.
- Server unreachable → pause loop, queue nothing (no local PII buffering), ask user.
- Action execution failure → retry ≤2 with fresh context → escalate to ask_user (NFR-007).
- VLM emits invalid JSON → one repair retry with schema-error feedback → ask_user.

## Deployment architecture
- Dev: everything on one laptop; server in mock mode (hardcoded actions) so client work isn't GPU-blocked.
- Staging: server on LAN GPU machine (docker compose), client laptop, demo sites container.
- Production (demo): same as staging + dashboard on projector.
- Disaster recovery: run logs are disposable (RPO: none needed); demo sites are stateless containers (RTO: restart).

## Scalability & availability
See SCALABILITY.md. MVP is single-agent by design; horizontal scaling = N stateless vLLM replicas
behind a load balancer when needed (V1+), no architecture change.
