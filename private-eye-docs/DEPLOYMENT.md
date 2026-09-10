# DEPLOYMENT.md

## Topology (event)
- Laptop A (client): agent + dashboard + vault + demo browser (headful).
- Machine B (server): any Linux + NVIDIA GPU 12 GB+, or cloud instance (RunPod/Colab bridge);
  docker compose services: `server` (FastAPI+vLLM AWQ), `demo-sites` (nginx:9001-9003), `dashboard` (static).
- Network: venue LAN; demo uses `ssh -L 8000:localhost:8000` tunnel client→server (no cert hassle);
  prod profile: Caddy + internal TLS.

## Resource estimates
| Node | CPU | RAM | GPU | Disk |
|---|---|---|---|---|
| Client | 2–4 cores | 4 GB (RSS cap 1.5 GB) | none | 3 GB (browsers+models) |
| Server | 8 cores | 32 GB | 12–16 GB VRAM (AWQ 7B) or Ollama q4 on 8 GB | 20 GB (model+images) |

## Cold-start checklist (at venue, ≤20 min)
1. `docker compose up -d demo-sites dashboard` → verify http://localhost:9001/kyc renders.
2. Server: pull model cache (pre-seeded in image) → `vllm serve` health 200.
3. Client: `playwright install` pre-done; `PE_SERVER=http://localhost:8000 python -m client.agent --selftest`.
4. Run `eval/benchmark.py` once to warm caches and confirm metric targets.
5. Packet-capture script ready on screen for the "what left the machine" moment.

## Backup/restore
Demo sites stateless; DB disposable. Only backup: the corpus + lockfiles (git).
