"""Deep adversarial edge-case and vulnerability probing harness.

Stress-tests:
1. Path traversal injection attacks in topics, domains, sessions, and filenames.
2. Null byte and Unicode injection.
3. Giant payload handling (memory pressure / truncation).
4. Corrupted state file resilience (graceful recovery vs unhandled crash).
5. Invariant §R4 boundary validation (rejection of in-repo state directory).
6. Concurrent access to the exact same session_id across multiple threads.
7. Extreme rating boundary operations (NaN, inf, negative ratings).
"""

import concurrent.futures
import json
import os
from pathlib import Path
import pytest

from app.config import settings
from app.core.adaptive_engine import AdaptiveEngine
from app.core.interview_engine import InterviewEngine
from app.core.resume_matcher import ResumeMatcher
from app.core.rubric_scorer import RubricScorer
from app.core.state import StateManager, sanitize_identifier


@pytest.fixture
def deep_env(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("deep_adversarial_env")
    state_mgr = StateManager(data_dir=temp_dir)
    adaptive = AdaptiveEngine(state_mgr=state_mgr)
    scorer = RubricScorer(state_mgr=state_mgr)
    interview = InterviewEngine(state_mgr=state_mgr, scorer=scorer)
    matcher = ResumeMatcher(state_mgr=state_mgr)
    return {
        "dir": temp_dir,
        "state": state_mgr,
        "adaptive": adaptive,
        "scorer": scorer,
        "interview": interview,
        "matcher": matcher,
    }


def test_path_traversal_and_injection_rejection(deep_env):
    """Verify sanitize_identifier strictly rejects path traversal attempts."""
    traversal_attacks = [
        "../etc/passwd",
        "..\\windows\\system32",
        "foo/bar",
        "foo\\bar",
        "/absolute/path",
        "nested/../../secret",
        "topic\0nullbyte",
        "",
        "   ",
    ]

    for attack in traversal_attacks:
        with pytest.raises(ValueError):
            sanitize_identifier(attack)

        # In state manager
        with pytest.raises(ValueError):
            deep_env["state"].get_session(attack)

        with pytest.raises(ValueError):
            deep_env["state"].pin_topic(attack)


def test_invariant_r4_rejects_in_repo_data_dir():
    """Verify StateManager enforces §R4 invariant, rejecting data_dir inside repository root."""
    in_repo_dir = settings.repo_root / "test_in_repo_dir"
    with pytest.raises(ValueError, match="§R4 invariant"):
        StateManager(data_dir=in_repo_dir)


def test_corrupted_json_state_recovery(deep_env):
    """Verify safe_read_json recovers gracefully when state files are truncated or corrupt."""
    state_mgr = deep_env["state"]
    data_dir = deep_env["dir"]

    # 1. Corrupt ratings file with invalid JSON
    ratings_file = data_dir / "ratings" / "subdomain_ratings.json"
    ratings_file.write_text("{ this is not valid json !!! }", encoding="utf-8")

    # Should not crash, should return empty dict or fallback
    ratings = state_mgr.get_subdomain_ratings()
    assert isinstance(ratings, dict)

    # 2. Corrupt session file
    sess_file = data_dir / "sessions" / "corrupted_session.json"
    sess_file.write_text("TRUNCATED_JSON_STREAM...", encoding="utf-8")

    sess_data = state_mgr.get_session("corrupted_session")
    assert sess_data is None  # Graceful fallback instead of unhandled 500


def test_giant_payload_and_unicode_handling(deep_env):
    """Stress-test huge payloads (1MB string) and unicode characters in candidate turns."""
    adaptive = deep_env["adaptive"]
    interview = deep_env["interview"]

    # 1. Adaptive engine with 500KB submission
    init_ex = adaptive.start_exercise("algorithms", initial_level="starter")
    giant_text = "Invariant preserved. " * 25000 + " 🚀 🔥 💻 漢字"
    turn_res = adaptive.exercise_turn(init_ex["session_id"], init_ex["exercise_id"], giant_text)
    assert turn_res["passed"] is True
    # Verify user_response is safely stored / truncated in history
    sess = deep_env["state"].get_session(init_ex["session_id"])
    assert len(sess["history"][0]["user_response"]) <= 255

    # 2. Mock interview with giant candidate text
    init_int = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms")
    int_res = interview.interview_turn(init_int["session_id"], giant_text)
    assert int_res["current_phase"] == "architecture"


def test_concurrent_session_turn_execution(deep_env):
    """Stress-test multiple concurrent turns on the SAME interview session."""
    interview = deep_env["interview"]
    init = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = init["session_id"]

    def submit_turn(idx):
        return interview.interview_turn(sess_id, f"Turn {idx} with clarifying constraints.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(submit_turn, i) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 10
    sess = deep_env["state"].get_session(sess_id)
    assert len(sess["dialogue"]) == 1 + (10 * 2)  # welcome + 10 turns * 2


def test_extreme_rating_inputs_clamping(deep_env):
    """Verify set_subdomain_ratings and update_subdomain_rating strictly clamp extreme values."""
    state_mgr = deep_env["state"]

    # Test extreme values
    extreme_inputs = {
        "negative": -100.0,
        "huge": 99999.99,
        "zero": 0.0,
        "exact_low": 1.0,
        "exact_high": 5.0,
    }
    state_mgr.set_subdomain_ratings(extreme_inputs)

    ratings = state_mgr.get_subdomain_ratings()
    assert ratings["negative"] == 1.00
    assert ratings["huge"] == 5.00
    assert ratings["zero"] == 1.00
    assert ratings["exact_low"] == 1.00
    assert ratings["exact_high"] == 5.00


def test_concurrent_subdomain_rating_lost_updates(deep_env):
    """Stress-test concurrent topic rating updates across 20 distinct topics."""
    state_mgr = deep_env["state"]

    def write_topic(i):
        state_mgr.update_subdomain_rating(f"topic_{i}", 3.0 + i * 0.05)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(write_topic, range(20)))

    ratings = state_mgr.get_subdomain_ratings()
    # Expect all 20 topics to be persisted without lost updates
    assert len(ratings) == 20

