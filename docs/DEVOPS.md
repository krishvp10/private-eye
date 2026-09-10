# DEVOPS.md

- **Git**: trunk-based. `main` protected; short-lived feature branches; PR = 1 reviewer + green CI.
- **Commits**: conventional commits (`feat(client): …`).
- **CI (GitHub Actions)**: ruff · mypy(shared,server) · pytest + e2e (mock server) · pip-audit ·
  leak-grep · benchmark gate (IoU≥0.95).
- **CD**: none beyond `docker compose up` (hackathon). V1: compose pull + health-gated restart.
- **Environments**: dev (mock server), staging (LAN GPU), demo (staging + projector dashboard).
  Secrets via `.env` (gitignored) + OS keychain for vault key.
- **IaC**: one `docker-compose.yml` + Dockerfiles; no K8s (justified: single-node demo, see ADR-0001).
- **Feature flags**: env vars only (`PE_MOCK_VLM=1`, `PE_HEADFUL=1`).
- **Releases**: tag `demo-v1.0` for the event; lockfiles committed.
