"""
Phase 7 Tests: Local Action Executor.
Validates:
1. Semantic action execution (click, fill, scroll).
2. Local value_ref resolution against LocalVault.
3. Strict rejection of malicious / non-whitelisted actions.
4. ExecutionResult reporting.
"""

import socket
import threading
import time

import pytest
import uvicorn
from playwright.async_api import async_playwright

from client.executor.execute import ActionExecutor, ExecutorSecurityException
from client.vault import LocalVault
from demo_sites.server import app
from shared.protocol import (
    ActionTarget,
    ActionType,
    AgentAction,
)


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


PORT = _get_free_port()
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
async def test_executor_fill_and_click():
    vault = LocalVault(
        {
            "user_profile.name": "Custom Test User",
            "user_profile.email": "test.user@custom.domain",
        }
    )
    executor = ActionExecutor(vault=vault)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/kyc")

        # 1. Fill Name using value_ref
        fill_action = AgentAction(
            action=ActionType.FILL,
            target=ActionTarget(element_id="field_name"),
            value_ref="user_profile.name",
        )
        res1 = await executor.execute(page, fill_action, step=1)
        assert res1.success is True

        # Verify page actually received vault value locally
        input_val = await page.input_value("#field_name")
        assert input_val == "Custom Test User"

        # 2. Click Cancel button
        click_action = AgentAction(
            action=ActionType.CLICK,
            target=ActionTarget(element_id="btn_cancel"),
        )
        res2 = await executor.execute(page, click_action, step=2)
        assert res2.success is True

        await browser.close()


@pytest.mark.asyncio
async def test_executor_rejects_malicious_actions():
    executor = ActionExecutor()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Reject invalid URL scheme
        nav_action = AgentAction(
            action=ActionType.NAVIGATE,
            url="javascript:alert(1)",
        )
        with pytest.raises(ExecutorSecurityException):
            await executor.execute(page, nav_action)

        await browser.close()


@pytest.mark.asyncio
async def test_executor_requires_confirmation_for_destructive_action():
    executor = ActionExecutor(require_confirmation=True)
    action = AgentAction(
        action=ActionType.CLICK,
        target=ActionTarget(element_id="btn_submit", name="Submit Application"),
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/kyc")
        result = await executor.execute(page, action, step=1)
        assert result.success is False
        assert result.error_message == "confirmation_required"
        await browser.close()


@pytest.mark.asyncio
async def test_executor_reference_metadata_must_match_current_page():
    executor = ActionExecutor()
    executor.set_reference_map(
        {
            "e1": {
                "element_id": "btn_cancel",
                "role": "button",
                "name": "Not Cancel",
            }
        }
    )
    action = AgentAction(
        action=ActionType.CLICK,
        target=ActionTarget(ref="e1"),
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/kyc")
        result = await executor.execute(page, action, step=1)
        assert result.success is False
        assert "reference_name_mismatch" in (result.error_message or "")
        await browser.close()
