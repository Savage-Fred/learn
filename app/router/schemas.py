"""Data structures and schemas for multi-model routing and execution harnesses."""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


@dataclass
class WatchdogResult:
    """Result of an isolated process execution under SubprocessWatchdog."""

    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    timed_out: bool = False


@dataclass
class HarnessResponse:
    """Standardized response from any provider execution harness."""

    text: str
    provider: str
    model: str
    tier: str  # "subscription_cli", "direct_api", "mock"
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
    thinking_tokens: int = 0
    duration_ms: int = 0
    estimated_cost_usd: float = 0.0
    nominal_value_usd: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class RouteRequest(BaseModel):
    """Routing request payload."""

    prompt: str = Field(..., min_length=1, description="Non-empty prompt text")
    provider: str = Field(default="claude", description="Preferred provider: claude, codex, agy, or direct_api")
    model: Optional[str] = Field(default=None, description="Model identifier override")
    timeout_sec: float = Field(default=30.0, ge=0.1, le=300.0, description="Execution deadline in seconds")
    workflow: str = Field(default="general", description="Workflow context for telemetry categorization")
    simulate_timeout: bool = Field(default=False, description="Simulate CLI timeout for test verification")
    simulate_failure_tier: Optional[str] = Field(default=None, description="Simulate failure of a specific tier")


class RouteResult(BaseModel):
    """Result returned by MultiModelRouter."""

    text: str
    tier: str
    provider: str
    model: str
    fallback_triggered: bool = False
    duration_ms: int
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
