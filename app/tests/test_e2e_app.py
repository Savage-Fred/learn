"""End-to-end integration tests for FastAPI routes, UI mounting, auth, and WebSocket."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.core import state


@pytest.fixture
def client(tmp_path_factory, monkeypatch):
    temp_dir = tmp_path_factory.mktemp("learn_app_test")
    monkeypatch.setattr(settings, "data_dir", temp_dir)
    state.data_dir = temp_dir
    state.ensure_layout()
    return TestClient(app)


def test_e2e_health_and_status(client):
    """Test /healthz and /api/v1/status."""
    res_health = client.get("/healthz")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_status = client.get("/api/v1/status")
    assert res_status.status_code == 200
    data = res_status.json()
    assert data["status"] == "operational"
    assert "leetcode" in data["domains_available"]


def test_e2e_ui_root(client):
    """Test GET / serves HTML single-page app."""
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Savage-Fred" in res.text or "learn:" in res.text


def test_e2e_topics_endpoints(client):
    """Test /api/topics endpoints: listing, detail, pin, unpin, durable learning."""
    # 1. List topics
    res_list = client.get("/api/topics")
    assert res_list.status_code == 200
    topics = res_list.json()["topics"]
    assert len(topics) >= 11

    # 2. Topic detail
    res_detail = client.get("/api/topics/leetcode/algorithms")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["topic_id"] == "algorithms"
    assert "fundamentals" in detail
    assert "rubric" in detail
    assert "exercises" in detail

    # 3. Pin topic
    res_pin = client.post("/api/topics/leetcode/algorithms/pin", json={"priority": "high", "notes": "Study hard"})
    assert res_pin.status_code == 200
    assert res_pin.json()["status"] == "pinned"

    # Pinned list
    res_pinned = client.get("/api/topics/pinned")
    assert res_pinned.status_code == 200
    pins = res_pinned.json()["pinned_topics"]
    assert any(p.get("topic_id") == "algorithms" for p in pins)

    # 4. Unpin topic
    res_unpin = client.delete("/api/topics/leetcode/algorithms/pin")
    assert res_unpin.status_code == 200
    assert res_unpin.json()["status"] == "unpinned"

    # 5. Durable learning capture
    res_learning = client.post(
        "/api/topics/leetcode/algorithms/learnings",
        json={
            "title": "Monotonic Stack Linear Scan Invariant",
            "mental_model": "Maintain elements in strictly increasing order to solve next-greater element in O(N).",
            "invariants": ["Stack elements are strictly monotonic", "Each element pushed and popped at most once"],
        },
    )
    created_payload = res_learning.json()
    assert created_payload["status"] == "created"
    assert "learn-" in created_payload["file_path"]

    # Clean up test artifact from repo tree
    created_file = Path(created_payload["absolute_path"])
    if created_file.exists():
        created_file.unlink()


def test_e2e_quiz_endpoints(client):
    """Test /api/quiz start, turn, and ratings."""
    # 1. Start quiz
    res_start = client.post("/api/quiz/start", json={"topic_id": "algorithms", "initial_level": "starter"})
    assert res_start.status_code == 200
    quiz_data = res_start.json()
    sess_id = quiz_data["session_id"]
    ex_id = quiz_data["exercise_id"]

    # 2. Submit turn
    res_turn = client.post(
        "/api/quiz/turn",
        json={
            "session_id": sess_id,
            "exercise_id": ex_id,
            "topic_slug": "algorithms",
            "user_response": "Preserve invariants with monotonic stack and budget protocol.",
        },
    )
    assert res_turn.status_code == 200
    turn_data = res_turn.json()
    assert turn_data["passed"] is True
    assert turn_data["new_rating"] > 3.0

    # 3. Ratings
    res_ratings = client.get("/api/quiz/ratings")
    assert res_ratings.status_code == 200
    assert "algorithms" in res_ratings.json()["ratings"]


def test_e2e_interview_endpoints(client):
    """Test /api/interview start, turn, and scorecard."""
    # 1. Start interview
    res_start = client.post(
        "/api/interview/start",
        json={
            "topic": "algorithms",
            "role_track": "faang_swe_l5_l6",
            "target_company": "Google",
            "mode": "hints",
        },
    )
    assert res_start.status_code == 200
    start_data = res_start.json()
    sess_id = start_data["session_id"]
    assert start_data["hints_remaining"] == 3

    # 2. Hint turn
    res_hint = client.post(
        f"/api/interview/{sess_id}/turn",
        json={"message": "Can I have a hint?", "turn_type": "request_hint"},
    )
    assert res_hint.status_code == 200
    assert res_hint.json()["hints_remaining"] == 2

    # 3. Regular turn
    res_turn = client.post(
        f"/api/interview/{sess_id}/turn",
        json={"message": "Here is my architecture addressing failover and scale."},
    )
    assert res_turn.status_code == 200
    assert res_turn.json()["current_phase"] == "architecture"

    # 4. Finalize & scorecard
    res_scorecard = client.get(f"/api/interview/{sess_id}/scorecard")
    assert res_scorecard.status_code == 200
    card = res_scorecard.json()
    assert card["session_id"] == sess_id
    assert card["bar_decision"] in ("Strong Hire", "Hire", "Leaning Hire", "No Hire")


def test_e2e_resume_endpoints(client):
    """Test /api/resume/analyze."""
    res = client.post(
        "/api/resume/analyze",
        json={
            "job_description_text": "Looking for Staff Software Engineer with distributed systems, concurrency, and algorithms.",
            "role_track": "faang_swe_l5_l6",
            "target_company": "Google",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "fit_score_percentage" in data
    assert len(data["custom_interview_loop"]) == 5
    assert len(data["recommended_learning_plan"]) > 0


def test_e2e_telemetry_endpoints(client):
    """Test /api/telemetry/summary."""
    res = client.get("/api/telemetry/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_requests" in data
    assert "total_tokens" in data


def test_e2e_network_auth_middleware(client, monkeypatch):
    """Verify loopback bypass and non-loopback token enforcement."""
    monkeypatch.setattr(settings, "api_token", "secret-test-token")

    # 1. Loopback request (testclient default) -> allowed without token
    res_loopback = client.get("/api/topics")
    assert res_loopback.status_code == 200

    # 2. Simulated non-loopback request without token -> 401
    remote_client = TestClient(app, client=("192.168.1.100", 50000))
    res_unauth = remote_client.get("/api/topics")
    assert res_unauth.status_code == 401

    # 3. Simulated non-loopback request with Bearer token -> 200
    res_auth = remote_client.get(
        "/api/topics",
        headers={"Authorization": "Bearer secret-test-token"},
    )
    assert res_auth.status_code == 200

    # 4. Simulated non-loopback with query parameter token -> 200
    res_query = remote_client.get("/api/topics?token=secret-test-token")
    assert res_query.status_code == 200


def test_e2e_websocket_stream(client):
    """Verify WebSocket interview streaming endpoint."""
    res_start = client.post(
        "/api/interview/start",
        json={"topic": "algorithms", "role_track": "faang_swe_l5_l6", "target_company": "Google"},
    )
    sess_id = res_start.json()["session_id"]

    with client.websocket_connect(f"/api/interview/{sess_id}/stream") as ws:
        ws.send_json({"message": "My design uses consensus quorum."})

        received_chunks = []
        done_event = None
        while True:
            msg = ws.receive_json()
            if msg["type"] == "chunk":
                received_chunks.append(msg["delta"])
            elif msg["type"] == "done":
                done_event = msg
                break

        assert len(received_chunks) > 0
        assert done_event is not None
        assert done_event["interviewer_message"]
