"""
PrivateEye Visual Web Dashboard Server.
Hosts real-time side-by-side visual privacy inspector on http://127.0.0.1:8080.
Features:
- Live step streaming via Server-Sent Events (SSE).
- Complete immutable step history with interactive timeline scrubber.
- Dynamic domain enumeration from declarative site configs.
- Zero-leak wire verification and latency waterfall metrics.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from demo_sites.site_loader import registry
from shared.config import config

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="PrivateEye Visual Privacy Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory step event queue, subscriber set, and complete step history
step_subscribers: list[asyncio.Queue] = []
step_history: dict[int, dict[str, Any]] = {}

latest_step_state: dict[str, Any] = {
    "status": "ready",
    "step": 0,
    "total_steps": 0,
    "available_steps": [],
    "task": "Ready to launch PrivateEye privacy agent",
    "url": "http://127.0.0.1:9001/login",
    "raw_image_b64": "",
    "sanitized_image_b64": "",
    "action": None,
    "detections": [],
    "redactions": [],
    "metrics": {
        "capture_ms": 0,
        "privacy_ms": 0,
        "redaction_ms": 0,
        "network_ms": 0,
        "execution_ms": 0,
        "total_ms": 0,
        "payload_bytes": 0,
        "raw_pii_leaks": 0,
    },
    "history": [],
}

if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>PrivateEye Dashboard loading...</h1>"


@app.get("/api/state")
async def get_state():
    """Return the latest step snapshot and available historical steps."""
    resp = dict(latest_step_state)
    resp["available_steps"] = sorted(list(step_history.keys()))
    resp["total_steps"] = len(step_history)
    return JSONResponse(resp)


@app.get("/api/domains")
async def get_domains():
    """Return all configured domains dynamically loaded from demo_configs/."""
    sites = registry.get_all_sites()
    return JSONResponse([
        {
            "id": s.site_id,
            "name": s.display_name,
            "entry_route": s.entry_route,
            "task": s.task,
        }
        for s in sites
    ])


@app.get("/api/history")
async def get_history():
    """Return summary list of all recorded steps in the active run."""
    steps_summary = [
        {
            "step": s,
            "url": data.get("url", ""),
            "action": data.get("action", {}),
            "detections_count": len(data.get("detections", [])),
            "redactions_count": len(data.get("redactions", [])),
            "total_ms": data.get("metrics", {}).get("total_ms", 0),
        }
        for s, data in sorted(step_history.items())
    ]
    return JSONResponse({
        "total_steps": len(step_history),
        "available_steps": sorted(list(step_history.keys())),
        "steps": steps_summary,
    })


@app.get("/api/history/{step_num}")
async def get_history_step(step_num: int):
    """Return full snapshot for a specific historical step (for replay scrubber)."""
    if step_num in step_history:
        return JSONResponse(step_history[step_num])
    return JSONResponse({"error": f"Step {step_num} not found"}, status_code=404)


@app.post("/api/step")
async def post_step(payload: dict[str, Any]):
    """Receives a step snapshot broadcast from PrivateEyeAgent."""
    global latest_step_state
    step = int(payload.get("step", 0))

    # Store full snapshot in immutable step history
    step_history[step] = dict(payload)

    latest_step_state.update(payload)
    latest_step_state["status"] = "running"
    latest_step_state["total_steps"] = len(step_history)
    latest_step_state["available_steps"] = sorted(list(step_history.keys()))

    # Broadcast to all active SSE subscribers
    data_str = json.dumps(payload)
    dead_subscribers = []
    for q in step_subscribers:
        try:
            q.put_nowait(data_str)
        except Exception:
            dead_subscribers.append(q)
    for q in dead_subscribers:
        step_subscribers.remove(q)

    return {"status": "ok", "step": step, "subscribers": len(step_subscribers)}


@app.get("/api/events")
async def events_stream(request: Request):
    """Server-Sent Events endpoint streaming real-time agent updates."""
    queue: asyncio.Queue = asyncio.Queue()
    step_subscribers.append(queue)

    async def event_generator():
        try:
            # Send initial state immediately upon connection
            yield f"data: {json.dumps(latest_step_state)}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {data}\n\n"
                except TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            if queue in step_subscribers:
                step_subscribers.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/trigger")
async def trigger_run(payload: dict[str, Any] | None = None):
    """Launch a background agent run for interactive demonstrations."""
    global step_history
    params = payload or {}
    domain = params.get("domain", "kyc")
    portal_port = params.get("port", config.PORT_PORTAL)
    server_port = config.PORT_SERVER

    # Clear step history on fresh run
    step_history.clear()

    # Match target URL dynamically from registry
    site = registry.get_site(domain)
    entry_route = site.entry_route if site else f"/{domain}"
    target_url = f"http://127.0.0.1:{portal_port}{entry_route}"

    cmd = [
        sys.executable,
        "-m",
        "client.agent",
        "--url",
        target_url,
        "--server-url",
        f"http://127.0.0.1:{server_port}",
        "--dashboard-url",
        f"http://127.0.0.1:{config.PORT_DASHBOARD}",
        "--max-steps",
        "15",
    ]
    env = dict(os.environ)
    env["PRIVATEEYE_DASHBOARD_URL"] = f"http://127.0.0.1:{config.PORT_DASHBOARD}"

    proc = subprocess.Popen(
        cmd,
        cwd=str(BASE_DIR.parent),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {
        "status": "launched",
        "pid": proc.pid,
        "domain": domain,
        "url": target_url,
    }


def run(host: str | None = None, port: int | None = None):
    h = host or config.HOST
    p = port or config.PORT_DASHBOARD
    uvicorn.run(app, host=h, port=p, log_level="info")


if __name__ == "__main__":
    run()
