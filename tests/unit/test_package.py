"""Check that the installed source package can be imported."""

from importlib import import_module


def test_app_package_is_importable() -> None:
    import_module("app")
