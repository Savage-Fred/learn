"""CLI runner for python -m app.mcp."""

import sys
from app.mcp.transports.stdio import run_stdio

if __name__ == "__main__":
    run_stdio()
