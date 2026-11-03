"""JSON-RPC 2.0 and Model Context Protocol (MCP) data structures and error constants."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# Standard JSON-RPC 2.0 Error Codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# Model Context Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "learn-mcp"
SERVER_VERSION = "0.1.0"


class JSONRPCRequest(BaseModel):
    """Incoming JSON-RPC 2.0 request payload."""

    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error specification."""

    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    """Outgoing JSON-RPC 2.0 response payload."""

    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


class ToolDefinition(BaseModel):
    """MCP tool registration definition."""

    name: str
    description: str
    inputSchema: Dict[str, Any]


class ToolContentItem(BaseModel):
    """Content item returned in an MCP tool call result."""

    type: str = "text"
    text: str


class ToolCallResult(BaseModel):
    """Envelope wrapping MCP tool execution output."""

    content: List[ToolContentItem]
    isError: bool = False
