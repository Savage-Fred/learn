"""Curricula discovery and content loader for Savage-Fred/learn topics."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from app.config import settings
from app.core.schemas import DifficultyTier
from app.core.state import sanitize_identifier


ALLOWED_DOMAINS = ["leetcode", "system-design", "security", "privacy-engineering"]

TOPIC_TO_DOMAIN_MAP = {
    "pythonic-patterns": "leetcode",
    "pythonic-coding-patterns": "leetcode",
    "algorithms": "leetcode",
    "masters-algorithms": "leetcode",
    "data-structures": "leetcode",
    "system-design": "system-design",
    "statistics": "system-design",
    "statistics-for-data-analysis": "system-design",
    "rust": "system-design",
    "go": "system-design",
    "authn-authz": "security",
    "modern-authn-authz": "security",
    "threat-modeling": "security",
    "agent-access-models": "security",
    "access-models-for-agents": "security",
    "pets-for-ai": "privacy-engineering",
    "differential-privacy": "privacy-engineering",
    "modern-differential-privacy": "privacy-engineering",
}


class TopicLoader:
    """Discovers, validates, and loads curriculum artifacts from the repository tree."""

    def __init__(self, repo_root: Optional[Path] = None, topics_root: Optional[Path] = None):
        self.repo_root = (repo_root or settings.repo_root).resolve()
        self.topics_root = (topics_root or settings.topics_root).resolve()

    def resolve_topic_dir(self, topic_slug: str, domain: Optional[str] = None) -> Optional[Tuple[str, Path]]:
        """Resolve topic directory path, handling aliases and domain mapping."""
        clean_slug = sanitize_identifier(topic_slug).lower()
        if domain:
            clean_domain = sanitize_identifier(domain).lower()
            candidate = self.topics_root / clean_domain / clean_slug
            if candidate.is_dir() and candidate.is_relative_to(self.topics_root):
                return clean_domain, candidate.resolve()

        mapped_domain = TOPIC_TO_DOMAIN_MAP.get(clean_slug)
        if mapped_domain:
            # Check domain folder first
            for candidate_slug in (clean_slug, clean_slug.replace("coding-", "").replace("masters-", "").replace("modern-", "").replace("-for-data-analysis", "")):
                candidate = self.topics_root / mapped_domain / candidate_slug
                if candidate.is_dir() and candidate.is_relative_to(self.topics_root):
                    return mapped_domain, candidate.resolve()

        # Check symlinks or folders at repo root or domain root
        for d in ALLOWED_DOMAINS:
            d_dir = self.topics_root / d
            if not d_dir.is_dir():
                continue
            for entry in d_dir.iterdir():
                if entry.is_dir() and entry.name == clean_slug:
                    return d, entry.resolve()

        # Fallback check at repo root (e.g. symlinks)
        root_candidate = self.repo_root / clean_slug
        if root_candidate.is_dir():
            real_path = root_candidate.resolve()
            if real_path.is_relative_to(self.topics_root):
                try:
                    rel_parts = real_path.relative_to(self.topics_root).parts
                    if rel_parts and rel_parts[0] in ALLOWED_DOMAINS:
                        return rel_parts[0], real_path
                except ValueError:
                    pass

        return None

    def list_topics(self, domain_filter: str = "all") -> List[Dict[str, Any]]:
        """List all topics across domains with metadata and counts."""
        target_domains = ALLOWED_DOMAINS if domain_filter == "all" else [domain_filter]
        topics = []

        for d in target_domains:
            d_dir = self.topics_root / d
            if not d_dir.is_dir():
                continue
            for entry in sorted(d_dir.iterdir()):
                if entry.is_dir() and not entry.name.startswith((".", "_")) and entry.name != "learnings":
                    slug = entry.name
                    readme = entry / "README.md"
                    title = slug.replace("-", " ").title()
                    role_tracks = []
                    if readme.exists():
                        try:
                            content = readme.read_text(encoding="utf-8")
                            lines = content.splitlines()
                            if lines and lines[0].startswith("#"):
                                title = lines[0].lstrip("#").strip()
                            if "Track 1" in content or "SWE" in content:
                                role_tracks.append("FAANG SWE (L5-L6)")
                            if "Track 2" in content or "Research" in content:
                                role_tracks.append("Research Engineer")
                            if "Track 3" in content or "Security" in content:
                                role_tracks.append("Security Engineer")
                            if "Track 4" in content or "Privacy" in content:
                                role_tracks.append("Privacy Engineer")
                        except Exception:
                            pass

                    ex_dir = entry / "exercises"
                    ex_count = len([f for f in ex_dir.glob("*.md") if not f.name.startswith(".")]) if ex_dir.is_dir() else 4

                    topics.append({
                        "topic_id": slug,
                        "slug": slug,
                        "domain": d,
                        "title": title,
                        "directory_path": f"{d}/{slug}",
                        "role_tracks": role_tracks or ["FAANG SWE (L5-L6)"],
                        "exercise_count": ex_count,
                    })
        return topics

    def load_topic_detail(self, domain: str, topic_slug: str) -> Optional[Dict[str, Any]]:
        """Load complete topic detail bundle."""
        resolved = self.resolve_topic_dir(topic_slug, domain)
        if not resolved:
            return None
        actual_domain, topic_dir = resolved

        fundamentals_text = (topic_dir / "fundamentals.md").read_text(encoding="utf-8") if (topic_dir / "fundamentals.md").exists() else ""
        rubric_text = (topic_dir / "rubric.md").read_text(encoding="utf-8") if (topic_dir / "rubric.md").exists() else ""
        readme_text = (topic_dir / "README.md").read_text(encoding="utf-8") if (topic_dir / "README.md").exists() else ""

        references = []
        ref_yaml = topic_dir / "references.yaml"
        ref_md = topic_dir / "references.md"
        if ref_yaml.exists():
            try:
                references = yaml.safe_load(ref_yaml.read_text(encoding="utf-8")) or []
            except Exception:
                pass
        elif ref_md.exists():
            references = [{"raw": ref_md.read_text(encoding="utf-8")}]

        exercises = []
        ex_dir = topic_dir / "exercises"
        if ex_dir.is_dir():
            for ex_file in sorted(ex_dir.glob("*.md")):
                if not ex_file.name.startswith("."):
                    content = ex_file.read_text(encoding="utf-8")
                    title = ex_file.stem.replace("_", " ").title()
                    for line in content.splitlines():
                        if line.startswith("#"):
                            title = line.lstrip("#").strip()
                            break
                    exercises.append({
                        "exercise_id": ex_file.stem,
                        "filename": ex_file.name,
                        "title": title,
                        "content": content,
                    })

        return {
            "topic_id": topic_slug,
            "slug": topic_slug,
            "domain": actual_domain,
            "directory_path": f"{actual_domain}/{topic_slug}",
            "readme": readme_text,
            "fundamentals": fundamentals_text,
            "rubric": rubric_text,
            "references": references,
            "exercises": exercises,
        }

    def load_exercise_content(self, topic_slug: str, tier: DifficultyTier) -> Tuple[str, List[str]]:
        """Load prompt and rubric criteria for a given topic and difficulty tier."""
        resolved = self.resolve_topic_dir(topic_slug)
        filename = f"{tier.value}.md"

        rubric_criteria = [
            "Correctness & Invariant preservation",
            "Edge-case robustness",
            "Computational complexity O(N)",
            "Idiomatic language conventions",
        ]

        if resolved:
            _, topic_dir = resolved
            ex_file = topic_dir / "exercises" / filename
            if ex_file.exists():
                try:
                    content = ex_file.read_text(encoding="utf-8")
                    prompt_match = re.search(r"## Problem Statement\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
                    prompt_text = prompt_match.group(1).strip() if prompt_match else content[:350]
                    return prompt_text, rubric_criteria
                except Exception:
                    pass

        defaults = {
            DifficultyTier.STARTER: f"Implement the baseline protocol/invariant for {topic_slug}.",
            DifficultyTier.L4: f"Solve a standard single-host {topic_slug} problem with edge-case handling.",
            DifficultyTier.L5: f"Implement a concurrent, high-throughput {topic_slug} component under strict memory constraints.",
            DifficultyTier.L6: f"Architect a resilient, distributed, partition-tolerant {topic_slug} system with zero data loss.",
        }
        return defaults.get(tier, f"Solve {tier.value} exercise for {topic_slug}."), rubric_criteria


topic_loader = TopicLoader()
