#!/usr/bin/env python3
"""Replace a video soundtrack with an isolated vocal stem using demucs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract vocals with demucs and mux them back into the video."
    )
    parser.add_argument("input", type=Path, help="Input video file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output video path. Defaults to <stem>_vocals.<ext> beside the input.",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep generated MP3 and demucs output directories.",
    )
    return parser.parse_args()


def require_commands() -> None:
    missing = [name for name in ("ffmpeg", "demucs") if shutil.which(name) is None]
    if missing:
        raise SystemExit(f"Error: missing required command(s): {', '.join(missing)}")


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("Running:", " ".join(command))
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def vocals_path(work_dir: Path, base_name: str) -> Path:
    return work_dir / "separated" / "htdemucs" / base_name / "vocals.wav"


def main() -> int:
    args = parse_args()
    require_commands()

    input_path = args.input.expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Error: input file does not exist: {input_path}")

    extension = input_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise SystemExit(f"Error: unsupported extension {extension!r}")

    base_name = input_path.stem
    work_dir = input_path.parent
    mp3_path = work_dir / f"{base_name}.mp3"
    vocals_file = vocals_path(work_dir, base_name)
    output_path = (
        args.output.expanduser().resolve()
        if args.output
        else work_dir / f"{base_name}_vocals{extension}"
    )

    if not vocals_file.exists():
        run(
            [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-i",
                str(input_path),
                "-vn",
                "-acodec",
                "libmp3lame",
                str(mp3_path),
            ],
            cwd=work_dir,
        )
        run(["demucs", "--two-stems=vocals", str(mp3_path)], cwd=work_dir)

    if not vocals_file.exists():
        raise SystemExit(f"Error: expected vocals stem not found: {vocals_file}")

    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-i",
            str(input_path),
            "-i",
            str(vocals_file),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            str(output_path),
        ],
        cwd=work_dir,
    )

    if not args.keep_temp:
        if mp3_path.exists():
            mp3_path.unlink()
        separated_dir = work_dir / "separated"
        if separated_dir.exists():
            shutil.rmtree(separated_dir)

    print(f"Created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
