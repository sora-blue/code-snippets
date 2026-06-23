---
name: workflow-skill-packaging
description: >-
  Packages ad-hoc project scripts into a reusable code-snippets workflow plus
  Cursor skill. Generalizes paths, wires workflows/run.py, writes SKILL.md and
  reference.md, sanitizes personal info, and updates README. Use when the user
  asks to turn a script into a skill, publish a workflow to code-snippets, or
  replicate the unity-emote-psb-extract packaging pattern.
---

# Workflow → Skill Packaging

Turn a one-off project script into a portable **workflow + Cursor skill** pair.

## When to use

- User finished a task in a project repo and wants it in `code-snippets`
- User asks to "整理成 skill" / "make this a skill" / "add to code-snippets"
- A script has hardcoded paths or project-specific names that must be generalized

## Outcomes

| Artifact | Location |
|----------|----------|
| Workflow scripts | `workflows/<name>/` |
| Shared library (if needed) | `workflows/<name>/*_lib.py` |
| Run entry | `workflows/run.py` `WORKFLOWS` map |
| Project skill | `.cursor/skills/<skill-name>/` |
| Docs | `README.md` workflow table + examples |

Optional: copy the same skill to `~/.cursor/skills/<skill-name>/` for global use.

## Checklist

```
- [ ] 1. Identify source scripts and what to exclude
- [ ] 2. Generalize (no hardcoded paths, game names, usernames)
- [ ] 3. Create workflows/<name>/ with argparse CLI
- [ ] 4. Wire workflows/run.py (WORKFLOWS, path flags, positional slots)
- [ ] 5. Write SKILL.md (frontmatter, quick start, flags)
- [ ] 6. Write reference.md (pitfalls, domain traps — progressive disclosure)
- [ ] 7. Update README.md table + one example command block
- [ ] 8. Sanitize scan (grep personal paths, game titles, real filenames)
- [ ] 9. Commit (user must ask explicitly)
```

## Phase 1 — Select what to migrate

**Migrate:** stable, reusable automation with clear inputs/outputs.

**Do not migrate:** one-off debug scripts, Il2Cpp dumps, secrets, `.env`, huge binaries, project-only data paths.

Read an existing skill in the target repo first (e.g. `mkv-whisper-transcribe`) and match its tone and section layout.

## Phase 2 — Generalize scripts

1. Remove `REPO = Path(__file__).parents[1]` defaults that point at a specific machine.
2. Replace defaults with relative dirs (`emote_pairs`, `out/`) or require CLI args.
3. Extract shared logic into `<topic>_lib.py`; thin CLIs import from same directory:

```python
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
```

4. All user paths via `argparse` (`--pairs`, `--output`, positional bundle path).
5. External tools via explicit flag (`--freemote`, not baked-in install path).

## Phase 3 — Wire `workflows/run.py`

Add to `WORKFLOWS`:

```python
"my-workflow": "my-topic/main_script.py",
```

Extend path handling in three places if new path flags exist:

- `_to_runtime_args` → `path_flags`
- `normalize_args` → `path_option_flags` and `key in { ... }` for `--flag=value`
- `positional_slots` for first positional input (e.g. input file)

Special cases: `--link-only` style modes that skip positional → set `positional_remaining = 0` when flag present.

Media workflows that need WSL: add name to `MEDIA_WORKFLOWS` only when ffmpeg/whisper-style routing applies.

## Phase 4 — Write the skill

### Directory

```
.cursor/skills/<skill-name>/
├── SKILL.md       # required — agent-facing, under ~500 lines
└── reference.md   # optional — traps, troubleshooting, long examples
```

### SKILL.md frontmatter

```yaml
---
name: skill-name-kebab-case
description: >-
  WHAT it does. WHEN to use it (trigger terms). Mention workflows/run.py entry
  name if applicable.
---
```

Description rules: third person, specific, includes trigger phrases.

### SKILL.md body sections (code-snippets pattern)

1. **Repo scripts** — table or bullet list with paths
2. **Prerequisites** — pip packages, external binaries
3. **Quick start** — `python workflows/run.py <entry> ...`
4. **Common flags** — table
5. **Critical rules** — non-obvious domain logic (short)
6. **Verify** — how to confirm success

Link to `reference.md` for depth; keep SKILL.md scannable.

### reference.md

- Domain pitfalls discovered during development
- Wrong vs right patterns (code snippets)
- Troubleshooting table
- No personal paths, game names, or machine-specific validation stats

## Phase 5 — Sanitize before publish

Grep the repo (at least new/changed files) for:

| Pattern | Action |
|---------|--------|
| `EnglishRoot`, username, `C:\Users\` | Remove or genericize |
| Steam / game install paths | Use `path/to/Game_Data/...` |
| Real OBS/Download filenames with dates | Use `D:\path\video.mkv` |
| Game titles used as sole examples | Generic placeholders (`char_a`, `scene_01`) |
| API keys, tokens | Never commit |

Generic placeholders are OK: `D:\path\`, `path/to/`, `/mnt/d/path/`.

## Phase 6 — README

Add one row to the workflow table and one example in the Windows/WSL block. List the skill in the Cursor Skills section.

## Phase 7 — Global copy (optional)

When user wants the skill everywhere:

```
~/.cursor/skills/<skill-name>/SKILL.md
~/.cursor/skills/<skill-name>/reference.md   # if present
```

Keep content identical to the project skill unless the global copy should be repo-agnostic (omit `workflows/run.py` paths → say "see code-snippets repo").

**Never** write to `~/.cursor/skills-cursor/` (Cursor-managed).

## Reference example

The `unity-emote-psb-extract` skill in code-snippets demonstrates the full pattern:

- `workflows/unity-emote/emote_lib.py` + `extract_pairs.py` + `scan_containers.py`
- `workflows/run.py` entries `unity-emote-scan`, `unity-emote-extract`
- `.cursor/skills/unity-emote-psb-extract/SKILL.md` + `reference.md`

See [reference.md](reference.md) for file-level templates and run.py diff checklist.

## Additional resources

- Cursor skill authoring: read `create-skill` skill (`~/.cursor/skills-cursor/create-skill/SKILL.md`) for metadata rules
- New skill from scratch only: use `create-skill` workflow (discovery → design → implement → verify)
