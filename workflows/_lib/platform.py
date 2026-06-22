"""Cross-platform helpers for workflows on Windows, WSL, and Linux."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath


def is_wsl() -> bool:
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        with open("/proc/version", encoding="utf-8") as handle:
            return "microsoft" in handle.read().lower()
    except OSError:
        return False


def is_windows_native() -> bool:
    return platform.system() == "Windows" and not is_wsl()


def windows_to_wsl_path(path: str | Path) -> str:
    resolved = str(Path(path).resolve())
    pure = PureWindowsPath(resolved)
    drive = pure.drive.rstrip(":").lower()
    if not drive:
        return resolved.replace("\\", "/")
    remainder = pure.as_posix().split(":", 1)[-1].lstrip("/")
    return f"/mnt/{drive}/{remainder}"


def wsl_to_windows_path(path: str | Path) -> str:
    text = str(path).replace("\\", "/")
    if not text.startswith("/mnt/"):
        return str(Path(text).resolve())
    parts = text.split("/")
    if len(parts) < 4:
        return text
    drive = parts[2].upper()
    tail = "/".join(parts[3:])
    return f"{drive}:\\{tail.replace('/', '\\')}"


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def require_commands(*names: str) -> None:
    missing = [name for name in names if not command_exists(name)]
    if missing:
        raise SystemExit(f"Error: missing required command(s): {', '.join(missing)}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_input_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def media_runtime_hint() -> str:
    if is_windows_native():
        if command_exists("ffmpeg") and command_exists("whisper"):
            return "windows-native"
        if shutil.which("wsl"):
            return "windows-via-wsl"
        return "windows-missing-tools"
    return "unix"


def build_wsl_command(command: list[str], *, workdir: Path | None = None) -> list[str]:
    root = repo_root()
    wsl_root = windows_to_wsl_path(root)
    wsl_workdir = windows_to_wsl_path(workdir or root)
    inner = " ".join(_shell_quote(part) for part in command)
    script = f"cd {_shell_quote(wsl_workdir)} && {inner}"
    return ["wsl", "-e", "bash", "-lc", script]


def run_workflow(command: list[str], *, workdir: Path | None = None) -> int:
    runtime = media_runtime_hint()
    if runtime == "windows-via-wsl":
        completed = subprocess.run(build_wsl_command(command, workdir=workdir))
        return completed.returncode
    completed = subprocess.run(command, cwd=workdir or repo_root())
    return completed.returncode


def python_executable() -> str:
    return sys.executable


def _shell_quote(value: str) -> str:
    if not value:
        return "''"
    if all(char.isalnum() or char in "/._-:" for char in value):
        return value
    return "'" + value.replace("'", "'\\''") + "'"
