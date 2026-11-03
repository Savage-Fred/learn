"""API router for mock interviews, progressive Socratic hints, rubrics, and WebSocket streaming."""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ConfigDict, Field

from app.config import settings
from app.core import (
    interview_engine,
    rubric_scorer,
    state,
    sanitize_identifier,
)

router = APIRouter(prefix="/interview", tags=["Interview"])


class InterviewStartRequest(BaseModel):
    topic: str
    role_track: str = "faang_swe_l5_l6"
    target_company: str = "Google"
    mode: str = Field(default="hints", pattern="^(hints|no-hints)$")
    time_limit_minutes: int = 45
    probing_mode: str = "standard"


class InterviewTurnRequest(BaseModel):
    message: Optional[str] = Field(default=None, alias="user_response")
    turn_type: str = "candidate_dialog"
    mode: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


@router.post("/start")
async def start_interview_endpoint(req: InterviewStartRequest):
    """Initiate mock interview session with configured mode and role track."""
    try:
        return interview_engine.start_interview(
            role_track=req.role_track,
            target_company=req.target_company,
            topic=req.topic,
            mode=req.mode,
            time_limit_minutes=req.time_limit_minutes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/turn")
async def interview_turn_endpoint(session_id: str, req: InterviewTurnRequest):
    """Submit candidate turn; returns interviewer response, phase progression, and hint status."""
    message = req.message or ""
    try:
        return interview_engine.interview_turn(
            session_id=session_id,
            message=message,
            turn_type=req.turn_type,
            mode=req.mode,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}/scorecard")
@router.post("/{session_id}/finalize")
async def get_or_finalize_scorecard(session_id: str):
    """Compute and retrieve 5-dimension rubric scorecard and calibrated bar decision."""
    try:
        return interview_engine.finalize_interview(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/{session_id}/stream")
async def interview_stream_ws(websocket: WebSocket, session_id: str, token: Optional[str] = None):
    """WebSocket streaming endpoint for real-time interview turns."""
    client_host = websocket.client.host if websocket.client else "unknown"
    is_loopback = client_host in ("127.0.0.1", "::1", "localhost", "testclient")

    if not is_loopback and settings.api_token:
        auth_token = token or websocket.headers.get("x-learn-token")
        auth_header = websocket.headers.get("authorization", "")
        if "Bearer " in auth_header:
            auth_token = auth_header.replace("Bearer ", "").strip()
        if auth_token != settings.api_token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")
            return

    await websocket.accept()
    clean_id = sanitize_identifier(session_id)
    session_state = state.get_session(clean_id)
    if not session_state:
        await websocket.send_json({"type": "error", "message": f"Session '{clean_id}' not found."})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not found")
        return

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            turn_type = data.get("turn_type", "candidate_dialog")

            # Execute turn via interview engine
            turn_result = interview_engine.interview_turn(
                session_id=clean_id,
                message=message,
                turn_type=turn_type,
            )
            full_reply = turn_result["interviewer_message"]
            words = full_reply.split(" ")
            for w in words:
                await websocket.send_json({"type": "chunk", "delta": w + " "})

            await websocket.send_json({
                "type": "done",
                "interviewer_message": full_reply,
                "current_phase": turn_result["current_phase"],
                "hints_remaining": turn_result["hints_remaining"],
            })
    except WebSocketDisconnect:
        pass
