"""Adversarial challenge test harness for Milestone 4 adaptive engine and mock interview.

Empirical verification of:
1. Adaptive Ladder & Elo Rating Dynamics (4 tiers, rating bounds, deltas, clamping, dual persistence, concurrency).
2. Mock Interview State Machine & Hints Budget (3-tier Socratic escalation, budget exhaustion, strict no-hints, adversarial probing, dual transcript persistence, finalization idempotency).
3. Rubric Scorer & Resume Matcher (5 rubric weights, 7 company calibration bars, 0-100% fit score, 5-round loop generation).
"""

import concurrent.futures
import json
from pathlib import Path
import pytest

from app.core.adaptive_engine import AdaptiveEngine
from app.core.interview_engine import InterviewEngine
from app.core.resume_matcher import ResumeMatcher
from app.core.rubric_scorer import RubricScorer
from app.core.schemas import (
    BarDecision,
    CompanyBar,
    DifficultyTier,
    InterviewMode,
    RoleTrack,
    RubricScores,
)
from app.core.state import StateManager
from app.core.topic_loader import TopicLoader


@pytest.fixture
def test_env(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("adversarial_challenge_env")
    state_mgr = StateManager(data_dir=temp_dir)
    loader = TopicLoader()
    adaptive = AdaptiveEngine(state_mgr=state_mgr, loader=loader)
    scorer = RubricScorer(state_mgr=state_mgr)
    interview = InterviewEngine(state_mgr=state_mgr, scorer=scorer)
    matcher = ResumeMatcher(state_mgr=state_mgr)
    return {
        "data_dir": temp_dir,
        "state": state_mgr,
        "loader": loader,
        "adaptive": adaptive,
        "scorer": scorer,
        "interview": interview,
        "matcher": matcher,
    }


# =============================================================================
# 1. Adaptive Ladder & Elo Rating Dynamics
# =============================================================================

def test_stress_alternating_ladder_and_tiers(test_env):
    """Empirically test rapid alternating passes and misses across all 4 tiers."""
    adaptive = test_env["adaptive"]
    state_mgr = test_env["state"]

    init = adaptive.start_exercise(topic_id="algorithms", initial_level="starter")
    sess_id = init["session_id"]
    ex_id = init["exercise_id"]

    pass_code = "Preserve topological sort invariant using Kahn's algorithm and monotonic queue."
    fail_code = "I don't know and am confused."

    # 1. Step up tier1 -> tier2 -> tier3 -> tier4
    # Turn 1: Pass at starter -> should advance to l4 / tier2_l4
    r1 = adaptive.exercise_turn(sess_id, ex_id, pass_code)
    assert r1["passed"] is True
    assert r1["next_difficulty_level"] == "l4"
    assert r1["next_tier"] == "tier2_l4"

    # Turn 2: Pass at l4 -> should advance to l5 / tier3_l5
    r2 = adaptive.exercise_turn(sess_id, r1["next_exercise"]["exercise_id"], pass_code)
    assert r2["passed"] is True
    assert r2["next_difficulty_level"] == "l5"
    assert r2["next_tier"] == "tier3_l5"

    # Turn 3: Pass at l5 -> should advance to l6 / tier4_l6
    r3 = adaptive.exercise_turn(sess_id, r2["next_exercise"]["exercise_id"], pass_code)
    assert r3["passed"] is True
    assert r3["next_difficulty_level"] == "l6"
    assert r3["next_tier"] == "tier4_l6"

    # Turn 4: Pass at ceiling l6 -> should remain clamped at l6 / tier4_l6
    r4 = adaptive.exercise_turn(sess_id, r3["next_exercise"]["exercise_id"], pass_code)
    assert r4["passed"] is True
    assert r4["next_difficulty_level"] == "l6"
    assert r4["next_tier"] == "tier4_l6"

    # Turn 5: Miss at l6 -> should step down to l5 / tier3_l5
    r5 = adaptive.exercise_turn(sess_id, r4["next_exercise"]["exercise_id"], fail_code)
    assert r5["passed"] is False
    assert r5["next_difficulty_level"] == "l5"
    assert r5["next_tier"] == "tier3_l5"

    # Turn 6: Miss at l5 -> should step down to l4 / tier2_l4
    r6 = adaptive.exercise_turn(sess_id, r5["next_exercise"]["exercise_id"], fail_code)
    assert r6["passed"] is False
    assert r6["next_difficulty_level"] == "l4"
    assert r6["next_tier"] == "tier2_l4"

    # Turn 7: Miss at l4 -> should step down to starter / tier1_starter
    r7 = adaptive.exercise_turn(sess_id, r6["next_exercise"]["exercise_id"], fail_code)
    assert r7["passed"] is False
    assert r7["next_difficulty_level"] == "starter"
    assert r7["next_tier"] == "tier1_starter"

    # Turn 8: Miss at floor starter -> should remain at starter / tier1_starter
    r8 = adaptive.exercise_turn(sess_id, r7["next_exercise"]["exercise_id"], fail_code)
    assert r8["passed"] is False
    assert r8["next_difficulty_level"] == "starter"
    assert r8["next_tier"] == "tier1_starter"

    # Rapid alternating 40 turns
    curr_ex = r8["next_exercise"]["exercise_id"]
    for i in range(40):
        action_pass = (i % 2 == 0)
        resp = adaptive.exercise_turn(sess_id, curr_ex, pass_code if action_pass else fail_code)
        curr_ex = resp["next_exercise"]["exercise_id"]
        assert resp["next_difficulty_level"] in ["starter", "l4", "l5", "l6"]
        assert resp["next_tier"] in ["tier1_starter", "tier2_l4", "tier3_l5", "tier4_l6"]
        assert 1.0 <= resp["new_rating"] <= 5.0


def test_rating_bounds_clamping_and_deltas(test_env):
    """Empirically test pass (+0.35), miss (-0.25), and strict bounds [1.0, 5.0]."""
    adaptive = test_env["adaptive"]
    state_mgr = test_env["state"]

    # Explicitly set starting rating to 3.00
    state_mgr.update_subdomain_rating("test-topic", 3.00)

    init = adaptive.start_exercise(topic_id="test-topic", initial_level="starter")
    sess_id = init["session_id"]
    ex_id = init["exercise_id"]

    pass_code = "Maintain invariant using async buffer lock and protocol state."
    fail_code = "I don't know."

    # 1. Single pass: 3.00 + 0.35 = 3.35
    t1 = adaptive.exercise_turn(sess_id, ex_id, pass_code)
    assert t1["passed"] is True
    assert t1["new_rating"] == 3.35

    # 2. Single miss: 3.35 - 0.25 = 3.10
    t2 = adaptive.exercise_turn(sess_id, t1["next_exercise"]["exercise_id"], fail_code)
    assert t2["passed"] is False
    assert t2["new_rating"] == 3.10

    # 3. Floor clamping at 1.00: 20 consecutive misses
    curr_ex = t2["next_exercise"]["exercise_id"]
    for _ in range(20):
        res = adaptive.exercise_turn(sess_id, curr_ex, fail_code)
        curr_ex = res["next_exercise"]["exercise_id"]
    assert res["new_rating"] == 1.00
    assert state_mgr.get_subdomain_ratings()["test-topic"] == 1.00

    # Extra miss when already at 1.00 -> remains strictly 1.00
    res_floor = adaptive.exercise_turn(sess_id, curr_ex, fail_code)
    assert res_floor["new_rating"] == 1.00
    assert res_floor["new_rating"] >= 1.00

    # 4. Ceiling clamping at 5.00: 20 consecutive passes
    curr_ex = res_floor["next_exercise"]["exercise_id"]
    for _ in range(20):
        res = adaptive.exercise_turn(sess_id, curr_ex, pass_code)
        curr_ex = res["next_exercise"]["exercise_id"]
    assert res["new_rating"] == 5.00
    assert state_mgr.get_subdomain_ratings()["test-topic"] == 5.00

    # Extra pass when already at 5.00 -> remains strictly 5.00
    res_ceil = adaptive.exercise_turn(sess_id, curr_ex, pass_code)
    assert res_ceil["new_rating"] == 5.00
    assert res_ceil["new_rating"] <= 5.00


def test_dual_persistence_ratings_and_turn_logging(test_env):
    """Verify dual-path persistence in ratings/subdomain_ratings.json and subdomain_ratings.json."""
    adaptive = test_env["adaptive"]
    state_mgr = test_env["state"]
    data_dir = test_env["data_dir"]

    init = adaptive.start_exercise(topic_id="storage-test", initial_level="starter")
    sess_id = init["session_id"]
    ex_id = init["exercise_id"]

    adaptive.exercise_turn(sess_id, ex_id, "Invariants strictly held via lock and raft protocol.")

    # 1. Dual rating files exist and are strictly identical
    file1 = data_dir / "ratings" / "subdomain_ratings.json"
    file2 = data_dir / "subdomain_ratings.json"
    assert file1.exists(), f"{file1} does not exist"
    assert file2.exists(), f"{file2} does not exist"

    data1 = json.loads(file1.read_text(encoding="utf-8"))
    data2 = json.loads(file2.read_text(encoding="utf-8"))
    assert data1 == data2
    assert "storage-test" in data1
    assert data1["storage-test"] == 1.35

    # 2. Turn logging in sessions/exercises.jsonl
    log_file = data_dir / "sessions" / "exercises.jsonl"
    assert log_file.exists()
    lines = [json.loads(line) for line in log_file.read_text(encoding="utf-8").strip().splitlines()]
    assert len(lines) >= 1
    assert lines[-1]["session_id"] == sess_id
    assert lines[-1]["topic"] == "storage-test"
    assert lines[-1]["passed"] is True
    assert lines[-1]["new_rating"] == 1.35


def test_concurrent_state_writes_safety(test_env):
    """Stress-test concurrent rating updates to verify atomic replacement and fcntl locking."""
    state_mgr = test_env["state"]
    data_dir = test_env["data_dir"]

    def update_rating(i):
        topic = f"topic-{i % 5}"
        rating = round(1.0 + (i % 40) * 0.1, 2)
        state_mgr.update_subdomain_rating(topic, rating)
        return topic, rating

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(update_rating, i) for i in range(50)]
        for f in concurrent.futures.as_completed(futures):
            f.result()

    # Verify files are valid JSON without corruptions
    file1 = data_dir / "ratings" / "subdomain_ratings.json"
    file2 = data_dir / "subdomain_ratings.json"
    data1 = json.loads(file1.read_text(encoding="utf-8"))
    data2 = json.loads(file2.read_text(encoding="utf-8"))
    assert data1 == data2
    assert len(data1) == 5
    for k, v in data1.items():
        assert 1.0 <= v <= 5.0


# =============================================================================
# 2. Mock Interview State Machine & Hints Budget
# =============================================================================

def test_socratic_hints_mode_escalation_and_rejection(test_env):
    """Test Socratic hints: exactly 3 hints, sequential escalation, 4th rejected."""
    interview = test_env["interview"]
    state_mgr = test_env["state"]

    res = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = res["session_id"]
    assert res["hints_remaining"] == 3

    # Hint 1: Conceptual
    t1 = interview.interview_turn(sess_id, "Can you provide a hint?", turn_type="request_hint")
    assert t1["hints_remaining"] == 2
    assert t1["hints_used"] == 1
    assert "Conceptual" in t1["interviewer_message"]

    # Hint 2: Structural
    t2 = interview.interview_turn(sess_id, "Need another hint please", turn_type="request_hint")
    assert t2["hints_remaining"] == 1
    assert t2["hints_used"] == 2
    assert "Structural" in t2["interviewer_message"]

    # Hint 3: Scaffold
    t3 = interview.interview_turn(sess_id, "One final hint please", turn_type="request_hint")
    assert t3["hints_remaining"] == 0
    assert t3["hints_used"] == 3
    assert "Scaffold" in t3["interviewer_message"]

    # Hint 4: Rejection (Budget Exhausted)
    t4 = interview.interview_turn(sess_id, "Can I have one more hint?", turn_type="request_hint")
    assert t4["hints_remaining"] == 0
    assert t4["hints_used"] == 3
    assert "exhausted" in t4["interviewer_message"].lower()

    # Hint 5: Still rejected
    t5 = interview.interview_turn(sess_id, "hint please", turn_type="request_hint")
    assert t5["hints_remaining"] == 0
    assert t5["hints_used"] == 3
    assert "exhausted" in t5["interviewer_message"].lower()


def test_strict_no_hints_mode_and_adversarial_probing(test_env):
    """Test Strict No-Hints: 0 budget, immediate rejection, adversarial probing at probing phase."""
    interview = test_env["interview"]
    state_mgr = test_env["state"]

    res = interview.start_interview(
        role_track="faang_swe_l5_l6",
        target_company="OpenAI",
        topic="system-design",
        mode="no-hints",
        time_limit_minutes=45,
    )
    sess_id = res["session_id"]
    assert res["hints_remaining"] == 0
    assert res["current_phase"] == "clarification"

    # Hint attempt in no-hints mode
    t_hint = interview.interview_turn(sess_id, "Give me a hint", turn_type="request_hint")
    assert t_hint["hints_remaining"] == 0
    assert "disabled" in t_hint["interviewer_message"].lower()

    # Advance through 5 phases
    # Clarification -> Architecture
    t1 = interview.interview_turn(sess_id, "Requirements clarified: 100k QPS, p99 < 10ms.")
    assert t1["current_phase"] == "architecture"

    # Architecture -> Implementation
    t2 = interview.interview_turn(sess_id, "Architecture: Partitioned Raft clusters with leader leases.")
    assert t2["current_phase"] == "implementation"

    # Implementation -> Verification
    t3 = interview.interview_turn(sess_id, "Implementation: Lock-free ring buffer and async IO.")
    assert t3["current_phase"] == "verification"

    # Verification -> Probing
    t4 = interview.interview_turn(sess_id, "Verification: TLA+ formal model verifying mutual exclusion.")
    assert t4["current_phase"] == "probing"

    # In no-hints mode at probing phase: turn triggers adversarial probing
    t5 = interview.interview_turn(sess_id, "We use consensus quorums.")
    assert "Adversarial follow-up" in t5["interviewer_message"]
    assert "network partition" in t5["interviewer_message"] or "concurrent writes" in t5["interviewer_message"]


def test_interview_transcripts_dual_persistence_and_finalization(test_env):
    """Verify dual transcript persistence in sessions/ and interviews/transcripts/ and finalization."""
    interview = test_env["interview"]
    state_mgr = test_env["state"]
    data_dir = test_env["data_dir"]

    res = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = res["session_id"]

    # Verify initial dual transcripts
    path_sess = data_dir / "sessions" / f"{sess_id}.json"
    path_trans = data_dir / "interviews" / "transcripts" / f"{sess_id}.json"
    assert path_sess.exists()
    assert path_trans.exists()
    assert json.loads(path_sess.read_text()) == json.loads(path_trans.read_text())

    # Add turns
    interview.interview_turn(sess_id, "Clarifying constraints.")
    interview.interview_turn(sess_id, "Architectural approach.")

    data_sess = json.loads(path_sess.read_text())
    data_trans = json.loads(path_trans.read_text())
    assert data_sess == data_trans
    assert len(data_sess["dialogue"]) == 5  # welcome + 2*(candidate + interviewer)

    # Finalize interview
    scorecard = interview.finalize_interview(sess_id)
    assert scorecard["session_id"] == sess_id
    assert scorecard["role_track"] == "faang_swe_l5_l6"
    assert scorecard["target_company"] == "Google"
    assert scorecard["bar_decision"] in [b.value for b in BarDecision]
    assert len(scorecard["rubric_scores"]) == 5

    # Verify scorecards persisted in both paths
    card_sess = data_dir / "sessions" / f"{sess_id}_scorecard.json"
    card_trans = data_dir / "interviews" / "scorecards" / f"{sess_id}_scorecard.json"
    assert card_sess.exists()
    assert card_trans.exists()
    assert json.loads(card_sess.read_text()) == json.loads(card_trans.read_text())

    # Idempotency check: calling finalize again returns identical scorecard
    scorecard_again = interview.finalize_interview(sess_id)
    assert scorecard_again == scorecard

    # Subsequent turn raises ValueError
    with pytest.raises(ValueError, match="already finalized"):
        interview.interview_turn(sess_id, "Turn after finalization")


# =============================================================================
# 3. Rubric Scorer & Resume Matcher
# =============================================================================

def test_rubric_scorer_weights_and_company_profiles(test_env):
    """Verify 5-dimension rubric weights and calibration across all 7 companies."""
    scorer = test_env["scorer"]
    state_mgr = test_env["state"]

    # Verify weights definition
    expected_weights = {
        "decomposition": 0.20,
        "execution": 0.25,
        "architecture": 0.25,
        "resilience": 0.15,
        "communication": 0.15,
    }
    assert scorer.DIMENSION_WEIGHTS == expected_weights
    assert sum(expected_weights.values()) == 1.00

    # Math test for RubricScores schema
    scores = RubricScores(
        decomposition=4.0,
        execution=5.0,
        architecture=4.0,
        resilience=3.0,
        communication=4.0,
    )
    # Expected: 4*0.2 + 5*0.25 + 4*0.25 + 3*0.15 + 4*0.15 = 0.8 + 1.25 + 1.0 + 0.45 + 0.6 = 4.10
    assert scores.weighted_average() == 4.10

    # Test all 7 companies calibration
    all_companies = ["OpenAI", "Google", "Anthropic", "Meta", "Databricks", "Netflix", "Apple"]
    for company in all_companies:
        assert company in scorer.COMPANY_PROFILES
        session_mock = {
            "session_id": f"sess-mock-{company}",
            "role_track": "faang_swe_l5_l6",
            "target_company": company,
            "topic": "algorithms",
            "hints_used": 0,
        }
        card = scorer.score_interview(session_mock)
        assert card["target_company"] == company
        assert company in card["feedback"]
        assert card["bar_decision"] in [b.value for b in BarDecision]
        assert card["overall_score"] >= 1.0

    # Verify hiring recommendation boundaries
    # hints_used = 0 -> hint_penalty = 0 -> execution = 4.0 -> overall = 4.5*0.2+4.0*0.25+4.5*0.25+4.0*0.15+5.0*0.15 = 4.38 -> Strong Hire
    sess_zero_hints = {
        "session_id": "sess-zh",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Google",
        "topic": "algorithms",
        "hints_used": 0,
    }
    card_zh = scorer.score_interview(sess_zero_hints)
    assert card_zh["overall_score"] >= 4.2
    assert card_zh["bar_decision"] == "Strong Hire"

    # hints_used = 4 -> hint_penalty = 1.0 -> execution = 3.0 -> overall = 4.5*0.2+3.0*0.25+4.5*0.25+4.0*0.15+5.0*0.15 = 4.125 -> 4.13 -> Hire (3.5 <= x < 4.2)
    sess_four_hints = {
        "session_id": "sess-4h",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Google",
        "topic": "algorithms",
        "hints_used": 4,
    }
    card_4h = scorer.score_interview(sess_four_hints)
    assert 3.5 <= card_4h["overall_score"] < 4.2
    assert card_4h["bar_decision"] == "Hire"


def test_resume_matcher_fit_score_matrix_and_loop(test_env):
    """Verify resume fit score in [0, 100], missing ratings default 1.0, 5-round loop."""
    matcher = test_env["matcher"]
    state_mgr = test_env["state"]
    data_dir = test_env["data_dir"]

    # 1. Test across all 4 role tracks and all 7 companies
    tracks = ["faang_swe_l5_l6", "faang_privacy_l6", "faang_security_l4_l6", "ai_lab_research_l4_l5"]
    companies = ["OpenAI", "Google", "Anthropic", "Meta", "Databricks", "Netflix", "Apple"]

    jd_text = "We are seeking a Staff Distributed Systems Engineer with expertise in algorithms, security, and consensus protocols."
    resume_text = "Experienced software engineer specializing in distributed systems, consensus algorithms, python, and privacy."

    for track in tracks:
        for company in companies:
            res = matcher.analyze_role_fit(
                job_description_text=jd_text,
                resume_text=resume_text,
                role_track=track,
                target_company=company,
            )
            assert 0.0 <= res["fit_score_percentage"] <= 100.0
            assert res["role_track"] == track
            assert res["target_company"] == company

            # Verify 5-round custom loop
            loop = res["custom_interview_loop"]
            assert len(loop) == 5
            assert loop[0]["type"] == "coding"
            assert loop[1]["type"] == "system_design"
            assert loop[2]["type"] == "domain_deep_dive"
            assert loop[3]["type"] == "architecture"
            assert loop[4]["type"] == "leadership"

            # Verify gap analysis persisted
            analysis_id = res["analysis_id"]
            saved_gap = state_mgr.get_gap_analysis(analysis_id)
            assert saved_gap is not None
            assert saved_gap["analysis_id"] == analysis_id

    # 2. Unassessed topic default behavior
    # Clear all ratings so all topics are unassessed
    state_mgr.set_subdomain_ratings({})
    res_unassessed = matcher.analyze_role_fit(
        job_description_text="Generic software engineer role.",
        resume_text="Junior developer.",
        role_track="faang_swe_l5_l6",
        target_company="Google",
    )
    for comp in res_unassessed["competencies_matched"]:
        assert comp["user_level"] == 1.0  # Unassessed baseline defaults to 1.0

    # 3. Boundary: Empty JD raises ValueError
    with pytest.raises(ValueError, match="cannot be empty"):
        matcher.analyze_role_fit(job_description_text="")
    with pytest.raises(ValueError, match="cannot be empty"):
        matcher.analyze_role_fit(job_description_text="   ")
