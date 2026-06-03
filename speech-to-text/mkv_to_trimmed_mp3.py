#!/usr/bin/env python3
"""Convert an MKV file to MP3 and remove long silence.

Requires ffmpeg to be installed and available on PATH.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an MKV file to MP3, trim leading/trailing silence, "
            "and remove long silence in the middle."
        )
    )
    parser.add_argument("input", type=Path, help="Input MKV file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output MP3 file. Defaults to the input filename with .mp3 extension.",
    )
    parser.add_argument(
        "--threshold",
        default="-30dB",
        help="Silence threshold used by ffmpeg silencedetect. Default: -30dB",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.5,
        help="Minimum silence duration in seconds before trimming. Default: 0.5",
    )
    parser.add_argument(
        "--bitrate",
        default="192k",
        help="MP3 audio bitrate. Default: 192k",
    )
    parser.add_argument(
        "--remove-silence-longer-than",
        type=float,
        default=5.0,
        help=(
            "Remove silence intervals in the middle that are longer than this "
            "many seconds. Use 0 to disable. Default: 5.0"
        ),
    )
    parser.add_argument(
        "--merge-silence-gap",
        type=float,
        default=2.0,
        help=(
            "Merge detected silence intervals separated by short non-silent gaps. "
            "This helps remove long quiet sections interrupted by brief noise. "
            "Default: 2.0"
        ),
    )
    parser.add_argument(
        "--min-keep-duration",
        type=float,
        default=1.0,
        help="Drop kept audio fragments shorter than this many seconds. Default: 1.0",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    return parser.parse_args()


def require_ffmpeg() -> None:
    missing = [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]
    if missing:
        raise SystemExit(f"Error: missing required command(s): {', '.join(missing)}")


def run_capture(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def probe_duration(input_path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]
    completed = run_capture(command)
    if completed.returncode != 0:
        print(completed.stderr, file=sys.stderr)
        raise SystemExit("Error: ffprobe could not read the input duration.")

    try:
        return float(completed.stdout.strip())
    except ValueError as exc:
        raise SystemExit(f"Error: invalid ffprobe duration: {completed.stdout!r}") from exc


def detect_silences(input_path: Path, threshold: str, duration: float) -> list[tuple[float, float | None]]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        str(input_path),
        "-vn",
        "-af",
        f"silencedetect=noise={threshold}:d={duration}",
        "-f",
        "null",
        "-",
    ]
    completed = run_capture(command)
    if completed.returncode != 0:
        print(completed.stderr, file=sys.stderr)
        raise SystemExit("Error: ffmpeg silencedetect failed.")

    intervals: list[tuple[float, float | None]] = []
    open_start: float | None = None
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
    start_re = re.compile(rf"silence_start:\s*({number})")
    end_re = re.compile(rf"silence_end:\s*({number})")

    for line in completed.stderr.splitlines():
        start_match = start_re.search(line)
        if start_match:
            open_start = max(0.0, float(start_match.group(1)))
            continue

        end_match = end_re.search(line)
        if end_match and open_start is not None:
            intervals.append((open_start, float(end_match.group(1))))
            open_start = None

    if open_start is not None:
        intervals.append((open_start, None))

    return intervals


def compute_trim_points(
    media_duration: float,
    silence_intervals: list[tuple[float, float | None]],
) -> tuple[float, float]:
    trim_start = 0.0
    trim_end = media_duration
    edge_tolerance = 0.10

    if silence_intervals:
        first_start, first_end = silence_intervals[0]
        if first_start <= edge_tolerance and first_end is not None:
            trim_start = min(first_end, media_duration)

        last_start, last_end = silence_intervals[-1]
        resolved_last_end = media_duration if last_end is None else last_end
        if resolved_last_end >= media_duration - edge_tolerance:
            trim_end = max(last_start, trim_start)

    if trim_end <= trim_start:
        raise SystemExit("Error: trim settings would remove the whole audio.")

    return trim_start, trim_end


def compute_keep_ranges(
    trim_start: float,
    trim_end: float,
    silence_intervals: list[tuple[float, float | None]],
    remove_silence_longer_than: float,
    merge_silence_gap: float,
) -> list[tuple[float, float]]:
    if remove_silence_longer_than <= 0:
        return [(trim_start, trim_end)]

    keep_ranges: list[tuple[float, float]] = []
    cursor = trim_start
    edge_tolerance = 0.10
    merged_silences: list[tuple[float, float]] = []

    for silence_start, silence_end in silence_intervals:
        if silence_end is None:
            silence_end = trim_end

        cut_start = max(silence_start, trim_start)
        cut_end = min(silence_end, trim_end)
        if cut_end <= cut_start:
            continue

        is_middle_silence = (
            cut_start > trim_start + edge_tolerance
            and cut_end < trim_end - edge_tolerance
        )
        if not is_middle_silence:
            continue

        if merged_silences and cut_start - merged_silences[-1][1] <= merge_silence_gap:
            previous_start, previous_end = merged_silences[-1]
            merged_silences[-1] = (previous_start, max(previous_end, cut_end))
        else:
            merged_silences.append((cut_start, cut_end))

    for cut_start, cut_end in merged_silences:
        if cut_end - cut_start <= remove_silence_longer_than:
            continue
        if cut_start > cursor:
            keep_ranges.append((cursor, cut_start))
        cursor = max(cursor, cut_end)

    if cursor < trim_end:
        keep_ranges.append((cursor, trim_end))

    if not keep_ranges:
        raise SystemExit("Error: silence removal would remove the whole audio.")

    return keep_ranges


def build_filter_complex(keep_ranges: list[tuple[float, float]]) -> str:
    parts = []
    labels = []
    for index, (start, end) in enumerate(keep_ranges):
        label = f"a{index}"
        labels.append(f"[{label}]")
        parts.append(
            f"[0:a]atrim=start={start:.6f}:end={end:.6f},"
            f"asetpts=PTS-STARTPTS[{label}]"
        )

    parts.append(f"{''.join(labels)}concat=n={len(keep_ranges)}:v=0:a=1[outa]")
    return ";".join(parts)


def build_command(args: argparse.Namespace, output: Path, keep_ranges: list[tuple[float, float]]) -> list[str]:
    if len(keep_ranges) == 1:
        trim_start, trim_end = keep_ranges[0]
        return [
            "ffmpeg",
            "-hide_banner",
            "-y" if args.overwrite else "-n",
            "-i",
            str(args.input),
            "-ss",
            f"{trim_start:.6f}",
            "-to",
            f"{trim_end:.6f}",
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            args.bitrate,
            str(output),
        ]

    return [
        "ffmpeg",
        "-hide_banner",
        "-y" if args.overwrite else "-n",
        "-i",
        str(args.input),
        "-filter_complex",
        build_filter_complex(keep_ranges),
        "-map",
        "[outa]",
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        args.bitrate,
        str(output),
    ]


def quote_concat_path(path: Path) -> str:
    return "'" + str(path).replace("'", "'\\''") + "'"


def build_segment_command(
    args: argparse.Namespace,
    output: Path,
    start: float,
    end: float,
) -> list[str]:
    return [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-ss",
        f"{start:.6f}",
        "-to",
        f"{end:.6f}",
        "-i",
        str(args.input),
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        args.bitrate,
        str(output),
    ]


def build_concat_command(args: argparse.Namespace, concat_list: Path, output: Path) -> list[str]:
    return [
        "ffmpeg",
        "-hide_banner",
        "-y" if args.overwrite else "-n",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(output),
    ]


def run(command: list[str], *, quiet: bool = False) -> int:
    if not quiet:
        print("Running:")
        print(" ".join(command))
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
    )
    return completed.returncode


def create_with_segment_concat(
    args: argparse.Namespace,
    output_path: Path,
    keep_ranges: list[tuple[float, float]],
) -> int:
    filtered_ranges = [
        (start, end)
        for start, end in keep_ranges
        if end - start >= args.min_keep_duration
    ]
    if not filtered_ranges:
        raise SystemExit("Error: min keep duration would remove the whole audio.")

    with tempfile.TemporaryDirectory(prefix=f"{output_path.stem}-segments-") as temp_name:
        temp_dir = Path(temp_name)
        segment_paths: list[Path] = []

        print(f"Extracting {len(filtered_ranges)} kept audio fragments...")
        for index, (start, end) in enumerate(filtered_ranges):
            if index == 0 or (index + 1) % 10 == 0 or index == len(filtered_ranges) - 1:
                print(f"Extracting fragment {index + 1}/{len(filtered_ranges)}")
            segment_path = temp_dir / f"segment-{index:04d}.mp3"
            returncode = run(build_segment_command(args, segment_path, start, end), quiet=True)
            if returncode != 0:
                return returncode
            segment_paths.append(segment_path)

        concat_list = temp_dir / "concat.txt"
        concat_list.write_text(
            "".join(f"file {quote_concat_path(path)}\n" for path in segment_paths),
            encoding="utf-8",
        )
        return run(build_concat_command(args, concat_list, output_path))


def main() -> int:
    args = parse_args()
    require_ffmpeg()

    input_path = args.input.expanduser().resolve()
    if not input_path.exists():
        print(f"Error: input file does not exist: {input_path}", file=sys.stderr)
        return 1
    if input_path.suffix.lower() != ".mkv":
        print(f"Warning: input file does not end with .mkv: {input_path}", file=sys.stderr)

    output_path = args.output.expanduser().resolve() if args.output else input_path.with_suffix(".mp3")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Detecting silence...")
    media_duration = probe_duration(input_path)
    silence_intervals = detect_silences(input_path, args.threshold, args.duration)
    trim_start, trim_end = compute_trim_points(media_duration, silence_intervals)
    keep_ranges = compute_keep_ranges(
        trim_start,
        trim_end,
        silence_intervals,
        args.remove_silence_longer_than,
        args.merge_silence_gap,
    )
    print(f"Input duration: {media_duration:.3f}s")
    print(f"Trim range: {trim_start:.3f}s to {trim_end:.3f}s")
    removed_count = len(keep_ranges) - 1
    if args.remove_silence_longer_than > 0:
        print(
            "Removed middle silence intervals longer than "
            f"{args.remove_silence_longer_than:.3f}s: {removed_count}"
        )
    print(f"Kept audio fragments: {len(keep_ranges)}")

    command_args = argparse.Namespace(**vars(args))
    command_args.input = input_path
    if len(keep_ranges) > 40:
        completed_returncode = create_with_segment_concat(command_args, output_path, keep_ranges)
    else:
        completed_returncode = run(build_command(command_args, output_path, keep_ranges))
    if completed_returncode != 0:
        return completed_returncode

    print(f"Created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
