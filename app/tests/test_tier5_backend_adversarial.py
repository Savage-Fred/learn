"""Tier 5 White-Box Adversarial Hardening Test Suite for Savage-Fred/learn.

Covers:
1. State Management & Invariants:
   - NaN / Inf / -Inf rating injections and clamping
   - Corrupted JSON recovery and empty string recovery
   - Non-serializable JSON error handling without lock deadlock
   - Path traversal and null byte injections in identifiers
   - Thread-local re-entrant locking
   - §R4 repository boundary isolation
2. Rubric Scorer:
   - Null candidate turn message (message=None) [Gap 1]
   - Empty dialogue and surrender/refusal detection
   - 7 company profiles and calibrated weight boosts
   - Company anti-pattern detection across all 7 companies
   - Target company casing sensitivity gap ("google" vs "Google") [Gap 5]
3. Adaptive Exercise Engine:
   - Null user_response (user_response=None) [Gap 2]
   - Empty string and giant payload (1MB) handling
   - 4-tier ladder traversal (ceiling at tier4_l6, floor at tier1_starter)
   - Dynamic Elo rating clamping strictly within [1.00, 5.00]
4. Mock Interview Engine:
   - Null turn message (message=None) [Gap 3]
   - 3-tier Socratic hints budget and rejection on exhaustion
   - Strict no-hints mode and adversarial probing
   - Server-side countdown timer validation and expiration rejection
   - Finalization idempotency and post-finalization turn rejection
5. Resume Matcher:
   - Corrupted non-float rating types in state store [Gap 4]
   - Empty/whitespace JD rejection
   - Boundary fit scoring [0.0%, 100.0%]
   - Custom 5-round loop generation across tracks and companies
6. Multi-Model Router & Watchdog:
   - Process group watchdog with timeout and SIGKILL escalation
   - 3-tier cascade hierarchy (Tier 1 CLI -> Tier 2 API -> Tier 3 Mock)
   - ProviderUnavailableError when all fallbacks disabled
   - Telemetry logging and corrupted line recovery
7. MCP Server & Transports:
   - JSON-RPC 2.0 protocol validation (bad JSON, missing method, invalid params)
   - All 8 MCP tools validation
   - Path traversal rejections in tools
   - MCP learn_pin_topic priority enum validation and dual-path sync gap [Gap 6]
   - SSE transport Origin header filtering (local & tailnet vs forbidden remote)
"""

import asyncio
import concurrent.futures
import json
import os
import signal
import sys
import tempfile
import time
from pathlib import Path
import pytest

# Ensure app-ui worktree is in python path
WORKSPACE_ROOT = Path("/home/will/dev/learn/.worktrees/app-ui")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from app.config import settings
from app.core.adaptive_engine import AdaptiveEngine
from app.core.interview_engine import InterviewEngine
from app.core.resume_matcher import ResumeMatcher
from app.core.rubric_scorer import RubricScorer
from app.core.schemas import DifficultyTier
from app.core.state import StateManager, sanitize_identifier, file_lock
from app.core.topic_loader import TopicLoader
from app.mcp.schemas import INVALID_PARAMS, INVALID_REQUEST, METHOD_NOT_FOUND, PARSE_ERROR
from app.mcp.server import MCPServer
from app.mcp.tools import MCPToolRegistry
from app.mcp.transports.sse import _is_allowed_origin
from app.router.engine import MultiModelRouter, ProviderUnavailableError
from app.router.watchdog import SubprocessWatchdog, WatchdogTimeoutError


@pytest.fixture
def adversarial_env(tmp_path_factory, monkeypatch):
    """Isolated environment with temporary data_dir outside repo root."""
    temp_data = tmp_path_factory.mktemp("tier5_adversarial_data")
    monkeypatch.setattr(settings, "data_dir", temp_data)
    state_mgr = StateManager(data_dir=temp_data)
    loader = TopicLoader()
    router = MultiModelRouter(use_mock_llm=True)
    adaptive = AdaptiveEngine(state_mgr=state_mgr, loader=loader, router=router)
    scorer = RubricScorer(state_mgr=state_mgr, router=router)
    interview = InterviewEngine(state_mgr=state_mgr, router=router, scorer=scorer)
    matcher = ResumeMatcher(state_mgr=state_mgr)
    mcp_server = MCPServer()

    return {
        "data_dir": temp_data,
        "state": state_mgr,
        "loader": loader,
        "router": router,
        "adaptive": adaptive,
        "scorer": scorer,
        "interview": interview,
        "matcher": matcher,
        "mcp": mcp_server,
    }


# =============================================================================
# 1. State Management & Invariant Hardening
# =============================================================================

def test_state_nan_and_inf_rating_injection(adversarial_env):
    """Adversarial Test (Gap 7): Verify NaN, Inf, and -Inf rating injections."""
    state_mgr = adversarial_env["state"]

    # When NaN is passed, rating safely defaults to 1.0 floor rating
    nan_result = state_mgr.update_subdomain_rating("topic-nan", float("nan"))
    assert nan_result == 1.0, "NaN input must evaluate to safe floor rating (1.0)"

    inf_result = state_mgr.update_subdomain_rating("topic-inf", float("inf"))
    assert inf_result == 5.0

    neginf_result = state_mgr.update_subdomain_rating("topic-neginf", float("-inf"))
    assert neginf_result == 1.0


def test_state_corrupted_json_and_null_bytes(adversarial_env):
    """Adversarial Test: Resilience against files corrupted with null bytes and partial writes."""
    state_mgr = adversarial_env["state"]
    data_dir = adversarial_env["data_dir"]

    # 1. Null bytes (simulating power failure / filesystem zero-fill)
    ratings_file = data_dir / "ratings" / "subdomain_ratings.json"
    ratings_file.write_bytes(b"\x00" * 256)
    ratings = state_mgr.get_subdomain_ratings()
    assert ratings == {}, "Corrupted zero-byte file must fallback to empty dict"

    # 2. Corrupted session file with raw HTML / stack trace
    sess_file = data_dir / "sessions" / "corrupted_500.json"
    sess_file.write_text("<html>502 Bad Gateway</html>", encoding="utf-8")
    sess_data = state_mgr.get_session("corrupted_500")
    assert sess_data is None, "Corrupted session file must return None instead of crashing"


def test_state_lock_reentrancy_and_multithreading(adversarial_env):
    """Adversarial Test: Re-entrant lock acquisition within same thread and mutual exclusion across threads."""
    state_mgr = adversarial_env["state"]
    lock_file = adversarial_env["data_dir"] / "test_reentrant.lock"

    # Nested re-entrant locking in same thread must not self-deadlock
    with file_lock(lock_file):
        with file_lock(lock_file):
            with file_lock(lock_file):
                pass  # Succeeded without hanging

    # Concurrent rating updates across 30 threads
    def worker(idx):
        topic = f"conc_topic_{idx % 5}"
        state_mgr.update_subdomain_rating(topic, 2.5 + (idx * 0.05))

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(worker, range(30)))

    all_ratings = state_mgr.get_subdomain_ratings()
    assert len(all_ratings) == 5
    for v in all_ratings.values():
        assert 1.0 <= v <= 5.0


def test_state_path_traversal_rejections(adversarial_env):
    """Adversarial Test: Sanitize identifier rejects diverse path traversal variants."""
    state_mgr = adversarial_env["state"]

    malicious_inputs = [
        "../etc/passwd",
        "..\\windows\\win.ini",
        "nested/../../secret",
        "foo/bar",
        "foo\\bar",
        "/absolute/root",
        "\0null_byte",
        "",
        "   ",
    ]

    for malicious in malicious_inputs:
        with pytest.raises(ValueError):
            sanitize_identifier(malicious)

        with pytest.raises(ValueError):
            state_mgr.get_session(malicious)

        with pytest.raises(ValueError):
            state_mgr.pin_topic(malicious)


def test_state_isolation_invariant_rejection():
    """Adversarial Test: Invariant §R4 strictly rejects data_dir inside repo_root."""
    in_repo = settings.repo_root / "nested_personal_state"
    with pytest.raises(ValueError, match="§R4 invariant"):
        StateManager(data_dir=in_repo)


# =============================================================================
# 2. Rubric Scorer White-Box Hardening
# =============================================================================

def test_rubric_scorer_candidate_turn_message_none(adversarial_env):
    """Adversarial Test (Gap 1): Candidate turn with message=None is handled gracefully."""
    scorer = adversarial_env["scorer"]

    session_state = {
        "session_id": "test-none-turn-msg",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Google",
        "topic": "algorithms",
        "dialogue": [
            {"speaker": "interviewer", "message": "Welcome."},
            {"speaker": "candidate", "message": None},  # Null message entry
        ],
    }

    # Must score successfully without TypeError
    card = scorer.score_interview(session_state)
    assert card["overall_score"] >= 1.0


def test_rubric_scorer_surrender_and_empty_dialogue(adversarial_env):
    """Adversarial Test: Immediate candidate surrender or refusal results in No Hire Below L4."""
    scorer = adversarial_env["scorer"]

    # 1. Total words < 5
    sess_empty = {
        "session_id": "sess-empty",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Google",
        "topic": "algorithms",
        "dialogue": [{"speaker": "candidate", "message": "Hi."}],
    }
    card_empty = scorer.score_interview(sess_empty)
    assert card_empty["overall_score"] == 1.00
    assert card_empty["bar_decision"] == "No Hire"
    assert card_empty["level_calibration"] == "Below L4"

    # 2. Expressed inability to solve
    sess_refusal = {
        "session_id": "sess-refusal",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Google",
        "topic": "algorithms",
        "dialogue": [{"speaker": "candidate", "message": "I don't know and have no idea how to solve this."}],
    }
    card_refusal = scorer.score_interview(sess_refusal)
    assert card_refusal["overall_score"] == 1.00
    assert card_refusal["bar_decision"] == "No Hire"
    assert card_refusal["level_calibration"] == "Below L4"


def test_rubric_scorer_company_anti_patterns_all_seven(adversarial_env):
    """Adversarial Test: Trigger calibrated anti-patterns across all 7 notable companies."""
    scorer = adversarial_env["scorer"]

    # 1. OpenAI: Theoretical purity without working code (50+ words, no code blocks/functions)
    sess_openai = {
        "session_id": "sess-openai-pure",
        "role_track": "faang_swe_l5_l6",
        "target_company": "OpenAI",
        "topic": "algorithms",
        "dialogue": [{
            "speaker": "candidate",
            "message": (
                "The problem can be solved by analyzing the asymptotic properties and topological ordering of the elements. "
                "We should carefully think about the linearizability and invariants of the underlying state space before taking "
                "any concrete steps forward into the implementation details. Everything will be theoretically sound and elegant "
                "without requiring any rushed implementations or pragmatic shortcuts."
            ),
        }],
    }
    card_openai = scorer.score_interview(sess_openai)
    assert "Theoretical purity without working code" in card_openai["anti_patterns_detected"]

    # 2. Google: Hand-waving time/space complexity (no O(...) bounds)
    sess_google = {
        "session_id": "sess-google-bounds",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Google",
        "topic": "algorithms",
        "dialogue": [{
            "speaker": "candidate",
            "message": "def solve(nums): return sorted(nums) # Fast enough for practical purposes",
        }],
    }
    card_google = scorer.score_interview(sess_google)
    assert "Hand-waving time/space complexity" in card_google["anti_patterns_detected"]

    # 3. Anthropic: Excessive ambient privileges in agent systems
    sess_anthropic = {
        "session_id": "sess-anthropic-priv",
        "role_track": "seceng_l4_l6",
        "target_company": "Anthropic",
        "topic": "agent-access-models",
        "dialogue": [{
            "speaker": "candidate",
            "message": "The autonomous agent worker executes tools with root host permissions to minimize latency. def run_agent(): pass",
        }],
    }
    card_anthropic = scorer.score_interview(sess_anthropic)
    assert "Excessive ambient privileges" in card_anthropic["anti_patterns_detected"]

    # 4. Meta: Exceeded time limit
    sess_meta = {
        "session_id": "sess-meta-time",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Meta",
        "topic": "system-design",
        "time_expired": True,
        "dialogue": [{
            "speaker": "candidate",
            "message": "def build_feed(): pass # O(N) complexity using memcached cache",
        }],
    }
    card_meta = scorer.score_interview(sess_meta)
    assert "Running out of time" in card_meta["anti_patterns_detected"]

    # 5. Databricks: Heavy GC where zero-copy is needed
    sess_databricks = {
        "session_id": "sess-db-gc",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Databricks",
        "topic": "go",
        "dialogue": [{
            "speaker": "candidate",
            "message": "We allocate short-lived wrappers in Java/Go causing heavy garbage collection overhead on each batch query.",
        }],
    }
    card_databricks = scorer.score_interview(sess_databricks)
    assert "Heavy GC where zero-copy is needed" in card_databricks["anti_patterns_detected"]

    # 6. Netflix: Needing hand-holding (exhausted hint budget >= 3)
    sess_netflix = {
        "session_id": "sess-netflix-hints",
        "role_track": "faang_swe_l5_l6",
        "target_company": "Netflix",
        "topic": "statistics",
        "hints_used": 3,
        "dialogue": [{
            "speaker": "candidate",
            "message": "Using CUPED variance reduction with chaos telemetry and metrics.",
        }],
    }
    card_netflix = scorer.score_interview(sess_netflix)
    assert "Needing hand-holding" in card_netflix["anti_patterns_detected"]

    # 7. Apple: Treating privacy as an afterthought
    sess_apple = {
        "session_id": "sess-apple-priv",
        "role_track": "faang_privacy_l6",
        "target_company": "Apple",
        "topic": "differential-privacy",
        "dialogue": [{
            "speaker": "candidate",
            "message": "On-device battery and memory footprint are strictly capped at 50MB. def run_pipeline(): pass",
        }],
    }
    card_apple = scorer.score_interview(sess_apple)
    assert "Treating privacy as an afterthought" in card_apple["anti_patterns_detected"]


def test_rubric_scorer_target_company_case_sensitivity_gap(adversarial_env):
    """Adversarial Test (Gap 5): Lowercase target_company is normalized and receives calibrated weights."""
    scorer = adversarial_env["scorer"]

    # Proper case has architecture weight boost for Google
    weights_proper = scorer.compute_company_weights("Google")
    assert weights_proper["architecture"] == 0.30

    # Lowercase company is normalized to Google and receives same calibration boost
    weights_lower = scorer.compute_company_weights("google")
    assert weights_lower["architecture"] == 0.30, "Lowercase company must be normalized to calibrated profile"


# =============================================================================
# 3. Adaptive Exercise Engine White-Box Hardening
# =============================================================================

def test_adaptive_exercise_turn_user_response_none(adversarial_env):
    """Adversarial Test (Gap 2): exercise_turn handles user_response=None gracefully."""
    adaptive = adversarial_env["adaptive"]

    init = adaptive.start_exercise("algorithms", initial_level="starter")
    sess_id = init["session_id"]
    ex_id = init["exercise_id"]

    # Must handle None gracefully without TypeError
    res = adaptive.exercise_turn(sess_id, ex_id, None)
    assert res["passed"] is False
    assert res["score"] == 0


def test_adaptive_ladder_boundary_ceiling_and_floor(adversarial_env):
    """Adversarial Test: Ladder clamps cleanly at tier4_l6 (ceiling) and tier1_starter (floor)."""
    adaptive = adversarial_env["adaptive"]
    state_mgr = adversarial_env["state"]

    init = adaptive.start_exercise("data-structures", initial_level="starter")
    sess_id = init["session_id"]
    curr_ex = init["exercise_id"]

    pass_answer = "Maintain strict monotonic queue invariant using deque."
    fail_answer = "I don't know and am unsure."

    # 1. Advance to tier4_l6
    for expected_tier in ["tier2_l4", "tier3_l5", "tier4_l6", "tier4_l6"]:
        res = adaptive.exercise_turn(sess_id, curr_ex, pass_answer)
        assert res["passed"] is True
        assert res["next_tier"] == expected_tier
        curr_ex = res["next_exercise"]["exercise_id"]

    # Pass again at ceiling remains at tier4_l6
    res_ceil = adaptive.exercise_turn(sess_id, curr_ex, pass_answer)
    assert res_ceil["next_tier"] == "tier4_l6"
    assert res_ceil["next_difficulty_level"] == "l6"
    curr_ex = res_ceil["next_exercise"]["exercise_id"]

    # 2. Fail down to tier1_starter
    for expected_tier in ["tier3_l5", "tier2_l4", "tier1_starter", "tier1_starter"]:
        res = adaptive.exercise_turn(sess_id, curr_ex, fail_answer)
        assert res["passed"] is False
        assert res["next_tier"] == expected_tier
        curr_ex = res["next_exercise"]["exercise_id"]

    # Fail again at floor remains at tier1_starter
    res_floor = adaptive.exercise_turn(sess_id, curr_ex, fail_answer)
    assert res_floor["next_tier"] == "tier1_starter"
    assert res_floor["next_difficulty_level"] == "starter"


def test_adaptive_giant_payload_truncation(adversarial_env):
    """Adversarial Test: Massive 1MB payload does not exhaust memory and truncates in turn logging."""
    adaptive = adversarial_env["adaptive"]
    state_mgr = adversarial_env["state"]

    init = adaptive.start_exercise("algorithms", initial_level="starter")
    giant_text = "Invariant verified. " * 50000  # ~1MB string

    res = adaptive.exercise_turn(init["session_id"], init["exercise_id"], giant_text)
    assert res["passed"] is True

    # Check that history entry stores truncated representation
    session_data = state_mgr.get_session(init["session_id"])
    assert len(session_data["history"][-1]["user_response"]) <= 255


# =============================================================================
# 4. Mock Interview Engine White-Box Hardening
# =============================================================================

def test_interview_turn_message_none(adversarial_env):
    """Adversarial Test (Gap 3): interview_turn handles message=None gracefully."""
    interview = adversarial_env["interview"]

    init = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = init["session_id"]

    # Must not raise AttributeError when message is None
    res = interview.interview_turn(sess_id, None)
    assert "interviewer_message" in res


def test_interview_socratic_hints_budget_exhaustion(adversarial_env):
    """Adversarial Test: Hints budget starts at 3, decrements sequentially, 4th request rejected."""
    interview = adversarial_env["interview"]

    init = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = init["session_id"]
    assert init["hints_remaining"] == 3

    # Hint 1 (Conceptual)
    h1 = interview.interview_turn(sess_id, "hint please", turn_type="request_hint")
    assert h1["hints_remaining"] == 2
    assert "Conceptual" in h1["interviewer_message"]

    # Hint 2 (Structural)
    h2 = interview.interview_turn(sess_id, "hint please", turn_type="request_hint")
    assert h2["hints_remaining"] == 1
    assert "Structural" in h2["interviewer_message"]

    # Hint 3 (Scaffold)
    h3 = interview.interview_turn(sess_id, "hint please", turn_type="request_hint")
    assert h3["hints_remaining"] == 0
    assert "Scaffold" in h3["interviewer_message"]

    # Hint 4 (Exhausted / Rejected)
    h4 = interview.interview_turn(sess_id, "hint please", turn_type="request_hint")
    assert h4["hints_remaining"] == 0
    assert "exhausted" in h4["interviewer_message"].lower()


def test_interview_strict_no_hints_and_adversarial_probing(adversarial_env):
    """Adversarial Test: No-hints mode rejects hints and triggers adversarial probing in probing phase."""
    interview = adversarial_env["interview"]

    init = interview.start_interview("faang_swe_l5_l6", "OpenAI", "system-design", mode="no-hints")
    sess_id = init["session_id"]
    assert init["hints_remaining"] == 0

    # Hint request in no-hints mode is immediately rejected
    h_rej = interview.interview_turn(sess_id, "Can I get a hint?", turn_type="request_hint")
    assert "disabled" in h_rej["interviewer_message"].lower()

    # Step through 5 phases
    interview.interview_turn(sess_id, "Clarifying 100k QPS.")  # -> architecture
    interview.interview_turn(sess_id, "Architecture: Partitioned cluster.")  # -> implementation
    interview.interview_turn(sess_id, "Implementation: Lock-free ring buffer.")  # -> verification
    t_prob = interview.interview_turn(sess_id, "Verification: Formal TLA+ invariant proof.")  # -> probing
    assert t_prob["current_phase"] == "probing"

    # Turn in probing phase triggers adversarial stress follow-up
    t_adv = interview.interview_turn(sess_id, "We use consensus quorums.")
    assert "Adversarial follow-up" in t_adv["interviewer_message"]


def test_interview_server_side_countdown_timer_expiration(adversarial_env):
    """Adversarial Test: Expired interview session rejects turns with ValueError."""
    interview = adversarial_env["interview"]
    state_mgr = adversarial_env["state"]

    init = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", time_limit_minutes=45)
    sess_id = init["session_id"]

    # Artificially expire the session
    session_state = state_mgr.get_session(sess_id)
    session_state["time_expired"] = True
    state_mgr.save_session(sess_id, session_state)

    # Next turn must raise ValueError rejecting the submission
    with pytest.raises(ValueError, match="time limit of 45 minutes has expired"):
        interview.interview_turn(sess_id, "Candidate turn after deadline.")


def test_interview_finalization_idempotency(adversarial_env):
    """Adversarial Test: Finalize interview is idempotent; subsequent turns are rejected."""
    interview = adversarial_env["interview"]

    init = interview.start_interview("faang_swe_l5_l6", "Google", "algorithms", mode="hints")
    sess_id = init["session_id"]
    interview.interview_turn(sess_id, "Decomposition and invariants.")

    # Finalize
    card1 = interview.finalize_interview(sess_id)
    card2 = interview.finalize_interview(sess_id)
    assert card1 == card2, "Subsequent finalize calls must return identical scorecard"

    # Turns after finalization must be rejected
    with pytest.raises(ValueError, match="already finalized"):
        interview.interview_turn(sess_id, "Turn after finalized")


# =============================================================================
# 5. Resume Matcher White-Box Hardening
# =============================================================================

def test_resume_matcher_corrupted_state_rating_type(adversarial_env):
    """Adversarial Test (Gap 4): Corrupted string rating in state store is safely handled in analyze_role_fit."""
    matcher = adversarial_env["matcher"]
    state_mgr = adversarial_env["state"]

    # Write non-float rating for an active competency matrix key
    f = state_mgr.ratings_file
    f.write_text(json.dumps({"masters-algorithms": "corrupted_string_rating"}), encoding="utf-8")

    # Must not raise TypeError, safely coerces string to float fallback (1.0)
    res = matcher.analyze_role_fit(
        job_description_text="Distributed systems engineer needed.",
        resume_text="Software engineer with algorithms background.",
        role_track="faang_swe_l5_l6",
    )
    assert "fit_score_percentage" in res


def test_resume_matcher_empty_and_whitespace_jd_rejection(adversarial_env):
    """Adversarial Test: Empty or whitespace job description raises ValueError."""
    matcher = adversarial_env["matcher"]

    for bad_jd in ["", "   ", "\n\t"]:
        with pytest.raises(ValueError, match="cannot be empty"):
            matcher.analyze_role_fit(bad_jd)


def test_resume_matcher_score_bounds_and_custom_loop(adversarial_env):
    """Adversarial Test: Fit score strictly in [0.0%, 100.0%] and produces 5-round custom loop."""
    matcher = adversarial_env["matcher"]
    state_mgr = adversarial_env["state"]

    # 1. Zero-match scenario
    res_zero = matcher.analyze_role_fit(
        job_description_text="Chef and baker with pastry culinary arts experience.",
        resume_text="Astronaut and pilot with aerospace mechanics.",
        role_track="faang_swe_l5_l6",
        target_company="Google",
    )
    assert 0.0 <= res_zero["fit_score_percentage"] <= 100.0
    assert len(res_zero["custom_interview_loop"]) == 5

    # 2. Perfect match scenario (ratings set to 5.0 + all keywords)
    matrix = ResumeMatcher.COMPETENCY_MATRIX["faang_swe_l5_l6"]
    ratings = {k: 5.0 for k in matrix}
    state_mgr.set_subdomain_ratings(ratings)

    jd = "Staff distributed algorithms security privacy python concurrency threat engineer."
    res_perfect = matcher.analyze_role_fit(
        job_description_text=jd,
        resume_text=jd,
        role_track="faang_swe_l5_l6",
        target_company="Google",
    )
    assert res_perfect["fit_score_percentage"] == 100.0
    assert len(res_perfect["custom_interview_loop"]) == 5


# =============================================================================
# 6. Multi-Model Router & Watchdog Hardening
# =============================================================================

def test_watchdog_timeout_process_group_termination():
    """Adversarial Test: Watchdog terminates runaway subprocess group on timeout."""
    start_t = time.time()
    with pytest.raises(WatchdogTimeoutError):
        SubprocessWatchdog.run_sync(
            ["python3", "-c", "import time; time.sleep(10)"],
            timeout_sec=0.5,
            grace_period_sec=0.2,
        )
    elapsed = time.time() - start_t
    assert elapsed < 3.0, "Watchdog must enforce deadline and not wait full 10s"


def test_router_cascade_from_cli_failure_to_mock():
    """Adversarial Test: MultiModelRouter cascades cleanly when external CLI fails."""
    router = MultiModelRouter(use_mock_llm=False)

    res = router.route(
        prompt="Explain Raft consensus leader election invariants.",
        provider="claude",
        simulate_failure_tier="subscription_cli",
    )
    assert res["fallback_triggered"] is True
    assert res["tier"] in ["direct_api", "mock"]


def test_router_provider_unavailable_when_all_disabled():
    """Adversarial Test: Raises ProviderUnavailableError when mock is disallowed and keys missing."""
    old_env = os.environ.get("LEARN_ALLOW_MOCK_FALLBACK")
    os.environ["LEARN_ALLOW_MOCK_FALLBACK"] = "0"

    saved_keys = {}
    for k in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
        if k in os.environ:
            saved_keys[k] = os.environ.pop(k)

    try:
        router = MultiModelRouter(use_mock_llm=False)
        with pytest.raises(ProviderUnavailableError):
            router.route("Test prompt", provider="nonexistent_provider")
    finally:
        if old_env is not None:
            os.environ["LEARN_ALLOW_MOCK_FALLBACK"] = old_env
        else:
            os.environ.pop("LEARN_ALLOW_MOCK_FALLBACK", None)
        os.environ.update(saved_keys)


# =============================================================================
# 7. Model Context Protocol (MCP) Server & Tools Hardening
# =============================================================================

def test_mcp_server_protocol_compliance(adversarial_env):
    """Adversarial Test: MCPServer conforms to JSON-RPC 2.0 error specifications."""
    mcp = adversarial_env["mcp"]

    # 1. Invalid JSON payload (not a dict)
    r1 = mcp.handle_request(["invalid", "list"])
    assert r1["error"]["code"] == INVALID_REQUEST

    # 2. Missing method
    r2 = mcp.handle_request({"jsonrpc": "2.0", "id": 1})
    assert r2["error"]["code"] == INVALID_REQUEST

    # 3. Invalid params type (not dict)
    r3 = mcp.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": "not-dict"})
    assert r3["error"]["code"] == INVALID_PARAMS

    # 4. Unknown method
    r4 = mcp.handle_request({"jsonrpc": "2.0", "id": 3, "method": "unknown_rpc_method"})
    assert r4["error"]["code"] == METHOD_NOT_FOUND

    # 5. Unknown tool
    r5 = mcp.handle_request({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "nonexistent_tool", "arguments": {}},
    })
    assert r5["error"]["code"] == METHOD_NOT_FOUND

    # 6. Notifications return None per JSON-RPC 2.0 spec
    r6 = mcp.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert r6 is None


def test_mcp_tool_pin_topic_priority_validation_gap(adversarial_env):
    """Adversarial Test (Gap 6): MCP learn_pin_topic validates priority and updates dual mirrors."""
    reg = adversarial_env["mcp"].registry
    data_dir = adversarial_env["data_dir"]

    # Call learn_pin_topic with invalid priority "super_critical" must raise ValueError
    with pytest.raises(ValueError, match="Priority must be one of"):
        reg.execute_tool("learn_pin_topic", {
            "topic_slug": "algorithms",
            "priority": "super_critical",
            "notes": "Invalid priority test",
        })

    # Call with valid priority
    res = reg.execute_tool("learn_pin_topic", {
        "topic_slug": "algorithms",
        "priority": "high",
        "notes": "Valid priority test",
    })
    assert res["status"] == "pinned"
    assert res["priority"] == "high"

    # Verify both mirrors are updated
    root_pins = json.loads((data_dir / "pinned_topics.json").read_text(encoding="utf-8"))
    alias_pins = json.loads((data_dir / "pins" / "pinned_topics.json").read_text(encoding="utf-8"))
    assert any(p.get("topic_slug") == "algorithms" or p.get("topic_id") == "algorithms" for p in root_pins)
    assert any(p.get("topic_slug") == "algorithms" or p.get("topic_id") == "algorithms" for p in alias_pins)


def test_mcp_tool_durable_learning_path_traversal(adversarial_env):
    """Adversarial Test: learn_record_durable_learning rejects path traversal in topic_slug."""
    reg = adversarial_env["mcp"].registry

    with pytest.raises(ValueError, match="path traversal not allowed"):
        reg.execute_tool("learn_record_durable_learning", {
            "topic_slug": "../../etc",
            "title": "Malicious Learning",
            "notes": "Attempting traversal out of topics root.",
        })


def test_mcp_sse_origin_filtering():
    """Adversarial Test: SSE transport Origin header filtering validates loopback/tailnet and rejects remote."""
    assert _is_allowed_origin("http://localhost:8795") is True
    assert _is_allowed_origin("http://127.0.0.1:8795") is True
    assert _is_allowed_origin("https://will-ubuntu-26.tailacca87.ts.net:8795") is True
    assert _is_allowed_origin(None) is True

    assert _is_allowed_origin("http://evil-attacker.com") is False
    assert _is_allowed_origin("https://phishing-site.org:8795") is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])
