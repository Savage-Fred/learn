"""Out-of-git personal user state management with atomic replacement and file locking."""

import fcntl
import json
import math
import os
import re
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings


import threading

_lock_state = threading.local()


@contextmanager
def file_lock(lock_file_path: Path):
    """Context manager acquiring an exclusive, thread-reentrant file lock via fcntl."""
    canonical_path = str(lock_file_path.resolve())
    if not hasattr(_lock_state, "locks"):
        _lock_state.locks = {}

    # Thread-local re-entrancy: avoid self-deadlock on nested lock calls
    if canonical_path in _lock_state.locks:
        _lock_state.locks[canonical_path]["count"] += 1
        try:
            yield
        finally:
            _lock_state.locks[canonical_path]["count"] -= 1
        return

    lock_file_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_file_path, "a")
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    _lock_state.locks[canonical_path] = {"file": f, "count": 1}
    try:
        yield
    finally:
        _lock_state.locks[canonical_path]["count"] -= 1
        if _lock_state.locks[canonical_path]["count"] == 0:
            del _lock_state.locks[canonical_path]
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            finally:
                f.close()


def sanitize_identifier(identifier: str) -> str:
    """Validate and sanitize identifiers against path traversal attacks."""
    if not identifier or not str(identifier).strip():
        raise ValueError("Identifier cannot be empty.")
    clean = str(identifier).strip()
    if clean == "." or ".." in clean or "/" in clean or "\\" in clean or "\0" in clean:
        raise ValueError(f"Security violation: path traversal detected in identifier '{clean}'.")
    return clean


def atomic_write_json(target_path: Path, data: Any, indent: int = 2) -> None:
    """Atomically write JSON data to target_path using temp file replacement and file locking."""
    target_path = target_path.resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = target_path.with_suffix(target_path.suffix + ".lock")

    with file_lock(lock_path):
        with tempfile.NamedTemporaryFile("w", dir=target_path.parent, delete=False, encoding="utf-8") as tf:
            temp_name = tf.name
            json.dump(data, tf, indent=indent)
            tf.flush()
            os.fsync(tf.fileno())
        os.replace(temp_name, target_path)


def safe_read_json(target_path: Path, default: Any = None) -> Any:
    """Safely read JSON data from target_path under shared/exclusive lock."""
    if not target_path.exists():
        return default
    lock_path = target_path.with_suffix(target_path.suffix + ".lock")
    with file_lock(lock_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return default
                return json.loads(content)
        except Exception:
            return default


class StateManager:
    """Personal state manager strictly rooted in settings.data_dir."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = (data_dir or settings.data_dir).expanduser().resolve()
        self._validate_isolation()
        self.ensure_layout()

    def _validate_isolation(self) -> None:
        """Enforce §R4 invariant: data_dir must not reside within repo_root."""
        repo_root = settings.repo_root.resolve()
        if self.data_dir.is_relative_to(repo_root):
            raise ValueError(
                f"Personal state directory {self.data_dir} must not be located inside repository root {repo_root} (§R4 invariant)"
            )

    def ensure_layout(self) -> None:
        """Create necessary subdirectories under data_dir."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sessions").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "resumes" / "gap_analyses").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "telemetry").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "ratings").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "pins").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "interviews" / "transcripts").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "interviews" / "scorecards").mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Canonical Resource Locks
    # -------------------------------------------------------------------------
    @property
    def ratings_lock_file(self) -> Path:
        return self.ratings_file.with_suffix(self.ratings_file.suffix + ".lock")

    @contextmanager
    def ratings_lock(self):
        with file_lock(self.ratings_lock_file):
            yield

    @property
    def pinned_topics_lock_file(self) -> Path:
        return self.pinned_topics_file.with_suffix(self.pinned_topics_file.suffix + ".lock")

    @contextmanager
    def pinned_topics_lock(self):
        with file_lock(self.pinned_topics_lock_file):
            yield

    def session_lock_file(self, session_id: str) -> Path:
        clean_id = sanitize_identifier(session_id)
        return self.data_dir / "sessions" / f"{clean_id}.json.lock"

    @contextmanager
    def session_lock(self, session_id: str):
        clean_id = sanitize_identifier(session_id)
        with file_lock(self.session_lock_file(clean_id)):
            yield

    def scorecard_lock_file(self, session_id: str) -> Path:
        clean_id = sanitize_identifier(session_id)
        return self.data_dir / "sessions" / f"{clean_id}_scorecard.json.lock"

    @contextmanager
    def scorecard_lock(self, session_id: str):
        clean_id = sanitize_identifier(session_id)
        with file_lock(self.scorecard_lock_file(clean_id)):
            yield

    # -------------------------------------------------------------------------
    # Pinned Topics (Dual-Path: root pinned_topics.json and pins/pinned_topics.json)
    # -------------------------------------------------------------------------
    @property
    def pinned_topics_file(self) -> Path:
        return self.data_dir / "pinned_topics.json"

    @property
    def pinned_topics_alias_file(self) -> Path:
        return self.data_dir / "pins" / "pinned_topics.json"

    def get_pinned_topics(self) -> List[Dict[str, Any]]:
        with self.pinned_topics_lock():
            pins = safe_read_json(self.pinned_topics_file)
            if pins is None:
                pins = safe_read_json(self.pinned_topics_alias_file, default=[])
            return pins or []

    def pin_topic(
        self,
        topic_slug: str,
        domain: str = "general",
        priority: str = "high",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_slug = sanitize_identifier(topic_slug)
        if priority not in ("high", "medium", "low"):
            raise ValueError(f"Priority must be one of ('high', 'medium', 'low'), got '{priority}'.")

        with self.pinned_topics_lock():
            pins = safe_read_json(self.pinned_topics_file)
            if pins is None:
                pins = safe_read_json(self.pinned_topics_alias_file, default=[])
            pins = pins or []
            timestamp = datetime.now(timezone.utc).isoformat()

            found = False
            result_item = None
            for item in pins:
                if item.get("topic_id") == clean_slug or item.get("topic_slug") == clean_slug:
                    item["priority"] = priority
                    item["notes"] = notes or ""
                    item["updated_at"] = timestamp
                    result_item = item
                    found = True
                    break

            if not found:
                result_item = {
                    "topic_id": clean_slug,
                    "topic_slug": clean_slug,
                    "domain": domain,
                    "priority": priority,
                    "notes": notes or "",
                    "pinned_at": timestamp,
                }
                pins.append(result_item)

            atomic_write_json(self.pinned_topics_file, pins)
            atomic_write_json(self.pinned_topics_alias_file, pins)
            return {"status": "pinned", **result_item}

    def unpin_topic(self, topic_slug: str) -> bool:
        clean_slug = sanitize_identifier(topic_slug)
        with self.pinned_topics_lock():
            pins = safe_read_json(self.pinned_topics_file)
            if pins is None:
                pins = safe_read_json(self.pinned_topics_alias_file, default=[])
            pins = pins or []
            initial_len = len(pins)
            pins = [p for p in pins if p.get("topic_id") != clean_slug and p.get("topic_slug") != clean_slug]
            removed = len(pins) < initial_len

            atomic_write_json(self.pinned_topics_file, pins)
            atomic_write_json(self.pinned_topics_alias_file, pins)
            return removed

    # -------------------------------------------------------------------------
    # Subdomain Ratings (Dual-Path: ratings/subdomain_ratings.json and subdomain_ratings.json)
    # -------------------------------------------------------------------------
    @property
    def ratings_file(self) -> Path:
        return self.data_dir / "ratings" / "subdomain_ratings.json"

    @property
    def ratings_alias_file(self) -> Path:
        return self.data_dir / "subdomain_ratings.json"

    def get_subdomain_ratings(self) -> Dict[str, float]:
        with self.ratings_lock():
            ratings = safe_read_json(self.ratings_file)
            if ratings is None:
                ratings = safe_read_json(self.ratings_alias_file, default={})
            return ratings or {}

    def update_subdomain_rating(self, topic_slug: str, new_rating: float) -> float:
        clean_slug = sanitize_identifier(topic_slug)
        try:
            val = float(new_rating)
            if math.isnan(val):
                val = 1.0
            elif math.isinf(val):
                val = 5.0 if val > 0 else 1.0
        except (ValueError, TypeError):
            val = 1.0
        clamped = round(max(1.0, min(5.0, val)), 2)

        with self.ratings_lock():
            ratings = safe_read_json(self.ratings_file)
            if ratings is None:
                ratings = safe_read_json(self.ratings_alias_file, default={})
            ratings = ratings or {}
            ratings[clean_slug] = clamped

            atomic_write_json(self.ratings_file, ratings)
            atomic_write_json(self.ratings_alias_file, ratings)
            return clamped

    def set_subdomain_ratings(self, ratings: Dict[str, float]) -> None:
        clamped = {}
        for k, v in ratings.items():
            try:
                val = float(v)
                if math.isnan(val):
                    val = 1.0
                elif math.isinf(val):
                    val = 5.0 if val > 0 else 1.0
            except (ValueError, TypeError):
                val = 1.0
            clamped[sanitize_identifier(k)] = round(max(1.0, min(5.0, val)), 2)
        with self.ratings_lock():
            atomic_write_json(self.ratings_file, clamped)
            atomic_write_json(self.ratings_alias_file, clamped)

    # -------------------------------------------------------------------------
    # Sessions & Interview Transcripts
    # -------------------------------------------------------------------------
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        clean_id = sanitize_identifier(session_id)
        with self.session_lock(clean_id):
            session_path = self.data_dir / "sessions" / f"{clean_id}.json"
            data = safe_read_json(session_path)
            if data is None:
                alias_path = self.data_dir / "interviews" / "transcripts" / f"{clean_id}.json"
                data = safe_read_json(alias_path)
            return data

    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        clean_id = sanitize_identifier(session_id)
        with self.session_lock(clean_id):
            primary = self.data_dir / "sessions" / f"{clean_id}.json"
            alias = self.data_dir / "interviews" / "transcripts" / f"{clean_id}.json"
            atomic_write_json(primary, session_data)
            atomic_write_json(alias, session_data)

    def get_scorecard(self, session_id: str) -> Optional[Dict[str, Any]]:
        clean_id = sanitize_identifier(session_id)
        with self.scorecard_lock(clean_id):
            card_path = self.data_dir / "sessions" / f"{clean_id}_scorecard.json"
            data = safe_read_json(card_path)
            if data is None:
                alias_path = self.data_dir / "interviews" / "scorecards" / f"{clean_id}_scorecard.json"
                data = safe_read_json(alias_path)
            return data

    def save_scorecard(self, session_id: str, scorecard_data: Dict[str, Any]) -> None:
        clean_id = sanitize_identifier(session_id)
        with self.scorecard_lock(clean_id):
            primary = self.data_dir / "sessions" / f"{clean_id}_scorecard.json"
            alias = self.data_dir / "interviews" / "scorecards" / f"{clean_id}_scorecard.json"
            atomic_write_json(primary, scorecard_data)
            atomic_write_json(alias, scorecard_data)

    def save_session_turn(
        self,
        session_id: str,
        turn_entry: Dict[str, Any],
        history_key: str = "dialogue",
        additional_updates: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Atomically append a turn entry to a session and persist under session_lock."""
        clean_id = sanitize_identifier(session_id)
        with self.session_lock(clean_id):
            session_state = self.get_session(clean_id)
            if not session_state:
                raise KeyError(f"Session '{clean_id}' not found.")
            session_state.setdefault(history_key, []).append(turn_entry)
            if history_key == "dialogue":
                session_state.setdefault("turns", []).append(turn_entry)
            if additional_updates:
                session_state.update(additional_updates)
            self.save_session(clean_id, session_state)
            return session_state


    def log_exercise_turn(self, turn_record: Dict[str, Any]) -> None:
        """Append turn record to sessions/exercises.jsonl."""
        log_file = self.data_dir / "sessions" / "exercises.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file = log_file.with_suffix(".lock")
        with file_lock(lock_file):
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(turn_record) + "\n")

    # -------------------------------------------------------------------------
    # Resumes & Gap Analyses
    # -------------------------------------------------------------------------
    def get_active_resume(self) -> Optional[str]:
        resume_file = self.data_dir / "resumes" / "active_resume.md"
        if not resume_file.exists():
            return None
        return resume_file.read_text(encoding="utf-8")

    def save_active_resume(self, content: str) -> Path:
        target = self.data_dir / "resumes" / "active_resume.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def save_gap_analysis(self, analysis_id: str, data: Dict[str, Any]) -> None:
        clean_id = sanitize_identifier(analysis_id)
        path = self.data_dir / "resumes" / "gap_analyses" / f"{clean_id}.json"
        atomic_write_json(path, data)

    def get_gap_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        clean_id = sanitize_identifier(analysis_id)
        path = self.data_dir / "resumes" / "gap_analyses" / f"{clean_id}.json"
        return safe_read_json(path)

    # -------------------------------------------------------------------------
    # Telemetry
    # -------------------------------------------------------------------------
    def get_telemetry_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        telemetry_file = self.data_dir / "telemetry" / "usage_costs.jsonl"
        if not telemetry_file.exists():
            return []
        records = []
        lock_file = telemetry_file.with_suffix(".lock")
        with file_lock(lock_file):
            with open(telemetry_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except Exception:
                            pass
        if limit:
            return records[-limit:]
        return records


# Global default state instance
state = StateManager()
