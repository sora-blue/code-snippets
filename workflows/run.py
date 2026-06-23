#!/usr/bin/env python3
"""Run a workflow script with Windows/WSL path and runtime handling."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).resolve().parent
if str(WORKFLOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WORKFLOWS_DIR))

from _lib.platform import (
    build_wsl_command,
    is_windows_native,
    media_runtime_hint,
    python_executable,
    repo_root,
    require_commands,
    resolve_input_path,
    windows_to_wsl_path,
)


WORKFLOWS = {
    "speech-to-text": "speech-to-text/mkv_whisper_workflow.py",
    "mkv-to-mp3": "speech-to-text/mkv_to_trimmed_mp3.py",
    "rss-to-opml": "rss-to-opml/rssconv.py",
    "strip-vocals": "media/strip_vocals.py",
    "unity-emote-scan": "unity-emote/scan_containers.py",
    "unity-emote-extract": "unity-emote/extract_pairs.py",
}


MEDIA_WORKFLOWS = {"speech-to-text", "mkv-to-mp3", "strip-vocals"}


def parse_args() -> argparse.Namespace:
    check_tools = "--check-tools" in sys.argv
    argv = [arg for arg in sys.argv if arg != "--check-tools"]

    parser = argparse.ArgumentParser(description="Run a code-snippets workflow.")
    parser.add_argument("workflow", choices=sorted(WORKFLOWS))
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to the workflow")
    namespace = parser.parse_args(argv[1:])
    namespace.check_tools = check_tools
    if namespace.args and namespace.args[0] == "--":
        namespace.args = namespace.args[1:]
    return namespace


def workflow_script(name: str) -> Path:
    return repo_root() / "workflows" / WORKFLOWS[name]


def required_tools(name: str) -> tuple[str, ...]:
    if name == "speech-to-text":
        return ("ffmpeg", "ffprobe", "whisper")
    if name == "mkv-to-mp3":
        return ("ffmpeg", "ffprobe")
    if name == "strip-vocals":
        return ("ffmpeg", "demucs")
    return ()


def _to_runtime_path(path: Path) -> str:
    return windows_to_wsl_path(path)


def _to_runtime_args(workflow_args: list[str]) -> list[str]:
    path_flags = {
        "-o",
        "--output",
        "--output-root",
        "--mp3",
        "--in",
        "--out",
        "--pairs",
        "--psb-out",
        "--freemote",
        "--manifest",
    }
    converted: list[str] = []
    index = 0
    while index < len(workflow_args):
        token = workflow_args[index]
        converted.append(token)
        if token in path_flags and index + 1 < len(workflow_args):
            converted.append(_to_runtime_path(Path(workflow_args[index + 1])))
            index += 2
            continue
        if not token.startswith("-") and _looks_like_existing_path(token):
            converted[-1] = _to_runtime_path(Path(token))
        index += 1
    return converted


def _looks_like_existing_path(token: str) -> bool:
    candidate = Path(token)
    if candidate.exists():
        return True
    return candidate.suffix != "" and (
        token.startswith("/") or (len(token) > 2 and token[1] == ":")
    )


def normalize_args(workflow: str, args: list[str]) -> list[str]:
    if not args:
        return args

    normalized: list[str] = []
    positional_slots = {
        "speech-to-text": 1,
        "mkv-to-mp3": 1,
        "strip-vocals": 1,
        "unity-emote-scan": 1,
        "unity-emote-extract": 1,
    }
    positional_remaining = positional_slots.get(workflow, 0)
    if workflow == "unity-emote-extract" and "--link-only" in args:
        positional_remaining = 0

    index = 0
    while index < len(args):
        token = args[index]
        if token in {"-h", "--help"}:
            normalized.append(token)
            index += 1
            continue

        if positional_remaining > 0 and not token.startswith("-"):
            normalized.append(str(resolve_input_path(token)))
            positional_remaining -= 1
            index += 1
            continue

        path_option_flags = {
            "-o",
            "--output",
            "--output-root",
            "--mp3",
            "--in",
            "--out",
            "--pairs",
            "--psb-out",
            "--freemote",
            "--manifest",
        }
        if token in path_option_flags and index + 1 < len(args):
            normalized.extend([token, str(resolve_input_path(args[index + 1]))])
            index += 2
            continue

        if token.startswith("--") and "=" in token:
            key, value = token.split("=", 1)
            if key in {
                "--output",
                "--output-root",
                "--mp3",
                "--in",
                "--out",
                "--pairs",
                "--psb-out",
                "--freemote",
                "--manifest",
            }:
                normalized.append(f"{key}={resolve_input_path(value)}")
            else:
                normalized.append(token)
            index += 1
            continue

        normalized.append(token)
        index += 1

    return normalized


def main() -> int:
    args = parse_args()
    script = workflow_script(args.workflow)
    if not script.exists():
        raise SystemExit(f"Error: workflow script not found: {script}")

    runtime = media_runtime_hint()
    if args.check_tools:
        tools = required_tools(args.workflow)
        print(f"runtime={runtime}")
        if runtime == "windows-via-wsl" and tools:
            checks = " && ".join(f"command -v {tool}" for tool in tools)
            command = build_wsl_command(["bash", "-lc", checks])
            return subprocess.run(command).returncode
        if tools:
            require_commands(*tools)
        print("ok")
        return 0

    workflow_args = normalize_args(args.workflow, args.args)
    use_wsl = (
        is_windows_native()
        and runtime == "windows-via-wsl"
        and args.workflow in MEDIA_WORKFLOWS
    )
    workflow_args = _to_runtime_args(workflow_args) if use_wsl else workflow_args
    command = [python_executable(), str(script), *workflow_args]

    if use_wsl:
        wsl_script = windows_to_wsl_path(script)
        wsl_command = ["python3", wsl_script, *workflow_args]
        completed = subprocess.run(build_wsl_command(wsl_command))
        return completed.returncode

    completed = subprocess.run(command, cwd=repo_root())
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
