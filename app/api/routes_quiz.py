"""API router for adaptive quizzes, difficulty progression, and proficiency ratings."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core import adaptive_engine, state, sanitize_identifier

router = APIRouter(prefix="/quiz", tags=["Quiz"])


class QuizStartRequest(BaseModel):
    topic_id: Optional[str] = None
    topic_slug: Optional[str] = None
    initial_level: str = "starter"


class QuizTurnRequest(BaseModel):
    topic_slug: Optional[str] = None
    topic_id: Optional[str] = None
    exercise_id: str
    user_answer: Optional[str] = Field(default=None, alias="user_response")
    session_id: Optional[str] = None
    domain: Optional[str] = None
    current_difficulty: Optional[str] = "tier1_starter"

    model_config = ConfigDict(populate_by_name=True)


@router.post("/start")
async def start_quiz_session(req: QuizStartRequest):
    """Start an adaptive quiz session."""
    topic = req.topic_id or req.topic_slug
    if not topic:
        raise HTTPException(status_code=400, detail="Must provide topic_id or topic_slug.")
    try:
        return adaptive_engine.start_exercise(topic_id=topic, initial_level=req.initial_level)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/turn")
async def quiz_turn(req: QuizTurnRequest):
    """Submit answer to adaptive exercise; returns score, feedback, rating update, and next tier."""
    user_answer = (req.user_answer or "").strip()
    topic = req.topic_slug or req.topic_id or "general"

    # If session_id not given or does not exist, start one
    session_id = req.session_id
    if not session_id or not state.get_session(session_id):
        # Initialize an implicit session
        start_payload = adaptive_engine.start_exercise(topic_id=topic, initial_level=req.current_difficulty or "starter")
        session_id = start_payload["session_id"]

    try:
        result = adaptive_engine.exercise_turn(
            session_id=session_id,
            exercise_id=req.exercise_id,
            user_response=user_answer,
        )
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ratings")
async def get_ratings():
    """Retrieve all current user subdomain proficiency ratings."""
    return {"ratings": state.get_subdomain_ratings()}
