"""
Re-export of shared schemas for convenience and backward compatibility.
"""

from shared.protocol import (
    ActionTarget,
    ActionType,
    AgentAction,
    BoundingBox,
    Detection,
    DetectionCategory,
    DetectionSource,
    ExecutionResult,
    ImageMeta,
    Redaction,
    RedactionMap,
    RedactionMethod,
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)

__all__ = [
    "ActionTarget",
    "ActionType",
    "AgentAction",
    "BoundingBox",
    "Detection",
    "DetectionCategory",
    "DetectionSource",
    "ExecutionResult",
    "ImageMeta",
    "Redaction",
    "RedactionMap",
    "RedactionMethod",
    "ScreenContext",
    "ScreenGraph",
    "ScreenNode",
]
