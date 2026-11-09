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
