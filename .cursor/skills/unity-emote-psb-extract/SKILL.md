---
name: unity-emote-psb-extract
description: >-
  Extract E-mote PSB and Texture2D pairs from Unity data.unity3d using
  ResourceManager container paths (not m_Name), export PNG textures, and
  optionally link with FreeMote PsBuild. Use when pairing PSB with textures
  for E-mote Editor, fixing AssetStudio export mismatches, or preparing
  emote_live2d / FreeMote decompile input.
---

# Unity E-mote PSB Extract

## Repo scripts

| Script | Role |
|--------|------|
| `workflows/unity-emote/scan_containers.py` | Inspect container paths, write manifest JSON |
| `workflows/unity-emote/extract_pairs.py` | Extract PSB+PNG pairs, optional PsBuild link |
| `workflows/unity-emote/emote_lib.py` | Shared pairing / export logic |
| `workflows/run.py` | Unified entry (`unity-emote-scan`, `unity-emote-extract`) |

## Prerequisites

| Dependency | Purpose |
|------------|---------|
| `UnityPy` | Read `data.unity3d` / AssetBundle |
| `Pillow` | Export Texture2D as PNG |
| FreeMote `PsBuild.exe` | Link PSB + textures (`--freemote`, optional) |

```bash
pip install UnityPy Pillow
```

## Quick start

**1. Scan containers (optional but recommended first run):**

```bash
python workflows/run.py unity-emote-scan "path/to/Game_Data/data.unity3d" -o manifest.json
```

**2. Extract + link:**

```bash
python workflows/run.py unity-emote-extract "path/to/Game_Data/data.unity3d" ^
  --pairs path/to/emote_pairs ^
  --psb-out path/to/emote_psb ^
  --freemote path/to/FreeMote ^
  --refresh-manifest
```

**Output:**

- `<pairs>/<folder>/` — `{folder}.psb` + `{folder}_texNNN.png`
- `<psb-out>/<folder>/` — `{folder}_linked.psb` (E-mote Editor ready)
- `<pairs>/MANIFEST.tsv`, `batch_summary.json`

## Common flags

| Flag | Default | Notes |
|------|---------|-------|
| `--prefix` | `anim/` | Container path prefix to scan |
| `--pairs` | `emote_pairs` | Raw extract root |
| `--psb-out` | `emote_psb` | Linked PSB root |
| `--freemote` | — | FreeMote dir with `PsBuild.exe` |
| `--manifest` | `<pairs>/container_manifest.json` | Cached container index |
| `--extract-only` | — | Skip PsBuild link |
| `--link-only` | — | Re-link from existing pairs + manifest |
| `--no-clean` | — | Do not wipe output dirs first |
| `--refresh-manifest` | — | Rewrite manifest from bundle |

## Pairing rules (critical)

- Pair by **ResourceManager container path**, same as [AssetStudio](https://github.com/Perfare/AssetStudio) `m_Container`.
- PSB at `anim/.../name`; textures at `anim/.../name_tex000`, `_tex001`, …
- **Never** pair only by `m_Name` — duplicate outfit names across `base` / `special` paths will mismatch.
- Read PSB bytes via `read_typetree()["m_Script"]` with `surrogateescape`; naive UTF-8 export truncates PSB and breaks PsBuild.

See [reference.md](reference.md) for pitfalls, folder naming, and Live2D next steps.

## Link-only (re-run PsBuild)

```bash
python workflows/run.py unity-emote-extract --link-only ^
  --pairs path/to/emote_pairs ^
  --psb-out path/to/emote_psb ^
  --freemote path/to/FreeMote
```

## Verify

- `batch_summary.json`: `ok` should equal `total`.
- Spot-check PSB size (~160 KB+ for typical CG; ~137 KB often means truncated export).
- Open `{folder}_linked.psb` in E-mote Editor.
