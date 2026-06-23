#!/usr/bin/env python3
"""Scan Unity ResourceManager container paths for E-mote PSB / Texture2D assets."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import UnityPy

from emote_lib import is_psb_bytes, get_textasset_bytes, iter_container_entries, resolve_object

PSB_MAGIC = b"PSB\x00"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unity_bundle", type=Path, help="data.unity3d or other UnityPy-loadable bundle")
    parser.add_argument("--prefix", default="anim/", help="container path prefix (default: anim/)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("container_manifest.json"),
        help="manifest JSON output path",
    )
    args = parser.parse_args()

    prefix = args.prefix if args.prefix.endswith("/") else args.prefix + "/"

    if not args.unity_bundle.is_file():
        print(f"ERROR: missing file: {args.unity_bundle}", file=sys.stderr)
        return 1

    env = UnityPy.load(str(args.unity_bundle))
    groups: dict[str, dict] = defaultdict(lambda: {"psb": None, "textures": []})

    for container_path, pptr in iter_container_entries(env):
        if not container_path.startswith(prefix):
            continue
        obj = resolve_object(env, pptr)
        if obj is None:
            continue

        if obj.type.name == "TextAsset":
            if is_psb_bytes(get_textasset_bytes(obj)):
                groups[container_path]["psb"] = {
                    "name": obj.read_typetree().get("m_Name", ""),
                    "path_id": obj.path_id,
                    "file": obj.assets_file.name,
                    "type": obj.type.name,
                }
        elif obj.type.name == "Texture2D":
            tex = obj.read()
            groups[container_path]["textures"].append(
                {
                    "name": tex.m_Name,
                    "path_id": obj.path_id,
                    "file": obj.assets_file.name,
                    "type": obj.type.name,
                    "index": len(groups[container_path]["textures"]),
                }
            )

    manifest = {k: v for k, v in sorted(groups.items()) if v["psb"] or v["textures"]}
    both = sum(1 for g in manifest.values() if g["psb"] and g["textures"])
    psb_only = sum(1 for g in manifest.values() if g["psb"] and not g["textures"])
    tex_only = sum(1 for g in manifest.values() if g["textures"] and not g["psb"])

    def base_key(path: str) -> str:
        name = path.rsplit("/", 1)[-1]
        if "_tex" in name:
            name = name.split("_tex", 1)[0]
        return path.rsplit("/", 1)[0] + "/" + name

    base_groups: dict[str, dict] = defaultdict(lambda: {"psb_paths": [], "tex_paths": []})
    for path, g in manifest.items():
        bk = base_key(path)
        if g["psb"]:
            base_groups[bk]["psb_paths"].append(path)
        if g["textures"]:
            base_groups[bk]["tex_paths"].append(path)
    base_with_both = sum(
        1 for bg in base_groups.values() if bg["psb_paths"] and bg["tex_paths"]
    )

    print(f"=== container scan ({prefix}) ===")
    print(f"Bundle: {args.unity_bundle}")
    print(f"entries: {len(manifest)}")
    print(f"PSB paths: {psb_only}")
    print(f"texture-only paths: {tex_only}")
    print(f"same-path PSB+texture (rare): {both}")
    print(f"base groups with PSB + texture path(s): {base_with_both}")
    print("Pairing: PSB container + sibling *_texNNN containers (not m_Name).")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
