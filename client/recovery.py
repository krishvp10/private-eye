"""Bounded, privacy-safe action recovery policy."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryDecision:
    retry: bool
    retry_count: int
    escalate: bool
    failure_class: str


class RecoveryController:
    """Retry non-destructive failures, then escalate instead of looping forever."""

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max(0, max_retries)

    def decide(self, failure_class: str, retry_count: int, destructive: bool) -> RecoveryDecision:
        if destructive or failure_class == "policy":
            return RecoveryDecision(False, retry_count, True, failure_class)
        if retry_count < self.max_retries:
            return RecoveryDecision(True, retry_count + 1, False, failure_class)
        return RecoveryDecision(False, retry_count, True, failure_class)
