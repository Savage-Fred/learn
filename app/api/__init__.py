"""API router aggregation and registration for Savage-Fred/learn."""

from app.api.routes_topics import router as topics_router
from app.api.routes_quiz import router as quiz_router
from app.api.routes_interview import router as interview_router
from app.api.routes_resume import router as resume_router
from app.api.routes_telemetry import router as telemetry_router

__all__ = [
    "topics_router",
    "quiz_router",
    "interview_router",
    "resume_router",
    "telemetry_router",
]
