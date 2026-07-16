#!/usr/bin/env python3
"""Generate deterministic neutral fallback PNGs for publishing workflows."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "default-images"
BLUE = "#002FA7"
PAPER = "#F4F1EA"
INK = "#151515"
MUTED = "#6A6965"
LINE = "#D7D3CA"
FONT_REGULAR = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_BOLD = "/System/Library/Fonts/HelveticaNeue.ttc"

SPECS = {
    "weixin_cover": ("weixin-cover.png", 900, 383),
    "weibo": ("social-landscape.png", 1200, 900),
    "universal": ("universal-square.png", 1200, 1200),
    "xiaohongshu": ("xiaohongshu-portrait.png", 1080, 1440),
}


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def draw_card(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(image)
    margin = max(36, round(min(width, height) * 0.09))
    blue = max(8, round(min(width, height) * 0.012))

    draw.rectangle((0, 0, width - 1, height - 1), outline=LINE, width=2)
    draw.rectangle((margin, margin, margin + blue, height - margin), fill=BLUE)
    draw.line((margin + blue + 28, margin, width - margin, margin), fill=INK, width=2)

    label_size = max(16, round(min(width, height) * 0.045))
    title_size = max(42, round(min(width, height) * 0.15))
    small_size = max(14, round(min(width, height) * 0.033))
    draw.text((margin + blue + 28, margin + 18), "WATTTER / KNOWLEDGE", fill=MUTED, font=font(FONT_REGULAR, label_size))

    title_y = round(height * 0.43)
    draw.text((margin + blue + 28, title_y), "IDEAS", fill=INK, font=font(FONT_BOLD, title_size))
    title_box = draw.textbbox((0, 0), "IDEAS", font=font(FONT_BOLD, title_size))
    title_width = title_box[2] - title_box[0]
    dot = max(10, round(title_size * 0.13))
    draw.ellipse(
        (margin + blue + 32 + title_width, title_y + title_size - dot * 2, margin + blue + 32 + title_width + dot, title_y + title_size - dot),
        fill=BLUE,
    )

    baseline = height - margin - small_size * 2
    draw.text((margin + blue + 28, baseline), "INSIGHT  /  PRACTICE  /  SYSTEM", fill=MUTED, font=font(FONT_REGULAR, small_size))
    draw.text((width - margin - small_size * 5, baseline), f"{width}×{height}", fill=MUTED, font=font(FONT_REGULAR, small_size))

    grid_left = round(width * 0.69)
    grid_top = round(height * 0.27)
    grid_size = max(18, round(min(width, height) * 0.065))
    gap = max(8, round(grid_size * 0.45))
    for row in range(3):
        for col in range(3):
            x = grid_left + col * (grid_size + gap)
            y = grid_top + row * (grid_size + gap)
            if x + grid_size < width - margin and y + grid_size < baseline - 12:
                fill = BLUE if (row, col) == (0, 2) else None
                draw.rectangle((x, y, x + grid_size, y + grid_size), outline=INK if fill is None else BLUE, fill=fill, width=2)
    return image


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets: dict[str, dict[str, object]] = {}
    for use_case, (filename, width, height) in SPECS.items():
        path = OUTPUT / filename
        draw_card(width, height).save(path, format="PNG", optimize=True)
        assets[use_case] = {"file": filename, "width": width, "height": height, "source": "bundled_default"}
    manifest = {"schema_version": 1, "accent": BLUE, "assets": assets}
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

