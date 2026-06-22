---
name: strip-vocals-from-video
description: >-
  Extract vocal stems with demucs and remux them into the original video,
  replacing the soundtrack. Supports mp4/mkv/avi/mov on WSL/Linux; on Windows
  use workflows/run.py for automatic WSL routing when ffmpeg/demucs are not in
  PATH. Use when the user wants to remove background music, keep vocals only,
  or isolate voice from a video file.
---

# Strip Vocals From Video

Keeps **vocals** and replaces the video audio track (despite the name — this is the legacy behavior of `strip_vocal_from_video.sh`).

## Script

`workflows/media/strip_vocals.py` (replaces `legacy/shell-scripts/strip_vocal_from_video.sh`)

## Prerequisites

- `ffmpeg`
- `demucs` (`pip install demucs`)

On Windows without these in PATH, use `workflows/run.py`.

## Run

```bash
python workflows/run.py strip-vocals "D:\path\video.mkv"
```

WSL / Linux:

```bash
python3 workflows/media/strip_vocals.py /mnt/d/path/video.mkv
```

**Default output:** `<stem>_vocals.<ext>` beside the input.

## Options

| Flag | Purpose |
|------|---------|
| `-o`, `--output` | Custom output path |
| `--keep-temp` | Keep intermediate MP3 and `separated/` folder |

## Notes

- First run downloads demucs models; can take several minutes.
- Heavy GPU workload — warn the user on long files.
- Supported extensions: `.mp4`, `.mkv`, `.avi`, `.mov`
