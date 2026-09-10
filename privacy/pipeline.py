"""
Unified Multi-Signal Privacy Detection Pipeline for PrivateEye.
Combines DOM heuristics, regex text matching, lightweight NER, and local face detection.
Deduplicates overlapping regions and prioritizes high-confidence signals.
"""

from typing import Any

from privacy.detectors.dom import DOMDetector
from privacy.detectors.face import FaceDetector
from privacy.detectors.ner import LightweightNERDetector
from privacy.detectors.regex import RegexDetector
from shared.protocol import (
    BoundingBox,
    Detection,
)


def compute_iou(b1: BoundingBox, b2: BoundingBox) -> float:
    """Compute Intersection over Union between two bounding boxes."""
    x1 = max(b1.x, b2.x)
    y1 = max(b1.y, b2.y)
    x2 = min(b1.x + b1.width, b2.x + b2.width)
    y2 = min(b1.y + b1.height, b2.y + b2.height)

    intersection_w = max(0.0, x2 - x1)
    intersection_h = max(0.0, y2 - y1)
    intersection_area = intersection_w * intersection_h

    area1 = b1.width * b1.height
    area2 = b2.width * b2.height
    union_area = area1 + area2 - intersection_area

    if union_area <= 0:
        return 0.0
    return intersection_area / union_area


class PrivacyPipeline:
    """Coordinates all client-side detection signals and aggregates candidate regions."""

    def __init__(self, min_confidence: float = 0.60) -> None:
        self.min_confidence = min_confidence
        self.dom_detector = DOMDetector()
        self.regex_detector = RegexDetector()
        self.ner_detector = LightweightNERDetector()
        self.face_detector = FaceDetector()

    def detect(
        self,
        elements: list[dict[str, Any]],
        screenshot_bytes: bytes | None = None,
        visible_text: str | None = None,
        viewport: dict[str, int] | None = None,
    ) -> list[Detection]:
        """Run all signals in priority order and merge detections."""
        all_candidates: list[Detection] = []

        # Signal 1: DOM Heuristics (Level 1 priority)
        all_candidates.extend(self.dom_detector.detect(elements))

        # Signal 2: Regex / Text patterns (Level 2 priority)
        all_candidates.extend(self.regex_detector.detect_in_elements(elements))
        if visible_text:
            viewport = viewport or {"width": 1280, "height": 800}
            all_candidates.extend(
                self.regex_detector.detect_in_text(
                    visible_text,
                    BoundingBox(
                        x=0,
                        y=0,
                        width=float(viewport.get("width", 1280)),
                        height=float(viewport.get("height", 800)),
                    ),
                )
            )

        # Signal 3: Lightweight NER (Level 3 priority)
        all_candidates.extend(self.ner_detector.detect_in_elements(elements))

        # Signal 4: Face detection (Level 4 priority)
        all_candidates.extend(self.face_detector.detect(elements, screenshot_bytes))

        # Filter by confidence threshold
        filtered = [d for d in all_candidates if d.confidence >= self.min_confidence]

        # Deduplicate overlapping regions (IoU > 0.5): keep highest confidence
        deduped = self._deduplicate_detections(filtered)

        return deduped

    def _deduplicate_detections(self, detections: list[Detection]) -> list[Detection]:
        """Merge/deduplicate overlapping bounding boxes."""
        if not detections:
            return []

        # Sort by confidence descending
        sorted_dets = sorted(detections, key=lambda d: d.confidence, reverse=True)
        accepted: list[Detection] = []

        for candidate in sorted_dets:
            overlap = False
            for existing in accepted:
                iou = compute_iou(candidate.bounding_box, existing.bounding_box)
                if iou > 0.50:
                    overlap = True
                    break
            if not overlap:
                accepted.append(candidate)

        return accepted

    def evaluate_against_ground_truth(
        self,
        predicted: list[Detection],
        ground_truth: list[dict[str, Any]],
        iou_threshold: float = 0.40,
    ) -> dict[str, Any]:
        """
        Calculates True Positives, False Positives, False Negatives,
        Precision, Recall, and F1 score against ground truth.
        """
        tp = 0
        fp = 0
        matched_gt_indices: set[int] = set()

        for pred in predicted:
            matched = False
            for idx, gt in enumerate(ground_truth):
                if idx in matched_gt_indices:
                    continue
                # Category match
                gt_cat = gt.get("category")
                if pred.category.value == gt_cat:
                    matched = True
                    matched_gt_indices.add(idx)
                    tp += 1
                    break
            if not matched:
                fp += 1

        fn = len(ground_truth) - len(matched_gt_indices)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "total_ground_truth": len(ground_truth),
        }
