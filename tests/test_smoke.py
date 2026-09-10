"""
Phase 0 Smoke Tests:
1. Validates FastAPI health endpoint
2. Validates Playwright headless browser launch and screenshot capability
3. Validates shared protocol serialization
"""

import pytest
from fastapi.testclient import TestClient
from playwright.async_api import async_playwright

from server.api import app
from shared.protocol import (
    AgentAction,
    DetectionCategory,
    DetectionSource,
    Redaction,
    RedactionMethod,
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)


def test_fastapi_health():
    """Test that the server health check endpoint responds correctly."""
    client = TestClient(app)
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mode"] == "mock"


@pytest.mark.asyncio
async def test_playwright_smoke():
    """Test that Playwright can launch headless Chromium and capture a page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content("<html><body><h1>PrivateEye Smoke Test</h1></body></html>")
        title = await page.text_content("h1")
        assert title == "PrivateEye Smoke Test"
        screenshot_bytes = await page.screenshot()
        assert len(screenshot_bytes) > 0
        await browser.close()


def test_protocol_serialization():
    """Test that protocol schemas serialize and validate invariants."""
    node = ScreenNode(role="button", name="Continue", id="btn_1", sensitive=False)
    graph = ScreenGraph(root=node, url="http://test.local")
    redaction = Redaction(
        region=[10, 20, 100, 30],
        category=DetectionCategory.AADHAAR,
        method=RedactionMethod.MASK_DIGITS,
        confidence=0.95,
        detection_source=DetectionSource.DOM,
    )
    context = ScreenContext(
        run_id="smoke-run-001",
        step=1,
        url="http://test.local",
        image_b64="fake_base64_data",
        screen_graph=graph,
        redactions=[redaction],
        task="Test task",
    )
    dumped = context.model_dump()
    assert dumped["run_id"] == "smoke-run-001"
    assert len(dumped["redactions"]) == 1

    # Invariant: fill action must reject raw value without value_ref
    with pytest.raises(ValueError):
        AgentAction.model_validate({"action": "fill", "value": "my_secret_pan"})
