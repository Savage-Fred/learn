"""Data schemas and types for Savage-Fred/learn core engines."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class DifficultyTier(str, Enum):
    STARTER = "tier1_starter"
    L4 = "tier2_l4"
    L5 = "tier3_l5"
    L6 = "tier4_l6"

    @classmethod
    def from_str(cls, val: str) -> "DifficultyTier":
        val_clean = val.lower().strip()
        mapping = {
            "starter": cls.STARTER,
            "tier1_starter": cls.STARTER,
            "tier1": cls.STARTER,
            "l4": cls.L4,
            "tier2_l4": cls.L4,
            "tier2": cls.L4,
            "l5": cls.L5,
            "tier3_l5": cls.L5,
            "tier3": cls.L5,
            "l6": cls.L6,
            "tier4_l6": cls.L6,
            "tier4": cls.L6,
        }
        if val_clean not in mapping:
            raise ValueError(f"Invalid difficulty level '{val}'. Must be starter, l4, l5, or l6.")
        return mapping[val_clean]

    @property
    def short_name(self) -> str:
        mapping = {
            DifficultyTier.STARTER: "starter",
            DifficultyTier.L4: "l4",
            DifficultyTier.L5: "l5",
            DifficultyTier.L6: "l6",
        }
        return mapping[self]


class InterviewMode(str, Enum):
    HINTS = "hints"
    NO_HINTS = "no-hints"


class InterviewPhase(str, Enum):
    INTRODUCTION = "introduction"
    PRESENTATION = "presentation"
    CLARIFICATION = "clarification"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    PROBING = "probing"
    DEBRIEF = "debrief"

    @classmethod
    def standard_e2e_phases(cls) -> List[str]:
        return ["clarification", "architecture", "implementation", "verification", "probing"]


class RoleTrack(str, Enum):
    SWE = "faang_swe_l5_l6"
    PRIVACY = "faang_privacy_l6"
    SECURITY = "faang_security_l4_l6"
    RESEARCH = "ai_lab_research_l4_l5"

    @classmethod
    def from_str(cls, val: str) -> "RoleTrack":
        val_clean = val.lower().strip()
        aliases = {
            "faang_swe_l5_l6": cls.SWE,
            "swe": cls.SWE,
            "general infrastructure / distributed systems engineer": cls.SWE,
            "faang_privacy_l6": cls.PRIVACY,
            "privacy": cls.PRIVACY,
            "privacy engineer": cls.PRIVACY,
            "faang_security_l4_l6": cls.SECURITY,
            "seceng_l4_l6": cls.SECURITY,
            "security": cls.SECURITY,
            "security engineer (agent & infra)": cls.SECURITY,
            "ai_lab_research_l4_l5": cls.RESEARCH,
            "research_eng_l4_l5": cls.RESEARCH,
            "research": cls.RESEARCH,
            "machine learning systems engineer": cls.RESEARCH,
        }
        if val_clean not in aliases:
            raise ValueError(f"Unsupported role_track '{val}'. Must be one of {[t.value for t in cls]}.")
        return aliases[val_clean]


class CompanyBar(str, Enum):
    OPENAI = "OpenAI"
    GOOGLE = "Google"
    ANTHROPIC = "Anthropic"
    META = "Meta"
    DATABRICKS = "Databricks"
    NETFLIX = "Netflix"
    APPLE = "Apple"

    @classmethod
    def from_str(cls, val: str) -> "CompanyBar":
        val_clean = val.strip()
        for company in cls:
            if company.value.lower() == val_clean.lower():
                return company
        raise ValueError(f"Unsupported target_company '{val}'. Must be one of {[c.value for c in cls]}.")


class BarDecision(str, Enum):
    STRONG_HIRE = "Strong Hire"
    HIRE = "Hire"
    LEANING_HIRE = "Leaning Hire"
    LEAN_HIRE = "Lean Hire"
    LEANING_NO_HIRE = "Leaning No Hire"
    LEAN_NO_HIRE = "Lean No Hire"
    NO_HIRE = "No Hire"
    STRONG_NO_HIRE = "Strong No Hire"


class RubricDimension(str, Enum):
    DECOMPOSITION = "decomposition"
    EXECUTION = "execution"
    ARCHITECTURE = "architecture"
    RESILIENCE = "resilience"
    COMMUNICATION = "communication"


class RubricScores(BaseModel):
    decomposition: float = Field(..., ge=1.0, le=5.0)
    execution: float = Field(..., ge=1.0, le=5.0)
    architecture: float = Field(..., ge=1.0, le=5.0)
    resilience: float = Field(..., ge=1.0, le=5.0)
    communication: float = Field(..., ge=1.0, le=5.0)

    def weighted_average(self) -> float:
        val = (
            self.decomposition * 0.20
            + self.execution * 0.25
            + self.architecture * 0.25
            + self.resilience * 0.15
            + self.communication * 0.15
        )
        return round(val, 2)


class CandidateTurn(BaseModel):
    message: str = Field(..., alias="user_response")
    turn_type: str = "candidate_dialog"
    mode: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class InterviewerResponse(BaseModel):
    session_id: str
    current_phase: str
    interviewer_message: str
    hints_remaining: int
    hints_used: int = 0
    turn_count: Optional[int] = None


class Scorecard(BaseModel):
    session_id: str
    role_track: str
    target_company: str
    topic: Optional[str] = None
    rubric_scores: Dict[str, float]
    overall_score: float
    bar_decision: str
    level_calibration: str
    feedback: str
    weaknesses_identified: List[str] = Field(default_factory=list)
    finalized_at: str
