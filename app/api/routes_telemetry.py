"""API router for usage telemetry, token metrics, and cost accounting."""

from typing import Any, Dict, List
from fastapi import APIRouter

from app.core import state

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])


@router.get("/summary")
async def get_telemetry_summary():
    """Retrieve summarized telemetry metrics, cost savings, and provider breakdown."""
    records = state.get_telemetry_records()

    total_tokens = sum(r.get("input_tokens", 0) + r.get("output_tokens", 0) for r in records)
    total_cost = sum(r.get("estimated_cost_usd", 0.0) for r in records)
    total_nominal = sum(r.get("nominal_value_usd", 0.0) for r in records)

    by_provider: Dict[str, int] = {}
    by_tier: Dict[str, int] = {}
    by_workflow: Dict[str, int] = {}

    for r in records:
        prov = r.get("provider", "unknown")
        by_provider[prov] = by_provider.get(prov, 0) + 1

        tier = r.get("execution_tier") or r.get("source_tier") or "unknown"
        by_tier[tier] = by_tier.get(tier, 0) + 1

        wf = r.get("workflow_type", "general")
        by_workflow[wf] = by_workflow.get(wf, 0) + 1

    return {
        "total_requests": len(records),
        "total_tokens": total_tokens,
        "total_input_tokens": sum(r.get("input_tokens", 0) for r in records),
        "total_output_tokens": sum(r.get("output_tokens", 0) for r in records),
        "total_estimated_cost_usd": round(total_cost, 4),
        "total_nominal_value_usd": round(total_nominal, 4),
        "breakdown_by_provider": by_provider,
        "breakdown_by_tier": by_tier,
        "breakdown_by_workflow": by_workflow,
        "recent_events": records[-20:] if records else [],
    }
