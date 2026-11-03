# Savage-Fred/learn

Local-first, Tailnet-reachable technical learning and L4–L6 interview preparation platform.

## Overview

`Savage-Fred/learn` is an engineering-first platform designed for staff-level (L4–L6) interview preparation across top-tier AI labs and FAANG companies (OpenAI, Google/DeepMind, Anthropic, Meta, Databricks, Netflix, Apple).

The platform orchestrates Claude, Codex (ChatGPT/Astra/Sol), and Gemini/Antigravity using a hybrid subscription-first execution architecture (invoking installed local CLI harnesses `claude`, `codex`, and `agy` alongside an MCP server, with direct API-key fallback and offline mock execution).

## Key Architectural Principles

1. **Strict Application & Domain Separation**: Platform code lives strictly in `app/`. Pedagogical knowledge domains live in dedicated root directories (`leetcode/`, `system-design/`, `security/`, `privacy-engineering/`).
2. **Dual Storage Boundary (The Clean-Tree Invariant)**: Curricula, invariants, and durable markdown learnings are Git-versioned in the repository. Personal user state (subdomain ratings, interview transcripts, quiz history, scorecards, resumes, telemetry) is persisted strictly outside Git in an XDG data directory (`$LEARN_DATA_DIR` or `~/.local/share/learn/`).
3. **Subscription-First, Zero-Cost Default**: Inference prioritizes active user subscriptions via local CLI harnesses (`claude`, `codex`, `agy`) in headless mode.
4. **Subprocess Isolation**: CLI harnesses run in dedicated OS session groups (`os.setsid`) with strict timeouts and `SIGTERM`/`SIGKILL` process-group cleanup.
5. **Tailnet Mesh Reachability**: The server binds to `0.0.0.0` or `127.0.0.1` on port `8795`, exposing a responsive Web UI and SSE MCP endpoint accessible locally and over Tailscale.

## Core UX Flows

1. **On-Demand Deep-Dive & Invariant Queries**: Instant axiomatic explanations with 5-section high-density format (Mental Model, Invariants, Code Pattern, Citations, Interview Probes).
2. **Topic Pinning & Priority Dashboard**: Priority queue with target mastery dates and urgency tracking.
3. **Rabbit-Hole Distillation to Durable Markdown**: Crystallize ad-hoc explorations into version-controlled markdown notes with YAML frontmatter in `<domain>/<topic>/learnings/`.
4. **Adaptive Exercise Progression (4-Tier Ladder)**: Real-time difficulty scaling from Tier 1 (Starter) to Tier 4 (Staff L6) with Elo-based rating adjustment and targeted invariant scaffolding.
5. **Full-Scale Mock Interview Engine**: 45–60 minute simulations in `hints` mode (3-tier progressive Socratic hints) or `no-hints` mode (timed adversarial stress probing).
6. **Role & Resume Alignment**: Job description ingestion, 0–100% fit scoring, gap matrix calculation, and customized 5-round mock loop planning.

## Installation & Development

```bash
# Setup virtual environment with Python 3.13
uv venv .venv --python 3.13
source .venv/bin/activate

# Install package in editable mode with development dependencies
uv pip install -e ".[dev]"

# Run test suite
pytest app/tests/test_foundation.py -v
```

## Documentation

- [System Architecture](docs/architecture.md)
- [UX Specification & Rubric](docs/ux-spec.md)
- [Multi-Agent Review Gate Receipts](docs/review-gate-receipts.md)

## License

Apache-2.0
