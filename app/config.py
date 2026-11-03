"""Runtime configuration and environment resolution for Savage-Fred/learn."""

import os
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Platform settings resolved from environment variables."""

    # Server binding
    host: str = Field(default_factory=lambda: os.getenv("LEARN_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("LEARN_PORT", "8795")))

    # Tailscale integration
    tailscale_ip: str = Field(default="100.64.162.123")
    magic_dns: str = Field(default="will-ubuntu-26.tailacca87.ts.net")

    # Mock LLM toggle
    use_mock_llm: bool = Field(
        default_factory=lambda: os.getenv("LEARN_USE_MOCK_LLM", "false").lower()
        in ("1", "true", "yes")
    )

    # Out-of-git personal state directory (Strict Invariant §R4)
    data_dir: Path = Field(
        default_factory=lambda: Path(
            os.getenv("LEARN_DATA_DIR", str(Path.home() / ".local" / "share" / "learn"))
        )
        .expanduser()
        .resolve()
    )

    # Repository paths
    repo_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.resolve()
    )

    @property
    def topics_root(self) -> Path:
        """Root directory containing domain curricula."""
        return self.repo_root

    def ensure_data_directories(self) -> None:
        """Create necessary subdirectories in out-of-git data directory."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sessions").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "resumes").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "telemetry").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "pins").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "ratings").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
