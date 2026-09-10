# ADR-0005: SQLite logs + single shared pydantic protocol module
Status: Accepted (2026-09-10)
Context: Need auditable run history and zero-drift client/server contract.
Decision: shared/protocol.py imported by both sides; SQLite (WAL) for runs/steps/redactions/metrics.
Alternatives: Postgres (rejected: no multi-writer need), JSONL (rejected: weak queryability for
benchmarks), hand-written JSON schemas duplicated per side (rejected: drift risk).
Consequences: One source of truth; evals are SQL queries; migration to Postgres documented for 10× scale.
