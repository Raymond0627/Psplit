import os
import pytest
from src.ui.app import App, APP_TITLE


@pytest.fixture(scope="module")
def app():
    instance = App()
    yield instance
    instance.destroy()


def test_app_title_constant():
    assert APP_TITLE == "Folio"


def test_icon_exists():
    assert os.path.exists("icon.ico")
    assert os.path.exists("icon.png")


def test_consistent_minimal_control_metrics(app):
    # One design system matching reference: 32px round icon buttons, 36px pill inputs, 36px action pills
    assert app.header_update_btn.cget("width") == 32
    assert app.header_update_btn.cget("height") == 32
    assert app.header_settings_btn.cget("width") == 32
    assert app.header_settings_btn.cget("height") == 32
    assert app.start_btn.cget("height") == 36
    assert app.open_btn.cget("height") == 36
    assert app.pdf_entry.cget("height") == 36
    assert app.out_entry.cget("height") == 36
    assert app.sep_entry.cget("height") == 36
    assert app.pattern_entry.cget("height") == 36


def test_header_buttons_use_vector_images(app):
    # No Unicode glyphs (they render as '?' on many Windows fonts)
    assert app.header_update_btn.cget("text") == ""
    assert app.header_settings_btn.cget("text") == ""
    assert app.header_update_btn.cget("image") is not None
    assert app.header_settings_btn.cget("image") is not None


def test_arrow_button_visible_and_idle_grayscale(app):
    assert app.has_update is False
    assert app.header_update_btn.winfo_manager() == "pack"
    assert app.header_update_btn.cget("fg_color") == "transparent"


def test_update_found_turns_button_emerald(app):
    app._on_update_found("v1.2.0", "notes", "https://example.com/setup.exe")
    try:
        assert app.has_update is True
        assert "v1.2.0" in app.header_update_btn.cget("text")
        assert app.header_update_btn.cget("fg_color") == "#1677FF"
    finally:
        if app._update_dialog is not None and app._update_dialog.winfo_exists():
            app._update_dialog._on_cancel()
        # Reset to idle so later tests start clean
        app.has_update = False
        app.update_info = None
        app.header_update_btn.configure(
            text="", image=app._arrow_idle_img, width=32,
            fg_color="transparent", hover_color=("#DCE8FA", "#1E2A42"),
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
