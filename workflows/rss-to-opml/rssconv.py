#!/usr/bin/env python3
"""Convert tab-separated RSS title/URL lines into an OPML export file."""

from __future__ import annotations

import argparse
import random
import re
import xml.sax.saxutils
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate OPML from RSS URLs")
    parser.add_argument("--in", dest="input_path", required=True, help="input file path")
    parser.add_argument("--out", dest="output_path", required=True, help="output file path")
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=5,
        help="length of icon text (first word prefix)",
    )
    return parser.parse_args()


def convert_line(line: str, icon_length: int) -> str | None:
    line = line.strip()
    if not line or "not found" in line:
        return None

    match = re.match(r"(.+)\s+(https?://\S+)", line)
    if not match:
        return None

    title = xml.sax.saxutils.escape(match.group(1).strip())
    url = xml.sax.saxutils.escape(match.group(2).strip())
    icon = title.split()[0][:icon_length]
    color = "#%06x" % random.randint(0, 0xFFFFFF)
    return (
        f'<outline type="rss" text="{title}" title="{title}" xmlUrl="{url}" '
        f'desc="{title}" icon="{icon}" iconType="2" color="{color}"/>'
    )


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_path).expanduser().resolve()
    output_path = Path(args.output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as handle_in, output_path.open(
        "w", encoding="utf-8"
    ) as handle_out:
        handle_out.write(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<opml version="1.0"><head><title>rolly rss export</title></head><body>\n'
        )
        for line in handle_in:
            outline = convert_line(line, args.length)
            if outline:
                handle_out.write(outline + "\n")
        handle_out.write("</body></opml>\n")

    print(f"Created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
