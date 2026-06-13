"""Helpers for running Langflow from a PyInstaller-frozen executable."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def langflow_package_dir() -> Path:
    if is_frozen():
        return bundle_root() / "langflow"
    return Path(__file__).resolve().parent.parent


def resolve_frontend_dir() -> Path:
    return langflow_package_dir() / "frontend"


def configure_frozen_environment() -> None:
    """Set env vars so settings and static file serving work inside a frozen bundle."""
    if not is_frozen():
        return

    config_dir = Path.home() / ".langflow"
    config_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("LANGFLOW_CONFIG_DIR", str(config_dir))
    os.environ.setdefault("LANGFLOW_SAVE_DB_IN_CONFIG_DIR", "true")
    os.environ.setdefault("LANGFLOW_WORKERS", "1")
    os.environ.setdefault("LANGFLOW_LOG_LEVEL", "error")
    os.environ.setdefault("LANGFLOW_OPEN_BROWSER", "true")

    # Standalone exe: default to local SQLite unless the user configured PostgreSQL.
    if not os.environ.get("LANGFLOW_DATABASE_URL"):
        db_file = config_dir / "langflow.db"
        os.environ["LANGFLOW_DATABASE_URL"] = f"sqlite:///{db_file.as_posix()}"

    frontend = resolve_frontend_dir()
    if frontend.is_dir() and (frontend / "index.html").exists():
        os.environ.setdefault("LANGFLOW_FRONTEND_PATH", str(frontend))
