"""API router for resume & job description analysis, gap scoring, and custom interview loops."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core import resume_matcher

router = APIRouter(prefix="/resume", tags=["Resume"])


class ResumeAnalyzeRequest(BaseModel):
    job_description_text: str
    resume_text: Optional[str] = None
    role_track: str = "faang_swe_l5_l6"
    target_company: str = "Google"
    target_level: Optional[str] = "L6"


@router.post("/analyze")
async def analyze_resume_fit(req: ResumeAnalyzeRequest):
    """Analyze job description and resume against competency matrix; produces fit score and custom loop."""
    try:
        return resume_matcher.analyze_role_fit(
            job_description_text=req.job_description_text,
            resume_text=req.resume_text,
            role_track=req.role_track,
            target_company=req.target_company,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
