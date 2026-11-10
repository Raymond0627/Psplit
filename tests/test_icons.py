import pytest
from src.ui.icons import arrow_down_icon, gear_icon


def _has_visible_pixels(img):
    # Alpha channel extrema: (min, max) — max > 0 means something is drawn
    return img.getchannel("A").getextrema()[1] > 0


def test_arrow_down_icon_renders():
    img = arrow_down_icon("#10B981", size=20)
    assert img.size == (20, 20)
    assert img.mode == "RGBA"
    assert _has_visible_pixels(img)


def test_gear_icon_renders():
    img = gear_icon("#9CA3AF", size=20)
    assert img.size == (20, 20)
    assert img.mode == "RGBA"
    assert _has_visible_pixels(img)


def test_icons_are_transparent_background():
    img = arrow_down_icon("#000000", size=20)
    # Corner pixels should be fully transparent
    assert img.getpixel((0, 0))[3] == 0


def test_badge_and_folder_and_play_icons():
    from src.ui.icons import (
        badge_icon,
        folder_icon,
        play_icon,
        document_illustration,
    )
    b = badge_icon("document", "#1677FF", size=20)
    assert b.size == (20, 20)
    assert _has_visible_pixels(b)

    f = folder_icon("#1677FF", size=16)
    assert f.size == (16, 16)
    assert _has_visible_pixels(f)

    p = play_icon("#FFFFFF", size=16)
    assert p.size == (16, 16)
    assert _has_visible_pixels(p)

    doc = document_illustration(width=160, height=110)
    assert doc.size == (160, 110)
    assert _has_visible_pixels(doc)
