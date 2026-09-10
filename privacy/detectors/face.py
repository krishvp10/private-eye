"""
Signal 4: Local Face Detector.
Provides both DOM-guided avatar/biometric detection and visual face detection
using local OpenCV image processing with zero cloud calls.
"""

from typing import Any

import cv2
import numpy as np

from shared.protocol import (
    BoundingBox,
    Detection,
    DetectionCategory,
    DetectionSource,
)


class FaceDetector:
    """Detects face and biometric regions on screen via DOM anchors and local OpenCV."""

    def __init__(self) -> None:
        # Load standard Haar cascade if available in OpenCV
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore[attr-defined]
            self.face_cascade = cv2.CascadeClassifier(cascade_path)  # type: ignore[attr-defined]
        except Exception:
            self.face_cascade = None

    def detect(self, elements: list[dict[str, Any]], screenshot_bytes: bytes | None = None) -> list[Detection]:
        detections: list[Detection] = []

        # 1. DOM-anchored biometric avatar detection
        for el in elements:
            category = (el.get("category") or "").lower()
            elem_id = el.get("id", "").lower()
            role = (el.get("role") or "").lower()
            field_type = (el.get("field_type") or "").lower()
            bbox_coords = el.get("bbox")

            if not bbox_coords or len(bbox_coords) != 4 or bbox_coords[2] <= 0 or bbox_coords[3] <= 0:
                continue

            # Text fields and buttons are never face images
            if field_type in {"text", "password", "number", "tel", "email", "input", "textarea"}:
                continue
            if role in {"textbox", "input", "checkbox", "combobox", "button"}:
                continue

            is_face_element = (
                category == "face"
                or (role in {"img", "figure", "image"} and ("face" in elem_id or "avatar" in elem_id))
                or elem_id.startswith("img_face")
                or elem_id.startswith("avatar")
            )
            if is_face_element:
                detections.append(
                    Detection(
                        category=DetectionCategory.FACE,
                        source=DetectionSource.FACE,
                        confidence=0.98,
                        bounding_box=BoundingBox.from_list(bbox_coords),
                        evidence_id=f"face:dom:{el.get('id', 'avatar')}",
                        text_preview="[FACE:AVATAR]",
                    )
                )

        # 2. Visual face detection on screenshot if bytes provided
        if screenshot_bytes and self.face_cascade and not self.face_cascade.empty():
            try:
                np_arr = np.frombuffer(screenshot_bytes, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30)
                    )
                    for (x, y, w, h) in faces:
                        detections.append(
                            Detection(
                                category=DetectionCategory.FACE,
                                source=DetectionSource.VISION,
                                confidence=0.88,
                                bounding_box=BoundingBox(x=float(x), y=float(y), width=float(w), height=float(h)),
                                evidence_id=f"face:visual:{x}_{y}",
                                text_preview="[FACE:VISUAL]",
                            )
                        )
            except Exception:
                pass

        return detections
