"""
Signal 3: Lightweight Local NER & Entity Detector.
Identifies PERSON names and ADDRESS entities using localized heuristics,
titles (Mr, Ms, Dr, Shri), and Indian address patterns (Road, Nagar, Layout, PIN)
without requiring heavy external downloads or cloud APIs.
"""

import re
from typing import Any, Dict, List
from shared.protocol import (
    BoundingBox,
    Detection,
    DetectionCategory,
    DetectionSource,
)

HONORIFICS = re.compile(r"\b(mr|ms|mrs|dr|shri|smt)\.?\s+[A-Z][a-z]+", re.IGNORECASE)
ADDRESS_KEYWORDS = re.compile(r"\b(road|rd|nagar|layout|sector|colony|street|cross|main|bengaluru|mumbai|delhi|pincode|\d{6})\b", re.IGNORECASE)


class LightweightNERDetector:
    """Local, offline Named Entity Recognition heuristics for Name and Address."""

    def detect_in_elements(self, elements: List[Dict[str, Any]]) -> List[Detection]:
        detections: List[Detection] = []

        for el in elements:
            bbox_coords = el.get("bbox")
            if not bbox_coords or len(bbox_coords) != 4 or bbox_coords[2] <= 0 or bbox_coords[3] <= 0:
                continue

            bounding_box = BoundingBox.from_list(bbox_coords)
            element_id = el.get("id", "unknown")
            text = f"{el.get('name', '')} {el.get('id', '')}"

            # Check address keywords
            if ADDRESS_KEYWORDS.search(text) or "address" in el.get("id", "").lower():
                detections.append(
                    Detection(
                        category=DetectionCategory.ADDRESS,
                        source=DetectionSource.NER,
                        confidence=0.82,
                        bounding_box=bounding_box,
                        evidence_id=f"ner:{element_id}:address",
                        text_preview="[NER:ADDRESS]",
                    )
                )

            # Check person names
            if HONORIFICS.search(text) or "name" in el.get("id", "").lower():
                detections.append(
                    Detection(
                        category=DetectionCategory.NAME,
                        source=DetectionSource.NER,
                        confidence=0.80,
                        bounding_box=bounding_box,
                        evidence_id=f"ner:{element_id}:name",
                        text_preview="[NER:NAME]",
                    )
                )

        return detections
