"""Core Model Context Protocol (MCP) server dispatcher."""

import json
import logging
from typing import Any, Dict, Optional

from app.mcp.schemas import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    MCP_PROTOCOL_VERSION,
    SERVER_NAME,
    SERVER_VERSION,
)
from app.mcp.tools import MCPToolRegistry

logger = logging.getLogger("learn.mcp")


class MCPServer:
    """JSON-RPC 2.0 compliant Model Context Protocol server."""

    def __init__(self, registry: Optional[MCPToolRegistry] = None):
        self.registry = registry or MCPToolRegistry()
        self.initialized: bool = False

    def handle_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming JSON-RPC 2.0 message."""
        if not isinstance(payload, dict):
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": INVALID_REQUEST,
                    "message": "Invalid Request: payload must be a JSON object",
                },
            }

        req_id = payload.get("id")
        method = payload.get("method")
        params = payload.get("params")
        if params is None:
            params = {}
        elif not isinstance(params, dict):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": INVALID_PARAMS,
                    "message": "Invalid Params: params must be a JSON object",
                },
            }

        if not method or not isinstance(method, str):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": INVALID_REQUEST,
                    "message": "Invalid Request: missing or invalid method",
                },
            }

        # 1. MCP Notifications (Must return None per JSON-RPC 2.0)
        if method.startswith("notifications/"):
            if method == "notifications/initialized":
                self.initialized = True
            return None

        # 2. Ping
        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        # 3. MCP Initialization Handshake
        if method == "initialize":
            self.initialized = True
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            }

        # 2. Tools Discovery
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.registry.list_tools()},
            }

        # 3. Tool Execution
        if method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})

            if not tool_name or not isinstance(tool_name, str):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": INVALID_PARAMS, "message": "Missing tool name in params"},
                }

            if not self.registry.has_tool(tool_name):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": METHOD_NOT_FOUND, "message": f"Tool '{tool_name}' not found"},
                }

            try:
                result_data = self.registry.execute_tool(tool_name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result_data)}],
                        "isError": False,
                    },
                }
            except ValueError as ve:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": INVALID_PARAMS, "message": str(ve)},
                }
            except KeyError as ke:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": INVALID_PARAMS, "message": str(ke)},
                }
            except Exception as e:
                logger.exception("Error executing MCP tool '%s'", tool_name)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": INTERNAL_ERROR, "message": f"Internal error: {str(e)}"},
                }

        # 4. Unknown Method
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": METHOD_NOT_FOUND, "message": f"Method not found: '{method}'"},
        }
