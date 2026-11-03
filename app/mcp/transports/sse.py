"""FastAPI Server-Sent Events (SSE) router for MCP over Tailnet."""

import asyncio
import json
import uuid
from typing import Dict, Optional
from fastapi import APIRouter, Request, Query
from starlette.responses import StreamingResponse, JSONResponse, Response

from app.mcp.server import MCPServer

router = APIRouter(tags=["mcp"])
mcp_server = MCPServer()

# Map session_id -> asyncio.Queue for streaming SSE events
active_sessions: Dict[str, asyncio.Queue] = {}


def _is_allowed_origin(origin: Optional[str]) -> bool:
    """Validate Origin header against local loopback and tailnet domains."""
    if not origin:
        return True
    origin_clean = origin.strip().lower()
    if origin_clean.startswith("http://localhost") or origin_clean.startswith("http://127.0.0.1"):
        return True
    if origin_clean.startswith("https://localhost") or origin_clean.startswith("https://127.0.0.1"):
        return True
    if origin_clean.endswith(".ts.net") or "ts.net:" in origin_clean or ".ts.net/" in origin_clean:
        return True
    return False


@router.get("/sse")
@router.get("/mcp/sse")
async def sse_connect(request: Request):
    """MCP SSE handshake: establishes persistent SSE stream and publishes endpoint event."""
    origin = request.headers.get("origin")
    if not _is_allowed_origin(origin):
        return JSONResponse(status_code=403, content={"error": "Forbidden: untrusted origin"})

    session_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    active_sessions[session_id] = queue

    async def event_generator():
        try:
            # First event: publish the message endpoint URI inside cleanup block
            endpoint_uri = f"/messages?session_id={session_id}"
            yield f"event: endpoint\ndata: {endpoint_uri}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"event: message\ndata: {json.dumps(message)}\n\n"
                except (asyncio.TimeoutError, TimeoutError):
                    # Keepalive comment
                    yield ": ping\n\n"
        finally:
            active_sessions.pop(session_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/messages")
@router.post("/mcp/messages")
async def sse_message(
    request: Request,
    session_id: Optional[str] = Query(None),
    sessionId: Optional[str] = Query(None),
):
    """Receive JSON-RPC request for an active SSE session."""
    origin = request.headers.get("origin")
    if not _is_allowed_origin(origin):
        return JSONResponse(status_code=403, content={"error": "Forbidden: untrusted origin"})

    target_session = session_id or sessionId
    if not target_session or target_session not in active_sessions:
        return JSONResponse(status_code=404, content={"error": f"Session '{target_session}' not found"})

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON"},
            },
        )

    queue = active_sessions[target_session]
    resp = mcp_server.handle_request(payload)
    if resp is not None:
        await queue.put(resp)

    return Response(status_code=202)


@router.post("/mcp/call")
@router.post("/mcp")
async def direct_mcp_call(request: Request):
    """Direct synchronous JSON-RPC POST endpoint for HTTP RPC clients."""
    origin = request.headers.get("origin")
    if not _is_allowed_origin(origin):
        return JSONResponse(status_code=403, content={"error": "Forbidden: untrusted origin"})

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON"},
            },
        )

    resp = mcp_server.handle_request(payload)
    return JSONResponse(content=resp or {})
