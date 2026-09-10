# Getting Started

1. `git clone <repo> && cd private-eye`
2. Install the engineering skills for the active coding agent: `npx skills@latest add mattpocock/skills`, then run `/setup-matt-pocock-skills` once in this repository.
3. `uv sync` (or `python -m venv .venv && python -m pip install -r requirements.txt`)
4. `python -m playwright install chromium firefox`
5. Copy `.env.example → .env`; set `PE_SERVER=http://localhost:8000`, vault vars `PE_VAULT_NAME` etc.
6. Start demo sites: `docker compose up demo-sites` → open http://localhost:9001/kyc
7. Mock run (no GPU needed): `PE_MOCK_VLM=1 python -m client.agent --task "Complete the KYC form"`
8. Real server: `docker compose up server` (needs GPU + pre-seeded model cache) or Ollama fallback.
9. Evidence: `python eval/benchmark.py && python eval/latency.py` → `reports/`.
Troubleshooting: see docs/troubleshooting.md (seeded during build).
