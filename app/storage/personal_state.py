"""Personal state persistence layer re-exporting core state management contracts.

Conforms to PROJECT.md:106 architectural layout.
"""

from app.core.state import (
    StateManager,
    sanitize_identifier,
    atomic_write_json,
    safe_read_json,
    file_lock,
    state,
)

__all__ = [
    "StateManager",
    "sanitize_identifier",
    "atomic_write_json",
    "safe_read_json",
    "file_lock",
    "state",
]
