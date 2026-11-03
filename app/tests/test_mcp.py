"""Integration and unit tests for Savage-Fred/learn MCP server, tools, and transports."""

import json
import io
import sys
from pathlib import Path
import pytest
import yaml
from httpx import AsyncClient, ASGITransport

from app.config import settings
from app.main import app
from app.mcp.protocol import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
)
from app.mcp.server import MCPServer
from app.mcp.tools import MCPToolRegistry
from app.mcp.transports.stdio import run_stdio


@pytest.fixture(autouse=True)
def isolate_mcp_data_dir(tmp_path, monkeypatch):
    """Ensure every test in test_mcp.py operates in an isolated temporary data directory."""
    monkeypatch.setattr(settings, "data_dir", tmp_path)


@pytest.fixture
def mcp():
    return MCPServer()


# -----------------------------------------------------------------------------
# 1. Protocol Handshake Tests
# -----------------------------------------------------------------------------
def test_mcp_initialize(mcp):
    resp = mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["id"] == 1
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "learn-mcp"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_notifications_initialized(mcp):
    resp = mcp.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert resp is None


# -----------------------------------------------------------------------------
# 2. Tools List & Completeness (All 8 Tools)
# -----------------------------------------------------------------------------
def test_mcp_tools_list_has_all_8_tools(mcp):
    resp = mcp.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = resp["result"]["tools"]
    assert len(tools) == 8
    names = {t["name"] for t in tools}
    expected = {
        "learn_list_topics",
        "learn_pin_topic",
        "learn_get_pinned_topics",
        "learn_record_durable_learning",
        "learn_query_proficiency_gaps",
        "learn_run_adaptive_exercise_turn",
        "learn_run_mock_interview_turn",
        "learn_analyze_job_description",
    }
    assert names == expected
    for t in tools:
        assert t["description"]
        assert t["inputSchema"]["type"] == "object"


# -----------------------------------------------------------------------------
# 3. Tool Calls (Happy Path & Aliases)
# -----------------------------------------------------------------------------
def test_tool_learn_list_topics(mcp):
    # All topics
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "learn_list_topics", "arguments": {"domain": "all"}},
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert "topics" in data
    assert len(data["topics"]) >= 11
    slugs = {t["slug"] for t in data["topics"]}
    assert "algorithms" in slugs
    assert "authn-authz" in slugs
    assert "differential-privacy" in slugs
    assert "go" in slugs

    # Filtered by domain
    resp_leetcode = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "learn_list_topics", "arguments": {"domain": "leetcode"}},
    })
    data_leetcode = json.loads(resp_leetcode["result"]["content"][0]["text"])
    for t in data_leetcode["topics"]:
        assert t["domain"] == "leetcode"


def test_tool_learn_pin_and_get_pinned_topics(mcp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    # Pin topic using topic_slug
    resp_pin = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "learn_pin_topic",
            "arguments": {
                "topic_slug": "algorithms",
                "priority": "high",
                "notes": "Focus on Dinic blocking flows",
            },
        },
    })
    data_pin = json.loads(resp_pin["result"]["content"][0]["text"])
    assert data_pin["status"] == "pinned"
    assert data_pin["topic_id"] == "algorithms"
    assert data_pin["priority"] == "high"

    # Query pinned topics
    resp_get = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {"name": "learn_get_pinned_topics", "arguments": {}},
    })
    data_get = json.loads(resp_get["result"]["content"][0]["text"])
    assert len(data_get["pinned_topics"]) == 1
    assert data_get["pinned_topics"][0]["topic_id"] == "algorithms"
    assert "Dinic" in data_get["pinned_topics"][0]["notes"]


def test_tool_learn_record_durable_learning(mcp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "repo_root", tmp_path)
    (tmp_path / "leetcode" / "algorithms" / "learnings").mkdir(parents=True, exist_ok=True)

    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "learn_record_durable_learning",
            "arguments": {
                "topic_slug": "algorithms",
                "title": "Dinic Blocking Flow Monotone Invariant",
                "mental_model": "Layered residual DAGs guarantee strictly increasing path lengths.",
                "invariants": [
                    "Residual capacity r_f(u,v) = c(u,v) - f(u,v) >= 0",
                    "Level graph distance strictly increases: dist(v) = dist(u) + 1",
                ],
                "notes": "Terminates in O(V^2 E) for general networks and O(E sqrt(V)) for unit networks.",
                "citable_sources": ["Dinic 1970 Algorithm for Solution of a Problem of Maximal Flow"],
            },
        },
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["status"] == "created"
    assert "file_path" in data

    created_file = Path(data["absolute_path"])
    assert created_file.exists()

    file_text = created_file.read_text(encoding="utf-8")
    parts = file_text.split("---")
    assert len(parts) >= 3
    fm = yaml.safe_load(parts[1])

    assert fm["topic"] == "algorithms"
    assert fm["domain"] == "leetcode"
    assert fm["title"] == "Dinic Blocking Flow Monotone Invariant"
    assert "Residual capacity" in fm["invariants_covered"][0]
    assert "Dinic 1970" in file_text


def test_tool_learn_query_proficiency_gaps(mcp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "learn_query_proficiency_gaps",
            "arguments": {"role_track": "faang_swe_l5_l6", "target_company": "Google"},
        },
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert "fit_score_percentage" in data or "role_fit_score" in data
    assert "high_leverage_gaps" in data or "assessed_gaps" in data
    assert "custom_interview_loop" in data
    assert len(data["custom_interview_loop"]) == 5


def test_tool_learn_run_adaptive_exercise_turn(mcp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "learn_run_adaptive_exercise_turn",
            "arguments": {
                "exercise_id": "tier1_starter",
                "user_response": "We maintain the invariant that at every step, the potential function Phi is non-negative.",
                "topic_slug": "algorithms",
            },
        },
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["passed"] is True
    assert data["score"] >= 4.0
    assert "next_tier" in data or "next_difficulty_level" in data


def test_tool_learn_run_mock_interview_turn_hints_and_no_hints(mcp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    # 1. Hints mode
    resp1 = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "learn_run_mock_interview_turn",
            "arguments": {
                "session_id": "mock-sess-1",
                "message": "Can I get a hint?",
                "turn_type": "request_hint",
                "mode": "hints",
            },
        },
    })
    data1 = json.loads(resp1["result"]["content"][0]["text"])
    assert data1["hints_remaining"] == 2
    assert "monotone" in data1["interviewer_message"].lower()

    # 2. No-hints mode
    resp2 = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "learn_run_mock_interview_turn",
            "arguments": {
                "session_id": "mock-sess-2",
                "message": "Can I get a hint?",
                "turn_type": "request_hint",
                "mode": "no-hints",
            },
        },
    })
    data2 = json.loads(resp2["result"]["content"][0]["text"])
    assert "disabled in strict" in data2["interviewer_message"]


def test_tool_learn_analyze_job_description(mcp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    jd = (
        "Staff Software Engineer, Distributed Systems & Security.\n"
        "Requirements: Master's in CS or equivalent, expertise in consensus algorithms, Raft, "
        "concurrency in Go, security access control models, and differential privacy."
    )
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "learn_analyze_job_description",
            "arguments": {"job_description_text": jd},
        },
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["fit_score_percentage"] >= 70.0
    assert len(data["custom_interview_loop"]) == 5
    assert len(data["high_leverage_gaps"]) >= 1


# -----------------------------------------------------------------------------
# 4. Error Boundary Tests
# -----------------------------------------------------------------------------
def test_missing_method_returns_invalid_request(mcp):
    resp = mcp.handle_request({"jsonrpc": "2.0", "id": 20})
    assert resp["error"]["code"] == INVALID_REQUEST


def test_unknown_method_returns_method_not_found(mcp):
    resp = mcp.handle_request({"jsonrpc": "2.0", "id": 21, "method": "unknown_rpc_method"})
    assert resp["error"]["code"] == METHOD_NOT_FOUND


def test_unknown_tool_returns_tool_not_found(mcp):
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 22,
        "method": "tools/call",
        "params": {"name": "nonexistent_custom_tool", "arguments": {}},
    })
    assert resp["error"]["code"] == METHOD_NOT_FOUND


def test_missing_required_tool_args_returns_invalid_params(mcp):
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 23,
        "method": "tools/call",
        "params": {"name": "learn_pin_topic", "arguments": {}},
    })
    assert resp["error"]["code"] == INVALID_PARAMS


# -----------------------------------------------------------------------------
# 5. Transport Tests (Stdio & SSE)
# -----------------------------------------------------------------------------
def test_stdio_transport_jsonrpc_stream(monkeypatch):
    req1 = json.dumps({"jsonrpc": "2.0", "id": "req-1", "method": "initialize"})
    req2 = json.dumps({"jsonrpc": "2.0", "id": "req-2", "method": "tools/list"})
    input_stream = io.StringIO(f"{req1}\n{req2}\n")
    output_stream = io.StringIO()

    monkeypatch.setattr(sys, "stdin", input_stream)
    monkeypatch.setattr(sys, "stdout", output_stream)

    run_stdio()

    lines = [line.strip() for line in output_stream.getvalue().splitlines() if line.strip()]
    assert len(lines) == 2

    res1 = json.loads(lines[0])
    assert res1["id"] == "req-1"
    assert res1["result"]["serverInfo"]["name"] == "learn-mcp"

    res2 = json.loads(lines[1])
    assert res2["id"] == "req-2"
    assert len(res2["result"]["tools"]) == 8


@pytest.mark.asyncio
async def test_sse_transport_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Direct POST call
        resp_direct = await client.post(
            "/mcp/call",
            json={"jsonrpc": "2.0", "id": 50, "method": "initialize"},
        )
        assert resp_direct.status_code == 200
        data_direct = resp_direct.json()
        assert data_direct["result"]["serverInfo"]["name"] == "learn-mcp"


# -----------------------------------------------------------------------------
# 6. Hardening Regression Tests (Astra Audit Verification)
# -----------------------------------------------------------------------------
def test_mcp_ping_and_notifications(mcp):
    """Verify ping returns empty result and notification returns None."""
    resp_ping = mcp.handle_request({"jsonrpc": "2.0", "id": 100, "method": "ping"})
    assert resp_ping["result"] == {}

    resp_notif = mcp.handle_request({"jsonrpc": "2.0", "method": "notifications/custom_notice"})
    assert resp_notif is None


def test_mcp_invalid_payload_and_params(mcp):
    """Verify non-dict payload and null/invalid params return JSON-RPC errors."""
    resp_str = mcp.handle_request("not-a-dict")  # type: ignore
    assert resp_str["error"]["code"] == INVALID_REQUEST

    resp_bad_params = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": "invalid-params-string",
    })
    assert resp_bad_params["error"]["code"] == INVALID_PARAMS


def test_tool_mock_interview_path_traversal_rejected(mcp):
    """Verify session_id with traversal attempts are rejected."""
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 102,
        "method": "tools/call",
        "params": {
            "name": "learn_run_mock_interview_turn",
            "arguments": {
                "session_id": "../../etc/passwd",
                "message": "Hello",
            },
        },
    })
    assert resp["error"]["code"] == INVALID_PARAMS
    assert "traversal" in resp["error"]["message"].lower()


def test_tool_durable_learning_invalid_domain_rejected(mcp):
    """Verify record durable learning rejects unknown or invalid domains."""
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 103,
        "method": "tools/call",
        "params": {
            "name": "learn_record_durable_learning",
            "arguments": {
                "topic_slug": "algorithms",
                "domain": "untrusted_domain",
                "title": "Title",
                "notes": "Some notes",
            },
        },
    })
    assert resp["error"]["code"] == INVALID_PARAMS
    assert "invalid domain" in resp["error"]["message"].lower()


def test_tool_adaptive_exercise_gibberish_rejected(mcp):
    """Verify repetitive low-entropy gibberish is rejected / marked not passed."""
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 104,
        "method": "tools/call",
        "params": {
            "name": "learn_run_adaptive_exercise_turn",
            "arguments": {
                "exercise_id": "tier1_starter",
                "user_response": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            },
        },
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["passed"] is False
    assert data["score"] <= 2.5


def test_tool_analyze_job_description_zero_match(mcp):
    """Verify completely unrelated job description gets low fit score (<30%)."""
    resp = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 105,
        "method": "tools/call",
        "params": {
            "name": "learn_analyze_job_description",
            "arguments": {
                "job_description_text": "Experienced French Pastry Chef specializing in croissants, baguette fermentation, and sourdough yeast.",
                "resume_text": "Experienced Staff Software Engineer specializing in distributed systems, consensus algorithms, security, and privacy.",
            },
        },
    })
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["fit_score_percentage"] <= 30.0


@pytest.mark.asyncio
async def test_sse_origin_header_validation():
    """Verify SSE endpoints reject untrusted Origin with 403 Forbidden."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Untrusted origin
        resp_untrusted = await client.post(
            "/mcp/call",
            headers={"origin": "http://evil-attacker.com"},
            json={"jsonrpc": "2.0", "id": 106, "method": "initialize"},
        )
        assert resp_untrusted.status_code == 403

        # Trusted localhost origin
        resp_trusted = await client.post(
            "/mcp/call",
            headers={"origin": "http://localhost:3000"},
            json={"jsonrpc": "2.0", "id": 107, "method": "initialize"},
        )
        assert resp_trusted.status_code == 200

