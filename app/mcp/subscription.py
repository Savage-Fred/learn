"""Client-owned teaching and assessment: curriculum and persistence, no model calls."""

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.core.durable_capture import DurableCaptureEngine
from app.core.schemas import DifficultyTier
from app.core.state import StateManager, atomic_write_json, file_lock, sanitize_identifier
from app.core.topic_loader import TopicLoader


def create_server() -> MCPServer:
    server = MCPServer(
        "learn-mcp",
        instructions=(
            "You teach and assess using the model in the connected AI client. "
            "Learn never invokes another model. Read topic curriculum and exercises, "
            "ask the learner to answer, evaluate against the supplied rubric, then "
            "record your assessment with evidence. Scores are client judgments, "
            "not independently verified grades. Use one stable assessment_id per "
            "answer; retry with the same ID. Save only distilled technical knowledge "
            "as durable learning; personal answers and grades belong in assessments."
        ),
    )
    loader = TopicLoader()
    state = StateManager()
    ledger = settings.data_dir / "mcp_assessments.json"
    read_only = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
    write = ToolAnnotations(destructiveHint=False, openWorldHint=False)

    def topic(topic_id: str) -> dict:
        resolved = loader.resolve_topic_dir(topic_id)
        if not resolved:
            raise ValueError(f"Unknown topic: {topic_id}")
        domain, directory = resolved
        if not directory.resolve().is_relative_to(loader.topics_root):
            raise ValueError("Topic resolves outside curriculum")
        detail = loader.load_topic_detail(domain, directory.name)
        if not detail:
            raise ValueError(f"Missing curriculum: {topic_id}")
        return detail

    def assessments() -> dict:
        # Fail on corrupt history rather than replacing it with an empty ledger.
        return json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else {}

    @server.tool(annotations=read_only)
    def learn_list_topics() -> dict:
        """List available curriculum topics; use their slugs with the reading tools."""
        return {"topics": loader.list_topics()}

    @server.tool(annotations=read_only)
    def learn_get_topic(topic_id: str) -> dict:
        """Read a topic's fundamentals, citations, rubric and complete exercises."""
        return topic(topic_id)

    @server.tool(annotations=read_only)
    def learn_get_exercise(topic_id: str, level: str = "starter") -> dict:
        """Read a real curriculum exercise and rubric; the connected AI evaluates it."""
        detail = topic(topic_id)
        tier = DifficultyTier.from_str(level)
        exercise = next(
            (e for e in detail["exercises"] if e["filename"] == f"{tier.value}.md"), None
        )
        if not exercise:
            raise ValueError(f"No curriculum exercise at {level}")
        return {
            "topic_id": detail["slug"],
            "exercise_id": f"{detail['slug']}/{tier.value}",
            "difficulty_level": tier.short_name,
            "prompt": exercise["content"],
            "rubric": detail["rubric"],
            "references": detail["references"],
            "assessment_source": "connected_ai_client",
        }

    @server.tool(annotations=read_only)
    def learn_get_progress(topic_id: str | None = None) -> dict:
        """Read shared pins, existing app ratings and recent client assessments."""
        canonical = topic(topic_id)["slug"] if topic_id else None
        with file_lock(ledger.with_suffix(".json.lock")):
            records = list(assessments().values())
        records = [r for r in records if not canonical or r["topic_id"] == canonical]
        recent = sorted(records, key=lambda r: r["created_at"], reverse=True)[:20]
        return {
            "pinned_topics": state.get_pinned_topics(),
            "app_ratings": state.get_subdomain_ratings(),
            "assessments": recent,
            "assessment_count": len(records),
            "assessment_source": "connected_ai_client",
        }

    @server.tool(annotations=ToolAnnotations(
        destructiveHint=False, idempotentHint=True, openWorldHint=False
    ))
    def learn_record_assessment(
        assessment_id: Annotated[str, Field(min_length=1, max_length=100)],
        topic_id: str,
        exercise_id: str,
        score: Annotated[float, Field(ge=1, le=5, allow_inf_nan=False, strict=True)],
        feedback: Annotated[str, Field(min_length=1, max_length=4000)],
        learner_response: Annotated[str, Field(min_length=1, max_length=50000)],
    ) -> dict:
        """Save the connected AI's rubric-based score and evidence exactly once per ID.

        This records a client judgment without invoking inference or changing the
        web app's legacy proficiency ratings. Reusing an ID for different content fails.
        """
        clean_id = sanitize_identifier(assessment_id)
        detail = topic(topic_id)
        valid_ids = {f"{detail['slug']}/{e['exercise_id']}" for e in detail["exercises"]}
        if exercise_id not in valid_ids:
            raise ValueError("Exercise does not belong to this topic's curriculum")
        if not feedback.strip() or not learner_response.strip():
            raise ValueError("Feedback and learner response must not be blank")
        record = {
            "assessment_id": clean_id, "topic_id": detail["slug"],
            "exercise_id": exercise_id, "score": score, "feedback": feedback,
            "learner_response": learner_response, "assessment_source": "connected_ai_client",
        }
        with file_lock(ledger.with_suffix(".json.lock")):
            history = assessments()
            previous = history.get(clean_id)
            if previous:
                if any(previous[k] != v for k, v in record.items()):
                    raise ValueError("Assessment ID already exists with different content")
                return {"status": "recorded", "assessment": previous}
            record["created_at"] = datetime.now(timezone.utc).isoformat()
            history[clean_id] = record
            atomic_write_json(ledger, history)
        return {"status": "recorded", "assessment": record}

    @server.tool(annotations=write)
    def learn_pin_topic(
        topic_id: str, priority: Literal["high", "medium", "low"] = "high", notes: str = ""
    ) -> dict:
        """Pin an existing topic for later study, shared across connected clients."""
        detail = topic(topic_id)
        return state.pin_topic(detail["slug"], detail["domain"], priority, notes)

    @server.tool(annotations=read_only)
    def learn_get_pinned_topics() -> dict:
        """Read the user's shared study queue."""
        return {"pinned_topics": state.get_pinned_topics()}

    @server.tool(annotations=write)
    def learn_record_durable_learning(
        topic_id: str, title: str, mental_model: str, invariants: list[str], notes: str = ""
    ) -> dict:
        """Write distilled technical knowledge to topic markdown, without a git commit.

        Do not include private assessment transcripts, scores or resume content.
        """
        detail = topic(topic_id)
        return DurableCaptureEngine().record_learning(
            detail["slug"], title, mental_model, invariants, detail["domain"], notes=notes
        )

    return server


def create_http_app(server: MCPServer, token: str | None = None):
    """Keep the SDK's protocol and DNS-rebinding checks; authenticate every request."""
    import secrets

    hosts = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*", "[::1]", "[::1]:*"]
    hosts.extend(h.strip() for h in os.getenv("LEARN_MCP_ALLOWED_HOSTS", "").split(",") if h.strip())
    app = server.streamable_http_app(
        json_response=True, stateless_http=True,
        transport_security=TransportSecuritySettings(
            allowed_hosts=hosts,
            allowed_origins=[
                "http://127.0.0.1", "http://127.0.0.1:*", "http://localhost",
                "http://localhost:*", "http://[::1]", "http://[::1]:*",
            ],
        ),
    )

    async def authenticate(request, call_next):
        if token and not secrets.compare_digest(
            request.headers.get("authorization", "").encode(), f"Bearer {token}".encode()
        ):
            return JSONResponse(
                {"error": "Invalid or missing bearer token"}, status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="learn-mcp"'},
            )
        return await call_next(request)

    app.add_middleware(BaseHTTPMiddleware, dispatch=authenticate)
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8797)
    args = parser.parse_args()
    if args.transport == "stdio":
        create_server().run()
    else:
        token = (settings.api_token or "").strip() or None
        if args.host not in ("127.0.0.1", "::1", "localhost") and not token:
            parser.error("Non-loopback HTTP binding requires LEARN_API_TOKEN")
        import uvicorn
        uvicorn.run(create_http_app(create_server(), token), host=args.host, port=args.port)
