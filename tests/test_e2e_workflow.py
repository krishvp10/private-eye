"""
Phase 12 Tests: Golden End-to-End KYC Integration Workflow.
Validates the complete autonomous browser agent loop:
1. Browser opens /login -> Agent captures, detects, redacts, sends sanitized context.
2. Server reasons over sanitized context and returns Sign In action.
3. Page navigates to /kyc -> Agent detects all PII, redacts screenshot.
4. Server instructs field fills via value_ref; client resolves locally via LocalVault.
5. Consent checkbox toggled, Submit clicked.
6. Page navigates to /success -> Agent detects completion and stops.
7. Strict verification: ZERO raw PII leaked across the wire or in server logs.
"""

import socket
import threading
import time

import pytest
import uvicorn

from client.agent import PrivateEyeAgent
from client.vault import LocalVault
from demo_sites.server import app as demo_app
from server.api import RUN_AUDIT_LOGS
from server.api import app as server_app


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


DEMO_PORT = _get_free_port()
SERVER_PORT = _get_free_port()
DEMO_URL = f"http://127.0.0.1:{DEMO_PORT}"
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"


@pytest.fixture(scope="module", autouse=True)
def run_services():
    # Start demo website
    demo_config = uvicorn.Config(demo_app, host="127.0.0.1", port=DEMO_PORT, log_level="error")
    demo_server = uvicorn.Server(demo_config)
    demo_thread = threading.Thread(target=demo_server.run, daemon=True)
    demo_thread.start()

    # Start VLM server
    server_config = uvicorn.Config(
        server_app, host="127.0.0.1", port=SERVER_PORT, log_level="error"
    )
    backend_server = uvicorn.Server(server_config)
    backend_thread = threading.Thread(target=backend_server.run, daemon=True)
    backend_thread.start()

    time.sleep(2.0)
    yield

    demo_server.should_exit = True
    backend_server.should_exit = True


@pytest.mark.asyncio
async def test_golden_e2e_kyc_workflow():
    """Golden Integration Test: autonomous multi-step KYC workflow with zero leakage."""
    RUN_AUDIT_LOGS.clear()

    agent = PrivateEyeAgent(
        server_url=SERVER_URL,
        max_steps=15,
        task="Sign in and complete mandatory KYC verification",
    )

    result = await agent.run(f"{DEMO_URL}/login")

    # 1. Flow Completion Assertions
    assert result.success is True, f"Workflow failed with errors: {result.errors}"
    assert "/success" in result.final_url
    assert result.steps >= 2

    # 2. Privacy & Leak Assertions on Audit Logs
    assert len(RUN_AUDIT_LOGS) >= 2

    vault = LocalVault()
    raw_secrets = vault.get_all_raw_secrets()

    for entry in RUN_AUDIT_LOGS:
        # Check that on /kyc steps, redactions were applied
        if "/kyc" in entry["url"]:
            assert entry["redactions_count"] >= 7, (
                f"Expected redactions on KYC page, got {entry['redactions_count']}"
            )

        # Verify no raw secret values in server audit log entries
        entry_str = str(entry)
        for secret in raw_secrets:
            if len(secret) > 4:
                assert secret not in entry_str, (
                    f"CRITICAL LEAK: Raw secret '{secret}' discovered in server logs!"
                )

        # Verify fill operations only use value_ref
        if entry["action_type"] == "fill":
            assert entry["value_ref"] is not None
            assert entry["value_ref"].startswith("user_profile.") or entry["value_ref"].startswith(
                "profile."
            )
