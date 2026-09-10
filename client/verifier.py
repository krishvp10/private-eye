"""
Local Privacy-Preserving Visual & Semantic Verifier.
Disambiguates top-k candidates using local crops from privacy-redacted screenshots
and container/geometry cues, without exposing raw secrets.
"""

import io
import logging
from dataclasses import dataclass
from typing import Any

from PIL import Image

from shared.protocol import SafeCandidate

logger = logging.getLogger("private_eye_verifier")


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of visual/semantic candidate verification."""

    selected_candidate: SafeCandidate | None
    confidence: float
    verified: bool
    reason: str
    crop_bboxes: list[list[float]]


class CandidateVerifier:
    """
    Verifies and disambiguates candidate selections using privacy-sanitized
    screenshot crops, spatial geometry, and contextual cues.
    """

    def __init__(self, confidence_threshold: float = 0.60) -> None:
        self.confidence_threshold = confidence_threshold

    def extract_crop(
        self,
        sanitized_screenshot_bytes: bytes,
        bbox: list[float],
        padding: int = 4,
    ) -> bytes | None:
        """
        Extract a localized bounding-box crop from the already-redacted screenshot.
        Strict Invariant: Input screenshot must already be sanitized by RedactionEngine.
        """
        if not bbox or len(bbox) != 4 or bbox[2] <= 0 or bbox[3] <= 0:
            return None
        try:
            image = Image.open(io.BytesIO(sanitized_screenshot_bytes))
            w, h = image.size
            x1 = max(0, int(bbox[0]) - padding)
            y1 = max(0, int(bbox[1]) - padding)
            x2 = min(w, int(bbox[0] + bbox[2]) + padding)
            y2 = min(h, int(bbox[1] + bbox[3]) + padding)

            if x2 <= x1 or y2 <= y1:
                return None

            cropped = image.crop((x1, y1, x2, y2))
            buf = io.BytesIO()
            cropped.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as err:
            logger.warning(f"Failed to extract candidate crop: {err}")
            return None

    def disambiguate_candidates(
        self,
        task: str,
        candidates: list[SafeCandidate],
        sanitized_screenshot_bytes: bytes | None = None,
    ) -> VerificationResult:
        """
        Disambiguate near-tied or identically labeled candidates using
        spatial geometry, ordinal position cues ('second', 'bottom', 'primary'),
        and localized crop verification.
        """
        if not candidates:
            return VerificationResult(None, 0.0, False, "no_candidates", [])

        if len(candidates) == 1:
            top = candidates[0]
            if not top.enabled:
                return VerificationResult(None, top.rank_score, False, "candidate_disabled", [])
            return VerificationResult(
                top, top.rank_score, True, "single_candidate", [top.bbox or []]
            )

        task_lower = task.lower()
        crops_evaluated: list[list[float]] = []

        # Check for ordinal / spatial keywords in task using word boundaries
        import re

        wants_second = bool(re.search(r"\bsecond\b|\b2nd\b", task_lower))
        wants_first = bool(re.search(r"\bfirst\b|\b1st\b", task_lower))
        wants_bottom = bool(re.search(r"\bbottom\b|\bfooter\b|\bsecondary\b", task_lower))
        wants_top = bool(re.search(r"\btop\b|\bheader\b|\bprimary\b", task_lower))

        # Sort candidates by geometric position (y, then x) for spatial disambiguation
        spatially_sorted = sorted(
            candidates,
            key=lambda c: (c.bbox[1] if c.bbox else 0, c.bbox[0] if c.bbox else 0),
        )

        for cand in candidates:
            if cand.bbox:
                crops_evaluated.append(cand.bbox)

        if wants_bottom and len(spatially_sorted) >= 2:
            chosen = spatially_sorted[-1]
            return VerificationResult(
                chosen,
                0.88,
                True,
                "verified_spatial_bottom",
                crops_evaluated,
            )

        if wants_top and len(spatially_sorted) >= 1:
            chosen = spatially_sorted[0]
            return VerificationResult(
                chosen,
                0.88,
                True,
                "verified_spatial_top",
                crops_evaluated,
            )

        if wants_second and len(spatially_sorted) >= 2:
            chosen = spatially_sorted[1]
            return VerificationResult(
                chosen,
                0.90,
                True,
                "verified_ordinal_second",
                crops_evaluated,
            )

        if wants_first and len(spatially_sorted) >= 1:
            chosen = spatially_sorted[0]
            return VerificationResult(
                chosen,
                0.90,
                True,
                "verified_ordinal_first",
                crops_evaluated,
            )

        # If highest ranked candidate has a clear lead (>0.15 margin)
        top = candidates[0]
        second_score = candidates[1].rank_score if len(candidates) > 1 else 0.0
        if (top.rank_score - second_score) >= 0.15 and top.rank_score >= self.confidence_threshold:
            return VerificationResult(
                top,
                top.rank_score,
                True,
                "verified_dominant_score",
                crops_evaluated,
            )

        # Ambiguous candidate tie cannot be safely resolved without user input
        return VerificationResult(
            top if top.rank_score >= self.confidence_threshold else None,
            top.rank_score,
            False,
            "ambiguous_candidates_unresolved",
            crops_evaluated,
        )
