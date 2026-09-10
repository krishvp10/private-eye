"""Unit tests for Privacy False-Negative Diagnostic Tool."""

import pytest

from eval.privacy_fn_diagnostic import bbox_iou, run_diagnostic


def test_bbox_iou_calculation():
    box_a = [0.0, 0.0, 100.0, 100.0]
    box_b = [0.0, 0.0, 100.0, 100.0]
    assert bbox_iou(box_a, box_b) == 1.0

    box_c = [200.0, 200.0, 50.0, 50.0]
    assert bbox_iou(box_a, box_c) == 0.0

    box_d = [50.0, 0.0, 100.0, 100.0]
    iou = bbox_iou(box_a, box_d)
    assert 0.3 < iou < 0.4


@pytest.mark.asyncio
async def test_run_diagnostic():
    diag = await run_diagnostic()
    assert "summary" in diag
    assert "total_expected_entities" in diag["summary"]
    assert diag["summary"]["total_expected_entities"] > 0
    assert "breakdown_by_root_cause" in diag
    assert "breakdown_by_category" in diag
    assert "missed_cases" in diag
