"""Unit tests for mock interview engine, Socratic hints, and rubric scoring."""

from pathlib import Path
import pytest

from app.core.interview_engine import InterviewEngine
from app.core.rubric_scorer import RubricScorer
from app.core.state import StateManager


@pytest.fixture
def interview_env(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("learn_interview_test")
    state_mgr = StateManager(data_dir=temp_dir)
    scorer = RubricScorer(state_mgr=state_mgr)
    engine = InterviewEngine(state_mgr=state_mgr, scorer=scorer)
    return engine, state_mgr, scorer, temp_dir


def test_interview_start_hints_vs_no_hints(interview_env):
    """Asserts hints budget is 3 in hints mode and 0 in no-hints mode."""
    engine, _, _, _ = interview_env

    # Hints mode
    h_res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    assert h_res["hints_remaining"] == 3
    assert h_res["current_phase"] == "clarification"

    # No-hints mode
    nh_res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="no-hints")
    assert nh_res["hints_remaining"] == 0


def test_interview_invalid_args_raise_value_error(interview_env):
    """Assert invalid role tracks, companies, or modes raise ValueError."""
    engine, _, _, _ = interview_env

    with pytest.raises(ValueError, match="Unsupported role_track"):
        engine.start_interview("invalid_track", "Google", "algorithms")

    with pytest.raises(ValueError, match="Unsupported target_company"):
        engine.start_interview("faang_swe_l5_l6", "NonexistentCompany", "algorithms")

    with pytest.raises(ValueError, match="Invalid mode"):
        engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="invalid_mode")


def test_interview_hints_mode_progressive_scaffolding(interview_env):
    """Verifies 3 progressive hint levels followed by budget exhaustion."""
    engine, _, _, _ = interview_env
    res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = res["session_id"]

    # Hint 1: Conceptual
    t1 = engine.interview_turn(sess_id, "Can I get a hint?", turn_type="request_hint")
    assert t1["hints_remaining"] == 2
    assert "Conceptual" in t1["interviewer_message"]

    # Hint 2: Structural
    t2 = engine.interview_turn(sess_id, "Need another hint please", turn_type="request_hint")
    assert t2["hints_remaining"] == 1
    assert "Structural" in t2["interviewer_message"]

    # Hint 3: Scaffold
    t3 = engine.interview_turn(sess_id, "One more hint", turn_type="request_hint")
    assert t3["hints_remaining"] == 0
    assert "Scaffold" in t3["interviewer_message"]

    # Hint 4: Exhausted
    t4 = engine.interview_turn(sess_id, "Another hint?", turn_type="request_hint")
    assert t4["hints_remaining"] == 0
    assert "exhausted" in t4["interviewer_message"].lower()


def test_interview_no_hints_mode_rejects_hints(interview_env):
    """Asserts hint requests are denied without deducting budget in no-hints mode."""
    engine, _, _, _ = interview_env
    res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="no-hints")
    sess_id = res["session_id"]

    t1 = engine.interview_turn(sess_id, "Can I get a hint?", turn_type="request_hint")
    assert t1["hints_remaining"] == 0
    assert "hints are disabled" in t1["interviewer_message"].lower()


def test_interview_phase_transitions(interview_env):
    """Verifies progression across all 5 standard E2E interview phases."""
    engine, _, _, _ = interview_env
    res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = res["session_id"]

    assert res["current_phase"] == "clarification"

    # Turn 1 -> Architecture
    t1 = engine.interview_turn(sess_id, "I clarify the scale constraints and write invariants.")
    assert t1["current_phase"] == "architecture"

    # Turn 2 -> Implementation
    t2 = engine.interview_turn(sess_id, "Here is my high-level distributed service layout.")
    assert t2["current_phase"] == "implementation"

    # Turn 3 -> Verification
    t3 = engine.interview_turn(sess_id, "Here is the core algorithm maintaining invariant correctness.")
    assert t3["current_phase"] == "verification"

    # Turn 4 -> Probing
    t4 = engine.interview_turn(sess_id, "We prove correctness by edge-case testing and monotonic bounds.")
    assert t4["current_phase"] == "probing"


def test_interview_adversarial_stress_probing(interview_env):
    """In no-hints mode at probing phase, adversarial stress question is asked."""
    engine, _, _, _ = interview_env
    res = engine.start_interview("faang_swe_l5_l6", "OpenAI", "system-design", mode="no-hints")
    sess_id = res["session_id"]

    # Advance to probing
    engine.interview_turn(sess_id, "Clarify requirements.")
    engine.interview_turn(sess_id, "Propose distributed event store.")
    engine.interview_turn(sess_id, "Implement partitioned ring buffer.")
    t4 = engine.interview_turn(sess_id, "Verify with checksums and linearizability proofs.")
    assert t4["current_phase"] == "probing"

    # Probing turn in no-hints mode returns adversarial question
    t5 = engine.interview_turn(sess_id, "We handle partitions with consensus quorum.")
    assert "Adversarial follow-up" in t5["interviewer_message"]
    assert "network partition" in t5["interviewer_message"]


def test_interview_scorecard_and_ratings_update(interview_env):
    """Finalizes interview, asserts 5-dimension rubric, bar decision, and rating update."""
    engine, state_mgr, _, _ = interview_env
    res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = res["session_id"]

    engine.interview_turn(sess_id, "Clarification details")
    engine.interview_turn(sess_id, "Architecture details")

    scorecard = engine.finalize_interview(sess_id)

    assert scorecard["session_id"] == sess_id
    assert scorecard["role_track"] == "faang_swe_l5_l6"
    assert scorecard["target_company"] == "Google"
    assert scorecard["bar_decision"] in ("Strong Hire", "Hire", "Leaning Hire", "No Hire")
    assert "rubric_scores" in scorecard
    assert len(scorecard["rubric_scores"]) == 5
    assert scorecard["overall_score"] >= 1.0

    # Subdomain ratings updated
    ratings = state_mgr.get_subdomain_ratings()
    assert "algorithms" in ratings


def test_finalized_interview_rejects_further_turns(interview_env):
    """Asserts ValueError when attempting turns on a finalized interview."""
    engine, _, _, _ = interview_env
    res = engine.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = res["session_id"]
    engine.finalize_interview(sess_id)

    with pytest.raises(ValueError, match="already finalized"):
        engine.interview_turn(sess_id, "Another turn after finalization")
