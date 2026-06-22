# code-snippets

个人可复用脚本库。活跃工作流在 `workflows/`，历史片段在 `legacy/`。

## 工作流

| 工作流 | 入口 | 说明 |
|--------|------|------|
| MKV 转 MP3（去静音） | `workflows/run.py mkv-to-mp3` | 需要 ffmpeg |
| MKV 转写 | `workflows/run.py speech-to-text` | 需要 ffmpeg + whisper |
| RSS → OPML | `workflows/run.py rss-to-opml` | 纯 Python |
| 视频保留人声 | `workflows/run.py strip-vocals` | 需要 ffmpeg + demucs |

## Windows / WSL

在 **Windows 原生** 若未安装 ffmpeg/whisper，统一入口 `workflows/run.py` 会自动通过 WSL 执行（路径 `D:\...` 会转换为 `/mnt/d/...`）。

```powershell
# Windows（自动走 WSL，若本机无 ffmpeg）
python workflows/run.py mkv-to-mp3 "D:\Downloads\obs\test\2026-06-03_11-11-27.mkv" -o "D:\Downloads\obs\test\out.mp3"

# WSL / Linux 直接调用
python3 workflows/speech-to-text/mkv_whisper_workflow.py /mnt/d/Downloads/obs/test/2026-06-03_11-11-27.mkv
```

## Cursor Skills

项目内技能：`.cursor/skills/`（`mkv-whisper-transcribe`、`rss-to-opml`、`strip-vocals-from-video`）。

## legacy/

Win32 小工具、算法练习、油猴脚本、过时爬虫等，不再维护。
