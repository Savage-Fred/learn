"""Foundation tests verifying package imports, health check, settings, and repository isolation."""

import os
import shutil
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
def test_settings_defaults(monkeypatch):
    """Verify default host, port, mock LLM flag, and repository paths under clean env."""
    monkeypatch.delenv("LEARN_HOST", raising=False)
    monkeypatch.delenv("LEARN_PORT", raising=False)
    monkeypatch.delenv("LEARN_USE_MOCK_LLM", raising=False)
    monkeypatch.delenv("LEARN_DATA_DIR", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)

    default_settings = Settings()
    assert default_settings.host == "127.0.0.1"
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
        assert payload.get("reachability", "").startswith("http://")
        assert "domains_available" in payload
        assert "priority_topics_available" in payload
        assert "data_dir" in payload


@pytest.mark.asyncio
async def test_api_status_endpoint_auth_token_enforcement(monkeypatch):
    """Verify remote non-loopback requests require valid LEARN_API_TOKEN when configured."""
    monkeypatch.setattr(settings, "api_token", "secret-test-token-123")
    transport = ASGITransport(app=fastapi_app, client=("192.168.1.100", 54321))

    # 1. Unauthenticated request rejected with 401
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_unauth = await client.get("/api/v1/status")
        assert res_unauth.status_code == 401

    # 2. Authenticated request accepted with 200
    headers = {"Authorization": "Bearer secret-test-token-123"}
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_auth = await client.get("/api/v1/status", headers=headers)
        assert res_auth.status_code == 200
        assert res_auth.json().get("status") == "operational"


@pytest.mark.unit
def test_personal_state_store_resolves_outside_repository_by_default(monkeypatch):
    """Verify personal state store resolves outside repository by default (§R4 invariant)."""
    monkeypatch.delenv("LEARN_DATA_DIR", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)

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


@pytest.mark.unit
def test_xdg_data_home_resolution(monkeypatch, tmp_path: Path):
    """Verify XDG_DATA_HOME environment variable precedence when LEARN_DATA_DIR is unset."""
    custom_xdg = tmp_path / "custom_xdg"
    monkeypatch.delenv("LEARN_DATA_DIR", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(custom_xdg))

    test_settings = Settings()
    expected_path = (custom_xdg / "learn").resolve()
    assert test_settings.data_dir == expected_path


@pytest.mark.unit
def test_rejection_of_in_repo_data_dir():
    """Verify Settings rejects personal state directories located inside repository root."""
    repo_root = settings.repo_root.resolve()
    invalid_data_dir = repo_root / "personal_state"
    with pytest.raises(ValueError, match="must not be located inside repository root"):
        Settings(data_dir=invalid_data_dir)


@pytest.mark.unit
def test_rejection_of_in_repo_data_dir_via_env(monkeypatch):
    """Verify Settings rejects in-repo LEARN_DATA_DIR via environment variable (§R4)."""
    repo_root = settings.repo_root.resolve()
    monkeypatch.setenv("LEARN_DATA_DIR", str(repo_root / "private_state"))
    with pytest.raises(ValueError, match="must not be located inside repository root"):
        Settings()


@pytest.mark.unit
def test_rejection_of_in_repo_xdg_data_home_via_env(monkeypatch):
    """Verify Settings rejects in-repo XDG_DATA_HOME via environment variable (§R4)."""
    repo_root = settings.repo_root.resolve()
    monkeypatch.delenv("LEARN_DATA_DIR", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(repo_root / "xdg"))
    with pytest.raises(ValueError, match="must not be located inside repository root"):
        Settings()


@pytest.mark.asyncio
async def test_api_status_endpoint_non_loopback_protects_data_dir():
    """Verify non-loopback clients do not receive raw local state path."""
    transport = ASGITransport(app=fastapi_app, client=("192.168.1.50", 12345))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/status")
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("data_dir") == "[protected]"


@pytest.mark.unit
def test_clean_repository_invariant(tmp_path: Path):
    """Verify .gitignore rules isolate personal state inside an isolated temporary git repo.

    Runs in a dedicated temporary git sandbox to ensure zero risk of modifying
    or deleting existing user data in the actual repository checkout.
    """
    # 1. Verify custom data directory outside repo initializes required subdirectories
    custom_data_dir = tmp_path / "test_learn_data"
    test_settings = Settings(data_dir=custom_data_dir)
    test_settings.ensure_data_directories()

    assert (custom_data_dir / "sessions").is_dir()
    assert (custom_data_dir / "resumes").is_dir()
    assert (custom_data_dir / "telemetry").is_dir()

    # 2. Test gitignore effectiveness inside an isolated temporary git repository
    sandbox_repo = tmp_path / "sandbox_repo"
    sandbox_repo.mkdir()

    # Copy project's authoritative .gitignore into sandbox
    src_gitignore = settings.repo_root / ".gitignore"
    dest_gitignore = sandbox_repo / ".gitignore"
    shutil.copyfile(src_gitignore, dest_gitignore)

    # Initialize git in sandbox
    subprocess.run(["git", "init"], cwd=sandbox_repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=sandbox_repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=sandbox_repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "add", ".gitignore"],
        cwd=sandbox_repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "chore: add gitignore"],
        cwd=sandbox_repo,
        capture_output=True,
        check=True,
    )

    # Populate sandbox with dummy personal state artifacts
    state_dirs = ["sessions", "interviews", "resumes", "telemetry", "personal_data", "pins", "ratings"]
    for d in state_dirs:
        (sandbox_repo / d).mkdir(parents=True, exist_ok=True)

    dummy_artifacts = [
        sandbox_repo / "user_profile.json",
        sandbox_repo / "pinned_topics.json",
        sandbox_repo / "sessions" / "session_123.json",
        sandbox_repo / "interviews" / "transcript_123.json",
        sandbox_repo / "resumes" / "my_resume.md",
        sandbox_repo / "telemetry" / "costs.jsonl",
        sandbox_repo / "personal_data" / "leak.txt",
        sandbox_repo / "pins" / "pinned_topics.json",
        sandbox_repo / "ratings" / "subdomain_ratings.json",
    ]

    for artifact in dummy_artifacts:
        artifact.write_text('{"dummy": true}\n', encoding="utf-8")

    # Query git status --porcelain in sandbox repo
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=sandbox_repo,
        capture_output=True,
        text=True,
        check=True,
    )

    untracked_lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    # Invariant: Every personal state artifact must be completely ignored by .gitignore
    assert (
        untracked_lines == []
    ), f"Clean repository invariant failed: untracked personal files found in git status: {untracked_lines}"
