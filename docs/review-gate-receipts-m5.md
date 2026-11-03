# Milestone 5 Review Gate Receipts: Tier 5 Adversarial Coverage Hardening

**PR**: [#5 Interactive Web Application, Adaptive Engine & Personal State](https://github.com/Savage-Fred/learn/pull/5)  
**Branch**: `feat/web-app-adaptive-engine` -> `feat/subscription-router-and-mcp`  
**Challengers**: Challenger 1 (`challenger_m5_1` - Backend), Challenger 2 (`challenger_m5_2` - Security/UI/Schema)  
**Worker**: Worker M5 (`worker_m5` - Adversarial Hardening)  
**Date**: 2026-11-03  

---

## 1. Review Summary & Audit Log

| Component | Audit Type | Challenger Verdict | Worker Resolution | Verification Status |
|---|---|---|---|---|
| **Backend & State Core** | White-Box Adversarial Stress | Gaps Found (7 defects) | Fully Patched & Hardened | **27/27 Tests Passed** |
| **Security, UI & Schemas** | Boundary & Penetration Audit | Gaps Found (8 defects) | Fully Patched & Hardened | **16/16 Tests Passed** |
| **Contract Compliance** | `PROJECT.md:106` Architecture | Missing `app/storage/personal_state.py` | Created & Re-exported | **Verified & Compliant** |
| **Regression & Invariants** | Independent E2E Test Suite | Clean Baseline (107 tests) | Maintained Zero Regressions | **107/107 Tests Passed** |
| **Concurrency & Locks** | Multithreaded State Stress | Clean Baseline (5 stress tests) | Maintained Zero Loss | **5/5 Stress Tests Passed** |

---

## 2. Adversarial Audit Findings & Remediation Receipts

### Finding 1: `RubricScorer.score_interview` Null Candidate Message Crash
- **Location**: `app/core/rubric_scorer.py:176`
- **Defect**: When a dialogue turn contained `{"speaker": "candidate", "message": None}`, calling `" ".join(t.get("message", "") ...)` returned `None` for that entry, raising `TypeError: sequence item 0: expected str instance, NoneType found`.
- **Resolution**: Replaced with `" ".join((t.get("message") or "") for t in candidate_turns).strip()`.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_rubric_scorer_candidate_turn_message_none`.

### Finding 2: `RubricScorer` Target Company Case-Insensitive Normalization
- **Location**: `app/core/rubric_scorer.py:100-115, 307-380`
- **Defect**: Passing lowercase company identifiers (e.g. `"google"`, `"openai"`) caused `compute_company_weights` and anti-pattern detectors to miss calibration profiles, falling back to uncalibrated default weights (Google architecture boost dropping from 0.30 to 0.25).
- **Resolution**: Added `RubricScorer.normalize_company()` classmethod performing case-insensitive canonicalization against `COMPANY_PROFILES`.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_rubric_scorer_target_company_case_sensitivity_gap`.

### Finding 3: `AdaptiveEngine.exercise_turn` Null User Response Crash
- **Location**: `app/core/adaptive_engine.py:121`
- **Defect**: While `_evaluate_response` handled empty inputs, turn record logging performed direct slice indexing `user_response[:250]`. When `user_response=None`, this crashed with `TypeError: 'NoneType' object is not subscriptable`.
- **Resolution**: Changed slice indexing to `(user_response or "")[:250]`.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_adaptive_exercise_turn_user_response_none`.

### Finding 4: `InterviewEngine.interview_turn` Null Turn Message Crash
- **Location**: `app/core/interview_engine.py:175`
- **Defect**: Direct evaluation of `"hint" in message.lower()` raised `AttributeError: 'NoneType' object has no attribute 'lower'` when `message` was `None`.
- **Resolution**: Introduced `safe_msg = str(message or "")` before performing keyword checks.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_interview_turn_message_none`.

### Finding 5: `ResumeMatcher.analyze_role_fit` Safe Float Coercion
- **Location**: `app/core/resume_matcher.py:149-152`
- **Defect**: If `subdomain_ratings.json` contained non-float or corrupted string ratings, unvalidated division `user_level / target_level` raised `TypeError: unsupported operand type(s) for /: 'str' and 'float'`.
- **Resolution**: Safely coerced rating lookups with `float()` inside `try...except (ValueError, TypeError)` with NaN/Inf filtering, cleanly falling back to novice level `1.0`.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_resume_matcher_corrupted_state_rating_type`.

### Finding 6: `sanitize_identifier` Single-Dot (`"."`) Traversal Bypass
- **Location**: `app/core/state.py:54-61`
- **Defect**: Single dot `"."` bypassed checks for `..`, `/`, `\\`, and `\0`, allowing directory aliasing and escape to domain roots in path resolution.
- **Resolution**: Explicitly reject `clean == "."` in `sanitize_identifier`.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_sanitize_identifier_rejects_dot_and_special_escapes`.

### Finding 7: `StateManager.update_subdomain_rating` NaN Injection Privilege Escalation
- **Location**: `app/core/state.py:258-275`
- **Defect**: In Python, `min(5.0, float('nan'))` evaluates to `5.0`. Passing `float('nan')` awarded users a maximum Staff rating of 5.00.
- **Resolution**: Added `math.isnan(val)` and `math.isinf(val)` checks in `update_subdomain_rating` and `set_subdomain_ratings`, safely resetting `NaN` inputs to the `1.0` floor rating.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_state_nan_and_inf_rating_injection`.

### Finding 8: MCP Tool `learn_pin_topic` Priority Validation & Dual Mirror Sync
- **Location**: `app/mcp/tools.py:345-395`
- **Defect**: Tool accepted arbitrary priority strings (e.g. `"super_critical"`) and wrote only to `pinned_topics.json`, allowing the mirror `pins/pinned_topics.json` to desynchronize.
- **Resolution**: Validated `priority in ("high", "medium", "low")` and delegated execution to `StateManager.pin_topic()`, enforcing dual atomic writes to both mirrors.
- **Verification**: Verified in `app/tests/test_tier5_backend_adversarial.py::test_mcp_tool_pin_topic_priority_validation_gap`.

### Finding 9: MCP Tools Unhandled `TypeError` on Corrupted String Ratings
- **Location**: `app/mcp/tools.py:326, 538, 624`
- **Defect**: `_handle_list_topics`, `_handle_query_proficiency_gaps`, and `_handle_run_adaptive_exercise_turn` performed unvalidated comparisons (`user_rating >= 4.0`, `min(c["required"], c["current"])`, and `curr_rating + 0.35`) against persisted ratings, crashing with JSON-RPC internal errors on string ratings.
- **Resolution**: Wrapped all rating lookups in safe float coercion with NaN/Inf filters and fallbacks (`0.0`, `2.0`, `2.5`).
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_mcp_tools_resilient_to_corrupted_or_string_ratings`.

### Finding 10: `MicroHighlighter` Regex Capture Group Destructuring Mismatch
- **Location**: `app/ui/static/app.js:464-545`
- **Defect**: Destructuring assumed 8 capture groups across all languages, causing Python strings to map to numbers (`tok-number`), Python numbers to unstyled identifiers, and Go punctuation (`:=`) to whitespace (`ws`).
- **Resolution**: Standardized regex token slots across Python, Go, Rust, and YAML to exactly 7 unified positions `[full, comment, str, num, key, ident, ws, punct] = m`.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_micro_highlighter_token_destructuring_python_accuracy` and `test_micro_highlighter_go_punctuation_highlighting`.

### Finding 11: `MicroHighlighter` Unclosed Quotes and Delimiter Retention
- **Location**: `app/ui/static/app.js:464-545`
- **Defect**: Non-matching characters and unclosed quotes were skipped by `re.exec()`, silently dropping code tokens from rendering.
- **Resolution**: Added gap-tracking slice logic (`if (m.index > lastIndex) out += this.escape(code.slice(lastIndex, m.index))`) and trailing slice preservation, guaranteeing 100% token retention.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_micro_highlighter_unclosed_quotes_retention`.

### Finding 12: Stored DOM XSS via Unescaped Pinned Topic Slugs
- **Location**: `app/ui/static/app.js:395-406`
- **Defect**: `renderPinnedBar` injected `slug` directly into `innerHTML` template literals without entity encoding, enabling script execution via malicious pinned topic slugs.
- **Resolution**: Escaped `slug`, `domain`, and `priority` using `MicroHighlighter.escape()` before injecting into HTML chips.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_web_ui_stored_xss_via_pinned_topic_slug`.

### Finding 13: Unhandled HTTP 500 on Path-Traversal `session_id` in `POST /api/quiz/turn`
- **Location**: `app/api/routes_quiz.py:48-65`
- **Defect**: `state.get_session(session_id)` was invoked outside the `try...except ValueError` block, crashing FastAPI with an unhandled 500 Internal Server Error when traversal identifiers were submitted.
- **Resolution**: Moved session retrieval inside the `try...except ValueError` block to return standard 400 Bad Request responses.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_quiz_turn_path_traversal_session_id_graceful_handling`.

### Finding 14: Information Disclosure: Internal Directory Exposure via Unchecked Domain
- **Location**: `app/api/routes_topics.py:38-85`, `app/core/topic_loader.py:47-90, 137-145`
- **Defect**: Querying `/api/topics?domain=app` traversed internal source directories (`app/api`, `app/core`, etc.) and exposed them as curriculum topics.
- **Resolution**: Enforced `ALLOWED_DOMAINS = ["leetcode", "system-design", "security", "privacy-engineering"]` across both API endpoints and core loader methods, rejecting invalid domains with HTTP 400.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_domain_whitelisting_strictly_enforced_in_topics_api`.

### Finding 15: Missing `app/storage/personal_state.py` Module
- **Location**: `PROJECT.md:106`, `app/storage/personal_state.py`
- **Defect**: Module specified in repository architecture layout was missing from `app/storage/`.
- **Resolution**: Created `app/storage/personal_state.py` re-exporting `StateManager`, `sanitize_identifier`, `atomic_write_json`, `safe_read_json`, `file_lock`, and `state`.
- **Verification**: Verified in `app/tests/test_tier5_security_ui_adversarial.py::test_personal_state_module_presence`.

### Finding 16: Test Fixture State Leak in `test_mcp.py`
- **Location**: `app/tests/test_mcp.py:25-28`
- **Defect**: `MCPServer` tests operated on the global `settings.data_dir` without isolation, leaking state and reading unisolated files.
- **Resolution**: Added autouse fixture `isolate_mcp_data_dir(tmp_path, monkeypatch)` guaranteeing strict temporary directory isolation across all tests in `test_mcp.py`.
- **Verification**: Verified across `app/tests/test_mcp.py`.

---

## 3. Comprehensive Verification Matrix

### Suite 1: Full Pytest Suite (`app/tests/`)
```bash
.venv/bin/pytest app/tests/ -v
```
**Result**: **152 passed in 1.65s (100% pass rate)**  
Included:
- `test_tier5_backend_adversarial.py`: 27/27 passed
- `test_tier5_security_ui_adversarial.py`: 16/16 passed
- `test_mcp.py`: 23/23 passed
- `test_curricula_integrity.py`: 12/12 passed
- `test_adversarial_deep_probe.py`: 7/7 passed
- `test_adversarial_challenge.py`: 9/9 passed
- `test_e2e_app.py`: 9/9 passed
- `test_router.py`: 16/16 passed
- `test_storage.py`: 8/8 passed
- `test_adaptive.py`: 7/7 passed
- `test_interview.py`: 7/7 passed
- `test_resume.py`: 6/6 passed
- `test_foundation.py`: 5/5 passed

### Suite 2: Independent E2E Test Runner (`tests_e2e/runner.py`)
```bash
.venv/bin/python3 /home/will/dev/learn/tests_e2e/runner.py -v
```
**Result**: **107/107 passed in 0.11s (100% pass rate)**  
- Tier 1 (Feature Coverage): 47/47 passed
- Tier 2 (Boundary & Corner Cases): 47/47 passed
- Tier 3 (Cross-Feature Combinations): 8/8 passed
- Tier 4 (Real-World Multi-Turn Scenarios): 5/5 passed

### Suite 3: Multithreaded Concurrency Stress Runner
```bash
.venv/bin/python3 /tmp/stress_concurrency_m4.py
```
**Result**: **5/5 tests passed with zero data corruption and zero lost updates**  
- Test 1 (30 concurrent sessions & scorecards): PASSED
- Test 2 (200 concurrent appends across 10 workers): PASSED
- Test 3 (Concurrent atomic writes vs continuous reading): PASSED
- Test 4 (Concurrent topic pinning, 20 distinct pins): PASSED
- Test 5 (Concurrent rating updates, 20 distinct topics): PASSED

### Suite 4: Clean Git Working Tree Verification
```bash
git status --porcelain
```
**Result**: Strictly zero untracked state files, cache dirt, or test logs in git tree.

---

## 4. Final Sign-Off

All 15 challenger findings and contractual specifications for Milestone 5 have been implemented with genuine production logic, validated against white-box adversarial test suites, and verified with zero regressions across the entire platform. Milestone 5 Adversarial Hardening is **COMPLETE** and verified.
