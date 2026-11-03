"""API router for topic exploration, listing, pinning, and durable learning capture."""

import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import settings
from app.core import (
    state,
    topic_loader,
    durable_capture,
    sanitize_identifier,
    ALLOWED_DOMAINS,
)

router = APIRouter(prefix="/topics", tags=["Topics"])


class PinRequest(BaseModel):
    priority: str = Field(default="high", pattern="^(high|medium|low)$")
    notes: Optional[str] = None


class DurableLearningCreate(BaseModel):
    title: str
    mental_model: str
    invariants: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    citable_sources: Optional[List[str]] = Field(default_factory=list)
    code_examples: Optional[str] = None
    target_level: str = "L6"
    tags: Optional[List[str]] = Field(default_factory=list)
    frontmatter_metadata: Optional[Dict[str, Any]] = None


@router.get("")
async def list_topics(domain: Optional[str] = Query(default="all")):
    """List all available curriculum topics, metadata, problem counts, and user status."""
    domain_filter = str(domain).lower().strip() if domain else "all"
    if domain_filter != "all" and domain_filter not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=400, detail=f"Invalid domain '{domain_filter}'; allowed domains are: {ALLOWED_DOMAINS}")
    try:
        topics = topic_loader.list_topics(domain_filter=domain_filter)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    pinned_slugs = {p.get("topic_id") or p.get("topic_slug") for p in state.get_pinned_topics()}
    ratings = state.get_subdomain_ratings()

    results = []
    for t in topics:
        slug = t["slug"]
        user_rating = ratings.get(slug, 0.0)
        user_status = "completed" if user_rating >= 4.0 else ("in_progress" if user_rating > 0.0 else "not_started")
        results.append({
            **t,
            "user_status": user_status,
            "user_rating": user_rating,
            "pinned": slug in pinned_slugs,
        })

    return {"topics": results}


@router.get("/pinned")
async def get_pinned():
    """Retrieve all pinned topics."""
    return {"pinned_topics": state.get_pinned_topics()}


@router.get("/{domain}/{topic_slug}")
async def get_topic_detail(domain: str, topic_slug: str):
    """Retrieve complete topic payload including fundamentals, references, rubrics, and exercises."""
    try:
        clean_domain = sanitize_identifier(domain).lower().strip()
        clean_slug = sanitize_identifier(topic_slug).lower().strip()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if clean_domain not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=400, detail=f"Invalid domain '{clean_domain}'; allowed domains are: {ALLOWED_DOMAINS}")

    detail = topic_loader.load_topic_detail(clean_domain, clean_slug)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Topic '{clean_slug}' not found under domain '{clean_domain}'.")

    ratings = state.get_subdomain_ratings()
    pinned_slugs = {p.get("topic_id") or p.get("topic_slug") for p in state.get_pinned_topics()}

    detail["user_rating"] = ratings.get(clean_slug, 0.0)
    detail["pinned"] = clean_slug in pinned_slugs

    return detail


@router.post("/{domain}/{topic_slug}/pin")
async def pin_topic_endpoint(domain: str, topic_slug: str, req: PinRequest):
    """Pin a topic to the user's priority study dashboard."""
    try:
        clean_domain = sanitize_identifier(domain)
        clean_slug = sanitize_identifier(topic_slug)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = state.pin_topic(topic_slug=clean_slug, domain=clean_domain, priority=req.priority, notes=req.notes)
    return result


@router.delete("/{domain}/{topic_slug}/pin")
async def unpin_topic_endpoint(domain: str, topic_slug: str):
    """Unpin a topic from the user's dashboard."""
    try:
        clean_domain = sanitize_identifier(domain)
        clean_slug = sanitize_identifier(topic_slug)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    removed = state.unpin_topic(clean_slug)
    return {"status": "unpinned", "topic_id": clean_slug, "domain": clean_domain, "found": removed}


@router.post("/{topic_slug}/pin")
async def pin_topic_direct(topic_slug: str, req: PinRequest):
    """Compatibility route: Pin topic without specifying domain in path."""
    try:
        clean_slug = sanitize_identifier(topic_slug)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = state.pin_topic(topic_slug=clean_slug, priority=req.priority, notes=req.notes)
    return result


@router.delete("/{topic_slug}/pin")
async def unpin_topic_direct(topic_slug: str):
    """Compatibility route: Unpin topic without specifying domain in path."""
    try:
        clean_slug = sanitize_identifier(topic_slug)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    removed = state.unpin_topic(clean_slug)
    return {"status": "unpinned", "topic_id": clean_slug, "found": removed}



@router.post("/{domain}/{topic_slug}/learnings")
async def create_durable_learning(domain: str, topic_slug: str, req: DurableLearningCreate):
    """Commit distilled learning breakthrough to canonical git-versioned markdown note."""
    try:
        result = durable_capture.record_learning(
            topic_slug=topic_slug,
            title=req.title,
            mental_model=req.mental_model,
            invariants=req.invariants,
            domain=domain,
            citable_sources=req.citable_sources,
            code_examples=req.code_examples,
            notes=req.notes,
            target_level=req.target_level,
            tags=req.tags,
            frontmatter_metadata=req.frontmatter_metadata,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{topic_slug}/learnings")
async def create_durable_learning_direct(topic_slug: str, req: DurableLearningCreate):
    """Compatibility route: Commit distilled learning breakthrough without domain in path."""
    try:
        result = durable_capture.record_learning(
            topic_slug=topic_slug,
            title=req.title,
            mental_model=req.mental_model,
            invariants=req.invariants,
            citable_sources=req.citable_sources,
            code_examples=req.code_examples,
            notes=req.notes,
            target_level=req.target_level,
            tags=req.tags,
            frontmatter_metadata=req.frontmatter_metadata,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
