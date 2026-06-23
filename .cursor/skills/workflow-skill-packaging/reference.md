# Workflow → Skill Packaging — Reference

## code-snippets layout

```
code-snippets/
├── workflows/
│   ├── run.py                 # unified CLI router
│   ├── _lib/platform.py       # path + WSL helpers
│   └── <topic>/
│       ├── <topic>_lib.py     # shared logic (optional)
│       ├── main.py            # primary entry
│       └── helper.py          # secondary entry (optional)
├── .cursor/skills/<skill-name>/
│   ├── SKILL.md
│   └── reference.md
└── README.md
```

## SKILL.md template (minimal)

```markdown
---
name: my-workflow
description: >-
  Does X using workflows/run.py my-workflow. Use when the user asks to ...
---

# My Workflow

## Repo scripts

| Script | Role |
|--------|------|
| `workflows/my-topic/main.py` | ... |
| `workflows/run.py` | Entry `my-workflow` |

## Prerequisites

| Dependency | Purpose |
|------------|---------|
| `some-package` | ... |

## Quick start

\`\`\`bash
python workflows/run.py my-workflow "path/to/input" --output path/to/out
\`\`\`

## Common flags

| Flag | Default | Notes |
|------|---------|-------|
| `--output` | — | ... |

## Verify

- Exit code 0
- Expected output files exist
```

## run.py integration checklist

When adding workflow `foo-bar` pointing to `my-topic/script.py`:

1. `WORKFLOWS["foo-bar"] = "my-topic/script.py"`
2. Add new `--flags` to `path_flags` in `_to_runtime_args`
3. Add same flags to `path_option_flags` in `normalize_args`
4. Add same flags to the `--key=value` branch `key in { ... }` set
5. If first arg is input file: `positional_slots["foo-bar"] = 1`
6. If optional positional when `--dry-run` / `--link-only`: guard with flag check
7. If needs ffmpeg WSL routing: add to `MEDIA_WORKFLOWS` and `required_tools`

## Script generalization patterns

### Before (project-local)

```python
REPO = Path(__file__).resolve().parents[1]
UNITY3D = Path(r"D:\Steam\...\data.unity3d")
OUT = REPO / "unity" / "emote_pairs"
```

### After (portable)

```python
parser.add_argument("unity_bundle", nargs="?", type=Path)
parser.add_argument("--pairs", type=Path, default=Path("emote_pairs"))
```

### Shared library split

| File | Contains |
|------|----------|
| `emote_lib.py` | dataclasses, pure functions, subprocess helpers |
| `extract_pairs.py` | `argparse`, `main()`, orchestration |
| `scan_containers.py` | smaller CLI reusing `emote_lib` |

## Domain knowledge → reference.md

Move to `reference.md` (not SKILL.md):

- Binary format quirks (magic bytes, encoding traps)
- Why naive pairing algorithms fail
- External tool CLI gotchas (absolute paths, cwd)
- Size/heuristic checks for corrupt output

Keep SKILL.md to: how to run, flags, one-line warnings.

## Sanitize grep patterns

```bash
rg -i "EnglishRoot|C:\\Users|steamapps|Downloads/obs|ProgramFiles" workflows .cursor README.md
rg "D:\\\\[^p]" .cursor README.md   # review non-placeholder D: paths
```

Replace with:

- `path/to/...` in skill docs (cross-platform)
- `D:\path\...` in README Windows examples (established repo convention)
- `.\relative\` in legacy code default paths

## Dual placement: project vs global

| Location | Use |
|----------|-----|
| `code-snippets/.cursor/skills/` | Versioned with workflows; team/share via git |
| `~/.cursor/skills/` | Same skill available in every Cursor project |

Sync policy: project repo is source of truth; copy to `~/.cursor/skills/` when user wants global discovery. Re-copy after substantive SKILL.md edits.

## Commit message shape

```
feat(workflows): add <name> workflow and Cursor skill

Generalize <source> scripts, wire run.py, document pitfalls in
reference.md. Sanitize personal paths from examples.
```

Only commit when the user explicitly asks.

## Anti-patterns

| Avoid | Why |
|-------|-----|
| Skill without workflow script | Agent cannot execute; drifts from truth |
| Workflow without run.py entry | Breaks Windows path normalization |
| Hardcoded paths in skill docs | Leaks personal info on push |
| 500+ line SKILL.md | Context bloat; split to reference.md |
| Migrating broken/exploratory scripts | Encodes wrong assumptions permanently |
