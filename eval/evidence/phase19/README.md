# Phase 19 raw-evidence contract

Put one JSON object per line in `checkpoint_pairs.jsonl`. Each pair must have
one `condition: "off"` and one `condition: "on"`, sharing identical
`task_id`, `initial_state_hash`, `environment`, `model`, `seed`, `step_budget`,
and `fault_schedule_hash`.

Required fields are enforced by `eval/phase19_causal_engine.py`:

`pair_id`, `task_id`, `initial_state_hash`, `environment`, `model`, `seed`,
`step_budget`, `fault_schedule_hash`, `condition`, `success`,
`first_failure_step`, `rollback_count`, and `recovery_success`.

Do not store fabricated traces, secret values, or participant personal data.
