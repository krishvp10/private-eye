"""Telemetry and Trace Recorder for Real-World Tasks."""

import json
from pathlib import Path

from eval.real_world.task_schema import StepTraceRecord, TaskExecutionResult


class ExecutionRecorder:
    """Collects and serializes per-step execution traces, screenshots, and telemetry."""

    def __init__(self, trace_dir: Path | None = None) -> None:
        self.trace_dir = trace_dir or Path("eval/reports/traces")
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.current_traces: list[StepTraceRecord] = []

    def record_step(self, trace: StepTraceRecord) -> None:
        self.current_traces.append(trace)

    def save_task_run(self, result: TaskExecutionResult) -> Path:
        out_file = self.trace_dir / f"{result.task_id}_{result.condition.value}.json"
        out_file.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
        return out_file

    def clear(self) -> None:
        self.current_traces.clear()
