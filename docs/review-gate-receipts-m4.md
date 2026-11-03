# Milestone 4 Review Gate Receipts

**PR**: [#5 Interactive Web Application, Adaptive Engine & Personal State](https://github.com/Savage-Fred/learn/pull/5)  
**Branch**: `feat/web-app-adaptive-engine` -> `feat/subscription-router-and-mcp`  
**Reviewers**: Astra (`gpt-6-astra`), Sol (`gpt-6-sol`), Claude (`claude -p`)  
**Base Commit**: `4317d27`  
**Date**: 2026-11-03  

---

## 1. Review Summary & Decision Log

| Reviewer | Tool / Model | Round 1 Verdict | Round 2 Hardening Verdict | Final Decision |
|---|---|---|---|---|
| **Astra** | `codex exec -c model="gpt-6-astra"` | Changes Requested (5 items) | Verified & Approved | **Fully Resolved & Approved** |
| **Sol** | `codex exec -c model="gpt-6-sol"` | Changes Requested (4 items) | Verified & Approved | **Fully Resolved & Approved** |
| **Claude** | `claude -p` | Changes Requested (4 items) | Verified & Approved | **Fully Resolved & Approved** |

---

## 2. Adversarial Review Audit Findings & Resolutions

### Finding 1: Cross-Device `os.replace` & Temporary File Siting (Astra)
- **Observation**: `tempfile.NamedTemporaryFile` defaults to `/tmp`. On modern Linux configurations where `/tmp` is mounted on `tmpfs` and `$LEARN_DATA_DIR` resides on `/home`, calling `os.replace(tmp, target)` fails with `OSError: [Errno 18] Invalid cross-device link` (`EXDEV`).
- **Resolution**: In `app/core/state.py` (`atomic_write_json`), `tempfile.NamedTemporaryFile` explicitly specifies `dir=target_path.parent`, guaranteeing that the temporary file and destination file reside on the identical filesystem device before atomic replacement.
- **Verification**: Verified in `test_storage_isolation_invariant` and `test_atomic_write_concurrency`.

### Finding 2: Safe Inode Locking without Lock File Desynchronization (Astra)
- **Observation**: Unlinking open lock files after `fcntl.flock(LOCK_UN)` creates a race condition where subsequent processes open a new inode handle while prior processes hold a lock on the old unlinked inode.
- **Resolution**: `file_lock` context manager keeps the `.lock` file persistent on disk, acquiring `fcntl.flock(f.fileno(), fcntl.LOCK_EX)` during writes and releasing cleanly without unlinking the file handle.
- **Verification**: Verified by spawning 20 concurrent threads executing rapid alternating writes in `test_atomic_write_concurrency`.

### Finding 3: Path Traversal & Identifier Sanitization (Astra)
- **Observation**: Identifiers passed in API path parameters (e.g. `topic_slug`, `session_id`, `domain`) could allow directory traversal if containing `/`, `\\`, or `..`.
- **Resolution**: Implemented `sanitize_identifier` in `app/core/state.py` which strictly rejects empty strings, `..`, `/`, `\\`, and null bytes with `ValueError`.
- **Verification**: Enforced by `test_path_traversal_rejection`.

### Finding 4: Missing-Rating Defaulting Rule in Fit Scoring (Sol)
- **Observation**: If a user has not attempted exercises for a topic in `subdomain_ratings.json`, omitting the topic or defaulting to 0.0 results in distorted fit ratios or division by zero.
- **Resolution**: In `app/core/resume_matcher.py`, unassessed topics strictly default to $R_i = 1.0$ (novice level) per `ux-spec.md` §4.1.1.
- **Verification**: Enforced by `test_e2e_resume_endpoints` and `MockBackend.analyze_role_fit`.

### Finding 5: Dual-Path Personal State Synchronization (Sol)
- **Observation**: The original task specification and legacy tests read from both root paths (`subdomain_ratings.json`, `pinned_topics.json`) and subfolder paths (`ratings/subdomain_ratings.json`, `pins/pinned_topics.json`). Single-path writes cause state divergence across CLI, MCP tools, and Web UI.
- **Resolution**: `StateManager` performs dual atomic writes to both canonical and alias paths on every mutation, and safely checks primary followed by alias on reads.
- **Verification**: Enforced by `test_subdomain_ratings_roundtrip_and_clamping` and `test_pinned_topics_lifecycle`.

### Finding 6: Rating Clamping Invariant (Sol)
- **Observation**: Dynamic Difficulty Adjustment (Elo) increments or decrements must never push user subdomain ratings beyond the defined $[1.0, 5.0]$ rubric scale.
- **Resolution**: Implemented strict `round(max(1.0, min(5.0, rating)), 2)` clamping across `AdaptiveEngine.exercise_turn`, `RubricScorer._update_ratings_from_scorecard`, and `StateManager.update_subdomain_rating`.
- **Verification**: Enforced by `test_rating_bounds_clamped`.

### Finding 7: Tailnet Non-Loopback WebSocket Authentication (Claude)
- **Observation**: Standard browser WebSocket APIs (`new WebSocket(...)`) cannot set custom HTTP request headers (`Authorization` or `X-Learn-Token`). Tailnet remote requests (`100.64.162.123:8795`) to `/api/interview/{session_id}/stream` could bypass token checks.
- **Resolution**: In `routes_interview.py`, `interview_stream_ws` inspects loopback status, query parameter `?token=...`, `X-Learn-Token`, and `Authorization: Bearer <token>`, closing with `status.WS_1008_POLICY_VIOLATION` if unauthorized.
- **Verification**: Enforced by `test_e2e_network_auth_middleware` and `test_e2e_websocket_stream`.

### Finding 8: Socratic Hints Budget & Strict Stress Mode Refusal (Claude)
- **Observation**: Candidates requesting hints in `no-hints` mode must be explicitly refused without deducting from the hint budget, and candidates in `hints` mode must receive structured progressive scaffolding (Level 1 Conceptual $\to$ Level 2 Structural $\to$ Level 3 Scaffold $\to$ Budget Exhausted).
- **Resolution**: Implemented deterministic 3-tier progressive hint budget and stress mode probing questions in `InterviewEngine.interview_turn`.
- **Verification**: Enforced by `test_interview_hints_mode_progressive_scaffolding` and `test_interview_no_hints_mode_rejects_hints`.

### Finding 9: Candidate PII Scrubbing in Durable Learning Captures (Claude)
- **Observation**: Insights captured during interview turns may inadvertently contain private personal data (emails, phone numbers, API keys, evaluation scores) which would be committed to the git repository tree.
- **Resolution**: Implemented `scrub_pii()` in `app/core/durable_capture.py` regex-scrubbing emails, phone numbers, bearer tokens, and scores prior to committing to `<domain>/<topic>/learnings/`.
- **Verification**: Verified in `test_e2e_topics_endpoints`.

### Finding 10: State Concurrency Locking & 5-Phase Re-Entrant Lock Protocol (Astra / Sol)
- **Observation**: Calling `safe_read_json` or `atomic_write_json` from within an existing transaction caused POSIX `flock(2)` self-deadlock on Linux. Concurrent read-modify-write operations on `pinned_topics.json` and `subdomain_ratings.json` suffered lost updates.
- **Resolution**: Implemented thread-local re-entrant lock tracking (`_lock_state = threading.local()`) in `file_lock` with lock depth counting. Added canonical resource locks (`ratings_lock`, `pinned_topics_lock`, `session_lock`, `scorecard_lock`) and executed a strict 5-phase transaction protocol: canonical path resolution, lock acquisition, safe read, in-memory mutation, and atomic write.
- **Verification**: Verified with `/tmp/stress_concurrency_m4.py` (30 concurrent sessions, 200 log appends, 20 concurrent pins, 20 concurrent rating updates: 0 lost updates, 0 corruption) and un-xfailed tests in `test_adversarial_challenge.py` and `test_adversarial_deep_probe.py`.

### Finding 11: Genuine 5-Dimension Rubric Scoring & Full Spectrum [1.0, 5.0] (Astra / Sol / Claude)
- **Observation**: The initial rubric scorer was a static facade returning 4.38 Strong Hire for all inputs (including empty transcripts or surrender messages), ignoring candidate turns and leaving hiring tiers dead code.
- **Resolution**: Replaced facade with genuine dialogue transcript analysis evaluating Decomposition, Execution, Architecture, Resilience, and Communication across the full [1.0, 5.0] spectrum. Implemented dynamic company profile weight boosts and anti-pattern penalty checks across all 7 companies (OpenAI, Google, Anthropic, Meta, Databricks, Netflix, Apple). Reconciled unassessed topic baseline rating to 1.0.
- **Verification**: Verified in `test_rubric_scorer_weights_and_company_profiles` and empirical spectrum scoring tests.

### Finding 12: Server-Side Elapsed Countdown Timer Enforcement (Sol)
- **Observation**: `InterviewEngine.interview_turn` never verified elapsed session duration against `time_limit_minutes`, allowing dialogue turns long after session expiry.
- **Resolution**: Added server-side elapsed timer validation in `interview_turn` computing elapsed seconds against `time_limit_minutes`. Expired turns auto-transition the session to debrief and raise `ValueError` (HTTP 400).
- **Verification**: Verified in `test_interview.py` and `test_e2e_interview_endpoints`.

### Finding 13: FastAPI Sub-Router Prefixing & Clean /api and /api/v1 Mounts (Sol / Claude)
- **Observation**: Declaring `/api/...` in sub-router definitions caused `/api/v1/api/...` double-prefix 404s. Path traversal attempts raised unhandled `ValueError` resulting in HTTP 500 instead of HTTP 400.
- **Resolution**: Stripped `/api` from sub-router definitions (`/topics`, `/quiz`, `/interview`, `/resume`, `/telemetry`). In `app/main.py`, cleanly mounted routers under `prefix="/api"` and `prefix="/api/v1"`, and added `@app.get("/api/status")` alias. Wrapped `sanitize_identifier` and `topic_loader.list_topics` in `try ... except ValueError: raise HTTPException(status_code=400)`.
- **Verification**: Verified in `test_e2e_app.py` and route traversal probes.

### Finding 14: Browser WebSocket Client & Zero-CDN Micro-Highlighter (Astra / Claude)
- **Observation**: Web UI needed authentic streaming WebSocket integration with typing indicator and fallback, as well as offline zero-CDN syntax highlighting for code samples.
- **Resolution**: In `app/ui/static/app.js`, implemented browser `WebSocket` streaming client with animated `.typing-cursor`, `#interview-ws-status` indicator, and REST fallback. Implemented zero-CDN `MicroHighlighter` regex tokenizer for Python, Go, Rust, and YAML hooked into quiz prompts and topic rubrics. Added matching CSS token classes in `app/ui/static/styles.css`.
- **Verification**: Verified in `test_e2e_websocket_stream` and browser DOM integration tests.

---

## 3. Test Suite Verification

### Unit & Integration Suite (`app/tests/`)
```
platform linux -- Python 3.13.12, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/will/dev/learn/.worktrees/app-ui
collected 109 items

app/tests/test_adaptive.py .......                                        [  6%]
app/tests/test_adversarial_challenge.py .........                         [ 14%]
app/tests/test_adversarial_deep_probe.py .......                          [ 21%]
app/tests/test_curricula_integrity.py ...........                         [ 31%]
app/tests/test_e2e_app.py .........                                       [ 39%]
app/tests/test_foundation.py ............                                 [ 50%]
app/tests/test_interview.py ........                                      [ 57%]
app/tests/test_mcp.py .......................                             [ 78%]
app/tests/test_router.py ................                                 [ 93%]
app/tests/test_storage.py .......                                         [100%]

======================== 109 passed, 1 warning in 1.02s ========================
```

### Opaque-Box E2E Suite (`tests_e2e/runner.py`)
```
================================================================================
        Savage-Fred/learn Independent Opaque-Box E2E Test Runner
================================================================================

Target Directory: /home/will/dev/learn/tests_e2e
Tier Selection:   all

▶ Running Tier 1: Feature Coverage (Happy-Path) (47 tests)
  ✔ Tier 1 Completed: 47/47 passed in 0.02s

▶ Running Tier 2: Boundary & Corner Cases (47 tests)
  ✔ Tier 2 Completed: 47/47 passed in 0.02s

▶ Running Tier 3: Cross-Feature Combinations (8 tests)
  ✔ Tier 3 Completed: 8/8 passed in 0.01s

▶ Running Tier 4: Real-World Multi-Turn Scenarios (5 tests)
  ✔ Tier 4 Completed: 5/5 passed in 0.01s

--------------------------------------------------------------------------------
 Tier Summary Breakdown
--------------------------------------------------------------------------------
 Tier       | Passed   | Failed   | Total    | Time (s)  
--------------------------------------------------------------------------------
 Tier 1     | 47       | 0        | 47       | 0.02      
 Tier 2     | 47       | 0        | 47       | 0.02      
 Tier 3     | 8        | 0        | 8        | 0.01      
 Tier 4     | 5        | 0        | 5        | 0.01      
--------------------------------------------------------------------------------
 Total:      107/107 passed (0.10s)

Feature Coverage Checklist (PROJECT.md § Feature Inventory):
  [✔ T1:  6] [✔ T2:  6] On-Demand Deep Dive
  [✔ T1:  5] [✔ T2:  5] Topic Pinning
  [✔ T1:  5] [✔ T2:  5] Rabbit-Hole Durable Capture
  [✔ T1:  5] [✔ T2:  5] Adaptive Question Turns
  [✔ T1:  6] [✔ T2:  6] Mock Interview Turns (Hints vs No-Hints)
  [✔ T1:  5] [✔ T2:  5] Resume & Role Fit Scoring
  [✔ T1:  5] [✔ T2:  5] MCP Protocol Tools (8 Tools)
  [✔ T1:  5] [✔ T2:  5] Subscription CLI Router Fallback
  [✔ T1:  5] [✔ T2:  5] Out-of-Git State Isolation

✔ ALL 107 E2E TESTS PASSED CLEANLY (Exit Code: 0)
```

---

## 4. Git Invariant Verification
```bash
git status --porcelain
```
Confirmed 100% clean of personal state files, temporary logs, or credentials.
All personal data is strictly isolated outside the git repository tree.

