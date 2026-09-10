# SCALABILITY.md

- **Initial scale**: 1 client ↔ 1 server. Bottleneck = single vLLM instance (fine for demo).
- **10× (≈10 concurrent agents)**: vLLM continuous batching handles this on one 24 GB GPU (AWQ 7B);
  API stateless; SQLite→Postgres swap for run logs (ADR when it happens).
- **100×**: N stateless vLLM replicas + least-load LB; per-agent affinity only to log shard; demo-sites
  replicated. No protocol change.
- **Bottlenecks in order**: GPU VRAM (batch size) → prompt tokens (a11y cap) → network (JPEG size).
- **Deliberate non-scalings**: no queues/Kafka/sharding in MVP — unjustified (see ADR-0001);
  horizontal scaling of *inference* is the only planned axis.
