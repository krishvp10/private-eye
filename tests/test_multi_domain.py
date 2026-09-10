"""
Multi-Domain Integration & Redaction Tests:
Validates PrivateEye across Banking/Checkout and Healthcare/Patient portals.
Ensures zero raw card numbers, CVVs, UHIDs, or clinical prescriptions ever leak.
"""

import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from playwright.async_api import async_playwright

from client.capture import capture_page
from client.vault import LocalVault
from demo_sites.server import app
from eval.leak_check import OutboundLeakInterceptor
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from server.mock_vlm import MockVLM
from shared.protocol import ScreenContext


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = get_free_port()
BASE_URL = f"http://127.0.0.1:{PORT}"
GROUND_TRUTH_FILE = Path(__file__).parent.parent / "demo_sites" / "ground_truth.json"


@pytest.fixture(scope="module", autouse=True)
def run_multi_domain_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.0)
    yield
    server.should_exit = True


@pytest.mark.asyncio
async def test_banking_checkout_redaction_and_vlm():
    """Verify banking checkout detects sensitive financial data and uses value_ref."""
    pipeline = PrivacyPipeline()
    redactor = RedactionEngine()
    mock_vlm = MockVLM()
    vault = LocalVault()
    leak_interceptor = OutboundLeakInterceptor(vault=vault)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"{BASE_URL}/checkout")

        captured = await capture_page(page)
        detections = pipeline.detect(
            captured.raw_elements,
            screenshot_bytes=captured.screenshot_bytes,
            visible_text=captured.visible_text,
            viewport=captured.viewport,
        )

        # Check detected categories include card, cvv, or sensitive input regions
        categories_found = {d.category.value for d in detections}
        assert "card" in categories_found or "password" in categories_found

        redacted = redactor.redact(
            captured.screenshot_bytes,
            captured.screen_graph,
            detections,
        )

        context = ScreenContext(
            run_id="checkout-test-01",
            step=1,
            url=page.url,
            image_b64="test",
            screen_graph=redacted.sanitized_graph,
            redactions=redacted.redaction_map.redactions,
            task="Complete payment transaction",
        )

        # Assert no raw card numbers or CVVs appear in the screen graph
        screen_graph_json = context.screen_graph.model_dump_json()
        assert "4532 1148 9201 8842" not in screen_graph_json
        assert "842" not in screen_graph_json
        leak_interceptor.assert_safe(screen_graph_json)

        # Test MockVLM provides value_ref indirection for checkout
        action = mock_vlm.analyze(context)
        assert action.action.value == "fill"
        assert action.value_ref == "user_profile.card_number"

        await browser.close()


@pytest.mark.asyncio
async def test_healthcare_patient_ehr_redaction_and_vlm():
    """Verify healthcare intake detects clinical diagnosis/prescriptions and uses value_ref."""
    pipeline = PrivacyPipeline()
    redactor = RedactionEngine()
    mock_vlm = MockVLM()
    vault = LocalVault()
    leak_interceptor = OutboundLeakInterceptor(vault=vault)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"{BASE_URL}/patient")

        captured = await capture_page(page)
        detections = pipeline.detect(
            captured.raw_elements,
            screenshot_bytes=captured.screenshot_bytes,
            visible_text=captured.visible_text,
            viewport=captured.viewport,
        )

        categories_found = {d.category.value for d in detections}
        assert "health" in categories_found or "uhid" in categories_found

        redacted = redactor.redact(
            captured.screenshot_bytes,
            captured.screen_graph,
            detections,
        )

        context = ScreenContext(
            run_id="patient-test-01",
            step=1,
            url=page.url,
            image_b64="test",
            screen_graph=redacted.sanitized_graph,
            redactions=redacted.redaction_map.redactions,
            task="Complete patient admission intake",
        )

        # Assert no raw clinical diagnosis or prescription appears in screen graph
        screen_graph_json = context.screen_graph.model_dump_json()
        assert "Type 2 Diabetes" not in screen_graph_json
        assert "Metformin 500mg" not in screen_graph_json
        leak_interceptor.assert_safe(screen_graph_json)

        # Test MockVLM returns value_ref indirection for UHID
        action = mock_vlm.analyze(context)
        assert action.action.value == "fill"
        assert action.value_ref == "user_profile.uhid"

        await browser.close()
