"""Stdio transport for local CLI harnesses (claude, codex, agy)."""

import json
import sys
from typing import Optional
from app.mcp.schemas import PARSE_ERROR
from app.mcp.server import MCPServer


def run_stdio(server: Optional[MCPServer] = None) -> None:
    """Read line-delimited JSON-RPC from sys.stdin, write responses to sys.stdout."""
    mcp = server or MCPServer()

    # Reconfigure streams to utf-8 if supported
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as jde:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": PARSE_ERROR, "message": f"Parse error: {str(jde)}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
            continue

        resp = mcp.handle_request(payload)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


def main():
    """Main entrypoint for stdio runner."""
    run_stdio()


if __name__ == "__main__":
    main()
