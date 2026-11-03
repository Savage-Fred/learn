"""Unit tests for adaptive progression engine, difficulty ladder, and Elo DDA."""

from pathlib import Path
import pytest

from app.core.adaptive_engine import AdaptiveEngine
from app.core.state import StateManager
from app.core.topic_loader import TopicLoader


@pytest.fixture
def adaptive_env(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("learn_adaptive_test")
    state_mgr = StateManager(data_dir=temp_dir)
    loader = TopicLoader()
    engine = AdaptiveEngine(state_mgr=state_mgr, loader=loader)
    return engine, state_mgr, temp_dir


def test_start_exercise_initialization(adaptive_env):
    """Test start_exercise returns proper schema and saves session."""
    engine, state_mgr, _ = adaptive_env
    payload = engine.start_exercise(topic_id="algorithms", initial_level="starter")

    assert "session_id" in payload
    assert "exercise_id" in payload
    assert payload["topic_id"] == "algorithms"
    assert payload["difficulty_level"] == "starter"
    assert payload["prompt"]
    assert len(payload["rubric_criteria"]) > 0

    # Session persisted
    sess = state_mgr.get_session(payload["session_id"])
    assert sess is not None
    assert sess["topic_id"] == "algorithms"


def test_start_exercise_empty_topic_raises_error(adaptive_env):
    """Assert empty topic raises ValueError."""
    engine, _, _ = adaptive_env
    with pytest.raises(ValueError):
        engine.start_exercise(topic_id="")
    with pytest.raises(ValueError):
        engine.start_exercise(topic_id="   ")


def test_quiz_pass_increments_rating_and_advances_tier(adaptive_env):
    """Submits passing answer; verifies rating increases and next difficulty advances."""
    engine, state_mgr, _ = adaptive_env
    init_res = engine.start_exercise("algorithms", initial_level="starter")
    sess_id = init_res["session_id"]
    ex_id = init_res["exercise_id"]

    # Passing solution with invariant reasoning
    passing_solution = (
        "We preserve the loop invariant by maintaining a monotonic deque of candidate indices. "
        "At each stride, expired indices are popped in O(1) amortized time."
    )
    turn_res = engine.exercise_turn(sess_id, ex_id, passing_solution)

    assert turn_res["passed"] is True
    assert turn_res["score"] >= 4
    assert turn_res["new_rating"] > 3.0  # Default initial rating was 3.0
    assert turn_res["next_difficulty_level"] in ("l4", "l5", "l6")
    assert turn_res["next_exercise"]["exercise_id"]

    # Rating persisted
    ratings = state_mgr.get_subdomain_ratings()
    assert ratings["algorithms"] == turn_res["new_rating"]


def test_quiz_fail_decrements_rating_and_scaffolds(adaptive_env):
    """Submits failing answer; verifies rating decreases and next difficulty drops."""
    engine, state_mgr, _ = adaptive_env
    init_res = engine.start_exercise("algorithms", initial_level="starter")
    sess_id = init_res["session_id"]
    ex_id = init_res["exercise_id"]

    failing_solution = "I am unsure and don't know how to handle the lock concurrency."
    turn_res = engine.exercise_turn(sess_id, ex_id, failing_solution)

    assert turn_res["passed"] is False
    assert turn_res["score"] <= 2
    assert turn_res["new_rating"] < 3.0
    assert turn_res["next_difficulty_level"] == "starter"


def test_consecutive_passes_reach_tier4_staff(adaptive_env):
    """Consecutive passes advance through ladder up to l6 / tier4_l6."""
    engine, state_mgr, _ = adaptive_env
    init_res = engine.start_exercise("system-design", initial_level="starter")
    sess_id = init_res["session_id"]
    ex_id = init_res["exercise_id"]

    strong_solution = (
        "We maintain the consensus protocol invariant via Raft term numbers and log index bounds. "
        "Each node maintains an append-only WAL with fcntl locks and async flush backpressure."
    )

    # Perform multiple passes
    for _ in range(6):
        res = engine.exercise_turn(sess_id, ex_id, strong_solution)
        ex_id = res["next_exercise"]["exercise_id"]

    assert res["new_rating"] >= 4.5
    assert res["next_difficulty_level"] == "l6"
    assert res["next_tier"] == "tier4_l6"


def test_rating_bounds_clamped(adaptive_env):
    """Ratings remain clamped strictly between 1.0 and 5.0."""
    engine, state_mgr, _ = adaptive_env
    init_res = engine.start_exercise("security", initial_level="starter")
    sess_id = init_res["session_id"]
    ex_id = init_res["exercise_id"]

    # Many passes
    for _ in range(12):
        res = engine.exercise_turn(sess_id, ex_id, "Invariants strictly preserved with lock and protocol budget.")
        ex_id = res["next_exercise"]["exercise_id"]
    assert res["new_rating"] == 5.0

    # Many fails
    for _ in range(25):
        res = engine.exercise_turn(sess_id, ex_id, "dont know confused fail")
        ex_id = res["next_exercise"]["exercise_id"]
    assert res["new_rating"] == 1.0


def test_exercise_session_turn_logging(adaptive_env):
    """Turn records are appended to sessions/exercises.jsonl."""
    engine, state_mgr, temp_dir = adaptive_env
    init_res = engine.start_exercise("rust", initial_level="starter")
    engine.exercise_turn(init_res["session_id"], init_res["exercise_id"], "Proper invariant reasoning with async buffer.")

    log_file = temp_dir / "sessions" / "exercises.jsonl"
    assert log_file.exists()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) >= 1
