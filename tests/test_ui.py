import os
import pytest
from src.ui.app import App, APP_TITLE

def test_app_title_constant():
    assert APP_TITLE == "Lumeed Psplit"

def test_icon_exists():
    assert os.path.exists("icon.ico")
    assert os.path.exists("icon.png")
