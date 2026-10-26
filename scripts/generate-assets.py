"""Generate Reel Hangman icons and splash screens.

Run with: python scripts/generate-assets.py
Requires Pillow. Re-run after `npx cap add android` / `npx cap add ios`
to populate the native projects as well.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
S = 1024
PUBLIC_ICONS = ROOT / "public" / "icons"
RESOURCES = ROOT / "resources"
ANDROID_RES = ROOT / "android" / "app" / "src" / "main" / "res"
IOS_ASSETS = ROOT / "ios" / "App" / "App" / "Assets.xcassets"

GOLD = (244, 201, 93, 255)
GOLD_SOFT = (231, 188, 81, 255)
CREAM = (247, 241, 227, 255)
INK = (10, 11, 17, 255)
MUTED = (147, 148, 167, 255)


def find_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    roots = [
        Path("C:/Windows/Fonts"),
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation"),
    ]
    for candidate in candidates:
        for root in roots:
            path = root / candidate
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size=size)
                except OSError:
                    pass
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def serif_bold(size: int) -> ImageFont.FreeTypeFont:
    return find_font(["georgiab.ttf", "Georgia Bold.ttf", "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"], size)


def serif_regular(size: int) -> ImageFont.FreeTypeFont:
    return find_font(["georgia.ttf", "Georgia.ttf", "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"], size)


def sans_bold(size: int) -> ImageFont.FreeTypeFont:
    return find_font(["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"], size)


def gradient_background(width: int, height: int, focus_y: float = 0.32) -> Image.Image:
    y, x = np.mgrid[0:height, 0:width]
    tx = x / max(1, width - 1)
    ty = y / max(1, height - 1)

    top = np.array([17, 19, 30], dtype=np.float32)
    bottom = np.array([5, 6, 10], dtype=np.float32)
    base = top[None, None, :] * (1 - ty[..., None]) + bottom[None, None, :] * ty[..., None]

    nx = (tx - 0.5) * 2.0
    ny = (ty - focus_y) * 2.0
    glow = np.exp(-((nx * nx * 1.1 + ny * ny * 1.45) / 0.22))
    warm = np.array([244, 201, 93], dtype=np.float32) * glow[..., None] * 0.20

    radius = np.sqrt((nx * 0.86) ** 2 + ((ty - 0.5) * 2.0) ** 2)
    vignette = np.clip(1.0 - np.maximum(0.0, radius - 0.55) ** 1.4 * 0.56, 0.48, 1.0)
    rgb = np.clip((base + warm) * vignette[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(rgb, "RGB").convert("RGBA")


def tracked_text(
    draw: ImageDraw.ImageDraw,
    center_x: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    tracking: float,
) -> float:
    widths = [draw.textlength(char, font=font) for char in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = center_x - total / 2
    for char, width in zip(text, widths):
        draw.text((x, y), char, font=font, fill=fill, anchor="ls")
        x += width + tracking
    return total


def draw_film_holes(draw: ImageDraw.ImageDraw, width: int, height: int, alpha: int = 26) -> None:
    hole_w = int(width * 0.026)
    hole_h = int(height * 0.045)
    gap = int(height * 0.018)
    margin = int(width * 0.045)
    y = int(height * 0.10)
    while y + hole_h < height * 0.90:
        for x in (margin, width - margin - hole_w):
            draw.rounded_rectangle(
                (x, y, x + hole_w, y + hole_h),
                radius=max(2, hole_w // 4),
                fill=(244, 201, 93, alpha),
            )
        y += hole_h + gap


def draw_gallows(layer: Image.Image, scale: float = 1.0) -> None:
    draw = ImageDraw.Draw(layer)
    center = S / 2

    def point(x: float, y: float) -> tuple[float, float]:
        return (center + (x - center) * scale, center + (y - center) * scale)

    def width(value: float) -> int:
        return max(1, round(value * scale))

    gold = GOLD
    cream = CREAM

    # Gallows
    for start, end, stroke in [
        ((250, 812), (780, 812), 13),
        ((360, 812), (360, 274), 13),
        ((360, 274), (716, 274), 13),
        ((360, 352), (446, 274), 9),
        ((372, 812), (548, 812), 9),
    ]:
        draw.line([point(*start), point(*end)], fill=gold, width=width(stroke), joint="curve")

    # Rope
    draw.line([point(682, 274), point(682, 404)], fill=(230, 222, 205, 255), width=width(5))

    # Head with a question mark
    head_radius = 79 * scale
    hx, hy = point(682, 480)
    draw.ellipse(
        (hx - head_radius, hy - head_radius, hx + head_radius, hy + head_radius),
        fill=cream,
        outline=gold,
        width=width(2),
    )

    q_font = serif_bold(round(112 * scale))
    draw.text((hx, hy - 2 * scale), "?", font=q_font, fill=INK, anchor="mm")

    # Body
    for start, end, stroke in [
        ((682, 559), (682, 684), 10),
        ((682, 596), (604, 646), 10),
        ((682, 596), (760, 646), 10),
        ((682, 684), (616, 794), 10),
        ((682, 684), (748, 794), 10),
    ]:
        draw.line([point(*start), point(*end)], fill=gold, width=width(stroke), joint="curve")


def art_layer(scale: float = 1.0) -> Image.Image:
    full = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw_gallows(full, 1.0)
    resized = full.resize((round(S * scale), round(S * scale)), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.alpha_composite(resized, ((S - resized.width) // 2, (S - resized.height) // 2))
    return layer


def make_icon(scale: float = 1.0, show_border: bool = True, show_holes: bool = True) -> Image.Image:
    image = gradient_background(S, S)
    if show_holes:
        overlay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw_film_holes(draw, S, S, 26)
        image.alpha_composite(overlay)

    if show_border:
        border = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(border)
        draw.rounded_rectangle(
            (26, 26, S - 26, S - 26),
            radius=226,
            outline=(244, 201, 93, 34),
            width=2,
        )
        image.alpha_composite(border)

    art = art_layer(scale)
    glow = art.filter(ImageFilter.GaussianBlur(14))
    glow_alpha = glow.split()[3].point(lambda value: int(value * 0.35))
    glow.putalpha(glow_alpha)
    image.alpha_composite(glow)
    image.alpha_composite(art)
    return image


def make_foreground() -> Image.Image:
    return art_layer(0.62)


def make_splash(width: int, height: int, portrait: bool) -> Image.Image:
    image = gradient_background(width, height, focus_y=0.38)

    # Soft focal glow behind the mark.
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    radius = int(min(width, height) * 0.34)
    gd.ellipse(
        (width // 2 - radius, height // 2 - radius, width // 2 + radius, height // 2 + radius),
        fill=(244, 201, 93, 10),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 4))
    image.alpha_composite(glow)

    if portrait:
        icon_size = int(min(width * 0.31, height * 0.17))
        icon_y = int(height * 0.285)
        title_y = int(height * 0.505)
        tagline_y = int(height * 0.55)
        title_size = int(width * 0.062)
        tagline_size = int(width * 0.017)
    else:
        icon_size = int(min(width, height) * 0.24)
        icon_y = int(height * 0.28)
        title_y = int(height * 0.57)
        tagline_y = int(height * 0.62)
        title_size = int(min(width, height) * 0.045)
        tagline_size = int(min(width, height) * 0.013)

    icon = make_icon(show_border=True, show_holes=True).resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (icon_size, icon_size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, icon_size - 1, icon_size - 1),
        radius=int(icon_size * 0.23),
        fill=255,
    )
    shine = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
    shine.alpha_composite(icon)
    image.paste(shine, ((width - icon_size) // 2, icon_y), mask)

    draw = ImageDraw.Draw(image)
    title_font = serif_regular(title_size)
    tracking = title_size * 0.20
    tracked_text(draw, width / 2, title_y, "REEL HANGMAN", title_font, CREAM, tracking)

    tagline_font = sans_bold(tagline_size)
    tracked_text(
        draw,
        width / 2,
        tagline_y,
        "LIGHTS. CAMERA. MISSING LETTERS.",
        tagline_font,
        (190, 171, 126, 255),
        tagline_size * 0.42,
    )
    return image


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, "PNG", optimize=True) if path.suffix == ".png" else image.save(path)
    print(f"  {path.relative_to(ROOT)}")


def save_transparent(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True)
    print(f"  {path.relative_to(ROOT)}")


def apply_android(icon: Image.Image, foreground: Image.Image, portrait_splash: Image.Image, square_splash: Image.Image) -> None:
    if not ANDROID_RES.exists():
        return
    densities = {
        "mdpi": 1.0,
        "hdpi": 1.5,
        "xhdpi": 2.0,
        "xxhdpi": 3.0,
        "xxxhdpi": 4.0,
    }
    for density, factor in densities.items():
        folder = ANDROID_RES / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        size = round(48 * factor)
        legacy = icon.resize((size, size), Image.Resampling.LANCZOS)
        save(legacy, folder / "ic_launcher.png")

        round_icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        round_icon.putalpha(mask)
        save_transparent(round_icon, folder / "ic_launcher_round.png")

        fg_size = round(108 * factor)
        save_transparent(foreground.resize((fg_size, fg_size), Image.Resampling.LANCZOS), folder / "ic_launcher_foreground.png")

    anydpi = ANDROID_RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    adaptive = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/ic_launcher_background" />\n'
        '    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
        "</adaptive-icon>\n"
    )
    (anydpi / "ic_launcher.xml").write_text(adaptive, encoding="utf-8")
    (anydpi / "ic_launcher_round.xml").write_text(adaptive, encoding="utf-8")

    values = ANDROID_RES / "values"
    values.mkdir(parents=True, exist_ok=True)
    (values / "ic_launcher_background.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<resources>\n"
        '    <color name="ic_launcher_background">#08090F</color>\n'
        "</resources>\n",
        encoding="utf-8",
    )

    splash_specs = {
        "drawable": (720, 1280, True),
        "drawable-port-mdpi": (320, 480, True),
        "drawable-port-hdpi": (480, 800, True),
        "drawable-port-xhdpi": (720, 1280, True),
        "drawable-port-xxhdpi": (960, 1600, True),
        "drawable-port-xxxhdpi": (1280, 1920, True),
        "drawable-land-mdpi": (480, 320, False),
        "drawable-land-hdpi": (800, 480, False),
        "drawable-land-xhdpi": (1280, 720, False),
        "drawable-land-xxhdpi": (1600, 960, False),
        "drawable-land-xxxhdpi": (1920, 1280, False),
    }
    for folder, (width, height, portrait) in splash_specs.items():
        path = ANDROID_RES / folder / "splash.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        save(make_splash(width, height, portrait=portrait), path)

    print("  Android launcher and splash assets applied.")


def apply_ios(icon: Image.Image, splash: Image.Image) -> None:
    app_icon_set = IOS_ASSETS / "AppIcon.appiconset"
    if not IOS_ASSETS.exists():
        return
    app_icon_set.mkdir(parents=True, exist_ok=True)
    save(icon.resize((1024, 1024), Image.Resampling.LANCZOS), app_icon_set / "AppIcon-512@2x.png")
    icon_contents = {
        "images": [
            {
                "filename": "AppIcon-512@2x.png",
                "idiom": "universal",
                "platform": "ios",
                "size": "1024x1024",
            }
        ],
        "info": {"author": "xcode", "version": 1},
    }
    (app_icon_set / "Contents.json").write_text(json.dumps(icon_contents, indent=2) + "\n", encoding="utf-8")

    splash_set = IOS_ASSETS / "Splash.imageset"
    splash_set.mkdir(parents=True, exist_ok=True)
    splash_image = splash.resize((2732, 2732), Image.Resampling.LANCZOS)
    save(splash_image, splash_set / "splash-2732x2732-2.png")
    save(splash_image, splash_set / "splash-2732x2732-1.png")
    save(splash_image, splash_set / "splash-2732x2732.png")
    splash_contents = {
        "images": [
            {"filename": "splash-2732x2732-2.png", "idiom": "universal", "scale": "1x"},
            {"filename": "splash-2732x2732-1.png", "idiom": "universal", "scale": "2x"},
            {"filename": "splash-2732x2732.png", "idiom": "universal", "scale": "3x"},
        ],
        "info": {"author": "xcode", "version": 1},
    }
    (splash_set / "Contents.json").write_text(json.dumps(splash_contents, indent=2) + "\n", encoding="utf-8")
    print("  iOS launcher and splash assets applied.")


def main() -> None:
    PUBLIC_ICONS.mkdir(parents=True, exist_ok=True)
    RESOURCES.mkdir(parents=True, exist_ok=True)

    icon = make_icon()
    foreground = make_foreground()
    maskable = make_icon(scale=0.82)
    splash_square = make_splash(2732, 2732, portrait=False)
    splash_portrait = make_splash(1440, 2560, portrait=True)
    splash_landscape = make_splash(2560, 1440, portrait=False)

    print("Web and PWA assets:")
    save(icon, PUBLIC_ICONS / "icon-512.png")
    save(icon.resize((192, 192), Image.Resampling.LANCZOS), PUBLIC_ICONS / "icon-192.png")
    save(maskable, PUBLIC_ICONS / "maskable-512.png")
    save(icon.resize((180, 180), Image.Resampling.LANCZOS), PUBLIC_ICONS / "apple-touch-icon.png")
    save(icon.resize((32, 32), Image.Resampling.LANCZOS), PUBLIC_ICONS / "favicon-32.png")
    save(icon, PUBLIC_ICONS / "icon-1024.png")

    print("Source resources:")
    save(icon, RESOURCES / "icon.png")
    save(foreground, RESOURCES / "icon-foreground.png")
    save(Image.new("RGBA", (1024, 1024), (8, 9, 15, 255)), RESOURCES / "icon-background.png")
    save(splash_square, RESOURCES / "splash.png")
    save(splash_portrait, RESOURCES / "splash-portrait.png")
    save(splash_landscape, RESOURCES / "splash-landscape.png")

    print("Native assets:")
    apply_android(icon, foreground, splash_portrait, splash_square)
    apply_ios(icon, splash_square)
    print("Done.")


if __name__ == "__main__":
    main()
