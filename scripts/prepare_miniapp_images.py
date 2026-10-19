"""Encode optional WebP derivatives on the asset/deployment machine, before collectstatic.

The checked-in PNGs remain untouched and are valid runtime fallbacks. This script
requires only Pillow, which is already declared in requirements/base.txt.
"""
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import os
import sys
import tempfile

from PIL import Image, ImageOps, features


IMAGE_DIR = Path(__file__).resolve().parents[1] / "static" / "miniapp" / "images"


@dataclass(frozen=True)
class ImageSpec:
    stem: str
    bounds: tuple[int, int]
    atlas: bool = False


IMAGES = (
    ImageSpec("plumbing-hero", (960, 640)),
    ImageSpec("service-scenes", (1024, 1024), atlas=True),
)


def _source(spec: ImageSpec, directory: Path) -> Image.Image:
    with Image.open(directory / f"{spec.stem}.png") as original:
        if original.format != "PNG":
            raise ValueError(f"{spec.stem}.png must be a PNG source image.")
        image = ImageOps.exif_transpose(original)
        if spec.atlas and (image.width != image.height or image.width % 2):
            image.close()
            raise ValueError("The service atlas must have four equal square quadrants.")
        if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
            rgba = image.convert("RGBA")
            flattened = Image.new("RGB", rgba.size, "white")
            flattened.paste(rgba, mask=rgba.getchannel("A"))
            rgba.close()
            image.close()
            return flattened
        rgb = image.convert("RGB")
        image.close()
        return rgb


def prepare(spec: ImageSpec, directory: Path, quality: int) -> Path:
    destination = directory / f"{spec.stem}.webp"
    temporary = None
    try:
        with _source(spec, directory) as image:
            image.thumbnail(spec.bounds, Image.Resampling.LANCZOS)
            with tempfile.NamedTemporaryFile(
                prefix=f".{spec.stem}-", suffix=".webp", dir=directory, delete=False,
            ) as output:
                temporary = Path(output.name)
                image.save(output, format="WEBP", quality=quality, method=6)
        if temporary.stat().st_size >= (directory / f"{spec.stem}.png").stat().st_size:
            raise ValueError(f"{spec.stem}: derivative is not smaller than the original PNG.")
        # collectstatic / the web server must be able to read the generated file.
        temporary.chmod(0o644)
        os.replace(temporary, destination)
        return destination
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def verify(spec: ImageSpec, directory: Path) -> str:
    source = directory / f"{spec.stem}.png"
    derivative = directory / f"{spec.stem}.webp"
    with _source(spec, directory) as original, Image.open(derivative) as image:
        image.load()
        if image.format != "WEBP" or image.mode != "RGB":
            raise ValueError(f"{derivative.name}: expected a readable RGB WebP image.")
        if image.width > spec.bounds[0] or image.height > spec.bounds[1]:
            raise ValueError(f"{derivative.name}: dimensions exceed the mobile asset bounds.")
        if spec.atlas and (image.width != image.height or image.width % 2):
            raise ValueError(f"{derivative.name}: atlas quadrants no longer align.")
        if abs(image.width / image.height - original.width / original.height) > 0.01:
            raise ValueError(f"{derivative.name}: source aspect ratio was changed.")
        dimensions = f"{image.width}x{image.height}"
    original_bytes, encoded_bytes = source.stat().st_size, derivative.stat().st_size
    if encoded_bytes >= original_bytes:
        raise ValueError(f"{derivative.name}: derivative is not smaller than the source.")
    saving = 100 * (1 - encoded_bytes / original_bytes)
    return f"{derivative.name}: {dimensions}, {encoded_bytes:,} bytes, {saving:.1f}% smaller"


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing derivatives without writing them.")
    parser.add_argument("--quality", type=int, default=82, help="WebP quality from 60 to 95 (default: 82).")
    options = parser.parse_args()
    if not 60 <= options.quality <= 95:
        parser.error("--quality must be between 60 and 95")
    if not features.check("webp"):
        print("Pillow needs WebP support on the asset/deployment machine.", file=sys.stderr)
        return 1
    try:
        for spec in IMAGES:
            if not options.check:
                prepare(spec, IMAGE_DIR, options.quality)
            print(verify(spec, IMAGE_DIR))
    except (OSError, ValueError) as error:
        print(f"Image preparation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
