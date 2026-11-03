"""FastAPI application entry point and CLI runner for Savage-Fred/learn."""

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.config import settings

app = FastAPI(
    title="Savage-Fred/learn",
    description="Local-first technical learning and L4-L6 interview preparation platform",
    version="0.1.0",
)


@app.middleware("http")
async def verify_network_access(request: Request, call_next):
    """Enforce authentication on non-loopback clients when LEARN_API_TOKEN is configured."""
    if settings.api_token:
        client_host = request.client.host if request.client else "unknown"
        is_loopback = client_host in ("127.0.0.1", "::1", "localhost", "testclient")
        if not is_loopback:
            auth_header = request.headers.get("Authorization", "")
            token_header = request.headers.get("X-Learn-Token", "")
            bearer_token = (
                auth_header.replace("Bearer ", "").strip()
                if "Bearer " in auth_header
                else ""
            )
            if (
                bearer_token != settings.api_token
                and token_header != settings.api_token
            ):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unauthorized: invalid or missing API token"},
                )
    return await call_next(request)


@app.get("/healthz")
@app.get("/health")
async def health_check():
    """Health check endpoint for service liveness."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/v1/status")
async def platform_status(request: Request):
    """Platform configuration and reachability status."""
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
