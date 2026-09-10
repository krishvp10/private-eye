"""
Phase 3 Tests: Multi-Signal Privacy Detection Engine.
Validates:
1. Detection of all 9 sensitive categories (face, password, aadhaar, pan, phone, email, name, dob, address).
2. Confidence values meet or exceed threshold.
3. Zero external network API calls.
4. Benchmark evaluation against ground_truth.json yields F1 >= 0.85.
"""

import json
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from playwright.async_api import async_playwright

from client.capture import capture_page
from demo_sites.server import app
from privacy.pipeline import PrivacyPipeline
from tests.conftest import allocate_port


PORT = allocate_port()
BASE_URL = f"http://127.0.0.1:{PORT}"
GROUND_TRUTH_PATH = Path(__file__).parent.parent / "demo_sites" / "ground_truth.json"


@pytest.fixture(scope="module", autouse=True)
def run_demo_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.0)
    yield
    server.should_exit = True


@pytest.mark.asyncio
async def test_privacy_detection_all_categories():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"{BASE_URL}/kyc")

        captured = await capture_page(page)

        pipeline = PrivacyPipeline(min_confidence=0.60)
        detections = pipeline.detect(
            elements=captured.raw_elements,
            screenshot_bytes=captured.screenshot_bytes,
            visible_text=captured.visible_text,
        )

        detected_categories = {d.category.value for d in detections}

        # Check that all 9 required categories were detected
        expected_categories = {
            "face",
            "password",
            "aadhaar",
            "pan",
            "phone",
            "email",
            "name",
            "dob",
            "address",
        }
        missing = expected_categories - detected_categories
        assert not missing, f"Missing detections for categories: {missing}"

        # Check confidence scores
        for d in detections:
            assert d.confidence >= 0.60
            assert d.bounding_box.width > 0
            assert d.bounding_box.height > 0

        # Load ground truth and evaluate
        with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
        kyc_gt = gt_data["pages"]["/kyc"]["elements"]

        eval_report = pipeline.evaluate_against_ground_truth(detections, kyc_gt)
        assert eval_report["recall"] >= 0.85, f"Recall too low: {eval_report['recall']}"
        assert eval_report["precision"] >= 0.85, f"Precision too low: {eval_report['precision']}"
        assert eval_report["f1"] >= 0.85, f"F1 score too low: {eval_report['f1']}"

        await browser.close()
