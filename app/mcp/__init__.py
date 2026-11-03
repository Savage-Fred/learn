"""Model Context Protocol (MCP) server subsystem with stdio and SSE transports."""

from app.mcp.schemas import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    ToolDefinition,
)
from app.mcp.server import MCPServer
from app.mcp.tools import MCPToolRegistry
from app.mcp.transports.sse import router as mcp_router
from app.mcp.transports.stdio import run_stdio

__all__ = [
    "MCPServer",
    "MCPToolRegistry",
    "run_stdio",
    "mcp_router",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCError",
    "ToolDefinition",
    "PARSE_ERROR",
    "INVALID_REQUEST",
    "METHOD_NOT_FOUND",
    "INVALID_PARAMS",
    "INTERNAL_ERROR",
]
