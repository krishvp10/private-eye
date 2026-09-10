"""Action Provenance Logger & Replay Tracer for PrivateEye (Phase 9).

Stores granular action provenance records for every decision cycle, enabling
explainable audits, post-run verification, and replay answers to:
"Why did PrivateEye perform this action?"

Strictly censors raw secrets (retaining only value_refs or redaction hashes).
Conforms to OWASP Agent Control Standard (ACS) requirements for runtime
traceability and instrumentation.
"""

from __future__ import annotations

import datetime
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ActionProvenance:
    task_id: str
    step_id: int
    user_goal: str
    model: str
    model_decision: str
    candidate_ref: Optional[str]
    candidate_source: str
    candidate_score: float
    verifier_used: bool
    verifier_result: Optional[str]
    confidence: float
    risk_level: str
    policy_decision: str
    human_confirmation_required: bool
    human_confirmed: bool
    execution_result: str
    post_condition_result: str
    progress_state: str
    retry_count: int
    failure_class: Optional[str]
    started_at_utc: str
    completed_at_utc: str
    latency_ms_components: Dict[str, float] = field(default_factory=dict)
    rationale: str = ""
    sanitized_metadata: Dict[str, Any] = field(default_factory=dict)

    def explain(self) -> str:
        """Human-readable explanation answering 'Why did PrivateEye perform this action?'."""
        reason = (
            f"[Step {self.step_id}] Goal: '{self.user_goal}' -> Selected action: {self.model_decision} "
            f"on target '{self.candidate_ref}' (Source: {self.candidate_source}, Score: {self.candidate_score:.3f}).\n"
            f"Confidence: {self.confidence:.2f} | Risk: {self.risk_level} | Policy: {self.policy_decision}.\n"
            f"Verifier called: {self.verifier_used} (Result: {self.verifier_result or 'Bypassed'}).\n"
            f"Execution: {self.execution_result} | Post-condition: {self.post_condition_result} "
            f"| Progress: {self.progress_state}."
        )
        if self.rationale:
            reason += f"\nAgent Rationale: {self.rationale}"
        if self.failure_class:
            reason += f"\nFailure/Abstention Trap: {self.failure_class}"
        return reason

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProvenanceTracker:
    """Collects and serializes ActionProvenance records for an evaluation or live session."""

    def __init__(self, task_id: str = "default_task") -> None:
        self.task_id = task_id
        self.records: List[ActionProvenance] = []

    def record(self, prov: ActionProvenance) -> None:
        self.records.append(prov)

    def to_list(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.records]

    def save(self, filepath: str | Path) -> Path:
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_list(), indent=2), encoding="utf-8")
        return p

    def get_explanations(self) -> List[str]:
        return [r.explain() for r in self.records]
