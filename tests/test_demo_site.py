"""
Phase 1 Integration Tests:
Validates that the synthetic KYC demo web application:
1. Serves /login, /kyc, /success correctly.
2. Contains all 9 deterministic sensitive fields declared in ground_truth.json.
3. Allows complete interactive flow via Playwright: login -> KYC -> submit -> success.
4. Correctly activates debug mode (?debug=1).
"""

import json
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from playwright.async_api import async_playwright

from demo_sites.server import app


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

PORT = get_free_port()
BASE_URL = f"http://127.0.0.1:{PORT}"
GROUND_TRUTH_FILE = Path(__file__).parent.parent / "demo_sites" / "ground_truth.json"


@pytest.fixture(scope="module", autouse=True)
def run_demo_server():
    """Start demo site in background thread for the duration of tests."""
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1.0)
    yield
    server.should_exit = True


@pytest.mark.asyncio
async def test_kyc_full_navigation_flow():
    """Verify complete login -> KYC form -> submit -> success navigation flow."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Step 1: Login page
        await page.goto(f"{BASE_URL}/login")
        assert await page.title() == "Portal Login — National Verification Service"
        assert await page.is_visible("#field_username")
        assert await page.is_visible("#field_password")

        # Click Sign In button
        await page.click("#btn_login")
        await page.wait_for_url(f"{BASE_URL}/kyc")
        assert "/kyc" in page.url

        # Step 2: Validate all ground-truth fields are present on /kyc
        with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
        kyc_elements = gt_data["pages"]["/kyc"]["elements"]

        for item in kyc_elements:
            elem_id = item["id"]
            locator = page.locator(f"#{elem_id}")
            assert await locator.count() == 1, f"Element #{elem_id} missing on /kyc"
            # Verify data-sensitive attribute
            is_sensitive = await locator.get_attribute("data-sensitive")
            assert is_sensitive == "true", f"Element #{elem_id} missing data-sensitive='true'"
            category = await locator.get_attribute("data-category")
            assert category == item["category"], f"Element #{elem_id} category mismatch: {category} vs {item['category']}"

        # Check consent checkbox
        consent_checkbox = page.locator("#field_consent")
        assert await consent_checkbox.is_checked()

        # Step 3: Click Submit Application
        await page.click("#btn_submit")
        await page.wait_for_url(f"{BASE_URL}/success")
        assert "/success" in page.url

        # Step 4: Validate Success Page
        heading = await page.text_content("#success_heading")
        assert heading == "KYC Certified"
        assert await page.is_visible("#btn_return")

        await browser.close()


@pytest.mark.asyncio
async def test_kyc_debug_mode():
    """Verify ?debug=1 renders ground-truth bounding box overlay indicators."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"{BASE_URL}/kyc?debug=1")
        assert await page.is_visible(".debug-banner")
        boxes = page.locator(".debug-box")
        box_count = await boxes.count()
        assert box_count >= 8, f"Expected at least 8 debug boxes, found {box_count}"

        await browser.close()
