import pytest
from src.core.updater import parse_version_tuple, is_newer_version, check_github_update

def test_parse_version_tuple():
    assert parse_version_tuple("v1.0.0") == (1, 0, 0)
    assert parse_version_tuple("1.2.3") == (1, 2, 3)
    assert parse_version_tuple("v2.10.4-beta") == (2, 10, 4)

def test_is_newer_version():
    assert is_newer_version("1.0.0", "1.0.1") is True
    assert is_newer_version("v1.0.0", "v1.1.0") is True
    assert is_newer_version("1.2.0", "1.1.9") is False
    assert is_newer_version("1.0.0", "1.0.0") is False
    assert is_newer_version("1.0.0", "v1.0.0") is False
