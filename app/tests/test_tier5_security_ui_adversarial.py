"""Tier 5 Adversarial Coverage Hardening Test Suite.

Milestone 5 White-Box Adversarial Audit across:
1. MicroHighlighter & Web UI Security (Syntax group destructuring, unclosed quotes, DOM XSS).
2. API Routes & Input Validation (Path traversal in quiz/turns, domain whitelisting, malformed payloads).
3. Security Boundaries & Tailnet Token Auth (Loopback vs Remote, query/header tokens, data_dir masking).
4. Curricula Schemas & Invariant Protection (Path traversal in durable capture, PII scrubbing).
5. State Isolation (§R4) & Storage Invariants (Data dir validation, symlinks, git status cleanliness).
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import Settings, settings
from app.core import ALLOWED_DOMAINS, state, topic_loader
from app.core.durable_capture import scrub_pii, durable_capture
from app.core.state import StateManager, sanitize_identifier
from app.main import app


@pytest.fixture
def client():
    """TestClient instance configured for HTTP/WebSocket tests."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def isolated_state(tmp_path_factory):
    """Provides an isolated StateManager completely outside repository root."""
    temp_dir = tmp_path_factory.mktemp("tier5_isolated_state")
    mgr = StateManager(data_dir=temp_dir)
    return {"dir": temp_dir, "state": mgr}


# =============================================================================
# 1. MicroHighlighter & Web UI Security
# =============================================================================

def _eval_micro_highlighter(js_code: str) -> str:
    """Helper to evaluate JS against MicroHighlighter using Node.js."""
    app_js_path = settings.repo_root / "app" / "ui" / "static" / "app.js"
    assert app_js_path.exists(), f"app.js not found at {app_js_path}"
    
    script = f"""
    const fs = require('fs');
    const fileContent = fs.readFileSync('{app_js_path}', 'utf8');
    const startIdx = fileContent.indexOf('const MicroHighlighter = {{');
    const endIdx = fileContent.indexOf('async function loadTopicDetail');
    const mhCode = fileContent.substring(startIdx, endIdx);
    const fn = new Function(mhCode + '\\nreturn MicroHighlighter;');
    const MicroHighlighter = fn();
    {js_code}
    """
    res = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return res.stdout.strip()


def test_micro_highlighter_token_destructuring_python_accuracy():
    """Empirically test whether Python string literals and numbers are correctly highlighted.
    
    EXPECTED BEHAVIOR:
    - Strings are highlighted with class 'tok-string'.
    - Numbers are highlighted with class 'tok-number'.
    
    KNOWN DEFECT EXPOSED:
    In app.js:528, the destructuring pattern causes Python strings to match 'num' (class 'tok-number')
    and numbers to match 'identOrKey' (plain text, unhighlighted).
    """
    js = """
    const code = 's = "hello"\\nn = 123';
    const highlighted = MicroHighlighter.highlight(code, 'python');
    console.log(JSON.stringify({
      string_is_tok_string: highlighted.includes('class="tok-string"'),
      string_is_tok_number: highlighted.includes('<span class="tok-number">&quot;hello&quot;</span>'),
      number_is_tok_number: highlighted.includes('<span class="tok-number">123</span>'),
      raw: highlighted
    }));
    """
    out = json.loads(_eval_micro_highlighter(js))
    
    # Asserting correct behavior:
    # Strings must have tok-string, numbers must have tok-number
    assert out["string_is_tok_string"], (
        f"MicroHighlighter BUG: Python strings are misclassified! Raw output: {out['raw']}"
    )
    assert out["number_is_tok_number"], (
        f"MicroHighlighter BUG: Python numbers are not highlighted! Raw output: {out['raw']}"
    )


def test_micro_highlighter_unclosed_quotes_retention():
    """Empirically test whether unclosed quotes or comments are preserved without silent dropping.
    
    EXPECTED BEHAVIOR:
    - Code with unclosed quotes like 'a = " b' must retain the quote in the output.
    
    KNOWN DEFECT EXPOSED:
    In app.js:465, the fallback group excludes quotes, causing unclosed quotes to be skipped and lost.
    """
    js = """
    const code = 'a = " b';
    const highlighted = MicroHighlighter.highlight(code, 'python');
    console.log(JSON.stringify({
      has_quote: highlighted.includes('&quot;') || highlighted.includes('"'),
      raw: highlighted
    }));
    """
    out = json.loads(_eval_micro_highlighter(js))
    assert out["has_quote"], (
        f"MicroHighlighter BUG: Unclosed double quote was silently dropped! Raw: {out['raw']}"
    )


def test_micro_highlighter_go_punctuation_highlighting():
    """Empirically test whether Go punctuation operators are wrapped in tok-punct.
    
    EXPECTED BEHAVIOR:
    - Go punctuation like ':=' must be wrapped in class 'tok-punct'.
    
    KNOWN DEFECT EXPOSED:
    In Go regex, group 6 (punct) maps to 'ws' in destructuring, omitting tok-punct.
    """
    js = """
    const code = 'x := 10';
    const highlighted = MicroHighlighter.highlight(code, 'go');
    console.log(JSON.stringify({
      has_tok_punct: highlighted.includes('class="tok-punct"'),
      raw: highlighted
    }));
    """
    out = json.loads(_eval_micro_highlighter(js))
    assert out["has_tok_punct"], (
        f"MicroHighlighter BUG: Go punctuation ':=' not highlighted in tok-punct! Raw: {out['raw']}"
    )


def test_web_ui_stored_xss_via_pinned_topic_slug(client):
    """Empirically test stored XSS injection via pinned topic slug.
    
    EXPOSED VULNERABILITY:
    sanitize_identifier does not reject HTML tags (<img onerror=...>), and renderPinnedBar
    in app.js inserts slug directly into innerHTML without escaping.
    """
    xss_payload = '<img src=x onerror=alert("XSS")>'
    # Attempt to pin topic with XSS slug
    res = client.post(f"/api/topics/general/{xss_payload}/pin", json={"priority": "high"})
    
    # Check if backend rejected it or allowed it
    # If backend accepts it, verify if UI renderPinnedBar is vulnerable
    if res.status_code == 200:
        pinned = client.get("/api/topics/pinned").json()["pinned_topics"]
        matching = [p for p in pinned if p.get("topic_id") == xss_payload or p.get("topic_slug") == xss_payload]
        assert len(matching) > 0
        
        # Test if app.js renderPinnedBar escapes it
        app_js = (settings.repo_root / "app" / "ui" / "static" / "app.js").read_text(encoding="utf-8")
        # In app.js: container.innerHTML = pins.map(p => `...<span>${slug}</span>...`)
        # Check if renderPinnedBar calls escape(slug)
        assert "MicroHighlighter.escape(slug)" in app_js or "escapeHtml(slug)" in app_js, (
            "SECURITY VULNERABILITY: Stored XSS in renderPinnedBar! "
            f"Slug '{xss_payload}' stored and injected unescaped into innerHTML."
        )


# =============================================================================
# 2. API Routes & Input Validation Robustness
# =============================================================================

def test_quiz_turn_path_traversal_session_id_graceful_handling(client):
    """Assert POST /api/quiz/turn handles invalid / traversal session_id gracefully with 400.
    
    EXPOSED BUG:
    app/api/routes_quiz.py:50 calls state.get_session(session_id) OUTSIDE try...except.
    When session_id contains traversal, sanitize_identifier raises ValueError, resulting in 500.
    """
    bad_payload = {
        "exercise_id": "tier1_starter",
        "session_id": "../traversal_attack",
        "user_response": "invariant held",
    }
    res = client.post("/api/quiz/turn", json=bad_payload)
    assert res.status_code != 500, (
        f"BUG FOUND: POST /api/quiz/turn crashed with HTTP 500 on path-traversal session_id! "
        f"Response: {res.text}"
    )
    assert res.status_code in (400, 404, 422)


def test_domain_whitelisting_strictly_enforced_in_topics_api(client):
    """Assert GET /api/topics with unwhitelisted domain (e.g. 'app') does not expose internal folders.
    
    EXPOSED BUG:
    GET /api/topics?domain=app returns internal source packages ('app/api', 'app/core', etc.)
    and GET /api/topics/app/ui returns HTTP 200 because domain is not checked against ALLOWED_DOMAINS.
    """
    # 1. Query with domain=app
    res_list = client.get("/api/topics?domain=app")
    topics = res_list.json().get("topics", [])
    exposed_internal_dirs = [t["slug"] for t in topics if t.get("directory_path", "").startswith("app/")]
    
    assert len(exposed_internal_dirs) == 0, (
        f"SECURITY / BOUNDARY LEAK: GET /api/topics?domain=app exposed internal source directories: "
        f"{exposed_internal_dirs}"
    )

    # 2. Topic detail with domain=app
    res_detail = client.get("/api/topics/app/ui")
    assert res_detail.status_code in (400, 404), (
        f"BOUNDARY VIOLATION: GET /api/topics/app/ui returned {res_detail.status_code} "
        f"instead of 400/404! Detail: {res_detail.text}"
    )


def test_sanitize_identifier_rejects_dot_and_special_escapes():
    """Assert sanitize_identifier rejects single dot ('.') which refers to directory itself."""
    # Single dot can cause directory confusion
    with pytest.raises(ValueError):
        sanitize_identifier(".")


def test_giant_payload_memory_handling(client):
    """Stress-test 2MB user answer payload in quiz turn without crashing."""
    giant_response = "A" * (2 * 1024 * 1024)
    res = client.post("/api/quiz/turn", json={
        "topic_slug": "algorithms",
        "exercise_id": "tier1_starter",
        "user_response": giant_response,
    })
    assert res.status_code in (200, 400, 413, 422)
    if res.status_code == 200:
        data = res.json()
        assert "new_rating" in data


# =============================================================================
# 3. Security Boundaries & Tailnet Token Auth
# =============================================================================

def test_tailnet_token_enforcement_on_remote_clients(monkeypatch):
    """Verify that remote (non-loopback) clients are strictly blocked when LEARN_API_TOKEN is set."""
    token = "test-secret-token-12345"
    monkeypatch.setattr(settings, "api_token", token)

    # Remote client without token -> 401
    remote_client = TestClient(app, base_url="http://100.64.1.5:8795", client=("100.64.1.5", 54321))
    res_unauth = remote_client.get("/api/status")
    assert res_unauth.status_code == 401, f"Expected 401 for remote client without token, got {res_unauth.status_code}"

    # Remote client with valid Bearer header -> 200
    res_auth = remote_client.get("/api/status", headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200
    assert res_auth.json()["data_dir"] == "[protected]"  # Masked for remote

    # Remote client with valid X-Learn-Token -> 200
    res_hdr = remote_client.get("/api/status", headers={"X-Learn-Token": token})
    assert res_hdr.status_code == 200

    # Remote client with valid query param -> 200
    res_query = remote_client.get(f"/api/status?token={token}")
    assert res_query.status_code == 200

    # Local loopback client without token -> 200 allowed
    local_client = TestClient(app, client=("127.0.0.1", 54321))
    res_local = local_client.get("/api/status")
    assert res_local.status_code == 200
    assert "[protected]" not in res_local.json()["data_dir"]


def test_websocket_stream_remote_auth_enforcement(monkeypatch):
    """Verify WebSocket streaming endpoint enforces token on remote clients."""
    token = "ws-secret-token-67890"
    monkeypatch.setattr(settings, "api_token", token)

    remote_client = TestClient(app, client=("100.64.1.5", 54321))
    
    # Remote WS connection without token should be disconnected / rejected
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with remote_client.websocket_connect("/api/interview/test-sess/stream") as ws:
            pass
    assert exc_info.value.code in (1008, 4401)


# =============================================================================
# 4. Curricula Schemas & Invariant Protection
# =============================================================================

def test_durable_learning_pii_scrubbing_rigor():
    """Verify scrub_pii thoroughly strips emails, phones, API keys, and bearer tokens."""
    dirty_text = (
        "Learned that user alice@example.com with phone +1-555-123-4567 "
        "deployed api_key='sk-ant-api03-abcdef1234567890' and Bearer tok_xyz1234567890123 "
        "with candidate_score: 4.8 on distributed consensus."
    )
    cleaned = scrub_pii(dirty_text)
    assert "alice@example.com" not in cleaned
    assert "+1-555-123-4567" not in cleaned
    assert "sk-ant-api03" not in cleaned
    assert "tok_xyz1234567890123" not in cleaned
    assert "candidate_score: 4.8" not in cleaned
    assert "[EMAIL_REDACTED]" in cleaned
    assert "[PHONE_REDACTED]" in cleaned


def test_durable_learning_path_traversal_rejection():
    """Verify record_learning rejects path traversal topic slugs and domains."""
    with pytest.raises(ValueError):
        durable_capture.record_learning(
            topic_slug="../../etc",
            title="Traversal Attempt",
            mental_model="Invariant bypass",
            invariants=["none"],
        )


# =============================================================================
# 5. State Isolation (§R4) & Storage Invariants
# =============================================================================

def test_settings_data_dir_validation_rejects_repo_root():
    """Assert Settings validator strictly rejects data_dir inside repository root."""
    repo_root = settings.repo_root.resolve()
    inside_repo = repo_root / "test_data"
    
    with pytest.raises(ValueError, match="§R4 invariant"):
        Settings(data_dir=inside_repo)


def test_settings_data_dir_validation_rejects_symlink_into_repo(tmp_path):
    """Assert Settings validator resolves symlinks and rejects symlink pointing into repo."""
    repo_root = settings.repo_root.resolve()
    target_inside = repo_root / "subdir"
    symlink_outside = tmp_path / "symlink_to_repo"
    symlink_outside.symlink_to(target_inside)
    
    with pytest.raises(ValueError, match="§R4 invariant"):
        Settings(data_dir=symlink_outside)


def test_personal_state_module_presence():
    """Verify app.storage.personal_state exists as documented in PROJECT.md line 106.
    
    KNOWN GAP EXPOSED:
    app/storage/personal_state.py is missing from app/storage/.
    """
    import importlib
    try:
        mod = importlib.import_module("app.storage.personal_state")
        assert hasattr(mod, "StateManager")
    except ModuleNotFoundError:
        pytest.fail("ARCHITECTURE / CONTRACT GAP: 'app.storage.personal_state' does not exist!")


def test_mcp_tools_resilient_to_corrupted_or_string_ratings(tmp_path, monkeypatch):
    """Verify MCP tools handle non-float ratings in subdomain_ratings.json without TypeError crash.
    
    KNOWN DEFECT EXPOSED:
    app/mcp/tools.py:326 and :624 fail with TypeError when ratings contain strings.
    """
    from app.mcp.server import MCPServer
    
    # Setup corrupted ratings file
    ratings_dir = tmp_path / "ratings"
    ratings_dir.mkdir(parents=True, exist_ok=True)
    corrupted_ratings = {
        "algorithms": "corrupted_string_rating",
        "data-structures": 3.5,
    }
    (ratings_dir / "subdomain_ratings.json").write_text(json.dumps(corrupted_ratings), encoding="utf-8")
    
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    
    server = MCPServer()
    # Call learn_list_topics
    res = server.handle_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "learn_list_topics", "arguments": {"domain": "all"}},
    })
    
    # Must not produce JSON-RPC internal error with TypeError
    assert "result" in res, (
        f"MCP DEFECT: learn_list_topics crashed on string rating in subdomain_ratings.json! Response: {res}"
    )
