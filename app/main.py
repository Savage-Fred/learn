"""FastAPI application entry point, Tailnet mesh integration, and UI mounting."""

from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, JSONResponse

from app.config import settings
from app.mcp import mcp_router
from app.api import (
    topics_router,
    quiz_router,
    interview_router,
    resume_router,
    telemetry_router,
)

app = FastAPI(
    title="Savage-Fred/learn",
    description="Local-first technical learning and L4-L6 interview preparation platform",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Static Files & UI Templates
# -----------------------------------------------------------------------------
ui_dir = Path(__file__).parent / "ui"
static_dir = ui_dir / "static"
templates_dir = ui_dir / "templates"

static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))


# -----------------------------------------------------------------------------
# Network Authorization Middleware
# -----------------------------------------------------------------------------
@app.middleware("http")
async def verify_network_access(request: Request, call_next):
    """Enforce authentication on non-loopback / Tailnet clients when LEARN_API_TOKEN is configured."""
    if settings.api_token:
        client_host = request.client.host if request.client else "unknown"
        is_loopback = client_host in ("127.0.0.1", "::1", "localhost", "testclient")
        if not is_loopback:
            auth_header = request.headers.get("Authorization", "")
            token_header = request.headers.get("X-Learn-Token", "")
            query_token = request.query_params.get("token", "")

            bearer_token = (
                auth_header.replace("Bearer ", "").strip()
                if "Bearer " in auth_header
                else ""
            )

            if (
                bearer_token != settings.api_token
                and token_header != settings.api_token
                and query_token != settings.api_token
            ):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unauthorized: invalid or missing API token"},
                )
    return await call_next(request)


# -----------------------------------------------------------------------------
# Router Registrations
# -----------------------------------------------------------------------------
app.include_router(mcp_router)

# Standard API routes under /api/...
app.include_router(topics_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(telemetry_router, prefix="/api")

# Compatibility aliases for /api/v1/...
app.include_router(topics_router, prefix="/api/v1", include_in_schema=False)
app.include_router(quiz_router, prefix="/api/v1", include_in_schema=False)
app.include_router(interview_router, prefix="/api/v1", include_in_schema=False)
app.include_router(resume_router, prefix="/api/v1", include_in_schema=False)
app.include_router(telemetry_router, prefix="/api/v1", include_in_schema=False)


# -----------------------------------------------------------------------------
# UI Root Route & Health Checks
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Serve the single-page application dashboard."""
    index_file = templates_dir / "index.html"
    if index_file.exists():
        return templates.TemplateResponse(request=request, name="index.html")
    return HTMLResponse("<html><body><h1>Savage-Fred/learn</h1><p>UI assets loading...</p></body></html>")


@app.get("/healthz")
@app.get("/health")
async def health_check():
    """Service liveness probe."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/status")
@app.get("/api/v1/status")
async def platform_status(request: Request):
    """Platform configuration, reachability status, and curriculum availability."""
    client_host = request.client.host if request.client else "unknown"
    is_trusted = client_host in ("127.0.0.1", "::1", "localhost", "testclient")
    exposed_data_dir = str(settings.data_dir) if is_trusted else "[protected]"

    reachability = (
        f"http://{settings.magic_dns}:{settings.port}"
        if settings.magic_dns
        else f"http://{settings.host}:{settings.port}"
    )

    return {
        "status": "operational",
        "host": settings.host,
        "port": settings.port,
        "reachability": reachability,
        "data_dir": exposed_data_dir,
        "use_mock_llm": settings.use_mock_llm,
        "domains_available": [
            "leetcode",
            "system-design",
            "security",
            "privacy-engineering",
        ],
        "priority_topics_available": [
            "pythonic-coding-patterns",
            "masters-algorithms",
            "data-structures",
            "modern-authn-authz",
            "pets-for-ai",
            "threat-modeling",
            "agent-access-models",
            "statistics-for-data-analysis",
            "rust",
            "go",
            "modern-differential-privacy",
        ],
    }


def run_server():
    """Launch Uvicorn server using configured host and port."""
    settings.ensure_data_directories()
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)


def cli():
    """Console script entry point."""
    run_server()


if __name__ == "__main__":
    cli()
