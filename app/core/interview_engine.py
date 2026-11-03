"""Mock interview orchestration engine supporting Socratic Hints and Strict Stress modes."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.core.rubric_scorer import RubricScorer, rubric_scorer
from app.core.schemas import CompanyBar, InterviewMode, RoleTrack
from app.core.state import state, StateManager, sanitize_identifier
from app.router import MultiModelRouter


class InterviewEngine:
    """Stateful interview coordinator managing turns, hints, stress probes, and transcripts."""

    PHASES = ["clarification", "architecture", "implementation", "verification", "probing"]

    SUPPORTED_ROLE_TRACKS = [
        "faang_swe_l5_l6",
        "faang_privacy_l6",
        "faang_security_l4_l6",
        "seceng_l4_l6",
        "ai_lab_research_l4_l5",
        "research_eng_l4_l5",
    ]

    SUPPORTED_COMPANIES = [
        "OpenAI",
        "Google",
        "Anthropic",
        "Meta",
        "Databricks",
        "Netflix",
        "Apple",
    ]

    def __init__(
        self,
        state_mgr: Optional[StateManager] = None,
        router: Optional[MultiModelRouter] = None,
        scorer: Optional[RubricScorer] = None,
    ):
        self.state_mgr = state_mgr or state
        self.router = router or MultiModelRouter()
        self.scorer = scorer or rubric_scorer

    def start_interview(
        self,
        role_track: str,
        target_company: str,
        topic: str,
        mode: str = "hints",
        time_limit_minutes: int = 45,
    ) -> Dict[str, Any]:
        """Initialize mock interview session with mode-specific hint budget and timer."""
        # Validation matching E2E boundary expectations
        if role_track not in self.SUPPORTED_ROLE_TRACKS:
            raise ValueError(f"Unsupported role_track '{role_track}'. Must be one of {self.SUPPORTED_ROLE_TRACKS}.")
        if target_company not in self.SUPPORTED_COMPANIES:
            raise ValueError(f"Unsupported target_company '{target_company}'. Must be one of {self.SUPPORTED_COMPANIES}.")
        if mode not in ["hints", "no-hints"]:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'hints' or 'no-hints'.")

        session_id = str(uuid.uuid4())
        clean_topic = sanitize_identifier(topic)
        hints_budget = 3 if mode == "hints" else 0

        welcome_msg = (
            f"Welcome to your {target_company} {role_track} interview on {clean_topic}. "
            "Please begin by stating your understanding of the problem and any clarifying assumptions."
        )

        session_state = {
            "session_id": session_id,
            "role_track": role_track,
            "target_company": target_company,
            "topic": clean_topic,
            "mode": mode,
            "time_limit_minutes": time_limit_minutes,
            "probing_mode": "adversarial_stress" if mode == "no-hints" else "standard",
            "current_phase": "clarification",
            "phase_step": 0,
            "hints_remaining": hints_budget,
            "hints_used": 0,
            "finalized": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "dialogue": [
                {
                    "speaker": "interviewer",
                    "turn_type": "welcome",
                    "message": welcome_msg,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "turns": [
                {
                    "speaker": "interviewer",
                    "turn_type": "welcome",
                    "message": welcome_msg,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

        self.state_mgr.save_session(session_id, session_state)

        return {
            "session_id": session_id,
            "role_track": role_track,
            "target_company": target_company,
            "topic": clean_topic,
            "mode": mode,
            "current_phase": "clarification",
            "interviewer_message": welcome_msg,
            "hints_remaining": hints_budget,
            "time_limit_minutes": time_limit_minutes,
        }

    def interview_turn(
        self,
        session_id: str,
        message: str,
        turn_type: str = "candidate_dialog",
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute interview turn, handling hints, phase transitions, and adversarial probes."""
        session_state = self.state_mgr.get_session(session_id)
        if not session_state:
            raise KeyError(f"Interview session '{session_id}' not found.")

        if session_state.get("finalized"):
            raise ValueError(f"Interview session '{session_id}' is already finalized.")

        effective_mode = mode or session_state.get("mode", "hints")

        candidate_entry = {
            "speaker": "candidate",
            "turn_type": turn_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        session_state.setdefault("dialogue", []).append(candidate_entry)
        session_state.setdefault("turns", []).append(candidate_entry)

        cur_phase = session_state.get("current_phase", "clarification")
        cur_idx = self.PHASES.index(cur_phase) if cur_phase in self.PHASES else 0

        # Socratic Hint Request vs Strict No-Hints Mode
        if turn_type == "request_hint" or ("hint" in message.lower() and len(message.split()) <= 4):
            if effective_mode == "no-hints":
                interviewer_reply = (
                    "In this strict interview mode, hints are disabled. "
                    "Please state your working assumptions and proceed with your technical approach."
                )
            else:
                remaining = session_state.get("hints_remaining", 0)
                if remaining <= 0:
                    interviewer_reply = "Your hint budget is exhausted. Please proceed with your current approach."
                else:
                    session_state["hints_remaining"] = remaining - 1
                    session_state["hints_used"] = session_state.get("hints_used", 0) + 1
                    used = session_state["hints_used"]
                    if used == 1:
                        interviewer_reply = "Hint (Conceptual): Consider the amortized bounds or topological dependency ordering."
                    elif used == 2:
                        interviewer_reply = "Hint (Structural): Structure your state using an event queue with monotone timestamps."
                    else:
                        interviewer_reply = "Hint (Scaffold): `class Buffer: def __init__(self): self.q = deque()`"
        else:
            # Advance phase or adversarial follow-up
            if effective_mode == "no-hints" and cur_phase == "probing":
                interviewer_reply = (
                    "Adversarial follow-up: How does your architecture behave if the primary node suffers "
                    "an unrecoverable network partition and concurrent writes spike by 100x?"
                )
            else:
                next_idx = min(len(self.PHASES) - 1, cur_idx + 1)
                session_state["current_phase"] = self.PHASES[next_idx]
                interviewer_reply = (
                    f"Understood. Let us proceed to the {self.PHASES[next_idx].upper()} phase. "
                    "How do you address edge-case failures and formal invariant verification?"
                )

        interviewer_entry = {
            "speaker": "interviewer",
            "turn_type": "interviewer_dialog",
            "message": interviewer_reply,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        session_state["dialogue"].append(interviewer_entry)
        session_state["turns"].append(interviewer_entry)

        self.state_mgr.save_session(session_id, session_state)

        return {
            "session_id": session_id,
            "current_phase": session_state["current_phase"],
            "interviewer_message": interviewer_reply,
            "hints_remaining": session_state.get("hints_remaining", 0),
            "hints_used": session_state.get("hints_used", 0),
            "turn_count": len(session_state["turns"]),
        }

    def finalize_interview(self, session_id: str) -> Dict[str, Any]:
        """Idempotently score completed interview session and persist scorecard."""
        session_state = self.state_mgr.get_session(session_id)
        if not session_state:
            raise KeyError(f"Interview session '{session_id}' not found.")

        existing_scorecard = self.state_mgr.get_scorecard(session_id)
        if session_state.get("finalized") and existing_scorecard:
            return existing_scorecard

        # Generate scorecard via RubricScorer
        scorecard = self.scorer.score_interview(session_state)

        session_state["finalized"] = True
        session_state["scorecard"] = scorecard
        self.state_mgr.save_session(session_id, session_state)

        return scorecard


interview_engine = InterviewEngine()
