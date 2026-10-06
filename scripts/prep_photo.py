from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def remove_background(image: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError as exc:
        raise SystemExit("Install scripts/requirements-portrait.txt to use background removal.") from exc
    return remove(image).convert("RGBA")


def prepare(source: Path, output: Path, keep_background: bool) -> None:
    image = Image.open(source).convert("RGBA")
    foreground = image if keep_background else remove_background(image)
    white = Image.new("RGBA", foreground.size, "white")
    composited = Image.alpha_composite(white, foreground).convert("L")
    gray = np.asarray(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced).save(output)
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove a portrait background and boost local contrast.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("source-prepped.png"))
    parser.add_argument("--keep-background", action="store_true")
    args = parser.parse_args()
    prepare(args.source, args.output, args.keep_background)


if __name__ == "__main__":
    main()
