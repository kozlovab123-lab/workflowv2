"""Entry point for the Windows PyInstaller build of Langflow."""

from __future__ import annotations

import multiprocessing
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


def _boot_log_path() -> Path:
    return Path.home() / ".langflow" / "langflow-exe-boot.log"


def _boot_log(message: str) -> None:
    """Write before PyInstaller/stdio is ready (survives early crashes)."""
    try:
        path = _boot_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")
    except OSError:
        pass


_boot_log("=== Langflow frozen entry loaded ===")


def _log_path() -> Path:
    path = Path.home() / ".langflow" / "langflow-exe.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class _Tee:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, data: str) -> None:
        for stream in self._streams:
            try:
                stream.write(data)
                stream.flush()
            except OSError:
                pass

    def flush(self) -> None:
        for stream in self._streams:
            try:
                stream.flush()
            except OSError:
                pass

    def isatty(self) -> bool:
        return False


def log(message: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {message}"
    _boot_log(message)
    try:
        print(line, flush=True)
    except OSError:
        with _log_path().open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def ensure_windows_console() -> None:
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return
    import ctypes

    kernel32 = ctypes.windll.kernel32
    if kernel32.GetConsoleWindow() == 0:
        kernel32.AllocConsole()
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")  # noqa: SIM115
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")  # noqa: SIM115
        sys.stdin = open("CONIN$", "r", encoding="utf-8", errors="replace")  # noqa: SIM115


def _install_output_tee() -> None:
    log_handle = _log_path().open("a", encoding="utf-8")
    if getattr(sys, "frozen", False):
        ensure_windows_console()
    if sys.stdout is not None:
        sys.stdout = _Tee(sys.stdout, log_handle)
    if sys.stderr is not None:
        sys.stderr = _Tee(sys.stderr, log_handle)


def pause(message: str = "Press Enter to exit...") -> None:
    log(message)
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass


def _explain_exit_code(code: int) -> str:
    if code == 3:
        return (
            "Uvicorn failed to start (exit code 3). See langflow-exe.log and langflow-exe-boot.log. "
            "Common: missing UI in build, DB error, or PostgreSQL < 15."
        )
    if code == 1:
        return "Langflow exited with an error. See log files in %USERPROFILE%\\.langflow\\"
    return f"Langflow exited with code {code}."


def main() -> None:
    _install_output_tee()
    log("Langflow executable starting...")
    log(f"Logs: {_log_path()} and {_boot_log_path()}")
    log(f"frozen={getattr(sys, 'frozen', False)} argv={sys.argv!r}")

    multiprocessing.freeze_support()

    if getattr(sys, "frozen", False) and len(sys.argv) == 1:
        sys.argv.append("run")
        log("No CLI args: defaulting to 'langflow run'")

    from langflow.utils.frozen_bundle import configure_frozen_environment

    configure_frozen_environment()

    import os

    log(f"LANGFLOW_CONFIG_DIR={os.environ.get('LANGFLOW_CONFIG_DIR', '')}")
    db_url = os.environ.get("LANGFLOW_DATABASE_URL", "")
    if db_url.startswith(("postgresql", "postgres")):
        log(f"LANGFLOW_DATABASE_URL={db_url}")
    else:
        log(f"LANGFLOW_DATABASE_URL={db_url or '(sqlite default)'}")

    from langflow.utils.frozen_bundle import resolve_frontend_dir

    frontend = resolve_frontend_dir()
    log(f"Frontend: {frontend} index.html={ (frontend / 'index.html').exists() }")

    from langflow.langflow_launcher import main as langflow_main

    log("Starting server. First launch can take 1-3 minutes. Then open http://127.0.0.1:7860")
    langflow_main()


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (1 if exc.code else 0)
        if code:
            log(_explain_exit_code(code))
            pause()
        sys.exit(code)
    except Exception:
        log("Fatal error:")
        for line in traceback.format_exc().splitlines():
            log(line)
        pause()
        sys.exit(1)
