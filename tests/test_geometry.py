"""
Unit tests for Overlay Geometry Engine (eval/geometry.py).
Validates mathematical containment mapping under arbitrary aspect ratios and dimensions.
"""

import pytest

from eval.geometry import calculate_containment, transform_bounding_box


def test_exact_aspect_ratio():
    # Source 1280x800 (16:10), Container 1280x800
    geom = calculate_containment(1280, 800, 1280, 800)
    assert geom.scale == 1.0
    assert geom.display_width == 1280
    assert geom.display_height == 800
    assert geom.offset_x == 0.0
    assert geom.offset_y == 0.0

    box = transform_bounding_box(100, 200, 300, 50, geom)
    assert box.left == 100.0
    assert box.top == 200.0
    assert box.width == 300.0
    assert box.height == 50.0


def test_wider_container_pillarbox():
    # Source 1280x800 (1.6:1), Container 1600x800 (2.0:1) -> width has black bars on left/right
    geom = calculate_containment(1600, 800, 1280, 800)
    assert geom.scale == 1.0
    assert geom.display_width == 1280
    assert geom.display_height == 800
    # Container width 1600 - display 1280 = 320 excess -> 160 on each side
    assert geom.offset_x == 160.0
    assert geom.offset_y == 0.0

    box = transform_bounding_box(100, 200, 300, 50, geom)
    assert box.left == 260.0  # 100 + 160
    assert box.top == 200.0
    assert box.width == 300.0
    assert box.height == 50.0


def test_taller_container_letterbox():
    # Source 1280x800 (1.6:1), Container 1280x1000 (1.28:1) -> height has black bars top/bottom
    geom = calculate_containment(1280, 1000, 1280, 800)
    assert geom.scale == 1.0
    assert geom.display_width == 1280
    assert geom.display_height == 800
    # Container height 1000 - display 800 = 200 excess -> 100 on top/bottom
    assert geom.offset_x == 0.0
    assert geom.offset_y == 100.0

    box = transform_bounding_box(100, 200, 300, 50, geom)
    assert box.left == 100.0
    assert box.top == 300.0  # 200 + 100
    assert box.width == 300.0
    assert box.height == 50.0


def test_scaled_down_container():
    # Source 1280x800, Container 640x400 (exact 0.5x scaling)
    geom = calculate_containment(640, 400, 1280, 800)
    assert geom.scale == 0.5
    assert geom.display_width == 640
    assert geom.display_height == 400
    assert geom.offset_x == 0.0
    assert geom.offset_y == 0.0

    box = transform_bounding_box(100, 200, 300, 50, geom)
    assert box.left == 50.0
    assert box.top == 100.0
    assert box.width == 150.0
    assert box.height == 25.0


def test_non_standard_aspect_ratio():
    # Source 1920x1080 (16:9), Container 800x600 (4:3)
    # scale = min(800/1920 = 0.41666, 600/1080 = 0.55555) -> 0.41666
    geom = calculate_containment(800, 600, 1920, 1080)
    assert pytest.approx(geom.scale, 0.001) == 800 / 1920
    assert geom.offset_x == 0.0
    assert geom.offset_y > 0.0  # Letterbox top/bottom

    box = transform_bounding_box(0, 0, 1920, 1080, geom)
    assert box.left == 0.0
    assert box.width == 800.0
    assert box.top == geom.offset_y
    assert pytest.approx(box.height, 0.001) == 1080 * geom.scale


def test_degenerate_dimensions():
    geom = calculate_containment(0, 0, 1280, 800)
    assert geom.scale == 1.0
    assert geom.offset_x == 0.0
    assert geom.offset_y == 0.0
