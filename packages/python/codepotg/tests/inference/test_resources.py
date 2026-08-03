"""Tests for resource metadata inference."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.inference.resources import extract_resource_from_x_codegen
from archives.codepotg.src.openapi.document import OpenApiDocument


def test_extract_resource_path_from_x_codegen() -> None:
    x_codegen = {
        "resource": {
            "name": "users",
            "path": ["platform", "auth"],
        }
    }

    resource = extract_resource_from_x_codegen(x_codegen)

    assert resource is not None
    assert resource.name == "users"
    assert resource.path == ("platform", "auth")


def test_extract_resource_ignores_invalid_path() -> None:
    x_codegen = {
        "resource": {
            "name": "users",
            "path": "platform/auth",
        }
    }

    resource = extract_resource_from_x_codegen(x_codegen)

    assert resource is not None
    assert resource.path == ()


def test_extract_resource_from_codegen_ref() -> None:
    document = OpenApiDocument(
        path=Path("openapi.yaml"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "x-codegen": {
                "resources": {
                    "apps": {
                        "name": "apps",
                        "path": ["platform"],
                        "route": "/platform/apps",
                    }
                }
            },
        },
    )

    resource = extract_resource_from_x_codegen(
        {"resource": {"$ref": "#/x-codegen/resources/apps"}},
        document,
    )

    assert resource is not None
    assert resource.name == "apps"
    assert resource.path == ("platform",)


def test_extract_resource_from_unresolved_codegen_ref_returns_none() -> None:
    document = OpenApiDocument(
        path=Path("openapi.yaml"),
        raw={
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        },
    )

    resource = extract_resource_from_x_codegen(
        {"resource": {"$ref": "#/x-codegen/resources/missing"}},
        document,
    )

    assert resource is None
