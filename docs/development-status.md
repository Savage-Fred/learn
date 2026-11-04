# Development baseline — 2026-11-03

Will asked Codex to take over development leadership. The immediate goal is a
trustworthy learning workflow, followed by completing the existing UI and hosting
work in [issue #6](https://github.com/Savage-Fred/learn/issues/6).
Baseline and CI work are tracked in [issue #7](https://github.com/Savage-Fred/learn/issues/7).

## Verified baseline

- Remote `main` is `f303b9c`, containing merged PRs #2–#5. The original primary
  checkout remains at `7ee2abe`; its local planning files are not the source tree.
- All 152 tracked tests in `app/tests` pass with deterministic inference. This
  includes production FastAPI integration tests in
  [test_e2e_app.py](../app/tests/test_e2e_app.py), plus router, MCP, state, curriculum,
  and adversarial checks. This does not establish live provider or browser behavior.
- The untracked `tests_e2e/` directory in the primary checkout reports 107 passes,
  but `tests_e2e/harness/client.py` always instantiates its separate `MockBackend`.
  Treat it as a reference contract suite, not production acceptance evidence.
- There were no GitHub Actions workflows or repository rulesets at handoff.
  [The new workflow](../.github/workflows/ci.yml) runs the tracked application suite
  on pull requests and main pushes, and rejects checkout changes left by tests.
  Requiring that check for merges remains a repository setting to configure.
- Uncommitted issue #6 work is preserved at `.worktrees/cloudflare-webui` on
  `feature/6-polished-cloudflare-webui`. It includes a UI rewrite, static build,
  deployment notes, and build tests. There is no open PR for that work at handoff.

## Development order and acceptance

1. **Establish a repeatable application check (#7).** Install `.[dev]` in a fresh
   Python environment; pass `python -m pytest -q app/tests`; leave the checkout
   unchanged; confirm the hosted workflow passes. The standalone mock suite is
   not included in the production check.
2. **Repair assessed quiz continuity.**
   [AdaptiveEngine](../app/core/adaptive_engine.py) loads a curriculum problem at
   session start, then returns a generic “Scaled problem” string after each turn.
   Its grading prompt omits the current exercise and rubric, and failed inference
   silently falls back to keyword/length scoring. Acceptance: a production API
   journey steps up and down through real curriculum problems; the grader receives
   the current problem and rubric; provider failure cannot silently change a real
   user's proficiency using heuristic grades. Mock assessment remains explicit
   in automated tests.
3. **Finish and review #6 against those checks.** Preserve the existing diff and
   continue it in an isolated worktree. Its browser `EdgeEngine` currently invents
   grades and token usage, and reports a learning download as a repository commit.
   Acceptance: static browsing and local pins work; assessed workflows accurately
   show backend availability; downloads describe their actual persistence; all six
   views receive browser, keyboard, and mobile checks. Before exposing the local
   harness through a tunnel, prove authenticated access succeeds and anonymous
   access fails through that actual proxy path.

## Reproduce the application check

From a clean implementation checkout, using Python 3.13:

```sh
python -m venv /tmp/learn-check-venv
/tmp/learn-check-venv/bin/python -m pip install -e '.[dev]'
LEARN_USE_MOCK_LLM=1 LEARN_DATA_DIR=/tmp/learn-check-data \
  /tmp/learn-check-venv/bin/python -m pytest -q app/tests
git status --porcelain
```

No live provider calls, browser validation, Cloudflare deployment, DNS changes, or
service restarts were performed during this baseline review. Release readiness
remains open until the functional and hosting checks above pass.
