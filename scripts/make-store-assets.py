"""Build the Google Play icon and feature graphic from the game artwork.

Run with:
    python scripts/make-store-assets.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "store-assets"
ICON = ROOT / "public" / "icons" / "icon-512.png"

GOLD = (244, 201, 93)
CREAM = (247, 241, 227)
MUTED = (176, 172, 160)
INK = (8, 9, 15)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("/System/Library/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def serif(size: int) -> ImageFont.FreeTypeFont:
    return font("georgiab.ttf", size)


def serif_italic(size: int) -> ImageFont.FreeTypeFont:
    return font("georgiai.ttf", size)


def sans_bold(size: int) -> ImageFont.FreeTypeFont:
    return font("arialbd.ttf", size)


def sans(size: int) -> ImageFont.FreeTypeFont:
    return font("arial.ttf", size)


def tracked(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill, tracking: int):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="ls")
        x += draw.textlength(ch, font=fnt) + tracking


def background(width: int, height: int) -> Image.Image:
    y, x = np.mgrid[0:height, 0:width]
    tx = x / (width - 1)
    ty = y / (height - 1)
    top = np.array([18, 20, 32], dtype=np.float32)
    bottom = np.array([5, 6, 11], dtype=np.float32)
    base = top[None, None, :] * (1 - ty[..., None]) + bottom[None, None, :] * ty[..., None]
    nx = (tx - 0.32) * 2.0
    ny = (ty - 0.5) * 2.0
    glow = np.exp(-((nx * nx * 0.7 + ny * ny * 1.1) / 0.20))
    warm = np.array([244, 201, 93], dtype=np.float32) * glow[..., None] * 0.18
    image = np.clip(base + warm, 0, 255).astype(np.uint8)
    return Image.fromarray(image, "RGB")


def film_strips(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for x in (0, width - 34):
        draw.rectangle([x, 0, x + 34, height], fill=(6, 7, 12))
        for y in range(14, height, 54):
            draw.rounded_rectangle(
                [x + 9, y, x + 25, y + 22],
                radius=5,
                fill=(29, 30, 39),
            )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    icon = Image.open(ICON).convert("RGBA")
    icon.resize((512, 512), Image.LANCZOS).save(OUT / "icon-512.png", "PNG")

    image = background(1024, 500)
    draw = ImageDraw.Draw(image)
    film_strips(draw, 1024, 500)

    # Icon card on the left.
    card = icon.resize((284, 284), Image.LANCZOS)
    mask = Image.new("L", (284, 284), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 283, 283], radius=55, fill=255)
    image.paste(card, (92, 108), mask)
    draw.rounded_rectangle([91, 107, 377, 393], radius=56, outline=(244, 201, 93, 90), width=2)

    # Right-hand type block.
    draw.text((420, 94), "OFFLINE CINEMA TRIVIA", font=sans_bold(17), fill=GOLD)
    draw.text((416, 132), "HANGMAN", font=serif(92), fill=CREAM)
    tracked(draw, (422, 252), "MOVIE TRIVIA", sans_bold(24), GOLD, 8)
    draw.text((420, 292), "Name the screen classic.", font=serif_italic(34), fill=CREAM)
    draw.text(
        (422, 356),
        "18,593 clues  ·  7 categories  ·  Offline play",
        font=sans(20),
        fill=MUTED,
    )

    draw.line([(422, 404), (944, 404)], fill=(70, 65, 50), width=1)
    draw.text((422, 427), "A movie & TV hangman game", font=sans(18), fill=(135, 132, 122))

    image.convert("RGB").save(OUT / "feature-graphic.png", "PNG")
    print("Wrote store-assets/icon-512.png and store-assets/feature-graphic.png")


if __name__ == "__main__":
    main()
