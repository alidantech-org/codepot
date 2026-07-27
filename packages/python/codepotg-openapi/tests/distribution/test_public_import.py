from __future__ import annotations

from codepotg_openapi import OpenApiSourceAdapter, create_plugin


def test_public_import_and_factory_are_real() -> None:
    assert create_plugin().__class__ is OpenApiSourceAdapter
