"""PyInstaller runtime hook: ensure a visible console on Windows (double-click launch)."""

import sys

if sys.platform == "win32" and getattr(sys, "frozen", False):
    import ctypes

    kernel32 = ctypes.windll.kernel32
    if kernel32.GetConsoleWindow() == 0:
        kernel32.AllocConsole()
        # Rebind stdio to the new console (PyInstaller may leave these as None).
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")  # noqa: SIM115
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")  # noqa: SIM115
        sys.stdin = open("CONIN$", "r", encoding="utf-8", errors="replace")  # noqa: SIM115
