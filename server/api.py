"""
FastAPI Server for PrivateEye VLM Backend.
Provides /v1/analyze, /v1/health, and /v1/runs endpoints.
Guarantees zero logging of raw screenshots or sensitive values.
"""

import logging
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from server.mock_vlm import MockVLM
from server.validation import validate_agent_action
from server.vlm import VLMAdapter
from shared.protocol import (
    AgentAction,
    ScreenContext,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SERVER] %(message)s",
)
logger = logging.getLogger("private_eye_server")

app = FastAPI(
    title="PrivateEye VLM Server",
    version="1.0.0",
    description="Privacy-Preserving VLM Backend for Browser Actions",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory audit run log (stores metadata only, NO raw images or PII)
RUN_AUDIT_LOGS: list[dict[str, Any]] = []

# Mock VLM instance
mock_vlm = MockVLM()
vlm = VLMAdapter()


@app.get("/v1/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint confirming server and model readiness."""
    return {
        "status": "ok",
        "service": "PrivateEye-VLM-Server",
        "mode": vlm.mode,
        "version": "1.0.0",
    }


@app.post("/v1/analyze", response_model=AgentAction)
async def analyze_screen(context: ScreenContext, request: Request) -> AgentAction:
    """
    Primary inference endpoint.
    Receives sanitized ScreenContext and returns safe AgentAction.
    """
    start_time = time.perf_counter()

    # Verify payload boundaries
    payload_size_kb = len(context.image_b64.encode("utf-8")) / 1024.0
    if payload_size_kb > 1024.0:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Sanitized image payload exceeds 1MB limit ({payload_size_kb:.1f} KB)",
        )

    # Select the configured provider. Mock mode remains the safe offline default.
    try:
        raw_action = await vlm.analyze(context)
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("VLM request failed closed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="VLM reasoning failed") from exc

    # Validate action against whitelist & LLM01 guardrails
    validated_action = validate_agent_action(raw_action.model_dump())

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Privacy-safe telemetry logging
    audit_entry = {
        "run_id": context.run_id,
        "step": context.step,
        "url": context.url,
        "payload_size_kb": round(payload_size_kb, 2),
        "redactions_count": len(context.redactions),
        "action_type": validated_action.action.value,
        "target": validated_action.target.model_dump() if validated_action.target else None,
        "value_ref": validated_action.value_ref,
        "duration_ms": duration_ms,
    }
    RUN_AUDIT_LOGS.append(audit_entry)

    logger.info(
        "Step %d: URL=%s | Redactions=%d | Action=%s | Latency=%.2fms",
        context.step,
        context.url,
        len(context.redactions),
        validated_action.action.value,
        duration_ms,
    )

    return validated_action


@app.get("/v1/runs")
async def get_run_audit() -> list[dict[str, Any]]:
    """Return read-only telemetry audit trail (PII-free)."""
    return RUN_AUDIT_LOGS


if __name__ == "__main__":
    import uvicorn

    from shared.config import config

    uvicorn.run(
        "server.api:app",
        host=config.SERVER_HOST,
        port=config.PORT_SERVER,
        log_level="info",
    )
