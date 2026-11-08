"""Adaptive exercise progression ladder and dynamic difficulty adjustment engine."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.core.schemas import DifficultyTier
from app.core.state import state, StateManager
from app.core.topic_loader import topic_loader, TopicLoader
from app.router import MultiModelRouter


DEFAULT_BASELINE_RATING = 1.0


class GradingUnavailableError(RuntimeError):
    """Live grading failed or was malformed; ratings and session state are unchanged."""


class StaleExerciseError(ValueError):
    """The submitted exercise is not the session's current one (already graded or foreign)."""


class AdaptiveEngine:
    """Manages adaptive quiz sessions, difficulty scaling, and subdomain ratings."""

    LADDER_TIERS = ["starter", "l4", "l5", "l6"]
    FULL_LADDER = ["tier1_starter", "tier2_l4", "tier3_l5", "tier4_l6"]

    def __init__(
        self,
        state_mgr: Optional[StateManager] = None,
        loader: Optional[TopicLoader] = None,
        router: Optional[MultiModelRouter] = None,
        default_rating: float = DEFAULT_BASELINE_RATING,
    ):
        self.state_mgr = state_mgr or state
        self.loader = loader or topic_loader
        self.router = router or MultiModelRouter()
        self.default_rating = default_rating

    def get_user_ratings(self) -> Dict[str, float]:
        """Fetch active user ratings."""
        return self.state_mgr.get_subdomain_ratings()

    def save_user_ratings(self, ratings: Dict[str, float]) -> None:
        """Persist subdomain ratings."""
        self.state_mgr.set_subdomain_ratings(ratings)

    def start_exercise(self, topic_id: str, initial_level: str = "starter") -> Dict[str, Any]:
        """Start a new adaptive exercise session."""
        if not topic_id or not topic_id.strip():
            raise ValueError("Topic ID cannot be empty.")

        tier = DifficultyTier.from_str(initial_level)
        topic_id = topic_id.strip()
        session_id = str(uuid.uuid4())
        exercise = self._load_exercise(topic_id, tier)

        # The session owns the current problem and rubric so every turn grades against it.
        session_state = {
            "session_id": session_id,
            "topic_id": topic_id,
            "current_difficulty": tier.value,
            "current_exercise": exercise,
            "history": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state_mgr.save_session(session_id, session_state)

        return {"session_id": session_id, "topic_id": topic_id, **exercise}

    def _load_exercise(self, topic_id: str, tier: DifficultyTier) -> Dict[str, Any]:
        """Load the curriculum problem and rubric for one ladder tier."""
        prompt, rubric = self.loader.load_exercise_content(topic_id, tier)
        return {
            "exercise_id": f"ex-{topic_id}-{tier.short_name}-{uuid.uuid4().hex[:6]}",
            "difficulty_level": tier.short_name,
            "prompt": prompt,
            "rubric_criteria": rubric,
        }

    def exercise_turn(self, session_id: str, exercise_id: str, user_response: str) -> Dict[str, Any]:
        """Process candidate solution, grade performance, update ratings, and advance ladder."""
        with self.state_mgr.session_lock(session_id):
            session_data = self.state_mgr.get_session(session_id)
            if not session_data:
                raise KeyError(f"Exercise session '{session_id}' not found.")

            topic_id = session_data.get("topic_id", "general")
            curr_tier = session_data.get("current_difficulty", "tier1_starter")
            # Sessions saved before the problem was persisted reload it from their tier.
            stored = session_data.get("current_exercise")
            if stored and exercise_id != stored["exercise_id"]:
                raise StaleExerciseError(
                    f"Exercise '{exercise_id}' is not this session's current exercise "
                    f"'{stored['exercise_id']}'; it may already have been graded."
                )
            current = stored or self._load_exercise(topic_id, DifficultyTier.from_str(curr_tier))

            # 1. Grade against the session's problem; raises before any state changes.
            score, passed, eval_feedback, source = self._evaluate_response(
                user_response,
                topic_id=topic_id,
                tier=curr_tier,
                problem=current["prompt"],
                rubric=current["rubric_criteria"],
            )

            # 2. Fetch and update ratings
            ratings = self.get_user_ratings()
            current_rating = ratings.get(topic_id, self.default_rating)

            # Determine ladder stepping based on current tier
            curr_idx = 0
            for i, t in enumerate(self.FULL_LADDER):
                if t == curr_tier or self.LADDER_TIERS[i] in curr_tier:
                    curr_idx = i
                    break

            if passed:
                new_rating = round(min(5.0, current_rating + 0.35), 2)
                next_idx = min(len(self.LADDER_TIERS) - 1, curr_idx + 1)
            else:
                new_rating = round(max(1.0, current_rating - 0.25), 2)
                next_idx = max(0, curr_idx - 1)

            next_level = self.LADDER_TIERS[next_idx]
            next_full_tier = self.FULL_LADDER[next_idx]
            next_exercise = self._load_exercise(topic_id, DifficultyTier(next_full_tier))
            self.state_mgr.update_subdomain_rating(topic_id, new_rating)

            # 3. Record turn in session history & log file
            turn_record = {
                "exercise_id": exercise_id,
                "graded_exercise_id": current["exercise_id"],
                "topic": topic_id,
                "score": score,
                "passed": passed,
                "assessment_source": source,
                "user_response": (user_response or "")[:250],
                "evaluation": eval_feedback,
                "feedback": eval_feedback,
                "new_rating": new_rating,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            session_data.setdefault("history", []).append(turn_record)
            session_data["current_difficulty"] = next_full_tier
            session_data["current_exercise"] = next_exercise
            self.state_mgr.save_session(session_id, session_data)
            self.state_mgr.log_exercise_turn({"session_id": session_id, **turn_record})

            return {
                "session_id": session_id,
                "exercise_id": exercise_id,
                "score": score,
                "passed": passed,
                "assessment_source": source,
                "evaluation": eval_feedback,
                "feedback": eval_feedback,
                "new_rating": new_rating,
                "next_difficulty_level": next_level,
                "next_tier": next_full_tier,
                "next_exercise": next_exercise,
            }

    def _evaluate_response(
        self,
        user_response: str,
        topic_id: str = "general",
        tier: str = "starter",
        problem: str = "",
        rubric: Optional[List[str]] = None,
    ) -> Tuple[int, bool, str, str]:
        """Grade a submission; returns (score, passed, feedback, assessment_source).

        Deterministic heuristics run only in explicit mock mode. In live mode a provider
        failure, the router's mock fallback, or malformed output raises
        GradingUnavailableError so no heuristic grade can change a real user's rating.
        """
        if not user_response or not user_response.strip():
            return 0, False, "Submission was empty. Please provide code or architectural reasoning.", "validation"

        if self.router.use_mock_llm or settings.use_mock_llm:
            return (*self._deterministic_grade(user_response), "deterministic_mock")

        rubric_text = "\n".join(f"- {c}" for c in (rubric or []))
        prompt = (
            f"You are a technical interview evaluator grading an adaptive exercise submission.\n"
            f"Topic: {topic_id}\n"
            f"Difficulty Tier: {tier}\n"
            f"Problem:\n{problem}\n\n"
            f"Rubric:\n{rubric_text}\n\n"
            f"Candidate Submission:\n{user_response}\n\n"
            f"Respond ONLY with JSON: {{\"score\": <1-5>, \"passed\": <true/false>, \"feedback\": \"<concise evaluation>\"}}"
        )
        try:
            res = self.router.route(prompt=prompt, workflow="adaptive_grading")
        except Exception as e:
            raise GradingUnavailableError(f"Grading provider failed; no grade was recorded: {e}") from e
        if res.get("provider") == "mock" or res.get("tier") == "mock":
            raise GradingUnavailableError(
                "No live grading provider responded; refusing to record a mock grade."
            )
        try:
            text = res.get("text") or ""
            # raw_decode stops at the end of the first object, so trailing prose with braces is fine.
            parsed, _ = json.JSONDecoder().raw_decode(text[text.index("{"):])
            score, passed = parsed["score"], parsed["passed"]
            valid = (
                isinstance(passed, bool)
                and isinstance(score, (int, float))
                and not isinstance(score, bool)
                and 1 <= score <= 5
            )
        except (AttributeError, ValueError, TypeError, KeyError):
            valid = False
        if not valid:
            raise GradingUnavailableError("Grader returned malformed output; no grade was recorded.")
        return int(round(score)), passed, str(parsed.get("feedback") or "Evaluated via MultiModelRouter."), "model"

    @staticmethod
    def _deterministic_grade(user_response: str) -> Tuple[int, bool, str]:
        """Keyword/length heuristics for explicit mock mode and automated tests only."""
        clean = user_response.strip()
        resp_lower = clean.lower()
        if any(neg in resp_lower for neg in ["unsure", "don't know", "dont know", "no idea", "confused", "fail"]):
            return 1, False, "Candidate expressed uncertainty; missed core invariants."

        if len(clean) >= 20 and len(set(resp_lower)) <= 4:
            return 1, False, "Submission is repetitive and carries no reasoning to grade."

        # High signal invariant patterns
        if any(term in resp_lower for term in ["invariant", "protocol", "lock", "async", "dp", "stride", "budget", "kahn", "raft"]):
            return 5, True, "Excellent solution: strictly preserves invariants, addresses concurrency, and adheres to rubrics."

        if len(clean) >= 30:
            return 4, True, "Good solution: covers primary constraints with minor edge-case oversights."

        return 2, False, "Insufficient solution: misses core invariants and failure handling."


adaptive_engine = AdaptiveEngine()

