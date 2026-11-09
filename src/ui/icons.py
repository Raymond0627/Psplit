"""Vector-style icon generation (anti-aliased, in-memory) for Lumeed Psplit."""

import math
from typing import Optional

from PIL import Image, ImageDraw

_SCALE = 4  # Supersampling factor for crisp anti-aliasing


def _new_canvas(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    big = size * _SCALE
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), big


def _finish(img: Image.Image, size: int) -> Image.Image:
    return img.resize((size, size), Image.LANCZOS)


def arrow_down_icon(color: str = "#9CA3AF", size: int = 20) -> Image.Image:
    """Render a clean downward-arrow (download) icon with a transparent background."""
    img, draw, s = _new_canvas(size)
    m = s / 20.0  # geometry designed on a 20x20 grid

    stem_w = 2.4 * m
    cx = s / 2
    top = 3.2 * m
    bottom = 11.2 * m

    # Stem
    draw.rounded_rectangle(
        [cx - stem_w / 2, top, cx + stem_w / 2, bottom + stem_w / 2],
        radius=stem_w / 2,
        fill=color,
    )

    # Arrow head (chevron)
    head_w = 5.6 * m
    head_top = 8.2 * m
    head_tip = 16.6 * m
    draw.line(
        [(cx - head_w, head_top), (cx, head_tip), (cx + head_w, head_top)],
        fill=color,
        width=int(round(2.4 * m)),
        joint="curve",
    )
    # Rounded caps for the chevron ends
    r = 1.2 * m
    for px, py in ((cx - head_w, head_top), (cx + head_w, head_top), (cx, head_tip)):
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

    return _finish(img, size)


def gear_icon(color: str = "#9CA3AF", size: int = 20) -> Image.Image:
    """Render a modern gear/settings icon with a transparent background."""
    img, draw, s = _new_canvas(size)
    cx = cy = s / 2

    outer = 8.2 * (s / 20.0)
    inner = 6.0 * (s / 20.0)
    hole = 2.6 * (s / 20.0)
    teeth = 8
    tooth_depth = 1.9 * (s / 20.0)

    # Gear body
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=color)

    # Teeth as rounded spokes
    for i in range(teeth):
        angle = (2 * math.pi / teeth) * i
        x1 = cx + math.cos(angle) * (inner - 0.4 * (s / 20.0))
        y1 = cy + math.sin(angle) * (inner - 0.4 * (s / 20.0))
        x2 = cx + math.cos(angle) * (outer + tooth_depth)
        y2 = cy + math.sin(angle) * (outer + tooth_depth)
        w = int(round(2.6 * (s / 20.0)))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=w)
        draw.ellipse([x2 - w / 2, y2 - w / 2, x2 + w / 2, y2 + w / 2], fill=color)

    # Center hole (punch out to transparent)
    draw.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=(0, 0, 0, 0))

    return _finish(img, size)
