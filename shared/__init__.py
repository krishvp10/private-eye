# shared/__init__.py
"""Shared schemas and protocol definitions for PrivateEye."""

from shared.protocol import (
    ActionTarget,
    AgentAction,
    BoundingBox,
    Detection,
    ExecutionResult,
    Redaction,
    RedactionMap,
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)

__all__ = [
    "ActionTarget",
    "AgentAction",
    "BoundingBox",
    "Detection",
    "ExecutionResult",
    "Redaction",
    "RedactionMap",
    "ScreenContext",
    "ScreenGraph",
    "ScreenNode",
]
