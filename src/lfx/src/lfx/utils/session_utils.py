"""Helpers for normalizing chat session identifiers."""

from __future__ import annotations

from uuid import UUID


def normalize_session_id(session_id: str | UUID | None) -> str | None:
    """Return a canonical dashed UUID string when possible.

    Playground and DB code paths may use the same logical session with different
    string forms (with/without dashes). Normalizing avoids empty history retrieval.
    """
    if session_id is None:
        return None

    value = str(session_id).strip()
    if not value:
        return value

    try:
        return str(UUID(value))
    except ValueError:
        hex_value = value.replace("-", "")
        if len(hex_value) == 32:
            try:
                return str(UUID(hex=hex_value))
            except ValueError:
                return value
        return value


def coerce_uuid(value: str | UUID | None) -> UUID | None:
    """Parse a UUID from dashed or 32-char hex string forms (SQLite-safe)."""
    return parse_flow_id(value)


def parse_flow_id(flow_id: str | UUID | None) -> UUID | None:
    """Parse flow_id to UUID, accepting dashed and 32-char hex forms."""
    if flow_id is None:
        return None
    value = str(flow_id).strip()
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        hex_value = value.replace("-", "")
        if len(hex_value) == 32:
            try:
                return UUID(hex=hex_value)
            except ValueError:
                return None
        return None
