"""Runtime configuration and environment resolution for Savage-Fred/learn."""

import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


def resolve_default_data_dir() -> Path:
    """Resolve data directory following priority: LEARN_DATA_DIR -> XDG_DATA_HOME -> ~/.local/share/learn."""
    if "LEARN_DATA_DIR" in os.environ and os.environ["LEARN_DATA_DIR"].strip():
        return Path(os.environ["LEARN_DATA_DIR"]).expanduser().resolve()
    if "XDG_DATA_HOME" in os.environ and os.environ["XDG_DATA_HOME"].strip():
        return (Path(os.environ["XDG_DATA_HOME"]) / "learn").expanduser().resolve()
    return (Path.home() / ".local" / "share" / "learn").resolve()


class Settings(BaseModel):
    """Platform settings resolved from environment variables."""

    # Server binding (defaults to loopback for security; opt-in non-loopback via LEARN_HOST=0.0.0.0)
    host: str = Field(default_factory=lambda: os.getenv("LEARN_HOST", "127.0.0.1"))
    port: int = Field(default_factory=lambda: int(os.getenv("LEARN_PORT", "8795")))

    # Tailscale & Network integration (environment-driven; no hardcoded machine identifiers)
    tailscale_ip: str | None = Field(
        default_factory=lambda: os.getenv("LEARN_TAILSCALE_IP")
    )
    magic_dns: str | None = Field(
        default_factory=lambda: os.getenv("LEARN_MAGIC_DNS")
    )
    api_token: str | None = Field(
        default_factory=lambda: os.getenv("LEARN_API_TOKEN")
    )

    # Mock LLM toggle
    use_mock_llm: bool = Field(
        default_factory=lambda: os.getenv("LEARN_USE_MOCK_LLM", "false").lower()
        in ("1", "true", "yes")
    )

    # Repository paths (supports explicit LEARN_REPO_ROOT override for non-editable installations)
    repo_root: Path = Field(
        default_factory=lambda: Path(
            os.getenv("LEARN_REPO_ROOT", str(Path(__file__).parent.parent.resolve()))
        ).resolve()
    )

    # Out-of-git personal state directory (Strict Invariant §R4)
    data_dir: Path = Field(
        default_factory=resolve_default_data_dir,
        validate_default=True,
    )

    @field_validator("data_dir")
    @classmethod
    def validate_data_dir_outside_repo(cls, v: Path) -> Path:
        """Enforce §R4 invariant: personal state directory must strictly reside outside repository root."""
        resolved = v.expanduser().resolve()
        repo_root = Path(
            os.getenv("LEARN_REPO_ROOT", str(Path(__file__).parent.parent.resolve()))
        ).resolve()
        if resolved.is_relative_to(repo_root):
            raise ValueError(
                f"Personal state directory {resolved} must not be located inside repository root {repo_root} (§R4 invariant)"
            )
        return resolved

    @property
    def topics_root(self) -> Path:
        """Root directory containing domain curricula."""
        return self.repo_root

    def ensure_data_directories(self) -> None:
        """Create necessary subdirectories in canonical out-of-git data directory."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sessions").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "resumes").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "telemetry").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
