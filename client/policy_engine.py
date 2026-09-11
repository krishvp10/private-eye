"""Local Safety Policy Engine for PrivateEye (Phase 8.6).

Formalizes action-risk tiers and enforces client-side safety guardrails:
- LOW RISK: scroll, read-only navigation, non-sensitive tab clicks.
- MEDIUM RISK: select, non-sensitive form edits, search queries.
- HIGH RISK: delete, purchase, submit, payment, password update, sensitive PII fills.

Enforces:
1. Risk classification based on action type, element semantics, and sensitivity.
2. Minimum confidence requirements by risk class.
3. Mandatory verification requirements for high-risk and sensitive actions.
4. Human-in-the-loop confirmation seams for irreversible operations.
"""

from dataclasses import dataclass
from enum import Enum

from shared.protocol import ActionType, SafeCandidate

HIGH_RISK_KEYWORDS = {
    "delete", "remove", "terminate", "destroy", "cancel subscription",
    "purchase", "pay", "order", "buy", "checkout", "transfer",
    "password", "pin", "ssn", "aadhaar", "pan", "cvv", "credit card",
}


class RiskClass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class PolicyDecision:
    action_permitted: bool
    risk_class: RiskClass
    requires_human_confirmation: bool
    requires_verifier: bool
    min_confidence_required: float
    reason: str


class LocalPolicyEngine:
    """Authoritative client-side safety policy gate."""

    def __init__(self, high_confidence_threshold: float = 0.88, medium_confidence_threshold: float = 0.65) -> None:
        self.high_conf = high_confidence_threshold
        self.med_conf = medium_confidence_threshold

    def classify_risk(
        self,
        action: ActionType,
        candidate: SafeCandidate | None = None,
        task: str = "",
        value_ref: str | None = None,
    ) -> RiskClass:
        """Classify the action risk tier based on action type, target name, and sensitivity."""
        # Check high-risk triggers
        if candidate and candidate.sensitive:
            return RiskClass.HIGH

        if value_ref and any(k in value_ref.lower() for k in ["password", "pin", "card", "cvv", "aadhaar", "pan"]):
            return RiskClass.HIGH

        cand_name = (candidate.name if candidate else "").lower()
        task_lower = task.lower()

        if any(kw in cand_name or kw in task_lower for kw in HIGH_RISK_KEYWORDS):
            return RiskClass.HIGH

        if action in (ActionType.FILL, ActionType.SELECT):
            return RiskClass.MEDIUM

        if action == ActionType.CLICK:
            role = candidate.role.lower() if candidate else ""
            if role in ("tab", "link"):
                return RiskClass.LOW
            return RiskClass.MEDIUM

        if action in (ActionType.SCROLL, ActionType.NAVIGATE, ActionType.DONE):
            return RiskClass.LOW

        return RiskClass.MEDIUM

    def evaluate_policy(
        self,
        action: ActionType,
        confidence: float,
        candidate: SafeCandidate | None = None,
        task: str = "",
        value_ref: str | None = None,
        verifier_passed: bool = False,
    ) -> PolicyDecision:
        """Evaluate whether a proposed action satisfies the local safety policy."""
        risk = self.classify_risk(action, candidate, task, value_ref)

        if risk == RiskClass.LOW:
            permitted = confidence >= 0.50
            return PolicyDecision(
                action_permitted=permitted,
                risk_class=risk,
                requires_human_confirmation=False,
                requires_verifier=False,
                min_confidence_required=0.50,
                reason="Low risk action permitted." if permitted else "Confidence too low even for low-risk action.",
            )

        if risk == RiskClass.MEDIUM:
            permitted = confidence >= self.med_conf
            requires_verifier = (confidence < self.high_conf) and not verifier_passed
            return PolicyDecision(
                action_permitted=permitted,
                risk_class=risk,
                requires_human_confirmation=False,
                requires_verifier=requires_verifier,
                min_confidence_required=self.med_conf,
                reason=(
                    "Medium risk action permitted."
                    if permitted
                    else f"Confidence {confidence:.2f} below medium-risk threshold ({self.med_conf:.2f})."
                ),
            )

        # HIGH RISK
        # High risk requires confidence >= 0.88
        if confidence < self.high_conf:
            return PolicyDecision(
                action_permitted=False,
                risk_class=risk,
                requires_human_confirmation=True,
                requires_verifier=True,
                min_confidence_required=self.high_conf,
                reason=f"High-risk action blocked: confidence {confidence:.2f} < {self.high_conf:.2f}.",
            )

        # Irreversible high risk (delete, purchase, money transfer) requires explicit confirmation
        cand_name = (candidate.name if candidate else "").lower()
        is_irreversible = any(kw in cand_name or kw in task.lower() for kw in ["delete", "terminate", "purchase", "pay", "transfer"])

        return PolicyDecision(
            action_permitted=True,
            risk_class=risk,
            requires_human_confirmation=is_irreversible,
            requires_verifier=True,
            min_confidence_required=self.high_conf,
            reason="High-risk action verified; confirmation required if irreversible." if is_irreversible else "High-risk action verified.",
        )
