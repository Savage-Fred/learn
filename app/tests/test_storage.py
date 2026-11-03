"""Unit tests for out-of-git personal state storage, atomic writes, and locking."""

import concurrent.futures
import json
import os
import subprocess
import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.core.state import (
    StateManager,
    sanitize_identifier,
    atomic_write_json,
    safe_read_json,
)


@pytest.fixture
def isolated_data_dir(tmp_path_factory):
    """Provides an isolated data directory guaranteed to be outside the repository."""
    temp_dir = tmp_path_factory.mktemp("learn_storage_test")
    return temp_dir


@pytest.fixture
def state_mgr(isolated_data_dir):
    return StateManager(data_dir=isolated_data_dir)


def test_storage_isolation_invariant(isolated_data_dir):
    """Assert StateManager rejects any data_dir located inside repo_root (§R4)."""
    repo_root = settings.repo_root.resolve()
    inside_dir = repo_root / ".test_internal_data"
    with pytest.raises(ValueError, match="must not be located inside repository root"):
        StateManager(data_dir=inside_dir)

    # Valid external dir should succeed
    mgr = StateManager(data_dir=isolated_data_dir)
    assert mgr.data_dir == isolated_data_dir.resolve()


def test_atomic_write_concurrency(isolated_data_dir):
    """Spawns 20 concurrent threads writing alternating updates; asserts valid JSON."""
    test_file = isolated_data_dir / "ratings" / "subdomain_ratings.json"

    def write_worker(idx: int):
        data = {f"topic_{idx}": 3.0 + (idx % 3) * 0.5}
        atomic_write_json(test_file, data)
        read_back = safe_read_json(test_file)
        assert isinstance(read_back, dict)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(write_worker, i) for i in range(20)]
        for f in concurrent.futures.as_completed(futures):
            f.result()

    final = safe_read_json(test_file)
    assert isinstance(final, dict)


def test_path_traversal_rejection(state_mgr):
    """Assert sanitize_identifier and state methods reject traversal attempts."""
    bad_identifiers = [
        "../etc/passwd",
        "../../evil",
        "/etc/shadow",
        "topic/subtopic",
        "topic\\subtopic",
        "topic\0null",
        "",
        "   ",
    ]
    for bad in bad_identifiers:
        with pytest.raises(ValueError):
            sanitize_identifier(bad)
        with pytest.raises(ValueError):
            state_mgr.pin_topic(bad)
        with pytest.raises(ValueError):
            state_mgr.unpin_topic(bad)
        with pytest.raises(ValueError):
            state_mgr.update_subdomain_rating(bad, 4.0)


def test_subdomain_ratings_roundtrip_and_clamping(state_mgr):
    """Test ratings persistence, clamping between 1.0 and 5.0, and dual-file synchronization."""
    assert state_mgr.get_subdomain_ratings() == {}

    # Test update and clamping
    r1 = state_mgr.update_subdomain_rating("algorithms", 4.25)
    assert r1 == 4.25

    # Clamp upper bound to 5.0
    r_high = state_mgr.update_subdomain_rating("rust", 7.5)
    assert r_high == 5.0

    # Clamp lower bound to 1.0
    r_low = state_mgr.update_subdomain_rating("go", -2.0)
    assert r_low == 1.0

    ratings = state_mgr.get_subdomain_ratings()
    assert ratings["algorithms"] == 4.25
    assert ratings["rust"] == 5.0
    assert ratings["go"] == 1.0

    # Dual-path verification: both primary and alias files must exist and match
    assert state_mgr.ratings_file.exists()
    assert state_mgr.ratings_alias_file.exists()
    with open(state_mgr.ratings_file, "r") as f1, open(state_mgr.ratings_alias_file, "r") as f2:
        assert json.load(f1) == json.load(f2)


def test_pinned_topics_lifecycle(state_mgr):
    """Test pin, update priority, list, and unpin topic idempotently."""
    assert state_mgr.get_pinned_topics() == []

    # Pin topic
    p1 = state_mgr.pin_topic("differential-privacy", domain="privacy-engineering", priority="high", notes="Must review Renyi DP")
    assert p1["status"] == "pinned"
    assert p1["topic_id"] == "differential-privacy"
    assert p1["priority"] == "high"

    # Update priority
    p1_updated = state_mgr.pin_topic("differential-privacy", domain="privacy-engineering", priority="medium")
    assert p1_updated["priority"] == "medium"

    # List pins
    pins = state_mgr.get_pinned_topics()
    assert len(pins) == 1
    assert pins[0]["topic_id"] == "differential-privacy"

    # Dual-path verification
    assert state_mgr.pinned_topics_file.exists()
    assert state_mgr.pinned_topics_alias_file.exists()

    # Unpin topic
    removed = state_mgr.unpin_topic("differential-privacy")
    assert removed is True
    assert state_mgr.get_pinned_topics() == []

    # Unpin non-existent topic returns False
    assert state_mgr.unpin_topic("differential-privacy") is False


def test_session_and_scorecard_roundtrip(state_mgr):
    """Verify session and scorecard serialization to sessions/ and interviews/."""
    sess_id = "test-session-1234"
    sess_data = {
        "session_id": sess_id,
        "topic": "algorithms",
        "current_phase": "architecture",
        "history": [{"speaker": "candidate", "message": "hello"}],
    }
    state_mgr.save_session(sess_id, sess_data)

    loaded = state_mgr.get_session(sess_id)
    assert loaded is not None
    assert loaded["session_id"] == sess_id
    assert loaded["current_phase"] == "architecture"

    # Scorecard
    card_data = {
        "session_id": sess_id,
        "overall_score": 4.5,
        "bar_decision": "Strong Hire",
    }
    state_mgr.save_scorecard(sess_id, card_data)

    loaded_card = state_mgr.get_scorecard(sess_id)
    assert loaded_card is not None
    assert loaded_card["overall_score"] == 4.5
    assert loaded_card["bar_decision"] == "Strong Hire"


def test_clean_git_status_after_mutations(state_mgr):
    """Assert mutations to personal state store do not modify git working tree."""
    # Perform various mutations
    state_mgr.pin_topic("algorithms", priority="high")
    state_mgr.update_subdomain_rating("algorithms", 4.5)
    state_mgr.save_session("session-xyz", {"foo": "bar"})
    state_mgr.save_active_resume("Resume content here")
    state_mgr.log_exercise_turn({"score": 5.0})

    # Run git status in repo_root
    res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(settings.repo_root),
        capture_output=True,
        text=True,
        check=True,
    )
    # Check that no ~/.local or data_dir files are tracked or untracked in repo
    for line in res.stdout.splitlines():
        assert "subdomain_ratings" not in line
        assert "pinned_topics" not in line
        assert "active_resume" not in line
