#!/usr/bin/env python3
"""
Extract E-mote PSB + Texture2D pairs from a Unity bundle using ResourceManager container paths.

Pair by container path (AssetStudio semantics), not by m_Name:
  PSB:     anim/.../name
  Textures: anim/.../name_tex000, name_tex001, ...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import UnityPy

from emote_lib import (
    build_pairs_from_manifest,
    extract_pairs,
    link_pairs,
    load_manifest,
    write_batch_summary,
)

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "unity_bundle",
        nargs="?",
        type=Path,
        help="data.unity3d or other UnityPy-loadable bundle",
    )
    parser.add_argument("--prefix", default="anim/", help="container path prefix (default: anim/)")
    parser.add_argument("--pairs", type=Path, default=Path("emote_pairs"), help="extract output root")
    parser.add_argument("--psb-out", type=Path, default=Path("emote_psb"), help="linked PSB output root")
    parser.add_argument(
        "--freemote",
        type=Path,
        default=None,
        help="FreeMote toolkit dir containing PsBuild.exe",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="container manifest JSON (default: <pairs>/container_manifest.json)",
    )
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument("--link-only", action="store_true")
    parser.add_argument("--no-clean", action="store_true")
    parser.add_argument("--refresh-manifest", action="store_true")
    args = parser.parse_args()

    prefix = args.prefix if args.prefix.endswith("/") else args.prefix + "/"
    clean = not args.no_clean
    manifest_path = args.manifest or (args.pairs / "container_manifest.json")

    extract_results = []
    link_results = []

    if args.link_only:
        if not manifest_path.is_file():
            print(f"Missing manifest: {manifest_path}", file=sys.stderr)
            return 1
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        pairs = build_pairs_from_manifest(manifest, prefix)
        psbuild = _require_psbuild(args.freemote)
        if psbuild is None:
            return 1
        link_results = link_pairs(pairs, args.pairs, args.psb_out, psbuild, clean=clean)
    else:
        bundle = args.unity_bundle
        if bundle is None or not bundle.is_file():
            print("unity_bundle path required (or use --link-only)", file=sys.stderr)
            return 2

        print(f"Loading {bundle} ...", flush=True)
        env = UnityPy.load(str(bundle))
        manifest = load_manifest(env, prefix)
        if args.refresh_manifest or not manifest_path.exists():
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Wrote {manifest_path}")

        pairs = build_pairs_from_manifest(manifest, prefix)
        print(f"Pairs to extract: {len(pairs)}", flush=True)
        extract_results = extract_pairs(env, pairs, args.pairs, clean=clean)

        if not args.extract_only:
            psbuild = args.freemote / "PsBuild.exe" if args.freemote else None
            if psbuild is None or not psbuild.is_file():
                print("Warning: --freemote with PsBuild.exe missing; skipping link", file=sys.stderr)
            else:
                link_results = link_pairs(pairs, args.pairs, args.psb_out, psbuild, clean=clean)

    if extract_results:
        write_batch_summary(
            extract_results,
            args.pairs / "batch_summary.json",
            "extract",
            pairing=f"ResourceManager container ({prefix}* + _texNNN)",
        )
        ok = sum(1 for r in extract_results if r.status == "ok")
        print(f"extract: {ok}/{len(extract_results)} ok")

    if link_results:
        write_batch_summary(link_results, args.psb_out / "batch_summary.json", "link")
        ok = sum(1 for r in link_results if r.status == "ok")
        print(f"link: {ok}/{len(link_results)} ok")

    all_results = extract_results + link_results
    return 0 if all(r.status == "ok" for r in all_results) else 1


def _require_psbuild(freemote: Path | None) -> Path | None:
    if freemote is None:
        print("--freemote required for --link-only", file=sys.stderr)
        return None
    psbuild = freemote / "PsBuild.exe"
    if not psbuild.is_file():
        print(f"Missing {psbuild}", file=sys.stderr)
        return None
    return psbuild


if __name__ == "__main__":
    raise SystemExit(main())
