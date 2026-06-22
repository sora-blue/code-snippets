import os
import sys
from pathlib import Path
from PIL import Image

SRC_DIR = Path(__file__).resolve().parent
OUT_DIR = SRC_DIR / "cleaned"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".heic", ".heif"}


def strip_metadata(src: Path) -> Image.Image:
    """Open image, strip all metadata, return bare RGB image."""
    img = Image.open(src)
    # Convert to mode that strips EXIF/profile info; keep palette if PNG
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")
    # Create a clean image with no info dict
    clean = Image.new(img.mode, img.size)
    clean.putdata(list(img.get_flattened_data()))
    return clean


def main():
    images = sorted(
        [f for f in SRC_DIR.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS],
        key=lambda f: f.name
    )

    if not images:
        print("No image files found.")
        return

    OUT_DIR.mkdir(exist_ok=True)

    digits = len(str(len(images)))
    for i, src in enumerate(images, start=1):
        ext = src.suffix.lower()
        # Standardize extension
        if ext == ".jpeg":
            ext = ".jpg"
        dst = OUT_DIR / f"{i:0{digits}d}{ext}"

        try:
            clean = strip_metadata(src)
            clean.save(dst, quality=95, optimize=True)
            print(f"  [{i}/{len(images)}] {src.name} -> {dst.name}")
        except Exception as e:
            print(f"  [SKIP] {src.name}: {e}", file=sys.stderr)

    print(f"\nDone. {len(images)} images saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
