"""
Local Synthetic Demonstration Web Application Server.
Hosts configurable, data-driven synthetic portals (KYC, Checkout, Patient EHR, and dynamic fixtures).
Driven by declarative schemas in demo_configs/. Runs 100% locally with zero external network dependencies.
"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from demo_sites.site_loader import registry, render_page_html
from shared.config import config

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Synthetic Enterprise Demonstration Portals")

# Mount static directory for CSS, JS, images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def read_template_if_exists(filename: str) -> str | None:
    path = TEMPLATES_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


@app.get("/", response_class=HTMLResponse)
async def index_redirect():
    return RedirectResponse(url="/login")


@app.get("/api/sites")
async def get_sites():
    """Return list of all configured demo sites and their metadata."""
    return JSONResponse([s.model_dump() for s in registry.get_all_sites()])


@app.get("/api/ground_truth")
async def get_ground_truth():
    """Return dynamically exported ground-truth annotations."""
    return JSONResponse(registry.export_combined_ground_truth())


# ---------------------------------------------------------------------------
# Dynamic Config-Driven Route Dispatcher with Legacy Template Fallback
# ---------------------------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
async def get_login():
    tpl = read_template_if_exists("login.html")
    if tpl:
        return tpl
    found = registry.find_route("/login")
    if found:
        return render_page_html(found[0], found[1])
    return HTMLResponse("<h1>Login not found</h1>", status_code=404)


@app.post("/login")
async def post_login(request: Request):
    return RedirectResponse(url="/kyc", status_code=303)


@app.get("/kyc", response_class=HTMLResponse)
async def get_kyc():
    tpl = read_template_if_exists("kyc.html")
    if tpl:
        return tpl
    found = registry.find_route("/kyc")
    if found:
        return render_page_html(found[0], found[1])
    return HTMLResponse("<h1>KYC not found</h1>", status_code=404)


@app.post("/kyc")
async def post_kyc(request: Request):
    return RedirectResponse(url="/success", status_code=303)


@app.get("/checkout", response_class=HTMLResponse)
async def get_checkout():
    tpl = read_template_if_exists("checkout.html")
    if tpl:
        return tpl
    found = registry.find_route("/checkout")
    if found:
        return render_page_html(found[0], found[1])
    return HTMLResponse("<h1>Checkout not found</h1>", status_code=404)


@app.post("/checkout")
async def post_checkout(request: Request):
    return RedirectResponse(url="/success", status_code=303)


@app.get("/patient", response_class=HTMLResponse)
async def get_patient():
    tpl = read_template_if_exists("patient.html")
    if tpl:
        return tpl
    found = registry.find_route("/patient")
    if found:
        return render_page_html(found[0], found[1])
    return HTMLResponse("<h1>Patient EHR not found</h1>", status_code=404)


@app.post("/patient")
async def post_patient(request: Request):
    return RedirectResponse(url="/success", status_code=303)


@app.get("/success", response_class=HTMLResponse)
async def get_success():
    tpl = read_template_if_exists("success.html")
    if tpl:
        return tpl
    found = registry.find_route("/success")
    if found:
        return render_page_html(found[0], found[1])
    return HTMLResponse("<h1>Success not found</h1>", status_code=404)


# ---------------------------------------------------------------------------
# Generic Route Handler for Dynamic & 4th Fixture Routes
# ---------------------------------------------------------------------------

@app.get("/{path:path}", response_class=HTMLResponse)
async def dynamic_route_get(path: str):
    full_path = f"/{path}"
    found = registry.find_route(full_path)
    if found:
        site, route = found
        return render_page_html(site, route)
    return HTMLResponse(f"<h1>Route '{full_path}' Not Found</h1>", status_code=404)


@app.post("/{path:path}")
async def dynamic_route_post(path: str, request: Request):
    full_path = f"/{path}"
    found = registry.find_route(full_path)
    if found:
        _, route = found
        target = route.next_route or "/success"
        return RedirectResponse(url=target, status_code=303)
    return RedirectResponse(url="/", status_code=303)


def run(host: str | None = None, port: int | None = None):
    h = host or config.HOST
    p = port or config.PORT_PORTAL
    uvicorn.run(app, host=h, port=p, log_level="warning")


if __name__ == "__main__":
    run()
