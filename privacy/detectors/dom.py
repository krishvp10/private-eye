"""
Signal 1: DOM Heuristic Privacy Detector.
Highest confidence detector operating on DOM element types, attributes, and accessible labels.
"""

from typing import Any

from shared.protocol import (
    BoundingBox,
    Detection,
    DetectionCategory,
    DetectionSource,
)

LABEL_CATEGORY_KEYWORDS = {
    DetectionCategory.PAN: ["pan", "permanent account number"],
    DetectionCategory.AADHAAR: ["aadhaar", "uidai", "aadhar"],
    DetectionCategory.UHID: ["uhid", "abha", "health id", "patient id"],
    DetectionCategory.CARD: ["card number", "card_number", "debit card", "credit card"],
    DetectionCategory.CVV: ["cvv", "security code", "cvc"],
    DetectionCategory.PHONE: ["phone", "mobile", "tel", "contact number"],
    DetectionCategory.EMAIL: ["email", "mail"],
    DetectionCategory.DOB: ["dob", "date of birth", "birth date", "bday", "expiry", "expiration"],
    DetectionCategory.PASSWORD: ["password", "pin", "passcode"],
    DetectionCategory.ADDRESS: ["address", "street", "residence", "postal"],
    DetectionCategory.NAME: ["name", "full name", "applicant name", "first name", "last name", "nominee name", "cardholder", "patient name"],
    DetectionCategory.FACE: ["face", "avatar", "biometric", "portrait", "photo"],
    DetectionCategory.HEALTH: ["diagnosis", "prescription", "medication", "medical history"],
}

AUTOCOMPLETE_MAP = {
    "current-password": DetectionCategory.PASSWORD,
    "new-password": DetectionCategory.PASSWORD,
    "email": DetectionCategory.EMAIL,
    "tel": DetectionCategory.PHONE,
    "tel-national": DetectionCategory.PHONE,
    "cc-number": DetectionCategory.CARD,
    "cc-csc": DetectionCategory.CVV,
    "cc-exp": DetectionCategory.DOB,
    "bday": DetectionCategory.DOB,
    "street-address": DetectionCategory.ADDRESS,
    "name": DetectionCategory.NAME,
}


class DOMDetector:
    """Detects sensitive regions by inspecting DOM tag attributes and accessible labels."""

    def detect(self, elements: list[dict[str, Any]]) -> list[Detection]:
        detections: list[Detection] = []

        for el in elements:
            bbox_coords = el.get("bbox")
            if not bbox_coords or len(bbox_coords) != 4 or bbox_coords[2] <= 0 or bbox_coords[3] <= 0:
                continue

            bounding_box = BoundingBox.from_list(bbox_coords)
            element_id = el.get("id", "unknown")
            field_type = (el.get("field_type") or "").lower()
            name_label = (el.get("name") or "").lower()
            category_attr = (el.get("category") or "").lower()
            is_sensitive = bool(el.get("sensitive", False))

            detected_cat: DetectionCategory | None = None
            confidence = 0.85

            # Rule 1: Explicit category attribute
            if category_attr:
                try:
                    detected_cat = DetectionCategory(category_attr)
                    confidence = 0.99
                except ValueError:
                    pass

            # Rule 2: Password field type
            if not detected_cat and field_type == "password":
                detected_cat = DetectionCategory.PASSWORD
                confidence = 0.99

            # Rule 3: Label keyword matching
            if not detected_cat:
                for cat, keywords in LABEL_CATEGORY_KEYWORDS.items():
                    if any(kw in name_label or kw in element_id.lower() for kw in keywords):
                        detected_cat = cat
                        confidence = 0.92
                        break

            # Rule 4: Generic sensitive tag
            if not detected_cat and is_sensitive:
                detected_cat = DetectionCategory.PASSWORD if "pass" in name_label else DetectionCategory.NAME
                confidence = 0.85

            if detected_cat:
                detections.append(
                    Detection(
                        category=detected_cat,
                        source=DetectionSource.DOM,
                        confidence=confidence,
                        bounding_box=bounding_box,
                        evidence_id=f"dom:{element_id}:{detected_cat.value}",
                        text_preview=f"[DOM:{detected_cat.value.upper()}]",
                    )
                )

        return detections
