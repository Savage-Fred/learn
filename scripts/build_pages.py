#!/usr/bin/env python3
"""Build script generating static Cloudflare Pages distribution artifact for learn.willmccarty.io."""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# If system python lacks dependencies, check for local virtual environment and re-exec
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3"
if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    try:
        import pydantic  # noqa: F401
    except ImportError:
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

ALLOWED_DOMAINS = ["leetcode", "system-design", "security", "privacy-engineering"]

STATIC_COMPANY_PROFILES = {
    "OpenAI": {
        "focus": "Practical execution, live coding speed, ML infrastructure, GPU IPC buffers.",
        "execution_weight_boost": 0.05,
        "anti_patterns": [
            "Theoretical purity without working code",
            "Inability to debug tests under pressure",
        ],
    },
    "Google": {
        "focus": "Asymptotic optimality, invariant proofs, massive global scale (Spanner, Zanzibar).",
        "architecture_weight_boost": 0.05,
        "anti_patterns": [
            "Hand-waving time/space complexity",
            "Ignoring network partitions",
        ],
    },
    "Anthropic": {
        "focus": "Extreme craftsmanship, agent tool safety, capability attenuation, constitutional alignment.",
        "resilience_weight_boost": 0.05,
        "anti_patterns": [
            "Excessive ambient privileges",
            "Neglecting sandboxing",
        ],
    },
    "Meta": {
        "focus": "High velocity, high-throughput caching (TAO), back-of-the-envelope calculations.",
        "execution_weight_boost": 0.05,
        "anti_patterns": [
            "Running out of time",
            "Over-complicating architecture",
        ],
    },
    "Databricks": {
        "focus": "Storage engines, query execution, cache lines, zero-copy, atomics.",
        "architecture_weight_boost": 0.05,
        "anti_patterns": [
            "Ignorance of cache lines",
            "Heavy GC where zero-copy is needed",
        ],
    },
    "Netflix": {
        "focus": "Microservice resilience, chaos engineering, continuous A/B testing (CUPED), high autonomy.",
        "resilience_weight_boost": 0.05,
        "anti_patterns": [
            "Needing hand-holding",
            "Weak operational ownership",
        ],
    },
    "Apple": {
        "focus": "On-device efficiency, cryptographic attestation (PCC), differential privacy bounds.",
        "resilience_weight_boost": 0.05,
        "anti_patterns": [
            "Disregard for memory constraints",
            "Treating privacy as an afterthought",
        ],
    },
}

STATIC_ROLE_TRACK_MATRIX = {
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

BASE_DIMENSION_WEIGHTS = {
    "decomposition": 0.20,
    "execution": 0.25,
    "architecture": 0.25,
    "resilience": 0.15,
    "communication": 0.15,
}


def compute_company_weights(company_name: str) -> Dict[str, float]:
    """Compute normalized 5-dimension weights for a company."""
    weights = dict(BASE_DIMENSION_WEIGHTS)
    profile = STATIC_COMPANY_PROFILES.get(company_name, {})
    for key, boost in profile.items():
        if key.endswith("_weight_boost") and isinstance(boost, (int, float)):
            dim = key.replace("_weight_boost", "")
            if dim in weights:
                weights[dim] += boost
                weights["communication"] = max(0.05, round(weights["communication"] - boost, 2))
    total = sum(weights.values())
    return {k: round(v / total, 4) for k, v in weights.items()}


def extract_topic_description(readme_text: str, default_title: str) -> str:
    """Extract clean concise summary description from topic README."""
    if not readme_text:
        return f"Technical curriculum module for {default_title}."

    paragraphs = [
        p.strip()
        for p in readme_text.split("\n\n")
        if p.strip() and not p.strip().startswith(("#", "**Domain", "---"))
    ]
    if paragraphs:
        first_para = paragraphs[0].replace("\n", " ").strip()
        if len(first_para) > 280:
            return first_para[:277] + "..."
        return first_para

    return f"Technical curriculum module for {default_title}."


def compile_catalog(topics_root: Optional[Path] = None) -> Dict[str, Any]:
    """Compile comprehensive static JSON catalog for learn.willmccarty.io."""
    t_root = Path(topics_root or REPO_ROOT).resolve()

    # Try importing from app.core; fallback to pure-filesystem discovery if unavailable
    use_core_loader = False
    try:
        from app.core.topic_loader import TopicLoader
        t_loader = TopicLoader(repo_root=t_root, topics_root=t_root)
        use_core_loader = True
    except Exception:
        use_core_loader = False

    topics_summary: List[Dict[str, Any]] = []
    topic_details_map: Dict[str, Any] = {}

    if use_core_loader:
        raw_topics = t_loader.list_topics("all")
        for t in raw_topics:
            domain = t["domain"]
            slug = t["slug"]
            detail = t_loader.load_topic_detail(domain, slug)
            readme = detail.get("readme", "") if detail else ""
            description = extract_topic_description(readme, t["title"])

            summary_entry = {
                "slug": slug,
                "topic_id": slug,
                "domain": domain,
                "title": t["title"],
                "description": description,
                "role_tracks": t.get("role_tracks", ["FAANG SWE (L5-L6)"]),
                "difficulty_tiers": ["starter", "l4", "l5", "l6"],
                "user_rating": 3.0,
                "pinned": False,
            }
            topics_summary.append(summary_entry)

            detail_entry = {
                "topic_id": slug,
                "slug": slug,
                "domain": domain,
                "title": t["title"],
                "readme": readme,
                "fundamentals": detail.get("fundamentals", "") if detail else "",
                "rubric": detail.get("rubric", "") if detail else "",
                "references": detail.get("references", []) if detail else [],
                "exercises": detail.get("exercises", []) if detail else [],
                "learnings": [],
            }
            topic_details_map[f"{domain}/{slug}"] = detail_entry
            if slug not in topic_details_map:
                topic_details_map[slug] = detail_entry
    else:
        # Pure filesystem traversal fallback
        for domain in ALLOWED_DOMAINS:
            d_dir = t_root / domain
            if not d_dir.is_dir():
                continue
            for entry in sorted(d_dir.iterdir()):
                if not entry.is_dir() or entry.name.startswith((".", "_")) or entry.name == "learnings":
                    continue
                slug = entry.name
                readme_file = entry / "README.md"
                readme_text = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
                title = slug.replace("-", " ").title()
                role_tracks = []
                if readme_text:
                    lines = readme_text.splitlines()
                    if lines and lines[0].startswith("#"):
                        title = lines[0].lstrip("#").strip()
                    if "Track 1" in readme_text or "SWE" in readme_text:
                        role_tracks.append("FAANG SWE (L5-L6)")
                    if "Track 2" in readme_text or "Research" in readme_text:
                        role_tracks.append("Research Engineer")
                    if "Track 3" in readme_text or "Security" in readme_text:
                        role_tracks.append("Security Engineer")
                    if "Track 4" in readme_text or "Privacy" in readme_text:
                        role_tracks.append("Privacy Engineer")

                description = extract_topic_description(readme_text, title)

                summary_entry = {
                    "slug": slug,
                    "topic_id": slug,
                    "domain": domain,
                    "title": title,
                    "description": description,
                    "role_tracks": role_tracks or ["FAANG SWE (L5-L6)"],
                    "difficulty_tiers": ["starter", "l4", "l5", "l6"],
                    "user_rating": 3.0,
                    "pinned": False,
                }
                topics_summary.append(summary_entry)

                fundamentals_file = entry / "fundamentals.md"
                rubric_file = entry / "rubric.md"
                fundamentals_text = fundamentals_file.read_text(encoding="utf-8") if fundamentals_file.exists() else ""
                rubric_text = rubric_file.read_text(encoding="utf-8") if rubric_file.exists() else ""

                # Parse exercises
                exercises = []
                ex_dir = entry / "exercises"
                if ex_dir.is_dir():
                    for ex_file in sorted(ex_dir.glob("*.md")):
                        if not ex_file.name.startswith("."):
                            ex_content = ex_file.read_text(encoding="utf-8")
                            ex_title = ex_file.stem.replace("_", " ").title()
                            for line in ex_content.splitlines():
                                if line.startswith("#"):
                                    ex_title = line.lstrip("#").strip()
                                    break
                            exercises.append({
                                "exercise_id": ex_file.stem,
                                "filename": ex_file.name,
                                "title": ex_title,
                                "content": ex_content,
                            })

                # References
                references = []
                ref_yaml = entry / "references.yaml"
                ref_md = entry / "references.md"
                if ref_yaml.exists():
                    try:
                        import yaml
                        references = yaml.safe_load(ref_yaml.read_text(encoding="utf-8")) or []
                    except Exception:
                        references = [{"raw": ref_yaml.read_text(encoding="utf-8")}]
                elif ref_md.exists():
                    references = [{"raw": ref_md.read_text(encoding="utf-8")}]

                detail_entry = {
                    "topic_id": slug,
                    "slug": slug,
                    "domain": domain,
                    "title": title,
                    "readme": readme_text,
                    "fundamentals": fundamentals_text,
                    "rubric": rubric_text,
                    "references": references,
                    "exercises": exercises,
                    "learnings": [],
                }
                topic_details_map[f"{domain}/{slug}"] = detail_entry
                if slug not in topic_details_map:
                    topic_details_map[slug] = detail_entry

    # Compile role tracks
    role_tracks: Dict[str, Any] = {}
    for track_id, matrix in STATIC_ROLE_TRACK_MATRIX.items():
        role_tracks[track_id] = {
            "id": track_id,
            "name": track_id.replace("_", " ").upper(),
            "weights": {
                topic: {"target_level": target, "weight": weight}
                for topic, (target, weight) in matrix.items()
            },
        }

    # Compile company profiles
    company_bars: Dict[str, Any] = {}
    for company, profile in STATIC_COMPANY_PROFILES.items():
        company_bars[company] = {
            **profile,
            "weights": compute_company_weights(company),
        }

    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "site": "https://learn.willmccarty.io",
        "domains": list(ALLOWED_DOMAINS),
        "topics": topics_summary,
        "topic_details": topic_details_map,
        "role_tracks": role_tracks,
        "company_bars": company_bars,
    }
    return catalog


def build_pages(
    out_dir: Optional[Union[str, Path]] = None,
    repo_root: Optional[Union[str, Path]] = None,
) -> Path:
    """Build static Cloudflare Pages distribution into out_dir."""
    root = Path(repo_root or REPO_ROOT).resolve()
    target_dir = Path(out_dir).resolve() if out_dir else (root / "dist").resolve()

    target_dir.mkdir(parents=True, exist_ok=True)
    static_dir = target_dir / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy UI templates and assets
    ui_dir = root / "app" / "ui"
    shutil.copyfile(ui_dir / "templates" / "index.html", target_dir / "index.html")
    shutil.copyfile(ui_dir / "static" / "styles.css", static_dir / "styles.css")
    shutil.copyfile(ui_dir / "static" / "app.js", static_dir / "app.js")

    # 2. Copy Cloudflare Pages headers and public assets
    public_dir = root / "public"
    shutil.copyfile(public_dir / "_headers", target_dir / "_headers")
    shutil.copyfile(public_dir / "favicon.svg", target_dir / "favicon.svg")
    shutil.copyfile(public_dir / "robots.txt", target_dir / "robots.txt")

    # 3. Generate static catalog.json
    catalog = compile_catalog(topics_root=root)
    catalog_path = static_dir / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    return target_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build static Cloudflare Pages site for learn.willmccarty.io"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Target output directory (defaults to <repo_root>/dist)",
    )
    args = parser.parse_args()

    out_dir = build_pages(out_dir=args.out_dir)
    print(f"Successfully built Cloudflare Pages distribution -> {out_dir}")


if __name__ == "__main__":
    main()
