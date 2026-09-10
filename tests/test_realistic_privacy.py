"""
End-to-end tests for Realistic Privacy Challenge Corpus Fixtures.
"""

from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from client.capture import capture_page
from privacy.pipeline import PrivacyPipeline

CORPUS_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "realistic_privacy_corpus"


@pytest.mark.asyncio
async def test_dark_mode_fixture_detections():
    html_path = CORPUS_DIR / "02_dark_mode.html"
    assert html_path.exists()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(html_path.as_uri(), wait_until="load")

        captured = await capture_page(page)
        pipeline = PrivacyPipeline()
        detections = pipeline.detect(
            captured.raw_elements,
            captured.screenshot_bytes,
            captured.visible_text,
            captured.viewport,
        )

        categories_found = {d.category.value for d in detections}
        assert "password" in categories_found
        assert "email" in categories_found

        await browser.close()


@pytest.mark.asyncio
async def test_decoy_numbers_fixture_not_overmasked():
    html_path = CORPUS_DIR / "07_decoy_numbers.html"
    assert html_path.exists()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(html_path.as_uri(), wait_until="load")

        captured = await capture_page(page)
        pipeline = PrivacyPipeline()
        detections = pipeline.detect(
            captured.raw_elements,
            captured.screenshot_bytes,
            captured.visible_text,
            captured.viewport,
        )

        # Real PAN must be detected
        pan_detected = any(
            "pan" in str(d.evidence_id).lower() or d.category.value == "pan" for d in detections
        )
        assert pan_detected is True

        # Non-PII decoys must not trigger false positive pan/aadhaar flags on their specific IDs
        decoy_elem_ids = {"decoy_tracking", "decoy_order", "decoy_serial"}
        detected_ids = {d.node_id for d in detections if hasattr(d, "node_id")}
        assert not (decoy_elem_ids & detected_ids)

        await browser.close()
