"""
Local Synthetic KYC Web Application Server.
Hosts /login, /kyc, /success pages on localhost (port 9001) for PrivateEye evaluation.
Runs 100% locally with zero external network dependencies.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Synthetic KYC Demonstration Portal")

# Mount static directory for CSS, JS, images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def read_template(filename: str) -> str:
    path = TEMPLATES_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def index_redirect():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def get_login():
    return read_template("login.html")


@app.post("/login")
async def post_login(request: Request):
    # Authenticate and redirect to KYC form
    return RedirectResponse(url="/kyc", status_code=303)


@app.get("/kyc", response_class=HTMLResponse)
async def get_kyc():
    return read_template("kyc.html")


@app.post("/kyc")
async def post_kyc(request: Request):
    # Process KYC submission and redirect to Success page
    return RedirectResponse(url="/success", status_code=303)


@app.get("/success", response_class=HTMLResponse)
async def get_success():
    return read_template("success.html")


def run(host: str = "127.0.0.1", port: int = 9001):
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    run()
