"""Frozen Release Candidate Configuration for PrivateEye v1.0-RC.

Specifies all hyper-parameters, thresholds, verifier modes, policy switches,
and fail-closed invariants for deployment and reproducible evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

RELEASE_VERSION: Final[str] = "v1.0-RC"
PRIMARY_MODEL: Final[str] = "qwen2.5-vl:3b"
BACKEND_RUNTIME: Final[str] = "Ollama"
DEFAULT_RESOLUTION_PX: Final[int] = 768
MAX_RESOLUTION_PX: Final[int] = 1024
CANDIDATE_K: Final[int] = 5
TEMPERATURE: Final[float] = 0.0

CONFIDENCE_THRESHOLD_HIGH: Final[float] = 0.88
CONFIDENCE_THRESHOLD_LOW: Final[float] = 0.65

VERIFIER_MODE: Final[str] = "selective"
RECOVERY_STRATEGY: Final[str] = "fresh_reasoning"
MAX_RECOVERY_RETRIES: Final[int] = 2

POLICY_ENGINE_ENABLED: Final[bool] = True
FAIL_CLOSED_ENABLED: Final[bool] = True
KILL_SWITCH_ENABLED: Final[bool] = True
HUMAN_CONFIRMATION_FOR_HIGH_RISK: Final[bool] = True


@dataclass(frozen=True)
class ReleaseConfig:
    version: str = RELEASE_VERSION
    model: str = PRIMARY_MODEL
    backend: str = BACKEND_RUNTIME
    resolution: int = DEFAULT_RESOLUTION_PX
    max_resolution: int = MAX_RESOLUTION_PX
    candidate_k: int = CANDIDATE_K
    temperature: float = TEMPERATURE
    confidence_high: float = CONFIDENCE_THRESHOLD_HIGH
    confidence_low: float = CONFIDENCE_THRESHOLD_LOW
    verifier_mode: str = VERIFIER_MODE
    recovery_strategy: str = RECOVERY_STRATEGY
    max_retries: int = MAX_RECOVERY_RETRIES
    policy_engine: bool = POLICY_ENGINE_ENABLED
    fail_closed: bool = FAIL_CLOSED_ENABLED
    kill_switch: bool = KILL_SWITCH_ENABLED
    human_confirmation_high_risk: bool = HUMAN_CONFIRMATION_FOR_HIGH_RISK

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "model": self.model,
            "backend": self.backend,
            "resolution": self.resolution,
            "max_resolution": self.max_resolution,
            "candidate_k": self.candidate_k,
            "temperature": self.temperature,
            "confidence_high": self.confidence_high,
            "confidence_low": self.confidence_low,
            "verifier_mode": self.verifier_mode,
            "recovery_strategy": self.recovery_strategy,
            "max_retries": self.max_retries,
            "policy_engine": self.policy_engine,
            "fail_closed": self.fail_closed,
            "kill_switch": self.kill_switch,
            "human_confirmation_high_risk": self.human_confirmation_high_risk,
        }


FROZEN_RELEASE_CONFIG: Final[ReleaseConfig] = ReleaseConfig()
