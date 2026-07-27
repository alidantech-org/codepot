from dataclasses import FrozenInstanceError

import pytest
from codepotg_language_dart import DartTargetOptions


def test_options_are_immutable_serializable_and_strict() -> None:
    options = DartTargetOptions.from_mapping(
        {"package_name": "example_sdk", "prefer_package_uris": True}
    )
    assert options.to_dict()["package_name"] == "example_sdk"
    assert options.to_dict()["prefer_package_uris"] is True
    with pytest.raises(FrozenInstanceError):
        options.package_name = "other"  # type: ignore[misc]
    with pytest.raises(ValueError, match="unknown Dart option"):
        DartTargetOptions.from_mapping({"annotation_style": "generated"})


def test_invalid_package_name_rejected() -> None:
    with pytest.raises(ValueError, match="valid Dart package name"):
        DartTargetOptions(package_name="Example-SDK")


def test_adapter_instance_is_immutable() -> None:
    from codepotg_language_dart import DartTargetAdapter

    adapter = DartTargetAdapter()
    with pytest.raises(FrozenInstanceError):
        adapter.options = adapter.options  # type: ignore[misc]
