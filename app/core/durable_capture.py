"""Durable learning capture engine with candidate PII scrubbing and canonical markdown formatting."""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from app.config import settings
from app.core.state import sanitize_identifier
from app.core.topic_loader import topic_loader, ALLOWED_DOMAINS, TOPIC_TO_DOMAIN_MAP


def scrub_pii(text: str) -> str:
    """Scrub personal identifiable information, tokens, and candidate scores."""
    if not text:
        return text

    # Email scrubbing
    scrubbed = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_REDACTED]", text)
    # Phone number scrubbing
    scrubbed = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE_REDACTED]", scrubbed)
    # Bearer tokens and API keys
    scrubbed = re.sub(r"(?i)(bearer\s+[a-zA-Z0-9_\-\.]{16,})", "Bearer [REDACTED_TOKEN]", scrubbed)
    scrubbed = re.sub(r"(?i)(api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}['\"]?)", "api_key=[REDACTED_KEY]", scrubbed)
    # Scorecard private metrics
    scrubbed = re.sub(r"(?i)(candidate_score\s*[:=]\s*\d+(?:\.\d+)?)", "candidate_score=[REDACTED]", scrubbed)
    return scrubbed


class DurableCaptureEngine:
    """Captures and stores distilled technical insights in git-versioned topic directories."""

    def __init__(self, topics_root: Optional[Path] = None):
        self.topics_root = (topics_root or settings.topics_root).resolve()

    def record_learning(
        self,
        topic_slug: str,
        title: str,
        mental_model: str,
        invariants: List[str],
        domain: Optional[str] = None,
        citable_sources: Optional[List[str]] = None,
        code_examples: Optional[str] = None,
        notes: Optional[str] = None,
        target_level: str = "L6",
        tags: Optional[List[str]] = None,
        frontmatter_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Distill breakthrough and write to <domain>/<topic>/learnings/<id>.md."""
        clean_slug = sanitize_identifier(topic_slug).lower()
        if not title or not title.strip():
            raise ValueError("Title cannot be empty.")
        if not mental_model or not mental_model.strip():
            raise ValueError("Mental model cannot be empty.")

        actual_domain = domain
        if not actual_domain:
            resolved = topic_loader.resolve_topic_dir(clean_slug)
            if resolved:
                actual_domain, _ = resolved
            else:
                actual_domain = TOPIC_TO_DOMAIN_MAP.get(clean_slug, "leetcode")

        actual_domain = sanitize_identifier(actual_domain).lower()
        if actual_domain not in ALLOWED_DOMAINS:
            raise ValueError(f"Invalid domain '{actual_domain}'. Must be one of {ALLOWED_DOMAINS}.")

        target_dir = (self.topics_root / actual_domain / clean_slug / "learnings").resolve()
        if not target_dir.is_relative_to(self.topics_root):
            raise ValueError("Invalid path: target directory escapes topics root.")

        target_dir.mkdir(parents=True, exist_ok=True)

        # Clean / scrub text
        clean_title = scrub_pii(title.strip())
        clean_model = scrub_pii(mental_model.strip())
        clean_invariants = [scrub_pii(inv) for inv in (invariants or [])]
        clean_notes = scrub_pii(notes.strip()) if notes else None
        clean_code = scrub_pii(code_examples.strip()) if code_examples else None
        clean_sources = [scrub_pii(s) for s in (citable_sources or [])]

        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:4]
        safe_title_slug = re.sub(r"[^\w\-_]+", "-", clean_title.lower()).strip("-")[:50]
        filename = f"learn-{date_str}-{safe_title_slug}-{rand_suffix}.md"
        target_file = target_dir / filename

        frontmatter = {
            "id": f"learn-{date_str}-{clean_slug}-{rand_suffix}",
            "topic": clean_slug,
            "domain": actual_domain,
            "title": clean_title,
            "date": now.isoformat(),
            "created_at": now.isoformat(),
            "target_level": target_level,
            "source_trigger": "on_demand_deep_dive",
            "invariants_covered": clean_invariants,
            "tags": tags or [actual_domain, clean_slug, "durable-learning"],
        }
        if frontmatter_metadata:
            frontmatter.update(frontmatter_metadata)

        content_lines = [
            "---",
            yaml.dump(frontmatter, sort_keys=False).strip(),
            "---",
            f"\n# {clean_title}\n",
        ]
        if clean_model:
            content_lines.extend(["## Mental Model\n", clean_model, "\n"])
        if clean_invariants:
            content_lines.append("## Invariants Preserved\n")
            for inv in clean_invariants:
                content_lines.append(f"- {inv}")
            content_lines.append("")
        if clean_notes:
            content_lines.extend(["## Notes & Technical Details\n", clean_notes, "\n"])
        if clean_sources:
            content_lines.append("## Citable Sources\n")
            for src in clean_sources:
                content_lines.append(f"- {src}")
            content_lines.append("")
        if clean_code:
            content_lines.extend(["## Code & Verification\n", clean_code, "\n"])

        target_file.write_text("\n".join(content_lines), encoding="utf-8")
        rel_path = str(target_file.relative_to(settings.repo_root))

        return {
            "status": "created",
            "file_path": rel_path,
            "absolute_path": str(target_file),
            "frontmatter": frontmatter,
        }


durable_capture = DurableCaptureEngine()
