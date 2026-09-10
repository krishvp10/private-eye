"""Adaptive Image Resolution Policy for PrivateEye.

Implements empirical resolution scaling:
- Default: 768px (MEDIUM, ~400k max pixels) for standard UI pages.
- Dynamic escalation to 1024px (HIGH, ~800k max pixels) when:
  - Any candidate target has bounding box dimension < 30px (small icons, checkboxes)
  - Grounding confidence is in the medium ambiguity band (0.65 <= confidence < 0.88)
- Local crop verification is triggered if ambiguity persists.
"""

from dataclasses import dataclass
from typing import Any, cast
from shared.protocol import SafeCandidate

RESOLUTION_TIERS: dict[str, dict[str, Any]] = {
    "LOW_448": {
        "max_pixels": 256 * 28 * 28,  # ~200k pixels
        "target_dimension": "448x448",
        "latency_factor": 0.65,
        "vram_gb": 2.8,
    },
    "MEDIUM_768": {
        "max_pixels": 512 * 28 * 28,  # ~400k pixels
        "target_dimension": "768x768",
        "latency_factor": 1.0,
        "vram_gb": 3.8,
    },
    "HIGH_1024": {
        "max_pixels": 1024 * 28 * 28,  # ~800k pixels
        "target_dimension": "1024x1024",
        "latency_factor": 1.45,
        "vram_gb": 4.6,
    },
}


@dataclass(frozen=True)
class ResolutionDecision:
    selected_tier: str
    target_dimension: str
    max_pixels: int
    escalated_due_to_small_target: bool
    escalated_due_to_ambiguity: bool
    requires_crop_verification: bool
    reason: str


def select_adaptive_resolution(
    candidates: list[SafeCandidate],
    confidence: float = 1.0,
    ambiguous: bool = False,
    small_target_threshold_px: float = 30.0,
) -> ResolutionDecision:
    """Select the optimal input resolution for a given step."""
    has_small_target = False
    for cand in candidates[:3]:
        if cand.bbox and len(cand.bbox) >= 4:
            _, _, w, h = cand.bbox
            if 0 < w < small_target_threshold_px or 0 < h < small_target_threshold_px:
                has_small_target = True
                break

    is_medium_confidence = (0.65 <= confidence < 0.88)

    if has_small_target or is_medium_confidence:
        requires_crop = ambiguous or (confidence < 0.75)
        return ResolutionDecision(
            selected_tier="HIGH_1024",
            target_dimension=cast(str, RESOLUTION_TIERS["HIGH_1024"]["target_dimension"]),
            max_pixels=cast(int, RESOLUTION_TIERS["HIGH_1024"]["max_pixels"]),
            escalated_due_to_small_target=has_small_target,
            escalated_due_to_ambiguity=is_medium_confidence,
            requires_crop_verification=requires_crop,
            reason=(
                f"Escalated to 1024px due to {'small target (<30px)' if has_small_target else 'confidence ambiguity'}."
            ),
        )

    # Standard default
    return ResolutionDecision(
        selected_tier="MEDIUM_768",
        target_dimension=cast(str, RESOLUTION_TIERS["MEDIUM_768"]["target_dimension"]),
        max_pixels=cast(int, RESOLUTION_TIERS["MEDIUM_768"]["max_pixels"]),
        escalated_due_to_small_target=False,
        escalated_due_to_ambiguity=False,
        requires_crop_verification=ambiguous,
        reason="Standard 768px default tier selected.",
    )
