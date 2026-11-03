"""Multi-model router subsystem with subscription-first CLI harnesses, watchdog, and telemetry."""

from app.router.engine import MultiModelRouter, ProviderUnavailableError
from app.router.harnesses import (
    BaseHarness,
    ClaudeHarness,
    CodexHarness,
    AgyHarness,
    DirectApiHarness,
    MockHarness,
    HarnessResponse,
)
from app.router.schemas import RouteRequest, RouteResult, WatchdogResult
from app.router.telemetry import TelemetryLogger, TelemetryRecord
from app.router.watchdog import SubprocessWatchdog, WatchdogTimeoutError

__all__ = [
    "MultiModelRouter",
    "ProviderUnavailableError",
    "BaseHarness",
    "ClaudeHarness",
    "CodexHarness",
    "AgyHarness",
    "DirectApiHarness",
    "MockHarness",
    "HarnessResponse",
    "RouteRequest",
    "RouteResult",
    "TelemetryLogger",
    "TelemetryRecord",
    "SubprocessWatchdog",
    "WatchdogResult",
    "WatchdogTimeoutError",
]
