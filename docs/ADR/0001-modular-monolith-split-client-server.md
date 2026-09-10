# ADR-0001: Two-process split (local client + remote server), no microservices
Status: Accepted (2026-09-10)
Context: Problem mandates client-side privacy enforcement + server-side reasoning. Temptation to
add message queues, workers, K8s.
Decision: Exactly two deployable units — client agent process, server (FastAPI+vLLM) — talking over one
JSON endpoint. SQLite logs. Docker Compose only.
Alternatives: K8s+queue microservices (rejected: zero requirement evidence; demo unreproducible);
single-process everything (rejected: server must be deployable off-device per problem statement).
Consequences: Simple ops, fast debugging; scaling story documented in SCALABILITY.md for later.
Risks: server becomes hot spot → mitigated by vLLM batching + replica scaling (V1+).
Migration: stateless API → LB + replicas; SQLite → Postgres when >10 writers.
