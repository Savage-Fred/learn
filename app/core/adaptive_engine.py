"""Adaptive exercise progression ladder and dynamic difficulty adjustment engine."""

import json
import os
import re
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
        short_tier = tier.short_name
        session_id = str(uuid.uuid4())
        exercise_id = f"ex-{topic_id.strip()}-{short_tier}-{uuid.uuid4().hex[:6]}"

        prompt, rubric = self.loader.load_exercise_content(topic_id.strip(), tier)

        payload = {
            "session_id": session_id,
            "exercise_id": exercise_id,
            "topic_id": topic_id.strip(),
            "difficulty_level": short_tier,
            "prompt": prompt,
            "rubric_criteria": rubric,
        }

        # Persist session state
        session_state = {
            "session_id": session_id,
            "topic_id": topic_id.strip(),
            "current_difficulty": tier.value,
            "history": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state_mgr.save_session(session_id, session_state)

        return payload

    def exercise_turn(self, session_id: str, exercise_id: str, user_response: str) -> Dict[str, Any]:
        """Process candidate solution, grade performance, update ratings, and advance ladder."""
        with self.state_mgr.session_lock(session_id):
            session_data = self.state_mgr.get_session(session_id)
            if not session_data:
                raise KeyError(f"Exercise session '{session_id}' not found.")

            topic_id = session_data.get("topic_id", "general")
            curr_tier = session_data.get("current_difficulty", "tier1_starter")

            # 1. Grade submission (Router LLM or Deterministic Fallback)
            score, passed, eval_feedback = self._evaluate_response(user_response, topic_id=topic_id, tier=curr_tier)

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
            self.state_mgr.update_subdomain_rating(topic_id, new_rating)

            # 3. Record turn in session history & log file
            turn_record = {
                "exercise_id": exercise_id,
                "topic": topic_id,
                "score": score,
                "passed": passed,
                "user_response": user_response[:250],
                "evaluation": eval_feedback,
                "feedback": eval_feedback,
                "new_rating": new_rating,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            session_data.setdefault("history", []).append(turn_record)
            session_data["current_difficulty"] = next_full_tier
            self.state_mgr.save_session(session_id, session_data)
            self.state_mgr.log_exercise_turn({"session_id": session_id, **turn_record})

            next_exercise = {
                "exercise_id": f"ex-{topic_id}-{next_level}-{uuid.uuid4().hex[:6]}",
                "prompt": f"Scaled problem at {next_level.upper()} level for {topic_id}.",
                "difficulty_level": next_level,
            }

            return {
                "session_id": session_id,
                "exercise_id": exercise_id,
                "score": score,
                "passed": passed,
                "evaluation": eval_feedback,
                "feedback": eval_feedback,
                "new_rating": new_rating,
                "next_difficulty_level": next_level,
                "next_tier": next_full_tier,
                "next_exercise": next_exercise,
            }

    def _evaluate_response(self, user_response: str, topic_id: str = "general", tier: str = "starter") -> Tuple[int, bool, str]:
        """Evaluate candidate response with router or deterministic fallback."""
        if not user_response or not user_response.strip():
            return 0, False, "Submission was empty. Please provide code or architectural reasoning."

        # Dynamic LLM routing when mock mode is disabled
        if not self.router.use_mock_llm and not settings.use_mock_llm:
            prompt = (
                f"You are a technical interview evaluator grading an adaptive exercise submission.\n"
                f"Topic: {topic_id}\n"
                f"Difficulty Tier: {tier}\n"
                f"Candidate Submission:\n{user_response}\n\n"
                f"Respond ONLY with JSON: {{\"score\": <1-5>, \"passed\": <true/false>, \"feedback\": \"<concise evaluation>\"}}"
            )
            try:
                res = self.router.route(prompt=prompt, workflow="adaptive_grading")
                text = res.get("text", "")
                m = re.search(r"(\{.*\})", text, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(1))
                    if "score" in parsed and "passed" in parsed:
                        return (
                            int(max(1, min(5, parsed["score"]))),
                            bool(parsed["passed"]),
                            str(parsed.get("feedback", "Evaluated via MultiModelRouter.")),
                        )
            except Exception:
                pass  # Fall back to deterministic grading

        resp_lower = user_response.lower()
        if any(neg in resp_lower for neg in ["unsure", "don't know", "dont know", "confused", "fail"]):
            return 1, False, "Candidate expressed uncertainty; missed core invariants."

        # High signal invariant patterns
        if any(term in resp_lower for term in ["invariant", "protocol", "lock", "async", "dp", "stride", "budget", "kahn", "raft"]):
            return 5, True, "Excellent solution: strictly preserves invariants, addresses concurrency, and adheres to rubrics."

        if len(user_response.strip()) >= 30:
            return 4, True, "Good solution: covers primary constraints with minor edge-case oversights."

        return 2, False, "Insufficient solution: misses core invariants and failure handling."


adaptive_engine = AdaptiveEngine()

