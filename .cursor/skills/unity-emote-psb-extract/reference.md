# Unity E-mote PSB Extract — Reference

## Container pairing model

Unity stores assets in `ResourceManager.m_Container` as `(path, PPtr)` entries. AssetStudio and UnityPy expose the same paths.

Typical E-mote layout (visual-novel style bundles):

```
anim/cg/scene_01              → TextAsset (PSB magic PSB\x00)
anim/cg/scene_01_tex000       → Texture2D
anim/cg/scene_01_tex001       → Texture2D
anim/char_a/base/outfit       → PSB
anim/char_a/base/outfit_tex000 → Texture2D
anim/char_a/special/outfit    → PSB (different variant, same m_Name)
```

**Same container path rarely holds both PSB and Texture2D.** Pair by:

1. PSB container = base path
2. Texture containers = base + `_tex` + zero-padded index

## Why m_Name pairing fails

Multiple PSB TextAssets can share `m_Name` (e.g. `outfit`) under different folders (`base` vs `special`). Exporting from flat `TextAsset/` + `Texture2D/` folders and matching by name assigns wrong textures.

Always use container path from the bundle index.

## PSB byte export

Wrong (truncates binary):

```python
obj.read().m_Script  # may decode as UTF-8 string, corrupting bytes
```

Correct:

```python
script = obj.read_typetree()["m_Script"]
if isinstance(script, str):
    data = script.encode("utf-8", "surrogateescape")
else:
    data = bytes(script)
```

Truncated PSB (~137714 B vs ~165510 B) causes FreeMote `PsBuild link` → `Dullahan load failed`.

## Object lookup index

`path_id` is only unique per assets file. Index by `(assets_file.name, path_id, type_name)` to avoid resolving a MonoScript instead of TextAsset.

## Folder naming

Container `anim/cg/scene_01` → folder `cg__scene_01` (strip `anim/` prefix, join segments with `__`).

Container `anim/char_a/base/outfit` → `char_a__base__outfit`.

## FreeMote link

```bash
PsBuild.exe link -o <absolute_out.psb> <absolute.psb> <absolute_tex000.png> ...
```

Use **absolute** `-o` path; relative output may land in the wrong cwd.

## AssetStudio workflow (manual alternative)

1. Open `data.unity3d` in AssetStudio
2. Filter `anim/` container paths
3. Export PSB TextAsset and `_texNNN` textures per base path
4. Run PsBuild link manually

This skill automates the same pairing logic.

## Live2D / decompile next steps

| Tool | Role |
|------|------|
| FreeMote `PsbDecompile.exe` | PSB → layers / intermediate |
| LiveMote (UlyssesWu/D2Evil) | E-mote → Live2D (not publicly released) |

Linked PSB from this workflow is the correct input for E-mote Editor and FreeMote decompile. Full Live2D conversion still needs manual rigging or unreleased tools.

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| `Dullahan load failed` | Truncated PSB export |
| Wrong textures on model | m_Name pairing or wrong variant folder |
| `path_id not found` | Missing `file` in manifest; re-scan with `--refresh-manifest` |
| 0 pairs | Wrong `--prefix`; scan first to see container paths |
| Link 0/N | Missing `--freemote` or PNG/PSB not in expected folder layout |
