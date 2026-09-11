"""Task Schema and Evaluation Models for Phase 16 Real-World Validation."""

from enum import Enum

from pydantic import BaseModel, Field


class TaskTier(str, Enum):
    TIER_A_SEARCH_KNOWLEDGE = "search_knowledge"
    TIER_B_ECOMMERCE = "ecommerce"
    TIER_C_TRAVEL = "travel"
    TIER_D_DEV_TOOLS = "dev_tools"
    TIER_E_PRODUCTIVITY_FORMS = "productivity_forms"
    TIER_F_DYNAMIC_PAGES = "dynamic_pages"
    TIER_G_VISUAL_HEAVY = "visual_heavy"
    TIER_H_ADVERSARIAL = "adversarial"


class ExecutionCondition(str, Enum):
    CONDITION_A_HUMAN = "human_baseline"
    CONDITION_B_AUTONOMOUS = "privateeye_autonomous"
    CONDITION_C_OVERSIGHT = "privateeye_oversight"


class TaskRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RealWorldTask(BaseModel):
    task_id: str
    tier: TaskTier
    title: str
    goal: str
    site_url: str
    risk_level: TaskRiskLevel = TaskRiskLevel.LOW
    expected_observable_end_state: str
    allowed_actions: list[str] = Field(default_factory=lambda: ["click", "fill", "select", "scroll", "navigate"])
    forbidden_actions: list[str] = Field(default_factory=lambda: ["checkout", "payment", "delete", "destroy"])
    expected_step_count: int = 5
    is_held_out: bool = False
    has_canary: bool = False
    canary_token: str | None = None


class StepTraceRecord(BaseModel):
    step: int
    url: str
    action_type: str
    target_ref: str | None = None
    target_name: str | None = None
    fast_path_used: bool = True
    vlm_fallback_used: bool = False
    perception_latency_ms: float = 0.0
    action_latency_ms: float = 0.0
    total_step_latency_ms: float = 0.0
    policy_permitted: bool = True
    policy_reason: str = "Permitted"
    post_condition_success: bool = True
    recovery_attempted: bool = False
    recovery_succeeded: bool = False
    human_intervened: bool = False
    intervention_reason: str | None = None


class TaskExecutionResult(BaseModel):
    task_id: str
    condition: ExecutionCondition
    success: bool
    final_url: str
    steps_executed: int
    expected_steps: int
    total_latency_seconds: float
    step_accuracy_rate: float
    fast_path_utilization_rate: float
    interventions_count: int = 0
    intervention_time_seconds: float = 0.0
    canary_leaks_detected: int = 0
    failure_class: str | None = None
    failure_root_cause: str | None = None
    traces: list[StepTraceRecord] = Field(default_factory=list)
