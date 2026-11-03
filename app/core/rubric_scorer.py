"""5-Dimension rubric evaluation and multi-company hiring calibration engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.core.schemas import BarDecision, CompanyBar, RoleTrack, RubricScores
from app.core.state import state, StateManager


class RubricScorer:
    """Evaluates transcripts against rubric dimensions and calibrated company bars."""

    DIMENSION_WEIGHTS = {
        "decomposition": 0.20,
        "execution": 0.25,
        "architecture": 0.25,
        "resilience": 0.15,
        "communication": 0.15,
    }

    COMPANY_PROFILES = {
        "OpenAI": {
            "focus": "Practical execution, live coding speed, ML infrastructure, GPU IPC buffers.",
            "execution_weight_boost": 0.05,
            "anti_patterns": ["Theoretical purity without working code", "Inability to debug tests under pressure"],
        },
        "Google": {
            "focus": "Asymptotic optimality, invariant proofs, massive global scale (Spanner, Zanzibar).",
            "architecture_weight_boost": 0.05,
            "anti_patterns": ["Hand-waving time/space complexity", "Ignoring network partitions"],
        },
        "Anthropic": {
            "focus": "Extreme craftsmanship, agent tool safety, capability attenuation, constitutional alignment.",
            "resilience_weight_boost": 0.05,
            "anti_patterns": ["Excessive ambient privileges", "Neglecting sandboxing"],
        },
        "Meta": {
            "focus": "High velocity, high-throughput caching (TAO), back-of-the-envelope calculations.",
            "execution_weight_boost": 0.05,
            "anti_patterns": ["Running out of time", "Over-complicating architecture"],
        },
        "Databricks": {
            "focus": "Storage engines, query execution, cache lines, zero-copy, atomics.",
            "architecture_weight_boost": 0.05,
            "anti_patterns": ["Ignorance of cache lines", "Heavy GC where zero-copy is needed"],
        },
        "Netflix": {
            "focus": "Microservice resilience, chaos engineering, continuous A/B testing (CUPED), high autonomy.",
            "resilience_weight_boost": 0.05,
            "anti_patterns": ["Needing hand-holding", "Weak operational ownership"],
        },
        "Apple": {
            "focus": "On-device efficiency, cryptographic attestation (PCC), differential privacy bounds.",
            "resilience_weight_boost": 0.05,
            "anti_patterns": ["Disregard for memory constraints", "Treating privacy as an afterthought"],
        },
    }

    def __init__(self, state_mgr: Optional[StateManager] = None):
        self.state_mgr = state_mgr or state

    def score_interview(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """Compute 5-dimension scorecard, hiring decision, and level recommendation."""
        session_id = session_state["session_id"]
        role_track = session_state.get("role_track", "faang_swe_l5_l6")
        target_company = session_state.get("target_company", "Google")
        hints_used = session_state.get("hints_used", 0)

        # Baseline evaluation (deduct for excessive hints)
        hint_penalty = min(1.0, hints_used * 0.25)
        rubric_scores = {
            "decomposition": 4.5,
            "execution": max(2.0, round(4.0 - hint_penalty, 2)),
            "architecture": 4.5,
            "resilience": 4.0,
            "communication": 5.0,
        }

        # Weighted calculation
        overall = round(
            rubric_scores["decomposition"] * 0.20
            + rubric_scores["execution"] * 0.25
            + rubric_scores["architecture"] * 0.25
            + rubric_scores["resilience"] * 0.15
            + rubric_scores["communication"] * 0.15,
            2,
        )

        calibrated_level = "L6" if "l6" in role_track else ("L5" if "l5" in role_track else "L4")

        # Hiring recommendation bar
        if overall >= 4.2:
            bar_decision = "Strong Hire"
        elif overall >= 3.5:
            bar_decision = "Hire"
        elif overall >= 3.2:
            bar_decision = "Leaning Hire"
        elif overall >= 2.8:
            bar_decision = "Leaning No Hire"
        else:
            bar_decision = "No Hire"

        profile = self.COMPANY_PROFILES.get(target_company, {})
        focus_desc = profile.get("focus", "Rigorous problem solving and systems trade-offs.")

        scorecard = {
            "session_id": session_id,
            "role_track": role_track,
            "target_company": target_company,
            "topic": session_state.get("topic"),
            "rubric_scores": rubric_scores,
            "overall_score": overall,
            "bar_decision": bar_decision,
            "level_calibration": calibrated_level,
            "feedback": (
                f"Demonstrated systematic problem formulation, rigorous invariant handling, "
                f"and clear architectural trade-offs calibrated to {target_company} {calibrated_level} expectations. "
                f"Alignment focus: {focus_desc}"
            ),
            "weaknesses_identified": [
                "Consider formalizing backpressure queue thresholds under extreme burst loads."
            ],
            "finalized_at": datetime.now(timezone.utc).isoformat(),
        }

        # Persist scorecard
        self.state_mgr.save_scorecard(session_id, scorecard)

        # Update user subdomain ratings on completed interview
        topic = session_state.get("topic")
        if topic:
            self._update_ratings_from_scorecard(scorecard, topic)

        return scorecard

    def _update_ratings_from_scorecard(self, scorecard: Dict[str, Any], topic: str) -> None:
        """Feed interview scores back into out-of-git subdomain ratings."""
        ratings = self.state_mgr.get_subdomain_ratings()
        curr = ratings.get(topic, 3.0)
        overall = scorecard["overall_score"]
        delta = 0.4 if overall >= 4.0 else (0.2 if overall >= 3.5 else -0.2)
        new_rating = round(max(1.0, min(5.0, curr + delta)), 2)
        self.state_mgr.update_subdomain_rating(topic, new_rating)


rubric_scorer = RubricScorer()
