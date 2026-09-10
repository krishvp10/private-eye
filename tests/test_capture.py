"""
Phase 2 Tests: Playwright Capture Engine
Validates that capture.py correctly extracts:
- Viewport screenshot bytes
- Visible text
- Interactive DOM nodes with bounding boxes
- Sanitized ScreenGraph adhering to the zero-leak invariant
"""

import json
import pytest
from playwright.async_api import async_playwright
from client.capture import capture_page
from demo_sites.server import app
import uvicorn
import threading
import time

PORT = 9002
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
async def test_capture_page_structure():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"{BASE_URL}/kyc")

        captured = await capture_page(page)

        # 1. Screenshot validation
        assert len(captured.screenshot_bytes) > 1000
        assert captured.url == f"{BASE_URL}/kyc"
        assert captured.viewport == {"width": 1280, "height": 800}

        # 2. Visible text validation
        assert "Individual Identity Certification" in captured.visible_text
        assert "MANDATORY KYC VERIFICATION" in captured.visible_text

        # 3. Screen graph validation
        graph = captured.screen_graph
        assert graph.root.role == "WebArea"
        child_ids = [c.id for c in graph.root.children]
        assert "field_name" in child_ids
        assert "field_email" in child_ids
        assert "field_aadhaar" in child_ids
        assert "field_pan" in child_ids
        assert "field_pin" in child_ids
        assert "btn_submit" in child_ids

        # 4. Strict Privacy Invariant: NO raw secret values in screen graph
        dumped_graph_str = graph.model_dump_json()
        assert "SuperSecretPass123!" not in dumped_graph_str
        assert "4839 2176 5201" not in dumped_graph_str
        assert "ABCDE1234F" not in dumped_graph_str

        # 5. Check bounding boxes
        for child in graph.root.children:
            if child.id in ["field_name", "btn_submit"]:
                assert child.bbox is not None
                assert len(child.bbox) == 4
                assert child.bbox[2] > 0  # width > 0
                assert child.bbox[3] > 0  # height > 0

        await browser.close()


@pytest.mark.asyncio
async def test_capture_cli(tmp_path):
    """Test CLI execution writes all 3 artifacts: screenshot, screen_graph, visible_text."""
    from client.capture import run_cli
    out_dir = str(tmp_path / "cli_out")
    await run_cli(f"{BASE_URL}/kyc", out_dir)

    out_p = tmp_path / "cli_out"
    assert (out_p / "screenshot.jpg").exists()
    assert (out_p / "screenshot.jpg").stat().st_size > 0
    assert (out_p / "screen_graph.json").exists()
    assert (out_p / "visible_text.json").exists()

