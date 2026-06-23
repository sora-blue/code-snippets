# code-snippets

个人可复用脚本库。活跃工作流在 `workflows/`，历史片段在 `legacy/`。

## 工作流

| 工作流 | 入口 | 说明 |
|--------|------|------|
| MKV 转 MP3（去静音） | `workflows/run.py mkv-to-mp3` | 需要 ffmpeg |
| MKV 转写 | `workflows/run.py speech-to-text` | 需要 ffmpeg + whisper |
| RSS → OPML | `workflows/run.py rss-to-opml` | 纯 Python |
| 视频保留人声 | `workflows/run.py strip-vocals` | 需要 ffmpeg + demucs |
| Unity E-mote 容器扫描 | `workflows/run.py unity-emote-scan` | 需要 UnityPy |
| Unity E-mote PSB 提取/链接 | `workflows/run.py unity-emote-extract` | 需要 UnityPy + Pillow；链接需 FreeMote |

## Windows / WSL

在 **Windows 原生** 若未安装 ffmpeg/whisper，统一入口 `workflows/run.py` 会自动通过 WSL 执行（路径 `D:\...` 会转换为 `/mnt/d/...`）。

```powershell
# Windows（自动走 WSL，若本机无 ffmpeg）
python workflows/run.py mkv-to-mp3 "D:\path\video.mkv" -o "D:\path\out.mp3"

# Unity E-mote（需 pip install UnityPy Pillow）
python workflows/run.py unity-emote-scan "D:\path\data.unity3d" -o D:\path\manifest.json
python workflows/run.py unity-emote-extract "D:\path\data.unity3d" --pairs D:\path\emote_pairs --psb-out D:\path\emote_psb --freemote D:\path\FreeMote --refresh-manifest

# WSL / Linux 直接调用
python3 workflows/speech-to-text/mkv_whisper_workflow.py /mnt/d/path/video.mkv
```

## Cursor Skills

项目内技能：`.cursor/skills/`（`mkv-whisper-transcribe`、`rss-to-opml`、`strip-vocals-from-video`、`unity-emote-psb-extract`、`workflow-skill-packaging`）。

全局技能（任意项目可用）：`~/.cursor/skills/workflow-skill-packaging`（与仓库内同名 skill 同步）。

## legacy/

Win32 小工具、算法练习、油猴脚本、过时爬虫等，不再维护。
