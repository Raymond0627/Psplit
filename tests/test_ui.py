import os
import pytest
from src.ui.app import App, APP_TITLE


@pytest.fixture(scope="module")
def app():
    instance = App()
    yield instance
    instance.destroy()


def test_app_title_constant():
    assert APP_TITLE == "Lumeed Psplit"


def test_icon_exists():
    assert os.path.exists("icon.ico")
    assert os.path.exists("icon.png")


def test_header_buttons_use_vector_images(app):
    # No Unicode glyphs (they render as '?' on many Windows fonts)
    assert app.header_update_btn.cget("text") == ""
    assert app.header_settings_btn.cget("text") == ""
    assert app.header_update_btn.cget("image") is not None
    assert app.header_settings_btn.cget("image") is not None


def test_arrow_button_visible_and_idle_grayscale(app):
    assert app.has_update is False
    assert app.header_update_btn.winfo_manager() == "pack"
    assert app.header_update_btn.cget("fg_color") == ("gray85", "gray25")


def test_update_found_turns_button_emerald(app):
    app._on_update_found("v1.2.0", "notes", "https://example.com/setup.exe")
    try:
        assert app.has_update is True
        assert "v1.2.0" in app.header_update_btn.cget("text")
        assert app.header_update_btn.cget("fg_color") == "#10B981"
    finally:
        if app._update_dialog is not None and app._update_dialog.winfo_exists():
            app._update_dialog._on_cancel()
        # Reset to idle so later tests start clean
        app.has_update = False
        app.update_info = None
        app.header_update_btn.configure(
            text="", image=app._arrow_idle_img, width=38,
            fg_color=("gray85", "gray25"), hover_color=("gray75", "gray35"),
        )


def test_settings_panel_toggles_without_freezing_app(app):
    app.header_settings_btn.invoke()
    assert app._settings_panel.winfo_manager() == "place"
    # Rapid theme switching must never lock the UI
    app._settings_panel._on_theme_changed("Dark")
    app._settings_panel._on_theme_changed("Light")
    app._settings_panel._on_theme_changed("Dark")
    app._on_close_settings_panel()
    assert app._settings_panel.winfo_manager() == ""
    # Settings button must still respond afterwards
    app.header_settings_btn.invoke()
    assert app._settings_panel.winfo_manager() == "place"
    app._on_close_settings_panel()
    assert app.grab_current() is None
