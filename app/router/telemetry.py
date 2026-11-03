"""Telemetry logger and cost accounting writing to out-of-git JSONL store."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.config import settings


class TelemetryRecord(BaseModel):
    """Unified telemetry schema fulfilling both specification and test assertions."""

    telemetry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Provider & model metadata
    provider: str
    model: str

    # Tier fields (both aliases provided for test and spec compliance)
    execution_tier: str
    source_tier: str

    # Token usage (both aliases provided)
    input_tokens: int
    prompt_tokens: int
    output_tokens: int
    completion_tokens: int
    cached_tokens: int = 0
    thinking_tokens: int = 0

    # Latency / duration (both aliases provided)
    duration_ms: int
    latency_ms: int

    # Financial accounting
    estimated_cost_usd: float = 0.0
    nominal_value_usd: float = 0.0

    # Workflow context
    success: bool = True
    error_message: Optional[str] = None
    workflow_type: str = "general"


class TelemetryLogger:
    """Manages persistent appending of telemetry events into $LEARN_DATA_DIR/telemetry/usage_costs.jsonl."""

    def __init__(self, data_dir: Optional[Path] = None):
        target = (data_dir or settings.data_dir).expanduser().resolve()
        repo = settings.repo_root.resolve()
        if target.is_relative_to(repo):
            raise ValueError(
                f"Telemetry data directory {target} must not be inside repository root {repo} (§R4 invariant)"
            )
        self.data_dir = target
        self.telemetry_file = self.data_dir / "telemetry" / "usage_costs.jsonl"

    def log(
        self,
        provider: str,
        model: str,
        tier: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        estimated_cost_usd: float = 0.0,
        nominal_value_usd: float = 0.0,
        cached_tokens: int = 0,
        thinking_tokens: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        workflow_type: str = "general",
    ) -> TelemetryRecord:
        """Create and append an immutable JSONL telemetry record."""
        self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)

        record = TelemetryRecord(
            provider=provider,
            model=model,
            execution_tier=tier,
            source_tier=tier,
            input_tokens=input_tokens,
            prompt_tokens=input_tokens,
            output_tokens=output_tokens,
            completion_tokens=output_tokens,
            cached_tokens=cached_tokens,
            thinking_tokens=thinking_tokens,
            duration_ms=duration_ms,
            latency_ms=duration_ms,
            estimated_cost_usd=estimated_cost_usd,
            nominal_value_usd=nominal_value_usd,
            success=success,
            error_message=error_message,
            workflow_type=workflow_type,
        )

        with open(self.telemetry_file, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")

        return record

    def get_records(self) -> List[Dict[str, Any]]:
        """Query all recorded telemetry entries."""
        if not self.telemetry_file.exists():
            return []
        records = []
        with open(self.telemetry_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
        return records
