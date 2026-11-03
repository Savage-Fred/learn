"""FastAPI application entry point and CLI runner for Savage-Fred/learn."""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings

app = FastAPI(
    title="Savage-Fred/learn",
    description="Local-first technical learning and L4-L6 interview preparation platform",
    version="0.1.0",
)


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

    return {
        "status": "operational",
        "host": settings.host,
        "port": settings.port,
        "tailnet_reachability": f"http://{settings.magic_dns}:{settings.port}",
        "data_dir": exposed_data_dir,
        "use_mock_llm": settings.use_mock_llm,
        "topics_available": [
            "leetcode",
            "system-design",
            "security",
            "privacy-engineering",
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
