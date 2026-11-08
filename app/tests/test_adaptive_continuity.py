"""Issue #9: quiz turns keep real curriculum and never record silent heuristic grades."""

import json
import sys

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.core import adaptive_engine, state
from app.core.adaptive_engine import AdaptiveEngine, GradingUnavailableError
from app.core.schemas import DifficultyTier
from app.core.state import StateManager
from app.core.topic_loader import topic_loader
from app.main import app
from app.mcp.server import MCPServer
from app.router import ProviderUnavailableError

PASS = "Invariant preserved with a lock-free protocol and bounded budget."
FAIL = "dont know"
GOOD_REPLY = '{"score": 4, "passed": true, "feedback": "Meets the rubric."}'


def curriculum(level: str) -> str:
    return topic_loader.load_exercise_content("algorithms", DifficultyTier.from_str(level))[0]


class FakeRouter:
    """Stands in for a live router so no test reaches a real provider CLI."""

    use_mock_llm = False

    def __init__(self, reply=GOOD_REPLY, error=None, provider="claude", tier="subscription_cli"):
        self.reply, self.error, self.provider, self.tier = reply, error, provider, tier
        self.prompts = []

    def route(self, prompt, workflow="general", **_):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return {"text": self.reply, "provider": self.provider, "tier": self.tier}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(state, "data_dir", tmp_path)
    state.ensure_layout()
    return TestClient(app)


def test_api_ladder_serves_real_curriculum_up_and_down(client):
    _, topic_dir = topic_loader.resolve_topic_dir("algorithms")
    for tier in DifficultyTier:
        assert (topic_dir / "exercises" / f"{tier.value}.md").exists()

    start = client.post("/api/quiz/start", json={"topic_id": "algorithms"}).json()
    assert start["prompt"] == curriculum("starter")
    session_id, exercise_id = start["session_id"], start["exercise_id"]

    served = []
    for answer, expected in [(PASS, "l4"), (PASS, "l5"), (PASS, "l6"), (FAIL, "l5"), (FAIL, "l4"), (FAIL, "starter")]:
        res = client.post("/api/quiz/turn", json={
            "session_id": session_id, "exercise_id": exercise_id,
            "topic_id": "algorithms", "user_response": answer,
        })
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["next_difficulty_level"] == expected
        assert body["next_exercise"]["prompt"] == curriculum(expected)
        assert body["next_exercise"]["rubric_criteria"]
        assert body["assessment_source"] == "deterministic_mock"
        exercise_id = body["next_exercise"]["exercise_id"]
        served.append(body["next_exercise"]["prompt"])
    assert len(set(served)) == 4


def test_live_grader_receives_current_problem_and_rubric_each_turn(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "use_mock_llm", False)
    router = FakeRouter()
    engine = AdaptiveEngine(state_mgr=StateManager(data_dir=tmp_path), router=router)

    start = engine.start_exercise("algorithms")
    first = engine.exercise_turn(start["session_id"], start["exercise_id"], "first answer")
    engine.exercise_turn(start["session_id"], first["next_exercise"]["exercise_id"], "second answer")

    assert first["assessment_source"] == "model"
    assert first["score"] == 4 and first["passed"] is True
    assert curriculum("starter") in router.prompts[0]
    assert curriculum("l4") in router.prompts[1]
    for criterion in start["rubric_criteria"]:
        assert criterion in router.prompts[1]


@pytest.mark.parametrize("router", [
    FakeRouter(error=ProviderUnavailableError("all providers down")),
    FakeRouter(provider="mock", tier="mock"),  # router's silent mock fallback
    FakeRouter(reply="Looks great to me!"),
    FakeRouter(reply='{"score": 9, "passed": true}'),
    FakeRouter(reply='{"score": "4", "passed": "yes"}'),
    FakeRouter(reply='{"score": NaN, "passed": true}'),
], ids=["provider-error", "mock-fallback", "no-json", "out-of-range", "wrong-types", "nan"])
def test_live_grading_failure_is_explicit_and_changes_nothing(tmp_path, monkeypatch, router):
    monkeypatch.setattr(settings, "use_mock_llm", False)
    mgr = StateManager(data_dir=tmp_path)
    engine = AdaptiveEngine(state_mgr=mgr, router=router)
    start = engine.start_exercise("algorithms")
    before = mgr.get_session(start["session_id"])

    with pytest.raises(GradingUnavailableError):
        engine.exercise_turn(start["session_id"], start["exercise_id"], PASS)

    assert mgr.get_subdomain_ratings() == {}
    assert mgr.get_session(start["session_id"]) == before


def test_api_reports_grading_failure_as_503_without_rating_change(client, monkeypatch):
    monkeypatch.setattr(settings, "use_mock_llm", False)
    monkeypatch.setattr(adaptive_engine, "router", FakeRouter(reply="not json"))
    start = client.post("/api/quiz/start", json={"topic_id": "algorithms"}).json()

    res = client.post("/api/quiz/turn", json={
        "session_id": start["session_id"], "exercise_id": start["exercise_id"],
        "topic_id": "algorithms", "user_response": PASS,
    })

    assert res.status_code == 503
    assert "no grade was recorded" in res.json()["detail"]
    assert client.get("/api/quiz/ratings").json()["ratings"] == {}


def test_legacy_mcp_turn_uses_shared_engine(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    mcp = MCPServer()
    call = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "learn_run_adaptive_exercise_turn",
        "arguments": {"exercise_id": "tier1_starter", "user_response": PASS, "topic_slug": "algorithms"},
    }}

    data = json.loads(mcp.handle_request(call)["result"]["content"][0]["text"])
    assert data["assessment_source"] == "deterministic_mock"
    assert data["next_tier"] == data["next_difficulty_level"] == "tier2_l4"
    assert data["next_exercise"] == "algorithms/exercises/tier2_l4.md"
    assert StateManager(tmp_path).get_session(data["session_id"])["current_difficulty"] == "tier2_l4"

    # Live mode: a malformed grade must not fall back to the legacy heuristic.
    monkeypatch.setattr(settings, "use_mock_llm", False)
    monkeypatch.setattr(
        sys.modules["app.core.adaptive_engine"], "MultiModelRouter", lambda: FakeRouter(reply="??")
    )
    ratings_before = StateManager(tmp_path).get_subdomain_ratings()
    resp = mcp.handle_request(call)
    assert "error" in resp or resp["result"].get("isError")
    assert StateManager(tmp_path).get_subdomain_ratings() == ratings_before
