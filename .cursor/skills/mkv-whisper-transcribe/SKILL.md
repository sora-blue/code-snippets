---
name: mkv-whisper-transcribe
description: >-
  Transcribe MKV or video files to text by trimming silence, converting to MP3,
  and running OpenAI Whisper. Works on WSL/Linux natively and on Windows via
  workflows/run.py (auto-routes to WSL when ffmpeg/whisper are missing). Use when
  the user asks to transcribe MKV, convert meeting recordings to text, extract
  subtitles from video, or run the speech-to-text workflow.
---

# MKV Whisper Transcribe

## Repo scripts

- `workflows/speech-to-text/mkv_whisper_workflow.py` — full pipeline
- `workflows/speech-to-text/mkv_to_trimmed_mp3.py` — audio-only step
- `workflows/run.py` — cross-platform entry (Windows → WSL fallback)

## Prerequisites

| Tool | Purpose |
|------|---------|
| `ffmpeg`, `ffprobe` | silence detect + MP3 export |
| `whisper` | transcription (`pip install openai-whisper`) |

On Windows without these in PATH, always use `workflows/run.py` (not the inner script directly).

## Quick start

**Unified entry (recommended on Windows):**

```bash
python workflows/run.py speech-to-text "<VIDEO.mkv>"
```

**WSL / Linux:**

```bash
python3 workflows/speech-to-text/mkv_whisper_workflow.py /mnt/d/path/to/file.mkv
```

**Output layout:** `<output-root>/<mkv-stem>/` containing `<stem>.mp3` plus Whisper files (`txt`, `vtt`, `srt`, …).

## Common flags

| Flag | Default | Notes |
|------|---------|-------|
| `--model` | `turbo` | Use `tiny` or `base` for quick tests |
| `--language` | `zh` | Whisper language code |
| `--mp3` | — | Skip MKV→MP3 if MP3 already exists |
| `--device` | auto | `cuda` when GPU available |
| `--output-root` | MKV parent dir | Per-file folder parent |

Pass flags after the workflow name in `run.py`:

```bash
python workflows/run.py speech-to-text "D:\path\file.mkv" --model tiny --language zh
```

## Verify tools

```bash
python workflows/run.py speech-to-text --check-tools
```

## Path rules

- Windows paths (`D:\...`) are accepted by `run.py` and converted for WSL.
- In WSL shells, prefer `/mnt/d/...` paths.
- Do not hand-edit paths when using `run.py`; pass the user’s path as-is.

## Audio-only (no Whisper)

```bash
python workflows/run.py mkv-to-mp3 "D:\path\file.mkv" -o "D:\path\out.mp3"
```
