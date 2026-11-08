"""Use the real MCP SDK/client; inference stays in the user's connected client."""

import asyncio
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import httpx
import httpx2
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
from starlette.testclient import TestClient

from app.config import settings
from app.core import state
from app.mcp.subscription import create_http_app, create_server
from app.router import MultiModelRouter

ROOT = Path(__file__).resolve().parents[2]
ASSESSMENT = {
    "assessment_id": "practice-001", "topic_id": "algorithms",
    "exercise_id": "algorithms/tier1_starter", "score": 3.5,
    "feedback": "Preserved the loop invariant; the complexity argument needs work.",
    "learner_response": "My answer and explanation of the loop invariant.",
}


def data(result):
    assert not result.is_error, result
    return json.loads(result.content[0].text)


@pytest.fixture
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(state, "data_dir", tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("Subscription MCP must not invoke server-side inference")

    monkeypatch.setattr(MultiModelRouter, "route", forbidden)
    return create_server()


@pytest.mark.asyncio
async def test_real_curriculum_and_idempotent_client_assessment(server, tmp_path):
    exercise = data(await server.call_tool("learn_get_exercise", {"topic_id": "algorithms"}))
    source = ROOT / "leetcode/algorithms/exercises/tier1_starter.md"
    assert exercise["prompt"] == source.read_text()
    assert exercise["rubric"] == (source.parent.parent / "rubric.md").read_text()
    first = data(await server.call_tool("learn_record_assessment", ASSESSMENT))
    retries = await asyncio.gather(*[
        server.call_tool("learn_record_assessment", ASSESSMENT) for _ in range(8)
    ])
    assert all(data(r) == first for r in retries)
    progress = data(await server.call_tool("learn_get_progress", {}))
    assert progress["assessment_count"] == 1
    assert progress["assessments"][0]["assessment_source"] == "connected_ai_client"
    assert progress["app_ratings"] == {}
    assert (tmp_path / "mcp_assessments.json").is_file()
    assert not tmp_path.is_relative_to(ROOT)


@pytest.mark.asyncio
async def test_http_client_uses_same_shared_progress(server, monkeypatch):
    data(await server.call_tool("learn_pin_topic", {"topic_id": "algorithms"}))
    monkeypatch.setenv("LEARN_MCP_ALLOWED_HOSTS", "learn.example")
    with TestClient(create_http_app(server, token="test-token"), base_url="http://127.0.0.1") as client:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-11-25", "capabilities": {},
            "clientInfo": {"name": "legacy-client", "version": "1"},
        }}
        assert client.post("/mcp", json=payload).status_code == 401
        assert client.post("/mcp?token=test-token", json=payload).status_code == 401
        assert client.post("/mcp", json=payload, headers={"Authorization": "Bearer wrong"}).status_code == 401
        headers = {"Authorization": "Bearer test-token", "Accept": "application/json, text/event-stream"}
        initialized = client.post("/mcp", json=payload, headers=headers)
        assert initialized.status_code == 200
        assert initialized.json()["result"]["protocolVersion"] == "2025-11-25"
        assert client.post("/mcp", json=payload, headers={**headers, "Host": "learn.example"}).status_code == 200
        headers["MCP-Protocol-Version"] = "2025-11-25"
        assert client.post("/mcp", json=payload, headers={**headers, "MCP-Protocol-Version": "1900-01-01"}).status_code == 400
        notification = client.post("/mcp", json={
            "jsonrpc": "2.0", "method": "notifications/initialized"
        }, headers=headers)
        assert notification.status_code == 202
        assert notification.content == b""
        for bad in ["http://localhost.evil.example", "https://evil.example"]:
            assert client.post("/mcp", json=payload, headers={**headers, "Origin": bad}).status_code == 403
        assert client.post("/mcp", json=payload, headers={**headers, "Host": "evil.example"}).status_code == 421
        response = client.post("/mcp", json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "learn_get_progress", "arguments": {}},
        }, headers=headers)
        progress = json.loads(response.json()["result"]["content"][0]["text"])
        assert progress["pinned_topics"][0]["topic_id"] == "algorithms"


@pytest.mark.asyncio
async def test_stdio_client_from_unrelated_working_directory(tmp_path):
    params = StdioServerParameters(
        command=str(Path(sys.executable).with_name("learn-mcp")), cwd=tmp_path,
        env={"LEARN_DATA_DIR": str(tmp_path / "data"), "LEARN_REPO_ROOT": str(ROOT)},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            tools = await client.list_tools()
            names = {t.name for t in tools.tools}
            assert {"learn_get_topic", "learn_get_exercise", "learn_record_assessment"} <= names
            assert "learn_run_adaptive_exercise_turn" not in names
            for tool in tools.tools:
                assert tool.annotations is not None
            data(await client.call_tool("learn_get_topic", {"topic_id": "algorithms"}))
            first = data(await client.call_tool("learn_record_assessment", ASSESSMENT))
            assert data(await client.call_tool("learn_record_assessment", ASSESSMENT)) == first
            for changes in [
                {"score": 6}, {"score": True}, {"score": "NaN"},
                {"exercise_id": "go/tier1_starter"}, {"assessment_id": "../escape"},
                {"feedback": " "}, {"learner_response": " "}, {"score": 2},
            ]:
                result = await client.call_tool("learn_record_assessment", {**ASSESSMENT, **changes})
                assert result.is_error, changes
            assert (await client.call_tool("learn_get_topic", {"topic_id": "../../etc"})).is_error
            progress = data(await client.call_tool("learn_get_progress", {}))
            assert progress["assessment_count"] == 1


@pytest.mark.asyncio
async def test_corrupt_history_is_never_overwritten(server, tmp_path):
    ledger = tmp_path / "mcp_assessments.json"
    ledger.write_text("{broken")
    # SDK client-facing error behavior is covered above; direct dispatch raises.
    with pytest.raises(Exception, match="Error executing tool") as error:
        await server.call_tool("learn_record_assessment", ASSESSMENT)
    assert isinstance(error.value.__cause__, json.JSONDecodeError)
    assert ledger.read_text() == "{broken"


@pytest.mark.asyncio
async def test_durable_learning_writes_technical_note_not_assessment(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "leetcode/algorithms", repo / "leetcode/algorithms")
    monkeypatch.setattr(settings, "repo_root", repo)
    monkeypatch.setattr(settings, "data_dir", tmp_path / "personal")
    server = create_server()
    result = data(await server.call_tool("learn_record_durable_learning", {
        "topic_id": "algorithms", "title": "Loop invariants", "mental_model": "Preserve a condition.",
        "invariants": ["The condition holds before and after every iteration."],
    }))
    assert result["status"] == "created"
    note = Path(result["absolute_path"])
    assert note.is_relative_to(repo / "leetcode/algorithms/learnings")
    assert "Preserve a condition." in note.read_text()
    assert not (tmp_path / "personal/mcp_assessments.json").exists()


@pytest.mark.asyncio
async def test_standard_http_client_over_real_transport(tmp_path):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}/mcp"
    env = {
        "PATH": os.environ["PATH"], "HOME": os.environ["HOME"],
        "LEARN_DATA_DIR": str(tmp_path), "LEARN_REPO_ROOT": str(ROOT),
        "LEARN_API_TOKEN": "http-test-token",
    }
    with (tmp_path / "http.log").open("w") as log:
        process = subprocess.Popen([
            sys.executable, "-m", "app.mcp", "--transport", "streamable-http", "--port", str(port)
        ], cwd=tmp_path, env=env, stdout=log, stderr=log)
        try:
            for _ in range(100):
                if process.poll() is not None:
                    pytest.fail((tmp_path / "http.log").read_text())
                try:
                    assert httpx.get(url).status_code == 401
                    break
                except httpx.ConnectError:
                    await asyncio.sleep(0.05)
            else:
                pytest.fail("MCP HTTP server failed to start")
            async with httpx2.AsyncClient(headers={"Authorization": "Bearer http-test-token"}) as http:
                async with streamable_http_client(url, http_client=http) as streams:
                    async with ClientSession(streams[0], streams[1]) as client:
                        await client.initialize()
                        exercise = data(await client.call_tool("learn_get_exercise", {"topic_id": "go"}))
                        assert exercise["exercise_id"] == "go/tier1_starter"
        finally:
            process.terminate()
            process.wait(timeout=10)


def test_non_loopback_requires_token(tmp_path):
    result = subprocess.run([
        sys.executable, "-m", "app.mcp", "--transport", "streamable-http", "--host", "0.0.0.0"
    ], cwd=tmp_path, env={
        "PATH": os.environ["PATH"], "HOME": os.environ["HOME"], "LEARN_DATA_DIR": str(tmp_path),
    }, capture_output=True, text=True, timeout=10)
    assert result.returncode == 2
    assert "requires LEARN_API_TOKEN" in result.stderr
