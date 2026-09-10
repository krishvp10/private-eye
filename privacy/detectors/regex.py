"""
Signal 2: Regex and Text Pattern Privacy Detector.
Detects structured sensitive numerical and alphanumeric identifiers:
Aadhaar, PAN, Phone, Email, DOB, and Credit Cards.
"""

import re
from typing import Any, Dict, List
from shared.protocol import (
    BoundingBox,
    Detection,
    DetectionCategory,
    DetectionSource,
)

# Regex specifications
PATTERNS = {
    DetectionCategory.AADHAAR: re.compile(
        r"\b[2-9][0-9]{3}\s*[-]?\s*[0-9]{4}\s*[-]?\s*[0-9]{4}\b"
    ),
    DetectionCategory.PAN: re.compile(
        r"\b[A-Z]\s*[A-Z]\s*[A-Z]\s*[A-Z]\s*[A-Z]\s*[0-9]\s*[0-9]\s*[0-9]\s*[0-9]\s*[A-Z]\b",
        re.IGNORECASE,
    ),
    DetectionCategory.PHONE: re.compile(
        r"\b(?:\+91|91|0)?[\s-]*[6-9]\d{4}[\s-]?\d{5}\b"
    ),
    DetectionCategory.EMAIL: re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    DetectionCategory.DOB: re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}/\d{2})\b"),
    DetectionCategory.CARD: re.compile(
        r"\b(?:4[0-9]{3}|5[1-5][0-9]{2}|6011|3[47][0-9]{2})[\s-]?[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b"
    ),
    DetectionCategory.UHID: re.compile(
        r"\b(?:UHID|ABHA)[-:\s][A-Za-z0-9-]{6,20}\b",
        re.IGNORECASE,
    ),
}


class RegexDetector:
    """Scans text content and DOM elements using calibrated regex patterns."""

    def detect_in_elements(self, elements: List[Dict[str, Any]]) -> List[Detection]:
        """Detect regex patterns associated with specific rendered DOM element regions."""
        detections: List[Detection] = []

        for el in elements:
            bbox_coords = el.get("bbox")
            if not bbox_coords or len(bbox_coords) != 4 or bbox_coords[2] <= 0 or bbox_coords[3] <= 0:
                continue

            bounding_box = BoundingBox.from_list(bbox_coords)
            element_id = el.get("id", "unknown")
            text_to_scan = f"{el.get('name', '')} {el.get('id', '')}"

            for category, regex in PATTERNS.items():
                if regex.search(text_to_scan):
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

    def detect_in_text(self, text: str, bounding_box: BoundingBox) -> List[Detection]:
        """Detect PII in visible prose when no element-level box is available."""
        detections: List[Detection] = []
        for category, regex in PATTERNS.items():
            if regex.search(text):
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

    def scan_raw_text(self, text: str) -> List[Dict[str, Any]]:
        """Identify matches in unstructured text strings."""
        matches = []
        for category, regex in PATTERNS.items():
            for m in regex.finditer(text):
                matches.append({
                    "category": category,
                    "matched_span": m.span(),
                    "category_name": category.value,
                })
        return matches
