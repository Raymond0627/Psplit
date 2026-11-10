"""Vector-style icon generation (anti-aliased, in-memory) for Lumeed Psplit.

Provides:
- logo_mark_icon: brand droplet/spiral mark (cyan/blue gradient feel)
- badge_icon: small colored rounded square badge with icon inside (document, lightning, list)
- folder_icon: clean filled/stroke folder icon (for browse/choose/open)
- play_icon: right-facing triangle for start button
- arrow_down_icon: down arrow for update
- gear_icon: settings gear
- info_icon: circular info glyph
- document_illustration: cute empty-state illustration matching the reference
- wave_background: generates an SVG/PNG subtle wave pattern for window background
"""

import math
from typing import Optional, Tuple

from PIL import Image, ImageDraw

_SCALE = 4


def _new_canvas(w: int, h: Optional[int] = None) -> Tuple[Image.Image, ImageDraw.ImageDraw, int, int]:
    h = h if h is not None else w
    bw, bh = w * _SCALE, h * _SCALE
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), bw, bh


def _finish(img: Image.Image, w: int, h: Optional[int] = None) -> Image.Image:
    h = h if h is not None else w
    return img.resize((w, h), Image.LANCZOS)


def arrow_down_icon(color: str = "#475569", size: int = 18) -> Image.Image:
    img, draw, w, h = _new_canvas(size)
    m = w / 20.0
    cx = w / 2
    stem_w = 2.0 * m
    draw.rounded_rectangle([cx - stem_w / 2, 4 * m, cx + stem_w / 2, 13 * m], radius=stem_w / 2, fill=color)
    draw.line([(cx - 4.5 * m, 9.5 * m), (cx, 14.5 * m), (cx + 4.5 * m, 9.5 * m)], fill=color, width=int(round(2.0 * m)), joint="curve")
    r = 1.0 * m
    for px, py in ((cx - 4.5 * m, 9.5 * m), (cx + 4.5 * m, 9.5 * m), (cx, 14.5 * m)):
        draw.ellipse([px - r, py - r, px + r, py + r], fill=color)
    # Tray bar
    draw.rounded_rectangle([cx - 5.5 * m, 16.5 * m, cx + 5.5 * m, 18.0 * m], radius=0.75 * m, fill=color)
    return _finish(img, size)


def gear_icon(color: str = "#475569", size: int = 18) -> Image.Image:
    img, draw, w, h = _new_canvas(size)
    cx = cy = w / 2
    outer = 7.5 * (w / 20.0)
    inner = 5.5 * (w / 20.0)
    hole = 2.5 * (w / 20.0)
    teeth = 8
    tooth_depth = 1.8 * (w / 20.0)
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=color)
    for i in range(teeth):
        angle = (2 * math.pi / teeth) * i
        x1 = cx + math.cos(angle) * (inner - 0.4 * (w / 20.0))
        y1 = cy + math.sin(angle) * (inner - 0.4 * (w / 20.0))
        x2 = cx + math.cos(angle) * (outer + tooth_depth)
        y2 = cy + math.sin(angle) * (outer + tooth_depth)
        lw = int(round(2.2 * (w / 20.0)))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)
        draw.ellipse([x2 - lw / 2, y2 - lw / 2, x2 + lw / 2, y2 + lw / 2], fill=color)
    draw.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=(0, 0, 0, 0))
    return _finish(img, size)


def logo_mark_icon(size: int = 22) -> Image.Image:
    """Blue/cyan ribbon droplet ring mark matching reference top-left."""
    img, draw, w, h = _new_canvas(size)
    cx, cy = w / 2, h / 2
    r_out = 9.0 * (w / 20.0)
    r_in = 4.8 * (w / 20.0)
    # Two-tone sweeping arc
    draw.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], fill="#1677FF")
    # Cyan highlight wedge
    draw.pieslice([cx - r_out, cy - r_out, cx + r_out, cy + r_out], start=160, end=330, fill="#38BDF8")
    # Cut out center
    draw.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=(0, 0, 0, 0))
    # Small internal curl
    draw.ellipse([cx - 2 * (w / 20.0), cy - 4.5 * (w / 20.0), cx + 5 * (w / 20.0), cy + 2.5 * (w / 20.0)], fill="#1677FF")
    return _finish(img, size)


def badge_icon(kind: str = "document", bg_color: str = "#1677FF", size: int = 22) -> Image.Image:
    """Rounded-square badge with a white glyph inside (document, lightning, list)."""
    img, draw, w, h = _new_canvas(size)
    corner = 5.0 * (w / 22.0)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=corner, fill=bg_color)
    cx, cy = w / 2, h / 2
    m = w / 22.0

    if kind == "document":
        # White page outline with lines
        px0, py0, px1, py1 = cx - 4.5 * m, cy - 6 * m, cx + 4.5 * m, cy + 6 * m
        draw.rounded_rectangle([px0, py0, px1, py1], radius=1.2 * m, outline="#FFFFFF", width=int(round(1.5 * m)))
        for dy in (-2 * m, 0.5 * m, 3 * m):
            draw.line([(cx - 2.5 * m, cy + dy), (cx + 2.5 * m, cy + dy)], fill="#FFFFFF", width=int(round(1.2 * m)))

    elif kind == "lightning":
        # Lightning bolt
        pts = [
            (cx + 0.5 * m, cy - 6 * m),
            (cx - 4.5 * m, cy - 0.5 * m),
            (cx - 0.5 * m, cy - 0.5 * m),
            (cx - 1.5 * m, cy + 6 * m),
            (cx + 4.5 * m, cy + 0.5 * m),
            (cx + 0.5 * m, cy + 0.5 * m),
        ]
        draw.polygon(pts, fill="#FFFFFF")

    elif kind == "list":
        # Three rounded horizontal list rows
        for dy in (-4 * m, 0, 4 * m):
            draw.ellipse([cx - 5.5 * m, cy + dy - 1.2 * m, cx - 3.1 * m, cy + dy + 1.2 * m], fill="#FFFFFF")
            draw.rounded_rectangle([cx - 1.5 * m, cy + dy - 1.0 * m, cx + 5.5 * m, cy + dy + 1.0 * m], radius=1 * m, fill="#FFFFFF")

    return _finish(img, size)


def folder_icon(color: str = "#FFFFFF", size: int = 15) -> Image.Image:
    """Clean folder icon."""
    img, draw, w, h = _new_canvas(size)
    m = w / 16.0
    # Tab
    draw.rounded_rectangle([1 * m, 2 * m, 7 * m, 6 * m], radius=1 * m, fill=color)
    # Body
    draw.rounded_rectangle([1 * m, 4.5 * m, 15 * m, 14 * m], radius=1.8 * m, fill=color)
    return _finish(img, size)


def play_icon(color: str = "#FFFFFF", size: int = 14) -> Image.Image:
    """Right-facing play triangle."""
    img, draw, w, h = _new_canvas(size)
    m = w / 16.0
    pts = [(4 * m, 2.5 * m), (13.5 * m, 8 * m), (4 * m, 13.5 * m)]
    draw.polygon(pts, fill=color)
    # Rounded corners trick
    for p in pts:
        draw.ellipse([p[0] - 0.8 * m, p[1] - 0.8 * m, p[0] + 0.8 * m, p[1] + 0.8 * m], fill=color)
    return _finish(img, size)


def info_icon(color: str = "#64748B", size: int = 18) -> Image.Image:
    """Circular info badge."""
    img, draw, w, h = _new_canvas(size)
    cx, cy = w / 2, h / 2
    r = 8.5 * (w / 20.0)
    m = w / 20.0
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(round(1.5 * m)))
    draw.ellipse([cx - 1 * m, cy - 5 * m, cx + 1 * m, cy - 3 * m], fill=color)
    draw.rounded_rectangle([cx - 1 * m, cy - 1.5 * m, cx + 1 * m, cy + 5 * m], radius=1 * m, fill=color)
    return _finish(img, size)


def document_illustration(width: int = 180, height: int = 120) -> Image.Image:
    """Soft pastel empty-state illustration with stacked sheets, checkmark pill and sparkles."""
    img, draw, w, h = _new_canvas(width, height)
    cx, cy = w / 2, h / 2
    sw, sh = 56 * _SCALE, 76 * _SCALE

    # Back tilted sheet (soft blue tint)
    back_box = [cx - sw / 2 - 8 * _SCALE, cy - sh / 2 - 4 * _SCALE, cx + sw / 2 - 8 * _SCALE, cy + sh / 2 - 4 * _SCALE]
    draw.rounded_rectangle(back_box, radius=8 * _SCALE, fill="#E0EDFF", outline="#D0E2FE", width=int(1.5 * _SCALE))

    # Main front sheet
    front_box = [cx - sw / 2 + 4 * _SCALE, cy - sh / 2 + 2 * _SCALE, cx + sw / 2 + 4 * _SCALE, cy + sh / 2 + 2 * _SCALE]
    draw.rounded_rectangle(front_box, radius=8 * _SCALE, fill="#FFFFFF", outline="#CFE1FD", width=int(2 * _SCALE))

    # Top-right folded corner hint
    fx1 = front_box[2]
    fy0 = front_box[1]
    cw = 14 * _SCALE
    draw.polygon([(fx1 - cw, fy0), (fx1, fy0 + cw), (fx1 - cw, fy0 + cw)], fill="#93C5FD")

    # Document text lines (light blue bars)
    line_x0 = front_box[0] + 10 * _SCALE
    line_x1 = front_box[2] - 12 * _SCALE
    for idx, dy in enumerate((18, 28, 38, 48)):
        lw = line_x1 if idx != 3 else (line_x0 + (line_x1 - line_x0) * 0.55)
        draw.rounded_rectangle(
            [line_x0, front_box[1] + dy * _SCALE, lw, front_box[1] + (dy + 3.5) * _SCALE],
            radius=2 * _SCALE,
            fill="#BFDBFE"
        )

    # Blue circular checkmark badge overlapping bottom-right of front sheet
    br_cx = front_box[2] - 2 * _SCALE
    br_cy = front_box[3] - 2 * _SCALE
    br_r = 13 * _SCALE
    # Outer white ring
    draw.ellipse([br_cx - br_r - 2 * _SCALE, br_cy - br_r - 2 * _SCALE, br_cx + br_r + 2 * _SCALE, br_cy + br_r + 2 * _SCALE], fill="#FFFFFF")
    draw.ellipse([br_cx - br_r, br_cy - br_r, br_cx + br_r, br_cy + br_r], fill="#1677FF")

    # Checkmark inside badge
    check_pts = [
        (br_cx - 5.5 * _SCALE, br_cy),
        (br_cx - 1.5 * _SCALE, br_cy + 4 * _SCALE),
        (br_cx + 5.5 * _SCALE, br_cy - 4 * _SCALE),
    ]
    draw.line(check_pts, fill="#FFFFFF", width=int(2.4 * _SCALE), joint="curve")

    # Sparkle stars in corners
    def _draw_sparkle(sx, sy, sr, fill):
        # 4-point star
        pts = [
            (sx, sy - sr),
            (sx + sr * 0.28, sy - sr * 0.28),
            (sx + sr, sy),
            (sx + sr * 0.28, sy + sr * 0.28),
            (sx, sy + sr),
            (sx - sr * 0.28, sy + sr * 0.28),
            (sx - sr, sy),
            (sx - sr * 0.28, sy - sr * 0.28),
        ]
        draw.polygon(pts, fill=fill)

    _draw_sparkle(cx - sw / 2 - 18 * _SCALE, cy - 20 * _SCALE, 6 * _SCALE, "#93C5FD")
    _draw_sparkle(cx - sw / 2 - 16 * _SCALE, cy + 24 * _SCALE, 4.5 * _SCALE, "#BFDBFE")
    _draw_sparkle(cx + sw / 2 + 22 * _SCALE, cy - 8 * _SCALE, 5.5 * _SCALE, "#93C5FD")

    return _finish(img, width, height)


def wave_backdrop(width: int, height: int, dark: bool = False) -> Image.Image:
    """Generate subtle organic wave illustration background matching reference."""
    img, draw, w, h = _new_canvas(width, height)
    base_bg = "#0F172A" if dark else "#EBF3FE"
    draw.rectangle([0, 0, w, h], fill=base_bg)

    # Top-right blue wave blob
    top_color = "#1E293B" if dark else "#D8E9FE"
    draw.chord([w * 0.45, -h * 0.5, w * 1.3, h * 0.55], start=0, end=360, fill=top_color)

    # Bottom-left flowing wave
    bot_color = "#1E293B" if dark else "#D1E5FE"
    draw.chord([-w * 0.2, h * 0.72, w * 0.85, h * 1.5], start=0, end=360, fill=bot_color)

    return _finish(img, width, height)
