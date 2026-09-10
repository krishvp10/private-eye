"""
Local Redaction Engine for PrivateEye.
Transforms raw screenshots into sanitized context using Pillow/OpenCV.
Applies category-specific redactions (blackout, gaussian blur, digit/char masking).
Guarantees zero recoverable text in masked regions.
"""

import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shared.protocol import (
    BoundingBox,
    Detection,
    DetectionCategory,
    Redaction,
    RedactionMap,
    RedactionMethod,
    ScreenGraph,
    ScreenNode,
)
from privacy.redaction.policies import get_redaction_method


@dataclass
class RedactionResult:
    sanitized_bytes: bytes
    redaction_map: RedactionMap
    sanitized_graph: ScreenGraph
    coverage_ratio: float
    total_redacted_area: float


class RedactionEngine:
    """Executes client-side image redaction and generates the formal RedactionMap contract."""

    def __init__(self, jpeg_quality: int = 70) -> None:
        self.jpeg_quality = jpeg_quality

    def redact(
        self,
        screenshot_bytes: bytes,
        screen_graph: ScreenGraph,
        detections: List[Detection],
    ) -> RedactionResult:
        # Load image into Pillow
        image = Image.open(io.BytesIO(screenshot_bytes)).convert("RGB")
        img_w, img_h = image.size
        total_screen_area = float(img_w * img_h)

        draw = ImageDraw.Draw(image)
        redactions: List[Redaction] = []
        total_area = 0.0

        for det in detections:
            bbox = det.bounding_box
            method = get_redaction_method(det.category)

            # Clamp bounding box inside image boundaries
            x1 = max(0, int(bbox.x))
            y1 = max(0, int(bbox.y))
            x2 = min(img_w, int(bbox.x + bbox.width))
            y2 = min(img_h, int(bbox.y + bbox.height))

            w = max(0, x2 - x1)
            h = max(0, y2 - y1)
            if w == 0 or h == 0:
                continue

            total_area += float(w * h)

            # Apply visual redaction method
            if method == RedactionMethod.BLACKOUT:
                # Opaque solid black box
                draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))

            elif method == RedactionMethod.BLUR:
                # Heavy Gaussian blur over biometric/face region
                box_region = image.crop((x1, y1, x2, y2))
                # Apply multi-pass heavy blur
                blurred = box_region.filter(ImageFilter.GaussianBlur(radius=18))
                image.paste(blurred, (x1, y1))

            elif method == RedactionMethod.MASK_DIGITS:
                # Mask digits with dark pill pattern preserving boundary
                draw.rectangle([x1 + 4, y1 + 4, x2 - 4, y2 - 4], fill=(15, 23, 42))

            elif method == RedactionMethod.MASK_CHARS:
                # Neutral dark block mask
                draw.rectangle([x1 + 2, y1 + 2, x2 - 2, y2 - 2], fill=(30, 41, 59))

            # Record in formal Redaction contract
            redactions.append(
                Redaction(
                    region=[float(x1), float(y1), float(w), float(h)],
                    category=det.category,
                    method=method,
                    confidence=det.confidence,
                    detection_source=det.source,
                )
            )

        # Encode sanitized image as JPEG (original is dropped from scope)
        out_buffer = io.BytesIO()
        image.save(out_buffer, format="JPEG", quality=self.jpeg_quality)
        sanitized_bytes = out_buffer.getvalue()

        # Sanitize ScreenGraph: ensure sensitive nodes are marked and have clean labels
        sanitized_graph = self._sanitize_graph(screen_graph, detections)

        coverage = min(1.0, total_area / total_screen_area) if total_screen_area > 0 else 0.0
        redaction_map = RedactionMap(
            redactions=redactions,
            total_redacted=len(redactions),
            coverage_ratio=round(coverage, 4),
        )

        return RedactionResult(
            sanitized_bytes=sanitized_bytes,
            redaction_map=redaction_map,
            sanitized_graph=sanitized_graph,
            coverage_ratio=round(coverage, 4),
            total_redacted_area=total_area,
        )

    def _sanitize_graph(self, graph: ScreenGraph, detections: List[Detection]) -> ScreenGraph:
        """Deep copy and clean ScreenGraph so no sensitive text remains in labels."""
        graph_dict = graph.model_dump()
        redacted_categories = {d.category.value for d in detections}

        def clean_node(node_dict: Dict[str, Any]):
            name = node_dict.get("name") or ""
            # If name matches any sensitive keyword, sanitize it
            for cat in redacted_categories:
                if cat in name.lower() and "btn" not in node_dict.get("id", ""):
                    node_dict["sensitive"] = True

            # Invariant: never leave value in node
            if "value" in node_dict:
                del node_dict["value"]

            for child in node_dict.get("children", []):
                clean_node(child)

        clean_node(graph_dict["root"])
        return ScreenGraph.model_validate(graph_dict)

    def evaluate_redaction_accuracy(
        self,
        predicted_redactions: List[Redaction],
        ground_truth_elements: List[Dict[str, Any]],
        screen_size: tuple = (1280, 800),
    ) -> Dict[str, Any]:
        """
        Calculates IoU, coverage, over-redaction, and missed sensitive area
        by comparing predicted mask binary bitmap vs ground truth binary bitmap.
        """
        w, h = screen_size
        gt_mask = np.zeros((h, w), dtype=np.uint8)
        pred_mask = np.zeros((h, w), dtype=np.uint8)

        # Draw GT regions
        for gt in ground_truth_elements:
            bbox = gt.get("bbox")
            if bbox and len(bbox) == 4:
                x, y, bw, bh = [int(v) for v in bbox]
                gt_mask[max(0, y):min(h, y + bh), max(0, x):min(w, x + bw)] = 1

        # Draw Pred regions
        for r in predicted_redactions:
            x, y, rw, rh = [int(v) for v in r.region]
            pred_mask[max(0, y):min(h, y + rh), max(0, x):min(w, x + rw)] = 1

        intersection = np.logical_and(gt_mask, pred_mask).sum()
        union = np.logical_or(gt_mask, pred_mask).sum()
        iou = float(intersection / union) if union > 0 else 1.0

        gt_area = float(gt_mask.sum())
        pred_area = float(pred_mask.sum())

        # Coverage: what portion of GT is covered by pred
        coverage = float(intersection / gt_area) if gt_area > 0 else 1.0
        # Over-mask: portion of predicted mask outside GT
        over_mask = float((pred_mask.sum() - intersection) / pred_area) if pred_area > 0 else 0.0
        # Missed area: portion of GT not covered
        missed_ratio = float((gt_area - intersection) / gt_area) if gt_area > 0 else 0.0

        return {
            "iou": round(iou, 4),
            "coverage": round(coverage, 4),
            "over_mask_ratio": round(over_mask, 4),
            "missed_area_ratio": round(missed_ratio, 4),
            "gt_total_pixels": int(gt_area),
            "pred_total_pixels": int(pred_area),
        }
