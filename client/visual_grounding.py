"""Privacy-safe visual context helpers for candidate grounding experiments."""

import io
from dataclasses import dataclass

from PIL import Image, ImageDraw

from shared.protocol import SafeCandidate


@dataclass(frozen=True)
class MarkedCandidateImage:
    image_bytes: bytes
    labels: dict[str, str]


def mark_candidates(
    sanitized_screenshot_bytes: bytes,
    candidates: list[SafeCandidate],
    padding: int = 4,
) -> MarkedCandidateImage:
    """Draw local candidate labels on an already-redacted screenshot."""
    image = Image.open(io.BytesIO(sanitized_screenshot_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)
    labels: dict[str, str] = {}
    for index, candidate in enumerate(candidates):
        if not candidate.bbox or len(candidate.bbox) != 4:
            continue
        label = f"C{index + 1}"
        x, y, width, height = candidate.bbox
        left = max(0, int(x) - padding)
        top = max(0, int(y) - padding)
        right = min(image.width, int(x + width) + padding)
        bottom = min(image.height, int(y + height) + padding)
        if right <= left or bottom <= top:
            continue
        draw.rectangle((left, top, right, bottom), outline=(255, 165, 0), width=2)
        draw.rectangle((left, max(0, top - 16), left + 28, top), fill=(255, 165, 0))
        draw.text((left + 3, max(0, top - 15)), label, fill=(0, 0, 0))
        labels[label] = candidate.ref

    output = io.BytesIO()
    image.save(output, format="PNG")
    return MarkedCandidateImage(output.getvalue(), labels)
