import pytest
from dryv.ports import ModulePathKind, ModulePathRequest

from dryv_language_dart import DartTargetAdapter, DartTargetOptions


def test_relative_paths_preserve_dart_suffix() -> None:
    adapter = DartTargetAdapter()
    assert (
        adapter.resolve_module_path(
            ModulePathRequest(
                "lib/src/users/user_service.dart",
                provider_artifact="lib/src/users/user.dart",
            )
        ).specifier
        == "./user.dart"
    )
    assert (
        adapter.resolve_module_path(
            ModulePathRequest(
                "lib/src/users/user_service.dart",
                provider_artifact="lib/src/shared/user.dart",
            )
        ).specifier
        == "../shared/user.dart"
    )


def test_package_uri_requires_explicit_package_and_library_root() -> None:
    adapter = DartTargetAdapter(DartTargetOptions(package_name="example_sdk"))
    facts = adapter.resolve_module_path(
        ModulePathRequest(
            "lib/src/service.dart",
            provider_artifact="lib/src/users/user.dart",
            project_root="lib",
        )
    )
    assert facts.kind is ModulePathKind.PACKAGE
    assert facts.specifier == "package:example_sdk/src/users/user.dart"
    with pytest.raises(ValueError, match="^DART_MODULE_PATH_UNSUPPORTED:"):
        adapter.resolve_module_path(
            ModulePathRequest(
                "lib/src/service.dart",
                provider_artifact="test/user.dart",
                project_root="test",
            )
        )


def test_provider_outside_lib_is_rejected() -> None:
    adapter = DartTargetAdapter(DartTargetOptions(package_name="example_sdk"))
    with pytest.raises(ValueError, match="^DART_MODULE_PATH_ESCAPE:"):
        adapter.resolve_module_path(
            ModulePathRequest(
                "lib/src/service.dart",
                provider_artifact="test/user.dart",
                project_root="lib",
            )
        )


def test_explicit_uris_are_preserved() -> None:
    adapter = DartTargetAdapter()
    for value, kind in [
        ("dart:async", ModulePathKind.EXPLICIT),
        ("package:example_sdk/src/user.dart", ModulePathKind.PACKAGE),
        ("./user.dart", ModulePathKind.EXPLICIT),
        ("../shared/user.dart", ModulePathKind.EXPLICIT),
    ]:
        facts = adapter.resolve_module_path(
            ModulePathRequest("lib/src/service.dart", explicit_module=value)
        )
        assert facts.specifier == value
        assert facts.kind is kind


@pytest.mark.parametrize(
    "value",
    [
        "http://example.com/user.dart",
        "https://example.com/user.dart",
        "ftp://example.com/user.dart",
        "file:///tmp/user.dart",
        "'dart:async'",
        "package:example_sdk/../user.dart",
        "package:example_sdk//user.dart",
        "..\\shared\\user.dart",
    ],
)
def test_invalid_explicit_uris(value: str) -> None:
    with pytest.raises(ValueError, match="^DART_MODULE_"):
        DartTargetAdapter().resolve_module_path(
            ModulePathRequest("lib/src/service.dart", explicit_module=value)
        )


def test_package_name_alone_is_unsupported() -> None:
    with pytest.raises(ValueError, match="^DART_MODULE_PATH_UNSUPPORTED:"):
        DartTargetAdapter().resolve_module_path(
            ModulePathRequest("lib/src/service.dart", package_name="example_sdk")
        )


def test_provider_filenames_are_never_rewritten() -> None:
    adapter = DartTargetAdapter()
    for provider in (
        "lib/src/model.dart",
        "lib/src/enum.dart",
        "lib/src/index.dart",
    ):
        facts = adapter.resolve_module_path(
            ModulePathRequest("lib/src/service.dart", provider_artifact=provider)
        )
        assert facts.specifier == f"./{provider.rsplit('/', 1)[-1]}"


def test_deterministic_results_and_stable_errors() -> None:
    adapter = DartTargetAdapter()
    request = ModulePathRequest(
        "lib/src/service.dart",
        provider_artifact="lib/src/user.dart",
    )
    assert adapter.resolve_module_path(request) == adapter.resolve_module_path(request)
    with pytest.raises(ValueError, match="^DART_MODULE_PATH_INVALID:"):
        adapter.resolve_module_path(
            ModulePathRequest("../service.dart", provider_artifact="lib/user.dart")
        )


@pytest.mark.parametrize(
    "value",
    [
        "./shared/./user.dart",
        "./shared//user.dart",
        "dart:foo.",
    ],
)
def test_invalid_explicit_uri_segments(value: str) -> None:
    with pytest.raises(ValueError, match="^DART_MODULE_"):
        DartTargetAdapter().resolve_module_path(
            ModulePathRequest("lib/src/service.dart", explicit_module=value)
        )


def test_artifact_suffixes_are_required() -> None:
    adapter = DartTargetAdapter()
    with pytest.raises(ValueError, match="^DART_MODULE_PATH_UNSUPPORTED:"):
        adapter.resolve_module_path(
            ModulePathRequest("lib/src/service.txt", provider_artifact="lib/src/user.dart")
        )
    with pytest.raises(ValueError, match="^DART_MODULE_PATH_UNSUPPORTED:"):
        adapter.resolve_module_path(
            ModulePathRequest("lib/src/service.dart", provider_artifact="lib/src/user.txt")
        )
