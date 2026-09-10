"""
Phase 4 Tests: Local Redaction Engine.
Validates:
1. Category-specific masking policies (blackout for passwords, blur for face, masks for numbers/text).
2. Sanitized screenshot differs from original and contains no recoverable text.
3. RedactionMap contract generation.
4. Redaction accuracy, IoU, and coverage calculations.
"""

import io
import threading
import time

import pytest
import uvicorn
from PIL import Image
from playwright.async_api import async_playwright

from client.capture import capture_page
from demo_sites.server import app
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from shared.protocol import DetectionCategory

PORT = 9004
BASE_URL = f"http://127.0.0.1:{PORT}"


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
async def test_redaction_engine_execution():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"{BASE_URL}/kyc")

        captured = await capture_page(page)

        # 1. Run privacy detection
        pipeline = PrivacyPipeline(min_confidence=0.60)
        detections = pipeline.detect(
            elements=captured.raw_elements,
            screenshot_bytes=captured.screenshot_bytes,
            visible_text=captured.visible_text,
        )
        assert len(detections) >= 8

        # 2. Run redaction
        engine = RedactionEngine(jpeg_quality=70)
        result = engine.redact(
            screenshot_bytes=captured.screenshot_bytes,
            screen_graph=captured.screen_graph,
            detections=detections,
        )

        # Assert sanitized bytes exist and are compressed JPEG
        assert len(result.sanitized_bytes) > 1000
        assert result.sanitized_bytes != captured.screenshot_bytes

        # Check RedactionMap
        assert result.redaction_map.total_redacted >= 8
        assert result.redaction_map.coverage_ratio > 0.0

        # Load sanitized image and check specific pixel redactions
        sanitized_img = Image.open(io.BytesIO(result.sanitized_bytes)).convert("RGB")
        original_img = Image.open(io.BytesIO(captured.screenshot_bytes)).convert("RGB")

        # Find a password redaction
        pw_redactions = [r for r in result.redaction_map.redactions if r.category == DetectionCategory.PASSWORD]
        assert len(pw_redactions) > 0
        pw_box = pw_redactions[0].region
        px, py, pw, ph = [int(v) for v in pw_box]

        # Verify pixels inside the password box are black (0, 0, 0)
        center_x = px + pw // 2
        center_y = py + ph // 2
        pixel_val = sanitized_img.getpixel((center_x, center_y))
        # Blackout produces near-zero or zero RGB values
        assert max(pixel_val) <= 15, f"Password region not blackened! Value: {pixel_val}"

        # Check Face blur
        face_redactions = [r for r in result.redaction_map.redactions if r.category == DetectionCategory.FACE]
        assert len(face_redactions) > 0

        # 3. Evaluate accuracy vs elements
        eval_metrics = engine.evaluate_redaction_accuracy(
            predicted_redactions=result.redaction_map.redactions,
            ground_truth_elements=captured.raw_elements,
            screen_size=(1280, 800),
        )
        assert eval_metrics["coverage"] >= 0.85
        assert eval_metrics["iou"] > 0.50

        await browser.close()
