"""Foundation tests verifying package imports, health check, settings, and repository isolation."""

import os
import subprocess
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

import app
from app.config import Settings, settings
from app.main import app as fastapi_app


@pytest.mark.unit
def test_app_package_imports_cleanly():
    """Verify app package imports cleanly with valid version string."""
    assert hasattr(app, "__version__")
    assert app.__version__ == "0.1.0"


@pytest.mark.unit
def test_settings_defaults():
    """Verify default host, port, mock LLM flag, and repository paths."""
    default_settings = Settings()
    assert default_settings.host == "0.0.0.0"
    assert default_settings.port == 8795
    assert default_settings.use_mock_llm is False
    assert default_settings.repo_root.is_dir()
    assert default_settings.topics_root == default_settings.repo_root


@pytest.mark.asyncio
async def test_healthz_endpoint():
    """Verify /healthz returns 200 OK with status ok."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("status") == "ok"
        assert payload.get("version") == "0.1.0"


@pytest.mark.asyncio
async def test_api_status_endpoint():
    """Verify /api/v1/status returns operational status and configuration."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/status")
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("status") == "operational"
        assert "tailnet_reachability" in payload
        assert "topics_available" in payload
        assert "data_dir" in payload


@pytest.mark.unit
def test_personal_state_store_resolves_outside_repository_by_default():
    """Verify personal state store resolves outside repository by default (§R4 invariant)."""
    # Create clean settings without LEARN_DATA_DIR override
    env_backup = os.environ.get("LEARN_DATA_DIR")
    try:
        if "LEARN_DATA_DIR" in os.environ:
            del os.environ["LEARN_DATA_DIR"]

        clean_settings = Settings()
        expected_default = (Path.home() / ".local" / "share" / "learn").resolve()
        assert clean_settings.data_dir == expected_default

        # Assert data_dir is outside repo_root
        repo_root = clean_settings.repo_root.resolve()
        is_inside_repo = False
        try:
            clean_settings.data_dir.resolve().relative_to(repo_root)
            is_inside_repo = True
        except ValueError:
            is_inside_repo = False

        assert not is_inside_repo, (
            f"Personal state directory {clean_settings.data_dir} must not be inside repo root {repo_root}"
        )
    finally:
        if env_backup is not None:
            os.environ["LEARN_DATA_DIR"] = env_backup


@pytest.mark.unit
def test_clean_repository_invariant(tmp_path: Path):
    """Verify executing data operations maintains clean repository invariant.

    Asserts that:
    1. Operating with an isolated data store creates directories outside the repo.
    2. Even if personal state files or directories are created locally,
       .gitignore strictly prevents them from showing up as untracked files
       in git status --porcelain.
    """
    # 1. Verify custom data directory outside repo operations cleanly
    custom_data_dir = tmp_path / "test_learn_data"
    test_settings = Settings(data_dir=custom_data_dir)
    test_settings.ensure_data_directories()

    assert (custom_data_dir / "sessions").is_dir()
    assert (custom_data_dir / "resumes").is_dir()
    assert (custom_data_dir / "telemetry").is_dir()
    assert (custom_data_dir / "pins").is_dir()

    # 2. Test gitignore effectiveness inside repo_root
    repo_root = test_settings.repo_root.resolve()

    # Create dummy personal state files and directories directly in repo root
    dummy_files = [
        repo_root / "user_profile.json",
        repo_root / "pinned_topics.json",
        repo_root / "sessions" / "dummy_session.json",
        repo_root / "resumes" / "dummy_resume.md",
        repo_root / "telemetry" / "dummy_usage.jsonl",
        repo_root / "personal_data" / "leak.txt",
    ]

    try:
        (repo_root / "sessions").mkdir(parents=True, exist_ok=True)
        (repo_root / "resumes").mkdir(parents=True, exist_ok=True)
        (repo_root / "telemetry").mkdir(parents=True, exist_ok=True)
        (repo_root / "personal_data").mkdir(parents=True, exist_ok=True)

        for dummy in dummy_files:
            dummy.write_text("{\"test\": true}\n", encoding="utf-8")

        # Query git status --porcelain
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )

        untracked_lines = [
            line for line in result.stdout.splitlines()
            if line.startswith("??") or line.startswith(" M") or line.startswith("A ")
        ]

        # Verify none of the dummy personal state files are tracked or untracked
        forbidden_patterns = [
            "user_profile.json",
            "pinned_topics.json",
            "sessions/",
            "resumes/",
            "telemetry/",
            "personal_data/",
        ]

        for line in untracked_lines:
            for pattern in forbidden_patterns:
                assert pattern not in line, (
                    f"Violation of Clean Repository Invariant: {pattern} reported in git status: {line}"
                )
    finally:
        # Clean up temporary test files in repo root
        for dummy in dummy_files:
            if dummy.exists():
                dummy.unlink()
        for folder in ["sessions", "resumes", "telemetry", "personal_data"]:
            dir_to_remove = repo_root / folder
            if dir_to_remove.exists() and not any(dir_to_remove.iterdir()):
                dir_to_remove.rmdir()
