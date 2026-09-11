"""
Signal 2: Regex and Text Pattern Privacy Detector.
Detects structured sensitive numerical and alphanumeric identifiers:
Aadhaar, PAN, Phone, Email, DOB, and Credit Cards.
"""

import re
import unicodedata
from typing import Any

from shared.protocol import (
    BoundingBox,
    Detection,
    DetectionCategory,
    DetectionSource,
)

INVISIBLE_CHARS = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad\u2060\u2061\u2062\u2063\u2064]"
)


UNICODE_ESCAPE_CHARS = re.compile(
    r"\\u(?:200[b-fB-F]|206[0-4]|feff|00ad)", re.IGNORECASE
)


def normalize_text_for_privacy(text: str) -> str:
    """Normalize Unicode and strip zero-width and invisible control characters."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    cleaned = INVISIBLE_CHARS.sub("", normalized)
    return UNICODE_ESCAPE_CHARS.sub("", cleaned)


# Regex specifications
PATTERNS = {
    DetectionCategory.AADHAAR: re.compile(
        r"\b[2-9][0-9]{3}[\s\.\-]*[0-9]{4}[\s\.\-]*[0-9]{4}\b"
    ),
    DetectionCategory.PAN: re.compile(
        r"\b[A-Za-z]{5}[\s\.\-]?[0-9]{4}[\s\.\-]?[A-Za-z]\b"
    ),
    DetectionCategory.PHONE: re.compile(
        r"\b(?:\+?91|0)?[\s\.\-]*[6-9]\d{4}[\s\.\-]?\d{5}\b"
    ),
    DetectionCategory.EMAIL: re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    DetectionCategory.DOB: re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}/\d{2})\b"),
    DetectionCategory.CARD: re.compile(
        r"\b(?:4[0-9]{3}|5[1-5][0-9]{2}|6011|3[47][0-9]{2})[\s\.\-]?[0-9]{4}[\s\.\-]?[0-9]{4}[\s\.\-]?[0-9]{4}\b"
    ),
    DetectionCategory.UHID: re.compile(
        r"\b(?:UHID|ABHA)[-:\s][A-Za-z0-9-]{6,20}\b",
        re.IGNORECASE,
    ),
}


class RegexDetector:
    """Scans text content and DOM elements using calibrated regex patterns."""

    def detect_in_elements(self, elements: list[dict[str, Any]]) -> list[Detection]:
        """Detect regex patterns associated with specific rendered DOM element regions."""
        detections: list[Detection] = []

        for el in elements:
            bbox_coords = el.get("bbox")
            if not bbox_coords or len(bbox_coords) != 4 or bbox_coords[2] <= 0 or bbox_coords[3] <= 0:
                continue

            bounding_box = BoundingBox.from_list(bbox_coords)
            element_id = el.get("id", "unknown")
            raw_text = (
                f"{el.get('name', '')} {el.get('id', '')} "
                f"{el.get('placeholder', '')} {el.get('value', '')} {el.get('text', '')}"
            )
            text_to_scan = normalize_text_for_privacy(raw_text)

            for category, regex in PATTERNS.items():
                if regex.search(text_to_scan) or regex.search(raw_text):
                    detections.append(
                        Detection(
                            category=category,
                            source=DetectionSource.REGEX,
                            confidence=0.90,
                            bounding_box=bounding_box,
                            evidence_id=f"regex:{element_id}:{category.value}",
                            text_preview=f"[REGEX:{category.value.upper()}]",
                        )
                    )

        return detections

    def detect_in_text(self, text: str, bounding_box: BoundingBox) -> list[Detection]:
        """Detect PII in visible prose when no element-level box is available."""
        detections: list[Detection] = []
        norm_text = normalize_text_for_privacy(text)
        for category, regex in PATTERNS.items():
            if regex.search(text) or regex.search(norm_text):
                detections.append(
                    Detection(
                        category=category,
                        source=DetectionSource.REGEX,
                        confidence=0.86,
                        bounding_box=bounding_box,
                        evidence_id=f"regex:visible-text:{category.value}",
                        text_preview=f"[REGEX:{category.value.upper()}]",
                    )
                )
        return detections

    def scan_raw_text(self, text: str) -> list[dict[str, Any]]:
        """Identify matches in unstructured text strings."""
        matches = []
        norm_text = normalize_text_for_privacy(text)
        seen_spans = set()
        for category, regex in PATTERNS.items():
            for m in regex.finditer(text):
                span = m.span()
                matches.append({
                    "category": category,
                    "matched_span": span,
                    "category_name": category.value,
                })
                seen_spans.add((category, span))
            if norm_text != text:
                for m in regex.finditer(norm_text):
                    span = m.span()
                    if (category, span) not in seen_spans:
                        matches.append({
                            "category": category,
                            "matched_span": span,
                            "category_name": category.value,
                        })
                        seen_spans.add((category, span))
        return matches
