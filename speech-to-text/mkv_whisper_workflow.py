#!/usr/bin/env python3
"""Create a per-MKV output folder, convert audio to MP3, then transcribe with Whisper."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run mkv_to_trimmed_mp3.py and Whisper, keeping generated files in "
            "a folder named after the MKV file."
        )
    )
    parser.add_argument("mkv", type=Path, help="Input MKV file")
    parser.add_argument(
        "--mp3",
        type=Path,
        help="Use an existing MP3 instead of converting the MKV.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Parent directory for the per-MKV folder. Defaults to the MKV directory.",
    )
    parser.add_argument(
        "--model",
        default="turbo",
        help="Whisper model name. Default: turbo",
    )
    parser.add_argument(
        "--language",
        default="zh",
        help="Whisper language. Default: zh",
    )
    parser.add_argument(
        "--output-format",
        default="all",
        choices=("txt", "vtt", "srt", "tsv", "json", "all"),
        help="Whisper output format. Default: all",
    )
    parser.add_argument(
        "--device",
        help="Whisper device, for example cpu or cuda. Defaults to Whisper's default.",
    )
    parser.add_argument(
        "--overwrite-mp3",
        action="store_true",
        help="Overwrite the generated MP3 when converting from MKV.",
    )
    parser.add_argument(
        "--threshold",
        default="-30dB",
        help="Silence threshold passed to mkv_to_trimmed_mp3.py. Default: -30dB",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.5,
        help="Minimum silence duration passed to mkv_to_trimmed_mp3.py. Default: 0.5",
    )
    parser.add_argument(
        "--bitrate",
        default="192k",
        help="MP3 bitrate passed to mkv_to_trimmed_mp3.py. Default: 192k",
    )
    parser.add_argument(
        "--remove-silence-longer-than",
        type=float,
        default=5.0,
        help=(
            "Remove middle silence intervals longer than this many seconds "
            "when converting from MKV. Use 0 to disable. Default: 5.0"
        ),
    )
    parser.add_argument(
        "--merge-silence-gap",
        type=float,
        default=2.0,
        help=(
            "Merge detected silence intervals separated by short non-silent gaps "
            "when converting from MKV. Default: 2.0"
        ),
    )
    parser.add_argument(
        "--min-keep-duration",
        type=float,
        default=1.0,
        help="Drop kept audio fragments shorter than this many seconds. Default: 1.0",
    )
    return parser.parse_args()


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Error: missing required command: {name}")


def run(command: list[str]) -> None:
    print("Running:")
    print(" ".join(command))
    completed = subprocess.run(command, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def prepare_existing_mp3(source_mp3: Path, target_mp3: Path) -> Path:
    source_mp3 = source_mp3.expanduser().resolve()
    if not source_mp3.exists():
        raise SystemExit(f"Error: MP3 file does not exist: {source_mp3}")
    if source_mp3.suffix.lower() != ".mp3":
        print(f"Warning: MP3 file does not end with .mp3: {source_mp3}", file=sys.stderr)

    if source_mp3 == target_mp3:
        return target_mp3

    if target_mp3.exists():
        print(f"Using existing output MP3: {target_mp3}")
        return target_mp3

    shutil.copy2(source_mp3, target_mp3)
    print(f"Copied MP3: {source_mp3} -> {target_mp3}")
    return target_mp3


def convert_mkv(script_path: Path, mkv_path: Path, mp3_path: Path, args: argparse.Namespace) -> None:
    command = [
        sys.executable,
        str(script_path),
        str(mkv_path),
        "-o",
        str(mp3_path),
        f"--threshold={args.threshold}",
        "--duration",
        str(args.duration),
        "--bitrate",
        args.bitrate,
        "--remove-silence-longer-than",
        str(args.remove_silence_longer_than),
        "--merge-silence-gap",
        str(args.merge_silence_gap),
        "--min-keep-duration",
        str(args.min_keep_duration),
    ]
    if args.overwrite_mp3:
        command.append("--overwrite")
    run(command)


def transcribe(mp3_path: Path, output_dir: Path, args: argparse.Namespace) -> None:
    command = [
        "whisper",
        str(mp3_path),
        "--language",
        args.language,
        "--task",
        "transcribe",
        "--model",
        args.model,
        "--output_format",
        args.output_format,
        "--output_dir",
        str(output_dir),
    ]
    if args.device:
        command.extend(["--device", args.device])
    run(command)


def main() -> int:
    args = parse_args()
    require_command("whisper")

    mkv_path = args.mkv.expanduser().resolve()
    if not mkv_path.exists():
        print(f"Error: MKV file does not exist: {mkv_path}", file=sys.stderr)
        return 1
    if mkv_path.suffix.lower() != ".mkv":
        print(f"Warning: input file does not end with .mkv: {mkv_path}", file=sys.stderr)

    script_path = Path(__file__).with_name("mkv_to_trimmed_mp3.py").resolve()
    if not args.mp3 and not script_path.exists():
        print(f"Error: conversion script does not exist: {script_path}", file=sys.stderr)
        return 1

    output_root = args.output_root.expanduser().resolve() if args.output_root else mkv_path.parent
    output_dir = output_root / mkv_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = output_dir / f"{mkv_path.stem}.mp3"

    if args.mp3:
        prepare_existing_mp3(args.mp3, mp3_path)
    else:
        convert_mkv(script_path, mkv_path, mp3_path, args)

    transcribe(mp3_path, output_dir, args)
    print(f"Done. Output directory: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
