"""Unity E-mote PSB + Texture2D pairing via ResourceManager container paths."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import UnityPy
from PIL import Image

PSB_MAGIC = b"PSB\x00"
TEX_SUFFIX_RE = re.compile(r"_tex(\d+)$")


@dataclass
class AnimPair:
    container: str
    folder: str
    psb_name: str
    psb_path_id: int
    psb_file: str
    textures: list[dict]


@dataclass
class PairResult:
    folder: str
    container: str
    status: str
    error: str | None = None


def iter_container_entries(env):
    for obj in env.objects:
        if obj.type.name != "ResourceManager":
            continue
        rm = obj.read()
        for entry in rm.m_Container:
            path, pptr = entry[0], entry[1]
            yield str(path), pptr


def resolve_object(env, pptr):
    try:
        return pptr.deref()
    except Exception:
        if hasattr(pptr, "path_id"):
            for obj in env.objects:
                if obj.path_id == pptr.path_id:
                    return obj
        return None


def get_textasset_bytes(obj) -> bytes:
    tree = obj.read_typetree()
    script = tree.get("m_Script", b"")
    if isinstance(script, (bytes, bytearray)):
        return bytes(script)
    if isinstance(script, str):
        return script.encode("utf-8", "surrogateescape")
    raise TypeError(f"unexpected m_Script type: {type(script)}")


def is_psb_bytes(data: bytes | bytearray | str) -> bool:
    if isinstance(data, str):
        data = data.encode("utf-8", "surrogateescape")
    return isinstance(data, (bytes, bytearray)) and data[:4] == PSB_MAGIC


def container_folder_name(container: str, prefix: str = "anim/") -> str:
    rest = container[len(prefix) :] if container.startswith(prefix) else container
    name = "__".join(rest.split("/"))
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "_")
    return name.strip(". ") or "unnamed"


def load_manifest(env, prefix: str = "anim/") -> dict:
    groups: dict[str, dict] = {}

    def ensure(path: str) -> dict:
        if path not in groups:
            groups[path] = {"psb": None, "textures": []}
        return groups[path]

    for container_path, pptr in iter_container_entries(env):
        if not container_path.startswith(prefix):
            continue
        obj = resolve_object(env, pptr)
        if obj is None:
            continue
        g = ensure(container_path)

        if obj.type.name == "TextAsset":
            raw = get_textasset_bytes(obj)
            if is_psb_bytes(raw):
                name = obj.read_typetree().get("m_Name", "")
                g["psb"] = {
                    "name": name,
                    "path_id": obj.path_id,
                    "file": obj.assets_file.name,
                    "type": obj.type.name,
                }
        elif obj.type.name == "Texture2D":
            tex = obj.read()
            g["textures"].append(
                {
                    "name": tex.m_Name,
                    "path_id": obj.path_id,
                    "file": obj.assets_file.name,
                    "type": obj.type.name,
                    "index": len(g["textures"]),
                }
            )

    return {k: v for k, v in sorted(groups.items()) if v["psb"] or v["textures"]}


def build_pairs_from_manifest(manifest: dict, prefix: str = "anim/") -> list[AnimPair]:
    psb_paths = sorted(p for p, g in manifest.items() if g.get("psb"))
    pairs: list[AnimPair] = []

    for base in psb_paths:
        tex_entries: list[tuple[int, str, dict]] = []
        tex_prefix = base + "_tex"
        for path, g in manifest.items():
            if not path.startswith(tex_prefix):
                continue
            suffix = path[len(base) :]
            m = TEX_SUFFIX_RE.search(suffix)
            if not m:
                continue
            idx = int(m.group(1))
            for t in g.get("textures") or []:
                tex_entries.append((idx, path, t))

        tex_entries.sort(key=lambda x: x[0])
        psb = manifest[base]["psb"]
        pairs.append(
            AnimPair(
                container=base,
                folder=container_folder_name(base, prefix),
                psb_name=psb["name"],
                psb_path_id=psb["path_id"],
                psb_file=psb.get("file", "resources.assets"),
                textures=[t for _, _, t in tex_entries],
            )
        )
    return pairs


def build_object_index(env) -> dict[tuple[str, int, str], object]:
    return {(obj.assets_file.name, obj.path_id, obj.type.name): obj for obj in env.objects}


def object_by_ref(index, *, file: str, path_id: int, type_name: str):
    obj = index.get((file, path_id, type_name))
    if obj is not None:
        return obj
    for (f, pid, _), candidate in index.items():
        if f == file and pid == path_id:
            return candidate
    raise KeyError(f"{type_name} path_id {path_id} in {file} not found")


def export_texture_png(obj, dest: Path) -> None:
    tex = obj.read()
    img = tex.image
    if img is None:
        img = Image.open(BytesIO(obj.get_raw_data()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, format="PNG")


def export_psb(obj, dest: Path) -> None:
    data = get_textasset_bytes(obj)
    if not data.startswith(PSB_MAGIC):
        raise ValueError(f"not a PSB: magic={data[:4]!r} len={len(data)}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def run_psbuild_link(psbuild: Path, psb: Path, pngs: list[Path], out: Path) -> tuple[int, str]:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(psbuild),
        "link",
        "-o",
        str(out.resolve()),
        str(psb.resolve()),
        *[str(p.resolve()) for p in pngs],
    ]
    proc = subprocess.run(
        cmd,
        cwd=psb.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()


def extract_pairs(env, pairs: list[AnimPair], pairs_root: Path, *, clean: bool) -> list[PairResult]:
    if clean and pairs_root.exists():
        shutil.rmtree(pairs_root)
    pairs_root.mkdir(parents=True, exist_ok=True)

    results: list[PairResult] = []
    manifest_lines = ["# container\tfolder\tpsb\ttextures", ""]
    obj_index = build_object_index(env)

    for pair in pairs:
        out_dir = pairs_root / pair.folder
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            psb_obj = object_by_ref(
                obj_index,
                file=pair.psb_file,
                path_id=pair.psb_path_id,
                type_name="TextAsset",
            )
            psb_file = out_dir / f"{pair.folder}.psb"
            export_psb(psb_obj, psb_file)

            png_names: list[str] = []
            for t in pair.textures:
                tex_obj = object_by_ref(
                    obj_index,
                    file=t.get("file", "resources.assets"),
                    path_id=t["path_id"],
                    type_name=t.get("type", "Texture2D"),
                )
                m = TEX_SUFFIX_RE.search(t["name"])
                out_name = (
                    f"{pair.folder}_tex{m.group(1)}.png" if m else f"{t['name']}.png"
                )
                export_texture_png(tex_obj, out_dir / out_name)
                png_names.append(out_name)

            manifest_lines.append(
                f"{pair.container}\t{pair.folder}\t{psb_file.name}\t{', '.join(png_names)}"
            )
            results.append(PairResult(pair.folder, pair.container, "ok"))
        except Exception as exc:
            results.append(PairResult(pair.folder, pair.container, "fail", str(exc)))

    (pairs_root / "MANIFEST.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return results


def link_pairs(
    pairs: list[AnimPair],
    pairs_root: Path,
    psb_root: Path,
    psbuild: Path,
    *,
    clean: bool,
) -> list[PairResult]:
    if clean and psb_root.exists():
        shutil.rmtree(psb_root)
    psb_root.mkdir(parents=True, exist_ok=True)

    results: list[PairResult] = []
    for pair in pairs:
        src_dir = pairs_root / pair.folder
        if not src_dir.is_dir():
            results.append(PairResult(pair.folder, pair.container, "fail", "missing extract folder"))
            continue
        psbs = list(src_dir.glob("*.psb"))
        pngs = sorted(src_dir.glob("*.png"), key=lambda p: p.name.lower())
        if not psbs or not pngs:
            results.append(PairResult(pair.folder, pair.container, "fail", "missing psb or png"))
            continue

        out_dir = psb_root / pair.folder
        linked = out_dir / f"{pair.folder}_linked.psb"
        code, log = run_psbuild_link(psbuild, psbs[0], pngs, linked)
        if code != 0 or not linked.is_file():
            results.append(PairResult(pair.folder, pair.container, "fail", log or f"exit {code}"))
        else:
            results.append(PairResult(pair.folder, pair.container, "ok"))
    return results


def write_batch_summary(results: list[PairResult], out_path: Path, step: str, **extra) -> None:
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "total": len(results),
        "ok": sum(1 for r in results if r.status == "ok"),
        "fail": sum(1 for r in results if r.status != "ok"),
        "results": [asdict(r) for r in results],
        **extra,
    }
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
