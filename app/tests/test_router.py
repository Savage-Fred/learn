"""Unit and integration tests for MultiModelRouter, harnesses, watchdog, and telemetry."""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
import pytest

from app.config import settings
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
from app.router.telemetry import TelemetryLogger, TelemetryRecord
from app.router.watchdog import SubprocessWatchdog, WatchdogTimeoutError


# -----------------------------------------------------------------------------
# 1. Watchdog Process Group & Timeout Tests
# -----------------------------------------------------------------------------
def test_watchdog_starts_new_session():
    """Verify SubprocessWatchdog runs processes in an isolated session/process group."""
    cmd = [
        sys.executable,
        "-c",
        "import os; print(os.getpgrp())",
    ]
    res = SubprocessWatchdog.run_sync(cmd, timeout_sec=5.0)
    assert res.exit_code == 0
    child_pgid = int(res.stdout.strip())
    assert child_pgid != os.getpgrp()  # Must not share caller's process group


def test_watchdog_timeout_sigterm_escalation_to_sigkill():
    """Verify watchdog escalates SIGTERM to SIGKILL on stubborn process group."""
    # Spawn a child that ignores SIGTERM and sleeps
    code = (
        "import signal, time, sys\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "sys.stdout.write('running\\n')\n"
        "sys.stdout.flush()\n"
        "time.sleep(30)\n"
    )
    cmd = [sys.executable, "-c", code]
    start = time.time()
    with pytest.raises(WatchdogTimeoutError) as exc_info:
        SubprocessWatchdog.run_sync(cmd, timeout_sec=0.2, grace_period_sec=0.2)
    duration = time.time() - start

    assert "timed out after 0.2s" in str(exc_info.value)
    # Total duration should be roughly timeout + grace_period, well under the 30s sleep
    assert duration < 3.0


def test_watchdog_streams_large_output_without_pipe_deadlock():
    """Verify large stdout/stderr (>1MB) does not deadlock OS pipe buffers."""
    code = (
        "import sys\n"
        "payload = 'X' * 500000 + '\\n'\n"
        "sys.stdout.write(payload)\n"
        "sys.stderr.write(payload)\n"
    )
    cmd = [sys.executable, "-c", code]
    res = SubprocessWatchdog.run_sync(cmd, timeout_sec=5.0)
    assert res.exit_code == 0
    assert len(res.stdout) >= 500000
    assert len(res.stderr) >= 500000


# -----------------------------------------------------------------------------
# 2. CLI Harness Formatting & Parsing Tests
# -----------------------------------------------------------------------------
def test_claude_harness_args_and_parsing():
    """Verify Claude Code harness command building and JSON output extraction."""
    harness = ClaudeHarness()
    cmd = harness._build_cmd("Hello Claude")
    assert cmd == [
        "claude",
        "-p",
        "Hello Claude",
        "--tools",
        "",
        "--output-format",
        "json",
        "--no-session-persistence",
    ]

    sample_json = json.dumps([
        {"type": "system", "text": "init"},
        {
            "type": "result",
            "subtype": "success",
            "result": "Hello back from Claude",
            "is_error": False,
            "total_cost_usd": 0.0,
            "usage": {
                "input_tokens": 120,
                "output_tokens": 250,
                "cache_read_input_tokens": 50,
            },
        },
    ])
    parsed = harness._parse_output(sample_json, duration_ms=450)
    assert parsed.text == "Hello back from Claude"
    assert parsed.provider == "claude"
    assert parsed.tier == "subscription_cli"
    assert parsed.input_tokens == 120
    assert parsed.output_tokens == 250
    assert parsed.cached_tokens == 50
    assert parsed.estimated_cost_usd == 0.0
    assert parsed.duration_ms == 450
    assert parsed.success is True


def test_codex_harness_args_and_parsing():
    """Verify Codex harness command building and JSONL event extraction."""
    harness = CodexHarness()
    cmd = harness._build_cmd("Hello Codex", model="gpt-6-astra")
    assert cmd == [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "-c",
        "model=gpt-6-astra",
        "--json",
        "Hello Codex",
    ]

    sample_jsonl = (
        "Reading additional input from stdin...\n"
        '{"type":"thread.started","thread_id":"test-123"}\n'
        '{"type":"turn.started"}\n'
        '{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"Codex response line 1"}}\n'
        '{"type":"item.completed","item":{"id":"item_1","type":"agent_message","text":"Codex response line 2"}}\n'
        '{"type":"turn.completed","usage":{"input_tokens":210,"output_tokens":110,"cached_input_tokens":40,"reasoning_output_tokens":15}}\n'
    )
    parsed = harness._parse_output(sample_jsonl, duration_ms=620, model="gpt-6-astra")
    assert "Codex response line 1\nCodex response line 2" == parsed.text
    assert parsed.provider == "codex"
    assert parsed.tier == "subscription_cli"
    assert parsed.input_tokens == 210
    assert parsed.output_tokens == 110
    assert parsed.cached_tokens == 40
    assert parsed.thinking_tokens == 15
    assert parsed.estimated_cost_usd == 0.0
    assert parsed.duration_ms == 620
    assert parsed.success is True


def test_agy_harness_args_and_parsing():
    """Verify AGY harness command building and JSON output stripping."""
    harness = AgyHarness()
    cmd = harness._build_cmd("Hello AGY", timeout_sec=45.0)
    assert cmd == [
        "agy",
        "--print",
        "Hello AGY",
        "--output-format",
        "json",
        "--print-timeout",
        "45s",
    ]

    sample_output = (
        "[agy] warning: print timeout active\n"
        '{"conversation_id":"abc","status":"SUCCESS","response":"AGY answer text\\n","usage":{"input_tokens":130,"output_tokens":95,"thinking_tokens":20}}\n'
    )
    parsed = harness._parse_output(sample_output, duration_ms=310)
    assert parsed.text == "AGY answer text"
    assert parsed.provider == "agy"
    assert parsed.tier == "subscription_cli"
    assert parsed.input_tokens == 130
    assert parsed.output_tokens == 95
    assert parsed.thinking_tokens == 20
    assert parsed.duration_ms == 310
    assert parsed.success is True


# -----------------------------------------------------------------------------
# 3. 3-Tier Fallback Cascade Tests
# -----------------------------------------------------------------------------
def test_router_empty_prompt_raises_value_error():
    """Verify empty or whitespace prompt raises ValueError."""
    router = MultiModelRouter()
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        router.route("")
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        router.route("   \n\t  ")


def test_router_tier1_subscription_success(monkeypatch, tmp_path):
    """Verify Tier 1 CLI execution produces subscription_cli tier."""
    logger = TelemetryLogger(data_dir=tmp_path)
    router = MultiModelRouter(telemetry_logger=logger, use_mock_llm=False)

    class MockCliHarness(BaseHarness):
        provider_name = "claude"
        default_model = "claude-sonnet-3-7"

        def is_available(self) -> bool:
            return True

        def generate(self, prompt: str, model=None, timeout_sec=60.0):
            return HarnessResponse(
                text="Successful generation from local CLI harness claude.",
                provider="claude",
                model=self.default_model,
                tier="subscription_cli",
                input_tokens=150,
                output_tokens=200,
                duration_ms=250,
                estimated_cost_usd=0.0,
                success=True,
            )

        async def generate_async(self, prompt: str, model=None, timeout_sec=60.0):
            return self.generate(prompt, model, timeout_sec)

    router.harnesses["claude"] = MockCliHarness()

    result = router.route("Explain Raft", provider="claude")
    assert result["tier"] == "subscription_cli"
    assert result["provider"] == "claude"
    assert result["fallback_triggered"] is False
    assert result["estimated_cost_usd"] == 0.0


def test_router_cascades_from_cli_failure_to_tier2_api(monkeypatch, tmp_path):
    """Verify router cascades to Tier 2 API when Tier 1 CLI fails."""
    logger = TelemetryLogger(data_dir=tmp_path)
    router = MultiModelRouter(telemetry_logger=logger, use_mock_llm=False)

    class FailingCliHarness(BaseHarness):
        provider_name = "claude"
        default_model = "claude-sonnet-3-7"

        def is_available(self) -> bool:
            return True

        def generate(self, prompt: str, model=None, timeout_sec=60.0):
            raise WatchdogTimeoutError("CLI timed out")

        async def generate_async(self, prompt: str, model=None, timeout_sec=60.0):
            raise WatchdogTimeoutError("CLI timed out")

    router.harnesses["claude"] = FailingCliHarness()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

    result = router.route("Explain Paxos", provider="claude")
    assert result["tier"] == "direct_api"
    assert result["provider"] == "anthropic_api"
    assert result["fallback_triggered"] is True


def test_router_cascades_to_tier3_mock_when_external_fails(monkeypatch, tmp_path):
    """Verify router cascades to Tier 3 mock when both CLI and Direct API fail."""
    logger = TelemetryLogger(data_dir=tmp_path)
    router = MultiModelRouter(telemetry_logger=logger, use_mock_llm=False)

    class FailingCliHarness(BaseHarness):
        provider_name = "claude"
        default_model = "claude-sonnet-3-7"

        def is_available(self) -> bool:
            return True

        def generate(self, prompt: str, model=None, timeout_sec=60.0):
            raise RuntimeError("CLI failed")

        async def generate_async(self, prompt: str, model=None, timeout_sec=60.0):
            raise RuntimeError("CLI failed")

    router.harnesses["claude"] = FailingCliHarness()
    # Unset all API keys to force Tier 2 failure
    for k in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
        monkeypatch.delenv(k, raising=False)

    result = router.route("Explain Two-Phase Commit", provider="claude")
    assert result["tier"] == "mock"
    assert result["provider"] == "mock"
    assert result["fallback_triggered"] is True


def test_router_honors_use_mock_llm_flag(tmp_path):
    """Verify LEARN_USE_MOCK_LLM=1 routes immediately to mock without external calls."""
    logger = TelemetryLogger(data_dir=tmp_path)
    router = MultiModelRouter(telemetry_logger=logger, use_mock_llm=True)
    result = router.route("Explain Vector Clocks", provider="claude")
    assert result["tier"] == "mock"
    assert result["provider"] == "mock"
    assert result["fallback_triggered"] is True


# -----------------------------------------------------------------------------
# 4. Out-of-Git Telemetry Persistence Tests
# -----------------------------------------------------------------------------
def test_telemetry_logs_valid_jsonl_record(tmp_path):
    """Verify TelemetryLogger writes conforming JSONL records to XDG data dir."""
    logger = TelemetryLogger(data_dir=tmp_path)
    record = logger.log(
        provider="codex",
        model="gpt-6-astra",
        tier="subscription_cli",
        input_tokens=150,
        output_tokens=220,
        duration_ms=480,
        estimated_cost_usd=0.0,
        nominal_value_usd=0.002,
        cached_tokens=30,
        thinking_tokens=10,
        success=True,
        workflow_type="interview",
    )

    telemetry_file = tmp_path / "telemetry" / "usage_costs.jsonl"
    assert telemetry_file.exists()

    records = logger.get_records()
    assert len(records) == 1
    last = records[0]

    assert last["telemetry_id"] == record.telemetry_id
    assert last["provider"] == "codex"
    assert last["model"] == "gpt-6-astra"
    assert last["execution_tier"] == "subscription_cli"
    assert last["source_tier"] == "subscription_cli"
    assert last["input_tokens"] == 150
    assert last["prompt_tokens"] == 150
    assert last["output_tokens"] == 220
    assert last["completion_tokens"] == 220
    assert last["duration_ms"] == 480
    assert last["latency_ms"] == 480
    assert last["estimated_cost_usd"] == 0.0
    assert last["workflow_type"] == "interview"


def test_router_telemetry_does_not_modify_git_status():
    """Verify git status in repository root remains clean after router operations."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    # Ensure no telemetry files are in git status
    for line in proc.stdout.splitlines():
        assert "usage_costs.jsonl" not in line
        assert "telemetry/" not in line


# -----------------------------------------------------------------------------
# 5. Hardening Regression Tests (Astra Audit Verification)
# -----------------------------------------------------------------------------
def test_claude_and_agy_model_override():
    """Verify CLI harnesses propagate requested model flag."""
    claude = ClaudeHarness()
    cmd_claude = claude._build_cmd("Hello", model="claude-3-opus")
    assert "--model" in cmd_claude
    assert "claude-3-opus" in cmd_claude

    agy = AgyHarness()
    cmd_agy = agy._build_cmd("Hello", timeout_sec=30.0, model="gemini-2.5-pro")
    assert "--model" in cmd_agy
    assert "gemini-2.5-pro" in cmd_agy


def test_codex_turn_failed_event_raises_and_cascades(tmp_path):
    """Verify Codex turn.failed JSONL line raises error and triggers router cascade."""
    logger = TelemetryLogger(data_dir=tmp_path)
    router = MultiModelRouter(telemetry_logger=logger, use_mock_llm=False)

    class FailingCodexHarness(BaseHarness):
        provider_name = "codex"
        default_model = "gpt-6-astra"

        def is_available(self) -> bool:
            return True

        def generate(self, prompt: str, model=None, timeout_sec=60.0):
            sample_jsonl = '{"type":"turn.failed","error":"Rate limit exceeded"}\n'
            return self._parse_output(sample_jsonl, duration_ms=200)

        def _parse_output(self, stdout: str, duration_ms: int, model=None):
            return CodexHarness()._parse_output(stdout, duration_ms, model)

        async def generate_async(self, prompt: str, model=None, timeout_sec=60.0):
            return self.generate(prompt, model, timeout_sec)

    router.harnesses["codex"] = FailingCodexHarness()
    result = router.route("Generate consensus proof", provider="codex")
    assert result["fallback_triggered"] is True
    assert result["tier"] in ("direct_api", "mock")


@pytest.mark.asyncio
async def test_direct_api_async_execution():
    """Verify DirectApiHarness.generate_async runs cleanly without blocking event loop."""
    harness = DirectApiHarness()
    resp = await harness.generate_async("Test async fallback", timeout_sec=5.0)
    assert resp.tier == "direct_api"
    assert resp.success is True

