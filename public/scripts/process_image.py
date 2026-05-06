from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "public" / "assets"
SOURCE = ASSETS / "hand-source.jpg"

TRANSPARENT = ASSETS / "hand-transparent.png"
BLUE = ASSETS / "hand-blue.jpg"
KINTSUGI = ASSETS / "hand-kintsugi.jpg"

TARGET_WIDTH = 1800


def resize(image: Image.Image) -> Image.Image:
    width, height = image.size
    if width <= TARGET_WIDTH:
        return image.copy()
    ratio = TARGET_WIDTH / width
    return image.resize((TARGET_WIDTH, int(height * ratio)), Image.Resampling.LANCZOS)


def build_kintsugi(image: Image.Image) -> Image.Image:
    warm = ImageEnhance.Color(image).enhance(1.22)
    warm = ImageEnhance.Contrast(warm).enhance(1.08)
    warm = ImageEnhance.Brightness(warm).enhance(1.03)

    overlay = Image.new("RGB", warm.size, "#f4d9ab")
    blended = Image.blend(warm, overlay, 0.08)
    sharpened = blended.filter(ImageFilter.UnsharpMask(radius=2.2, percent=110, threshold=2))
    return sharpened


def build_blue(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    blue = ImageOps.colorize(gray, black="#10233e", mid="#577fb0", white="#e6f1ff")
    blue = ImageEnhance.Contrast(blue).enhance(1.12)
    blue = ImageEnhance.Color(blue).enhance(0.95)
    return blue


def build_transparent(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    background = [[False for _ in range(width)] for _ in range(height)]
    queue: deque[tuple[int, int]] = deque()

    def is_background_candidate(x: int, y: int) -> bool:
        red, green, blue, _ = pixels[x, y]
        value = max(red, green, blue)
        luminance = int((red * 299 + green * 587 + blue * 114) / 1000)
        chroma = value - min(red, green, blue)
        return luminance < 86 and value < 104 and chroma < 72

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if background[y][x] or not is_background_candidate(x, y):
            continue
        background[y][x] = True
        queue.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))

    alpha = Image.new("L", rgba.size, 255)
    alpha_px = alpha.load()

    for y in range(height):
        for x in range(width):
            if background[y][x]:
                alpha_px[x, y] = 0

    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.6))
    alpha = ImageOps.autocontrast(alpha)
    rgba.putalpha(alpha)
    box = rgba.getbbox()
    if box:
        left, top, right, bottom = box
        pad = 48
        crop_box = (
            max(left - pad, 0),
            max(top - pad, 0),
            min(right + pad, width),
            min(bottom + pad, height),
        )
        rgba = rgba.crop(crop_box)

    rgba = ImageEnhance.Brightness(rgba).enhance(1.03)
    return rgba


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source image not found: {SOURCE}")

    ASSETS.mkdir(parents=True, exist_ok=True)

    original = Image.open(SOURCE).convert("RGB")
    working = resize(original)

    build_kintsugi(working).save(KINTSUGI, quality=92)
    build_blue(working).save(BLUE, quality=92)
    build_transparent(working).save(TRANSPARENT)


if __name__ == "__main__":
    main()
