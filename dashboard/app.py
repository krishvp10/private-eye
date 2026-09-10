"""
PrivateEye Visual Web Dashboard Server.
Hosts real-time side-by-side visual privacy inspector on http://127.0.0.1:8080.
Streams live step captures, redaction overlays, and zero-leak telemetry via Server-Sent Events (SSE).
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

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

# In-memory step event queue and subscriber set
step_subscribers: List[asyncio.Queue] = []
latest_step_state: Dict[str, Any] = {
    "status": "ready",
    "step": 0,
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
    """Return the latest step snapshot."""
    return JSONResponse(latest_step_state)


@app.post("/api/step")
async def post_step(payload: Dict[str, Any]):
    """Receives a step snapshot broadcast from PrivateEyeAgent."""
    global latest_step_state
    latest_step_state.update(payload)
    latest_step_state["status"] = "running"
    
    # Store in history
    hist = latest_step_state.setdefault("history", [])
    hist.append({
        "step": payload.get("step", 0),
        "url": payload.get("url", ""),
        "action": payload.get("action", {}),
        "detections_count": len(payload.get("detections", [])),
        "redactions_count": len(payload.get("redactions", [])),
        "total_ms": payload.get("metrics", {}).get("total_ms", 0),
    })

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

    return {"status": "ok", "subscribers": len(step_subscribers)}


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
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield ": keepalive\n\n"
        finally:
            if queue in step_subscribers:
                step_subscribers.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/trigger")
async def trigger_run(payload: Optional[Dict[str, Any]] = None):
    """Launch a background agent run for interactive demonstrations."""
    params = payload or {}
    domain = params.get("domain", "kyc")
    port = params.get("port", 9001)

    url_map = {
        "kyc": f"http://127.0.0.1:{port}/login",
        "checkout": f"http://127.0.0.1:{port}/checkout",
        "patient": f"http://127.0.0.1:{port}/patient",
    }
    target_url = url_map.get(domain, url_map["kyc"])

    # Launch CLI run in background
    cmd = [
        sys.executable,
        "-m",
        "client.agent",
        "--url",
        target_url,
        "--server-url",
        "http://127.0.0.1:8000",
        "--max-steps",
        "15",
    ]
    env = dict(os.environ)
    env["PRIVATEEYE_DASHBOARD_URL"] = "http://127.0.0.1:8080"
    
    proc = subprocess.Popen(
        cmd,
        cwd=str(BASE_DIR.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "status": "launched",
        "pid": proc.pid,
        "domain": domain,
        "url": target_url,
    }


def run(host: str = "127.0.0.1", port: int = 8080):
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run()
