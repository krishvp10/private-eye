"""Process-Level Failure Taxonomy for Real-World Browser Agent Evaluation."""

from enum import Enum

from pydantic import BaseModel


class FailureClass(str, Enum):
    PERCEPTION = "PERCEPTION"
    DOM_ARIA = "DOM_ARIA"
    VISUAL = "VISUAL"
    CANDIDATE_RANKING = "CANDIDATE_RANKING"
    SEMANTIC_SELECTION = "SEMANTIC_SELECTION"
    PRIVACY = "PRIVACY"
    REDACTION = "REDACTION"
    POLICY = "POLICY"
    EXECUTION = "EXECUTION"
    POST_CONDITION = "POST_CONDITION"
    NO_PROGRESS = "NO_PROGRESS"
    RECOVERY = "RECOVERY"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    WEBSITE_VARIABILITY = "WEBSITE_VARIABILITY"
    ANTI_BOT = "ANTI_BOT"
    CAPTCHA = "CAPTCHA"
    NETWORK = "NETWORK"
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"
    UX = "UX"
    UNKNOWN = "UNKNOWN"


class FailureDiagnostic(BaseModel):
    task_id: str
    step: int
    failure_class: FailureClass
    root_cause: str
    is_recoverable: bool
    safety_boundary_held: bool = True
    evidence_snippet: str = ""
    regression_test_recommended: bool = True
