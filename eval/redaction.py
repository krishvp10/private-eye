"""
Redaction Evaluation and Metrics Analysis.
Computes Intersection-over-Union (IoU), coverage percentage, and over-redaction
against synthetic ground-truth annotations.
"""

from typing import Any

import numpy as np

from shared.protocol import Redaction


def compute_redaction_metrics(
    redactions: list[Redaction],
    ground_truth_bboxes: list[list[float]],
    screen_size: tuple[int, int] = (1280, 800),
) -> dict[str, Any]:
    """
    Generate pixel-level bitmap masks for ground-truth vs predicted redactions,
    and calculate exact IoU, coverage, and over-mask metrics.
    """
    w, h = screen_size
    gt_mask = np.zeros((h, w), dtype=np.uint8)
    pred_mask = np.zeros((h, w), dtype=np.uint8)

    # Draw Ground Truth
    for bbox in ground_truth_bboxes:
        if len(bbox) == 4:
            x, y, bw, bh = [int(v) for v in bbox]
            gt_mask[max(0, y):min(h, y + bh), max(0, x):min(w, x + bw)] = 1

    # Draw Predicted Redactions
    for r in redactions:
        x, y, rw, rh = [int(v) for v in r.region]
        pred_mask[max(0, y):min(h, y + rh), max(0, x):min(w, x + rw)] = 1

    intersection = float(np.logical_and(gt_mask, pred_mask).sum())
    union = float(np.logical_or(gt_mask, pred_mask).sum())
    iou = intersection / union if union > 0 else 1.0

    gt_area = float(gt_mask.sum())
    pred_area = float(pred_mask.sum())

    coverage = intersection / gt_area if gt_area > 0 else 1.0
    over_mask = (pred_area - intersection) / pred_area if pred_area > 0 else 0.0
    missed_area = (gt_area - intersection) / gt_area if gt_area > 0 else 0.0

    return {
        "iou": round(iou, 4),
        "coverage": round(coverage, 4),
        "over_mask_ratio": round(over_mask, 4),
        "missed_area_ratio": round(missed_area, 4),
        "gt_pixels": int(gt_area),
        "pred_pixels": int(pred_area),
    }
