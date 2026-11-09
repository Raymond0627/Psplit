import os
import pytest
from src.ui.app import App, APP_TITLE

def test_app_title_constant():
    assert APP_TITLE == "Lumeed Psplit"

def test_icon_exists():
    assert os.path.exists("icon.ico")
    assert os.path.exists("icon.png")

def test_app_has_update_attributes():
    app = App()
    try:
        assert hasattr(app, "header_update_btn")
        assert hasattr(app, "_check_updates_background")
        assert hasattr(app, "_on_update_found")
    finally:
        app.destroy()
