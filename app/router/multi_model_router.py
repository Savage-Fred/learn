"""Backward-compatible entry point re-exporting MultiModelRouter from engine.py."""

from app.router.engine import MultiModelRouter, ProviderUnavailableError

__all__ = ["MultiModelRouter", "ProviderUnavailableError"]
