"""Role and resume alignment engine computing fit scores and customized loops."""

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.core.schemas import CompanyBar, RoleTrack
from app.core.state import state, StateManager


class ResumeMatcher:
    """Matches job descriptions and resumes against role tracks and company bars."""

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

    COMPETENCY_MATRIX = {
        "faang_swe_l5_l6": {
            "pythonic-coding-patterns": (4.2, 0.10),
            "masters-algorithms": (4.5, 0.15),
            "data-structures": (4.5, 0.15),
            "modern-authn-authz": (3.5, 0.05),
            "pets-for-ai": (2.5, 0.05),
            "threat-modeling": (3.0, 0.05),
            "agent-access-models": (3.0, 0.05),
            "statistics-for-data-analysis": (3.8, 0.10),
            "rust": (4.0, 0.15),
            "go": (4.0, 0.10),
            "modern-differential-privacy": (2.0, 0.05),
        },
        "faang_privacy_l6": {
            "pythonic-coding-patterns": (3.8, 0.05),
            "masters-algorithms": (3.5, 0.05),
            "data-structures": (3.8, 0.05),
            "modern-authn-authz": (4.5, 0.15),
            "pets-for-ai": (4.8, 0.20),
            "threat-modeling": (4.5, 0.15),
            "agent-access-models": (4.2, 0.10),
            "statistics-for-data-analysis": (4.2, 0.05),
            "rust": (3.0, 0.02),
            "go": (3.0, 0.03),
            "modern-differential-privacy": (4.8, 0.15),
        },
        "faang_security_l4_l6": {
            "pythonic-coding-patterns": (3.8, 0.05),
            "masters-algorithms": (3.5, 0.05),
            "data-structures": (3.8, 0.05),
            "modern-authn-authz": (4.8, 0.20),
            "pets-for-ai": (3.5, 0.05),
            "threat-modeling": (4.8, 0.20),
            "agent-access-models": (4.8, 0.20),
            "statistics-for-data-analysis": (3.0, 0.05),
            "rust": (4.0, 0.08),
            "go": (4.0, 0.05),
            "modern-differential-privacy": (2.5, 0.02),
        },
        "ai_lab_research_l4_l5": {
            "pythonic-coding-patterns": (4.6, 0.15),
            "masters-algorithms": (4.2, 0.12),
            "data-structures": (4.5, 0.15),
            "modern-authn-authz": (2.5, 0.03),
            "pets-for-ai": (3.0, 0.05),
            "threat-modeling": (2.5, 0.03),
            "agent-access-models": (3.5, 0.05),
            "statistics-for-data-analysis": (4.6, 0.15),
            "rust": (4.5, 0.20),
            "go": (3.0, 0.05),
            "modern-differential-privacy": (2.5, 0.02),
        },
    }

    TOPIC_CURRICULA = {
        "pythonic-coding-patterns": "leetcode/pythonic-patterns",
        "masters-algorithms": "leetcode/algorithms",
        "algorithms": "leetcode/algorithms",
        "data-structures": "leetcode/data-structures",
        "modern-authn-authz": "security/authn-authz",
        "authn-authz": "security/authn-authz",
        "pets-for-ai": "privacy-engineering/pets-for-ai",
        "threat-modeling": "security/threat-modeling",
        "agent-access-models": "security/agent-access-models",
        "statistics-for-data-analysis": "system-design/statistics",
        "statistics": "system-design/statistics",
        "rust": "system-design/rust",
        "go": "system-design/go",
        "modern-differential-privacy": "privacy-engineering/differential-privacy",
        "differential-privacy": "privacy-engineering/differential-privacy",
    }

    def __init__(self, state_mgr: Optional[StateManager] = None):
        self.state_mgr = state_mgr or state

    def analyze_role_fit(
        self,
        job_description_text: str,
        resume_text: Optional[str] = None,
        role_track: str = "faang_swe_l5_l6",
        target_company: str = "Google",
    ) -> Dict[str, Any]:
        """Compute fit score, detect gaps, and generate custom interview loop."""
        if not job_description_text or not job_description_text.strip():
            raise ValueError("Job description text cannot be empty.")
        if role_track not in self.SUPPORTED_ROLE_TRACKS:
            raise ValueError(f"Unsupported role track: '{role_track}'.")
        if target_company not in self.SUPPORTED_COMPANIES:
            raise ValueError(f"Unsupported company: '{target_company}'.")

        # Resolve resume
        active_resume = resume_text
        if not active_resume:
            active_resume = self.state_mgr.get_active_resume()
        if not active_resume:
            active_resume = "Software Engineer with distributed systems and algorithms background."

        # Fetch ratings (missing topics default to 1.0)
        ratings = self.state_mgr.get_subdomain_ratings()

        canonical_track = role_track
        if role_track == "seceng_l4_l6":
            canonical_track = "faang_security_l4_l6"
        elif role_track == "research_eng_l4_l5":
            canonical_track = "ai_lab_research_l4_l5"

        track_matrix = self.COMPETENCY_MATRIX.get(canonical_track, self.COMPETENCY_MATRIX["faang_swe_l5_l6"])
        weighted_competency_fit = 0.0
        competencies_matched = []
        gaps = []

        for topic, (target_level, weight) in track_matrix.items():
            raw_level = ratings.get(topic, 1.0)
            try:
                user_level = float(raw_level)
                if math.isnan(user_level) or math.isinf(user_level):
                    user_level = 1.0
            except (ValueError, TypeError):
                user_level = 1.0
            fit_ratio = min(1.0, user_level / target_level)
            weighted_competency_fit += weight * fit_ratio
            delta = round(target_level - user_level, 2)

            status = "match" if delta <= 0 else ("partial" if delta <= 0.8 else "gap")
            competencies_matched.append({
                "skill": topic.replace("-", " ").title(),
                "topic_id": topic,
                "user_level": user_level,
                "required_level": target_level,
                "status": status,
            })

            if delta > 0:
                priority = "critical" if delta >= 1.0 and weight >= 0.10 else ("high" if delta >= 0.5 else "moderate")
                gaps.append({
                    "topic_id": topic,
                    "priority": priority,
                    "delta": delta,
                    "reason": f"Required for {target_company} {role_track} loop.",
                })

        jd_lower = job_description_text.lower()
        res_lower = active_resume.lower()
        keywords = ["distributed", "algorithms", "security", "privacy", "python", "concurrency", "threat"]
        matched_kw = [k for k in keywords if k in jd_lower and k in res_lower]
        keyword_factor = len(matched_kw) * 5.0

        # Calculate final fit score clamped strictly between 0.0 and 100.0
        raw_score = (weighted_competency_fit * 70.0) + keyword_factor
        fit_score = round(max(0.0, min(100.0, raw_score)), 1)

        calibrated_level = "L5" if "l5" in role_track else "L6"
        target_level = "L6" if "l6" in role_track else "L5"

        # Sort gaps
        sorted_gaps = sorted(gaps, key=lambda x: x["delta"], reverse=True)
        top_gap = sorted_gaps[0]["topic_id"] if sorted_gaps else "threat-modeling"

        custom_loop = [
            {"round": 1, "topic": "algorithms", "type": "coding", "target_level": target_level},
            {"round": 2, "topic": "system-design", "type": "system_design", "target_level": target_level},
            {"round": 3, "topic": top_gap, "type": "domain_deep_dive", "target_level": target_level},
            {"round": 4, "topic": "authn-authz", "type": "architecture", "target_level": target_level},
            {"round": 5, "topic": "behavioral", "type": "leadership", "target_level": target_level},
        ]

        learning_plan = [
            {
                "topic_id": g["topic_id"],
                "curriculum_path": self.TOPIC_CURRICULA.get(g["topic_id"], f"curricula/{g['topic_id']}"),
                "priority": g["priority"],
            }
            for g in sorted_gaps[:5]
        ]

        analysis_id = str(uuid.uuid4())
        result = {
            "analysis_id": analysis_id,
            "role_track": role_track,
            "target_company": target_company,
            "fit_score_percentage": fit_score,
            "calibrated_level": calibrated_level,
            "target_level": target_level,
            "competencies_matched": competencies_matched[:5],
            "high_leverage_gaps": sorted_gaps[:4],
            "custom_interview_loop": custom_loop,
            "recommended_learning_plan": learning_plan,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.state_mgr.save_gap_analysis(analysis_id, result)
        return result


resume_matcher = ResumeMatcher()
