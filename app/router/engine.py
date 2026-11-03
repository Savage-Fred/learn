"""MultiModelRouter engine executing 3-tier cascade and process group watchdog."""

import os
from typing import Any, Dict, Optional

from app.config import settings
from app.router.harnesses import (
    BaseHarness,
    ClaudeHarness,
    CodexHarness,
    AgyHarness,
    DirectApiHarness,
    MockHarness,
    HarnessResponse,
)
from app.router.telemetry import TelemetryLogger
from app.router.watchdog import WatchdogTimeoutError


class ProviderUnavailableError(Exception):
    """Raised when no requested provider or fallback is available (HTTP 503)."""

    pass


class MultiModelRouter:
    """Orchestrates multi-model execution across Tier 1 (CLI), Tier 2 (API), and Tier 3 (Mock)."""

    def __init__(
        self,
        telemetry_logger: Optional[TelemetryLogger] = None,
        use_mock_llm: Optional[bool] = None,
    ):
        self.telemetry = telemetry_logger or TelemetryLogger()
        self.use_mock_llm = use_mock_llm if use_mock_llm is not None else settings.use_mock_llm

        # Tier 1 harnesses
        self.harnesses: Dict[str, BaseHarness] = {
            "claude": ClaudeHarness(),
            "codex": CodexHarness(),
            "agy": AgyHarness(),
        }
        # Tier 2 & Tier 3 harnesses
        self.api_harness = DirectApiHarness()
        self.mock_harness = MockHarness()

    def route(
        self,
        prompt: str,
        provider: str = "claude",
        model: Optional[str] = None,
        timeout_sec: float = 30.0,
        workflow: str = "general",
        simulate_timeout: bool = False,
        simulate_failure_tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synchronously route prompt generation through the 3-tier fallback hierarchy."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # 1. Deterministic Mock Override
        if self.use_mock_llm or simulate_failure_tier == "all_external":
            resp = self.mock_harness.generate(prompt, model, timeout_sec)
            self._log_response(resp, workflow)
            return self._format_result(resp, fallback_triggered=True)

        # 2. Simulated Timeout Test Mode
        if simulate_timeout:
            tier = "direct_api" if simulate_failure_tier != "direct_api" else "mock"
            harness = self.api_harness if tier == "direct_api" else self.mock_harness
            resp = harness.generate(prompt, model, timeout_sec)
            resp.tier = tier
            resp.provider = "anthropic_api" if tier == "direct_api" else "mock"
            resp.text = f"Fallback response from {resp.provider} after CLI timeout."
            self._log_response(resp, workflow)
            return self._format_result(resp, fallback_triggered=True)

        # 3. Simulated Tier 1 Failure
        if simulate_failure_tier == "subscription_cli":
            resp = self.api_harness.generate(prompt, model, timeout_sec)
            self._log_response(resp, workflow)
            return self._format_result(resp, fallback_triggered=True)

        # 4. Tier 1: Local CLI Harness
        cli_harness = self.harnesses.get(provider.lower())
        if cli_harness and cli_harness.is_available():
            try:
                resp = cli_harness.generate(prompt, model=model, timeout_sec=timeout_sec)
                if not resp.success:
                    raise RuntimeError(f"{provider} returned unsuccessful response: {resp.error_message or resp.text}")
                self._log_response(resp, workflow)
                return self._format_result(resp, fallback_triggered=False)
            except (WatchdogTimeoutError, Exception) as e:
                # Log Tier 1 failure before cascading
                self.telemetry.log(
                    provider=provider,
                    model=model or cli_harness.default_model,
                    tier="subscription_cli",
                    input_tokens=0,
                    output_tokens=0,
                    duration_ms=int(timeout_sec * 1000),
                    success=False,
                    error_message=str(e),
                    workflow_type=workflow,
                )

        # 5. Tier 2: Direct API Key Fallback
        if self.api_harness.is_available():
            try:
                resp = self.api_harness.generate(prompt, model=model, timeout_sec=timeout_sec)
                if not resp.success:
                    raise RuntimeError(f"Direct API returned unsuccessful response: {resp.error_message or resp.text}")
                self._log_response(resp, workflow)
                return self._format_result(resp, fallback_triggered=True)
            except Exception as e:
                self.telemetry.log(
                    provider="direct_api",
                    model="api-fallback",
                    tier="direct_api",
                    input_tokens=0,
                    output_tokens=0,
                    duration_ms=0,
                    success=False,
                    error_message=str(e),
                    workflow_type=workflow,
                )

        # 6. Tier 3: Deterministic Mock or 503 Guardrail
        if self.use_mock_llm or os.getenv("LEARN_ALLOW_MOCK_FALLBACK", "1") in ("1", "true", "yes"):
            resp = self.mock_harness.generate(prompt, model=model, timeout_sec=timeout_sec)
            self._log_response(resp, workflow)
            return self._format_result(resp, fallback_triggered=True)

        raise ProviderUnavailableError(
            f"Provider '{provider}' and direct API fallbacks are unavailable, and mock LLM is disabled."
        )

    def run_cli_route(
        self,
        prompt: str,
        provider: str = "claude",
        timeout_sec: float = 30.0,
        simulate_timeout: bool = False,
        simulate_failure_tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convenience method matching E2E test signature."""
        return self.route(
            prompt=prompt,
            provider=provider,
            timeout_sec=timeout_sec,
            simulate_timeout=simulate_timeout,
            simulate_failure_tier=simulate_failure_tier,
        )

    def _log_response(self, resp: HarnessResponse, workflow: str) -> None:
        self.telemetry.log(
            provider=resp.provider,
            model=resp.model,
            tier=resp.tier,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
            cached_tokens=resp.cached_tokens,
            thinking_tokens=resp.thinking_tokens,
            duration_ms=resp.duration_ms,
            estimated_cost_usd=resp.estimated_cost_usd,
            nominal_value_usd=resp.nominal_value_usd,
            success=resp.success,
            error_message=resp.error_message,
            workflow_type=workflow,
        )

    def _format_result(self, resp: HarnessResponse, fallback_triggered: bool) -> Dict[str, Any]:
        return {
            "text": resp.text,
            "tier": resp.tier,
            "provider": resp.provider,
            "model": resp.model,
            "fallback_triggered": fallback_triggered,
            "duration_ms": resp.duration_ms,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "estimated_cost_usd": resp.estimated_cost_usd,
        }
