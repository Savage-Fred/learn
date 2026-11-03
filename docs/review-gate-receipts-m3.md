# Milestone 3 Review Gate Receipts

**PR**: [#4 Subscription Multi-Model Router, Local MCP Server & CLI Plugins](https://github.com/Savage-Fred/learn/pull/4)  
**Branch**: `feat/subscription-router-and-mcp` -> `feat/topic-curricula-seed`  
**Reviewers**: Astra (`gpt-6-astra`), Sol (`gpt-6-sol`), Claude (`claude -p`)  
**Base Commit**: `74193d5`  
**Date**: 2026-11-03  

---

## 1. Review Summary & Decision Log

| Reviewer | Tool / Model | Round 1 Verdict | Round 2 Hardening Verdict | Final Decision |
|---|---|---|---|---|
| **Astra** | `codex exec -c model="gpt-6-astra"` | Changes Requested (9 items) | Verified & Approved | **Fully Resolved & Approved** |
| **Sol** | `codex exec -c model="gpt-6-sol"` | Changes Requested (4 items) | Verified & Approved | **Fully Resolved & Approved** |
| **Claude** | `claude -p` | Changes Requested (6 items) | Verified & Approved | **Fully Resolved & Approved** |

---

## 2. Adversarial Review Audit Findings & Resolutions

### Finding 1: Watchdog Descendant Process Group Reaping
- **Observation**: If a process group leader exited upon receiving `SIGTERM`, `proc.communicate(timeout=grace_period)` returned, but grandchildren that ignored `SIGTERM` remained alive and orphaned under init.
- **Resolution**: Updated `SubprocessWatchdog.run_sync` and `run_async` to unconditionally send `signal.SIGKILL` to the process group (`os.killpg(pgid, signal.SIGKILL)`) whenever the timeout expires, guaranteeing that all child and grandchild processes in the session group are terminated.
- **Verification**: Verified with live subprocess test spawning SIGTERM-ignoring grandchildren; confirmed 100% clean termination without zombie or background leaks. Enforced in `test_watchdog_timeout_sigterm_escalation_to_sigkill`.

### Finding 2: Async Watchdog Task Cancellation Safety
- **Observation**: When an async caller cancelled `SubprocessWatchdog.run_async`, the underlying subprocess group was not immediately killed, leaving dangling background processes.
- **Resolution**: Wrapped the process communication loop in a `try...except asyncio.CancelledError:` block that immediately kills the process group with `SIGKILL` and awaits process exit before re-raising the cancellation.
- **Verification**: Tested async cancellation under event loop interruption.

### Finding 3: MCP Path Traversal & Storage Boundary Containment
- **Observation**: In Python's `pathlib.Path`, `/data_dir / '/etc/passwd'` evaluates to `'/etc/passwd'`. An attacker passing `/` or `..` in `session_id` or `domain` could escape local storage sandboxes.
- **Resolution**: 
  - In `_handle_run_mock_interview_turn`: sanitized `session_id = Path(str(session_id)).name`, rejected `/`, `\\`, and `..`, and asserted that the resulting file path is strictly relative to `settings.data_dir`.
  - In `_handle_record_durable_learning`: restricted `domain` strictly to `["leetcode", "system-design", "security", "privacy-engineering"]` and asserted containment within `settings.topics_root`.
- **Verification**: Enforced by regression tests `test_tool_mock_interview_path_traversal_rejected` and `test_tool_durable_learning_invalid_domain_rejected`.

### Finding 4: Model Override Propagation in CLI Harnesses
- **Observation**: `ClaudeHarness` and `AgyHarness` did not propagate caller-specified model overrides to their respective CLIs.
- **Resolution**: Updated `ClaudeHarness._build_cmd` to append `["--model", model]` when supplied, and `AgyHarness._build_cmd` to append `["--model", model]`.
- **Verification**: Enforced by `test_claude_and_agy_model_override`.

### Finding 5: Codex Harness Failure Event Detection
- **Observation**: `CodexHarness._parse_output` parsed JSONL lines but did not detect `turn.failed` error events, which could prevent the router from initiating a fallback cascade.
- **Resolution**: Explicitly checked for `etype == "turn.failed"` in the JSONL stream and raised `RuntimeError` on failure to trigger immediate cascade to Tier 2 (API) or Tier 3 (Mock). Also verified `res.exit_code == 0`.
- **Verification**: Enforced by `test_codex_turn_failed_event_raises_and_cascades`.

### Finding 6: Direct API Async Execution Fidelity
- **Observation**: `DirectApiHarness._call_api_async` called `_call_api_sync`, performing synchronous blocking I/O on the asyncio event loop.
- **Resolution**: Implemented genuine asynchronous HTTP POST calls using `await client.post(...)` for both Anthropic and OpenAI API fallbacks.
- **Verification**: Enforced by `test_direct_api_async_execution`.

### Finding 7: JSON-RPC Defensive Parsing & Ping Method
- **Observation**: `MCPServer.handle_request` assumed `payload` was always a valid `dict`, causing `AttributeError` on non-dict inputs or null params. Furthermore, standard MCP `ping` was unhandled.
- **Resolution**: Validated `isinstance(payload, dict)` and `isinstance(params, dict)`. Added `ping` method returning empty object `{}`. Handled all `notifications/*` methods returning `None` per JSON-RPC 2.0.
- **Verification**: Enforced by `test_mcp_ping_and_notifications` and `test_mcp_invalid_payload_and_params`.

### Finding 8: SSE Session Queue Leak Prevention & Origin Header Validation
- **Observation**: In `app/mcp/transports/sse.py`, if an SSE connection was severed during handshake before the event loop, the session queue remained in `active_sessions`. Additionally, browser clients on local network could execute cross-origin requests.
- **Resolution**: Placed the initial endpoint publication yield inside the `try...finally:` block to ensure `active_sessions.pop(session_id, None)` is always called. Added `_is_allowed_origin` validator rejecting untrusted origins with HTTP 403 Forbidden.
- **Verification**: Enforced by `test_sse_origin_header_validation`.

### Finding 9: Adaptive Exercise & Job Description Heuristics
- **Observation**: Trivial repetitive strings (e.g. `'x' * 30`) passed adaptive exercise grading. Unrelated job descriptions received default high base scores.
- **Resolution**: Added entropy/diversity checks (`unique_chars > 4`) and rejection of low-effort tokens in adaptive exercises. Assigned fit score of 25.0% for job descriptions with zero skill matches.
- **Verification**: Enforced by `test_tool_adaptive_exercise_gibberish_rejected` and `test_tool_analyze_job_description_zero_match`.

### Finding 10: Plugin Interpreter Portability
- **Observation**: Plugin configurations referenced generic `python` command, which may resolve to Python 2.7 or fail in non-interactive PATHs on Debian/Ubuntu systems.
- **Resolution**: Updated `claude-code/.mcp.json`, `claude/.mcp.json`, `codex/config_snippet.toml`, and `antigravity/mcp/learn.json` to explicitly use `python3`.
- **Verification**: Tested invocation with `python3 -m app.mcp` across all transports.

---

## 3. Test Suite Verification

### Unit & Integration Suite (`app/tests/`)
```
platform linux -- Python 3.13.12, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/will/dev/learn/.worktrees/routing-and-mcp
collected 62 items

app/tests/test_curricula_integrity.py ...........                         [ 17%]
app/tests/test_foundation.py ............                                 [ 37%]
app/tests/test_mcp.py .......................                             [ 74%]
app/tests/test_router.py ................                                 [100%]

============================== 62 passed in 0.76s ==============================
```

### Opaque-Box E2E Suite (`tests_e2e/runner.py`)
```
================================================================================
        Savage-Fred/learn Independent Opaque-Box E2E Test Runner
================================================================================
Target Directory: /home/will/dev/learn/tests_e2e
Tier Selection:   all

▶ Running Tier 1: Feature Coverage (Happy-Path) (47 tests) -> 47/47 passed (0.02s)
▶ Running Tier 2: Boundary & Corner Cases (47 tests)       -> 47/47 passed (0.02s)
▶ Running Tier 3: Cross-Feature Combinations (8 tests)    -> 8/8 passed (0.01s)
▶ Running Tier 4: Real-World Multi-Turn Scenarios (5 tests)-> 5/5 passed (0.01s)

Total: 107/107 passed (0.10s)
✔ ALL 107 E2E TESTS PASSED CLEANLY (Exit Code: 0)
```

---

## 4. Final Sign-Off

- **Astra (`gpt-6-astra`)**: APPROVED. All 9 hardening findings addressed with zero regressions.
- **Sol (`gpt-6-sol`)**: APPROVED. Process group lifecycle and session isolation verified.
- **Claude (`claude -p`)**: APPROVED. Architecture, error boundaries, and MCP schemas conform to spec.
