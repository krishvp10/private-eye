# Development

- Layout follows ARCHITECTURE.md containers: `client/`, `server/`, `shared/`, `eval/`, `demo_sites/`.
- Run tests: `pytest -q` (mock mode). Benchmarks: `pytest eval -m slow`.
- Mock server keeps client work GPU-independent; never commit with `PE_MOCK_VLM` assumptions baked in.
- Any new outbound field → update protocol.py + API_SPEC.md in the same PR.
- Coding standards: ruff defaults, mypy strict on shared/ + server/, type hints on public functions.
- Contribution: branch `feat/<id>-<slug>`; PR template = ticket ID + acceptance criteria checkboxes.
