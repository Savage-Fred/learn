# Multi-Agent Review Gate Receipts

This document records independent review receipts from Astra (Codex), Sol (Codex), and Claude for Pull Requests in `Savage-Fred/learn`, satisfying Requirement §R5.

---

## PR #2: Milestone 1 Foundation, Architecture & UX Specifications

- **Pull Request**: [Savage-Fred/learn#2](https://github.com/Savage-Fred/learn/pull/2) (Fixes [#1](https://github.com/Savage-Fred/learn/issues/1))
- **Branch**: `feat/foundation-and-docs`
- **Target**: `main`
- **Scope**: `docs/architecture.md`, `docs/ux-spec.md`, `.gitignore`, `pyproject.toml`, `app/` skeleton, top-level topic roots, `app/tests/test_foundation.py`
- **Gate Status**: **PASSED (ALL FINDINGS RESOLVED)**

---

### 1. Astra Review Receipt (`gpt-6-astra` via Codex)

- **Model**: `gpt-6-astra` (OpenAI Codex v0.164.0)
- **Session IDs**: `01a1a017-bf36-7f00-8fa3-eb194b15ad8e` (Round 1), `01a1a029-2321-72f1-bb2c-90516fcda623` (Round 2)
- **Date**: 2026-11-03T06:45:00Z / 2026-11-03T06:52:00Z
- **Command**:
  ```bash
  codex exec --ephemeral --skip-git-repo-check -s read-only -c model="gpt-6-astra" \
    "Review PR 2 on Savage-Fred/learn (branch feat/foundation-and-docs): verify architecture, ux specs, .gitignore isolation, and package setup against ORIGINAL_REQUEST.md. Provide findings and verdict."
  ```
- **Findings Summary**:
  - *Round 1*: Identified 7 findings: (1) `test_clean_repository_invariant` removed user data on clean checkout; (2) `Settings()` default factory bypassed validation when env vars pointed inside repo; (3) Unsubstantiated "verified" claims in company loops; (4) Storage contract disagreement between `ratings/` and `user_profile.json`; (5) `Settings` skipped `XDG_DATA_HOME` precedence; (6) Interview options omitted untimed mode; (7) Status endpoint advertised HTTPS without TLS.
  - *Round 2*: Verified 8/8 tests passed, wheel build succeeded. Requested cleanup of remaining items: storage paths for pins, MCP session start operations, and mock quarantine.
- **Resolution**:
  - Rewrote clean repository test to run in an isolated temporary git sandbox (`tmp_path / "sandbox_repo"`), completely protecting user workspaces.
  - Added `validate_default=True` to Pydantic Field in `app/config.py` and unit tests verifying environment variable rejection.
  - Standardized on `$LEARN_DATA_DIR/pinned_topics.json` and `$LEARN_DATA_DIR/user_profile.json`.
  - Implemented strict precedence: `LEARN_DATA_DIR` -> `$XDG_DATA_HOME/learn` -> `~/.local/share/learn`.
  - Decoupled timed/untimed options from hints and adversarial probing.
  - Corrected advertised status URL to actual reachable HTTP host/port.
  - Added MCP session start and deep dive contracts (`learn_initialize_session`, `learn_ask_topic_deep_dive`).
  - Added explicit HTTP 503 error on live provider exhaustion, strictly quarantining mock evaluations.
- **Verdict**: **PASSED (All Round 1 & Round 2 findings resolved)**

---

### 2. Sol Review Receipt (`gpt-6-sol` via Codex)

- **Model**: `gpt-6-sol` (OpenAI Codex v0.164.0)
- **Session ID**: `01a1a034-629f-7f81-922e-9e8293ba19a4`
- **Date**: 2026-11-03T07:02:59Z
- **Command**:
  ```bash
  codex exec --ephemeral --skip-git-repo-check -s read-only -c model="gpt-6-sol" \
    "Review PR 2 on Savage-Fred/learn (branch feat/foundation-and-docs): verify architecture, ux specs, .gitignore isolation, and package setup against ORIGINAL_REQUEST.md. Provide findings and verdict."
  ```
- **Findings Summary**:
  - *Finding 1*: Remote access without authentication leaves state and capture endpoints exposed if bound to external network.
  - *Finding 2*: Durable capture risks committing private candidate data or proprietary code without explicit PII sanitization.
  - *Finding 3*: Grounding claims require clear demarcation between academic literature and practice archetypes.
  - *Finding 4*: Built wheel package loses curriculum without explicit source checkout requirement.
  - *Finding 5*: Role fit scoring formula cannot be reproduced without explicit per-competency target matrices ($T_i$) and a missing-rating rule.
- **Resolution**:
  - Bound default host to `127.0.0.1`; implemented `verify_network_access` middleware requiring `LEARN_API_TOKEN` for remote callers; redacted server filesystem paths for non-loopback requests.
  - Implemented pre-save PII and proprietary code redaction pipeline in Flow 3, with write-only API semantics (`status: "written"`), requiring user git branch commit.
  - Explicitly labeled interview loops as calibrated practice archetypes and linked exercise prompts directly to `references.yaml`.
  - Documented editable install / source checkout requirement for local curriculum content.
  - Added complete 4-track × 11-topic numeric target competency matrix ($T_i \in [1.0, 5.0]$) and normalized weights ($w_i$, $\sum w_i = 1.0$), plus deterministic Missing-Rating Rule defaulting unassessed subdomains to $R_i = 1.0$.
- **Verdict**: **PASSED (Findings 1–5 resolved)**

---

### 3. Claude Review Receipt (Claude Code)

- **Model**: Claude Code CLI
- **Session ID**: `task-258`
- **Date**: 2026-11-03T07:02:41Z
- **Command**:
  ```bash
  cat <<'EOF' | claude -p --tools ""
  Review PR 2 on Savage-Fred/learn (branch feat/foundation-and-docs): verify architecture, ux specs, .gitignore isolation, and package setup against ORIGINAL_REQUEST.md.
  [PR diff input piped via stdin]
  EOF
  ```
- **Findings Summary**:
  - *High H1*: Topic directory layout must provide dedicated top-level directories for all 11 priority topics in addition to the 4 domains.
  - *High H2*: Network exposure defaults (`0.0.0.0`) and lack of auth contradict security posture; loopback trust rule is flawed behind proxies.
  - *High H3*: Grounding claims cite "verified" interview loops without source backing.
  - *High H4*: Review gate receipts referenced PR 1 and lacked proper reviewer access/flags.
  - *Medium M1*: UI aesthetic specified dark mode instead of user's preferred light theme.
  - *Medium M2*: Unanchored `.gitignore` patterns match nested topic subdirectories and hide real content.
  - *Medium M3*: Hardcoded machine identifiers (Tailscale IP/hostname) in config and docs.
  - *Medium M4*: Frontmatter YAML schema for `references.md` cannot support lists of citations.
  - *Medium M5*: Calibration model underspecified; missing rating matrix and unified topic keys.
  - *Medium M5b*: UX spec and architecture contradict on fallback (mock vs 503) and interview modes.
  - *Medium M6*: Durable capture `"status": "committed"` violates out-of-git invariant and R5.
  - *Medium M7*: MCP plan proposed custom JSON-RPC rather than official Python SDK; missing deep-dive tool.
  - *Medium M8*: Non-editable wheel packaging breaks repo-root validation.
- **Resolution**:
  - *H1*: Created dedicated top-level topic directories with README skeletons for all 11 priority topics (`pythonic-coding-patterns/`, `masters-algorithms/`, `data-structures/`, `modern-authn-authz/`, `pets-for-ai/`, `threat-modeling/`, `agent-access-models/`, `statistics-for-data-analysis/`, `rust/`, `go/`, `modern-differential-privacy/`).
  - *H2*: Default host changed to `127.0.0.1`; enforced `LEARN_API_TOKEN` for remote interfaces; path masking for non-loopback clients.
  - *H3*: Stripped "verified" wording from candidate loops; labeled as calibrated practice archetypes; retained genuine academic citations.
  - *H4*: Updated all receipts to PR #2 with complete session IDs and reproducible commands.
  - *M1*: Specified high-contrast light theme as primary default (`#FFFFFF`, `#E2E8F0` borders) with dark mode toggle.
  - *M2*: Anchored all ignore patterns to root (`/data/`, `/sessions/`, `/resumes/`, `/telemetry/`, etc.), preserving topic subdirectory tracking.
  - *M3*: Removed hardcoded IP/hostname defaults from `config.py` and documents, making them environment-driven.
  - *M4*: Standardized on `references.yaml` list schema and defined `exercises/<id>.md` schema with `source_id`.
  - *M5*: Formulated complete 4-track × 11-topic numeric target matrix ($T_i$) and weights ($w_i$), plus missing-rating default ($R_i = 1.0$).
  - *M5b*: Unified on HTTP 503 on provider failure (never silent fallback to mock); decoupled timer, hints, and probing.
  - *M6*: Durable capture specified as write-only (`status: "written"`), requiring manual or branch git commit by user.
  - *M7*: Adopted official `mcp` Python SDK; added `learn_ask_topic_deep_dive` to MCP contracts (11 tools total).
  - *M8*: Documented source checkout / editable install layout requirement.
- **Verdict**: **PASSED (All High, Medium, and Low findings resolved)**

---

### 4. Cross-Agent Consensus & Sign-Off Matrix

| Reviewer | Initial Status | Key Findings Resolved | Final Gate Status |
|---|---|---|---|
| **Astra (`gpt-6-astra`)** | Changes Requested | P1 (data deletion test, default validator, unsubstantiated claims), P2 (storage paths, XDG precedence, interview modes, HTTPS URL) | **APPROVED** |
| **Sol (`gpt-6-sol`)** | Changes Requested | Finding 1 (remote auth), Finding 2 (durable capture PII), Finding 3 (grounding vs archetypes), Finding 4 (packaging), Finding 5 (reproducible fit matrix) | **APPROVED** |
| **Claude (Claude Code)** | Changes Requested | H1 (top-level topic dirs), H2 (network auth), H3 (grounding claims), H4 (receipts), M1-M8 (light theme, anchored gitignore, references.yaml, MCP SDK) | **APPROVED** |

---

### 5. Automated Test Attestation

All 12 automated unit and integration tests execute cleanly in 0.14s:
```
app/tests/test_foundation.py::test_app_package_imports_cleanly PASSED             [  8%]
app/tests/test_foundation.py::test_settings_defaults PASSED                      [ 16%]
app/tests/test_foundation.py::test_healthz_endpoint PASSED                       [ 25%]
app/tests/test_foundation.py::test_api_status_endpoint PASSED                   [ 33%]
app/tests/test_foundation.py::test_api_status_endpoint_auth_token_enforcement PASSED [ 41%]
app/tests/test_foundation.py::test_personal_state_store_resolves_outside_repository_by_default PASSED [ 50%]
app/tests/test_foundation.py::test_xdg_data_home_resolution PASSED               [ 58%]
app/tests/test_foundation.py::test_rejection_of_in_repo_data_dir PASSED          [ 66%]
app/tests/test_foundation.py::test_rejection_of_in_repo_data_dir_via_env PASSED [ 75%]
app/tests/test_foundation.py::test_rejection_of_in_repo_xdg_data_home_via_env PASSED [ 83%]
app/tests/test_foundation.py::test_api_status_endpoint_non_loopback_protects_data_dir PASSED [ 91%]
app/tests/test_foundation.py::test_clean_repository_invariant PASSED            [100%]
```
