import pytest
from codepotg.ports import ModulePathKind, ModulePathRequest

from codepotg_language_typescript import (
    AliasBinding,
    IndexResolutionPolicy,
    TypeScriptExtensionPolicy,
    TypeScriptTargetAdapter,
    TypeScriptTargetOptions,
)


def test_relative_paths_and_declaration_suffix_omission() -> None:
    adapter = TypeScriptTargetAdapter()
    assert (
        adapter.resolve_module_path(
            ModulePathRequest(
                "src/groups/users/user.service.ts",
                provider_artifact="src/groups/users/user.types.ts",
            )
        ).specifier
        == "./user.types"
    )
    assert (
        adapter.resolve_module_path(
            ModulePathRequest(
                "src/groups/users/service.ts",
                provider_artifact="src/groups/shared/types.d.ts",
            )
        ).specifier
        == "../shared/types"
    )


def test_preserve_extension_and_omit_index() -> None:
    options = TypeScriptTargetOptions(
        extension_policy=TypeScriptExtensionPolicy.PRESERVE,
        index_policy=IndexResolutionPolicy.OMIT_INDEX,
    )
    adapter = TypeScriptTargetAdapter(options)
    assert (
        adapter.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                provider_artifact="src/users/index.ts",
            )
        ).specifier
        == "./users"
    )
    omitted = TypeScriptTargetAdapter(
        TypeScriptTargetOptions(index_policy=IndexResolutionPolicy.OMIT_INDEX)
    )
    assert (
        omitted.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                provider_artifact="src/users/index.ts",
            )
        ).specifier
        == "./users"
    )


def test_alias_longest_match() -> None:
    options = TypeScriptTargetOptions(
        aliases=(
            AliasBinding("@", "src"),
            AliasBinding("@domain", "src/domain"),
        )
    )
    adapter = TypeScriptTargetAdapter(options)
    facts = adapter.resolve_module_path(
        ModulePathRequest(
            "src/service.ts",
            provider_artifact="src/domain/users/user.ts",
        )
    )
    assert facts.kind is ModulePathKind.ALIAS
    assert facts.specifier == "@domain/users/user"


def test_package_modes() -> None:
    adapter = TypeScriptTargetAdapter(TypeScriptTargetOptions(package_name="example-sdk"))
    assert (
        adapter.resolve_module_path(
            ModulePathRequest("src/service.ts", package_name="@scope/pkg")
        ).specifier
        == "@scope/pkg"
    )
    facts = adapter.resolve_module_path(
        ModulePathRequest(
            "src/service.ts",
            provider_artifact="src/types/user.ts",
            project_root="src",
        )
    )
    assert facts.specifier == "example-sdk/types/user"


@pytest.mark.parametrize(
    "value",
    [
        "http://example.com/x",
        "'pkg'",
        "import x",
        "pkg;evil",
        "..\\evil",
    ],
)
def test_invalid_explicit_modules(value: str) -> None:
    with pytest.raises(ValueError, match="^TS_MODULE_"):
        TypeScriptTargetAdapter().resolve_module_path(
            ModulePathRequest("src/service.ts", explicit_module=value)
        )


def test_explicit_and_deterministic() -> None:
    adapter = TypeScriptTargetAdapter()
    request = ModulePathRequest(
        "src/service.ts",
        explicit_module="@scope/package/subpath",
    )
    assert adapter.resolve_module_path(request) == adapter.resolve_module_path(request)
    assert adapter.resolve_module_path(request).kind is ModulePathKind.EXPLICIT


def test_invalid_planned_paths_have_stable_errors() -> None:
    with pytest.raises(ValueError, match="^TS_MODULE_PATH_INVALID:"):
        TypeScriptTargetAdapter().resolve_module_path(
            ModulePathRequest("../service.ts", provider_artifact="src/user.ts")
        )


def test_index_omission_applies_with_preserved_extensions_for_all_modes() -> None:
    options = TypeScriptTargetOptions(
        extension_policy=TypeScriptExtensionPolicy.PRESERVE,
        index_policy=IndexResolutionPolicy.OMIT_INDEX,
        package_name="example-sdk",
        aliases=(AliasBinding("@", "src"),),
    )
    adapter = TypeScriptTargetAdapter(options)
    assert (
        adapter.resolve_module_path(
            ModulePathRequest("app/service.ts", provider_artifact="src/users/index.ts")
        ).specifier
        == "@/users"
    )
    package_adapter = TypeScriptTargetAdapter(
        TypeScriptTargetOptions(
            extension_policy=TypeScriptExtensionPolicy.PRESERVE,
            index_policy=IndexResolutionPolicy.OMIT_INDEX,
            package_name="example-sdk",
        )
    )
    assert (
        package_adapter.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                provider_artifact="src/index.ts",
                project_root="src",
            )
        ).specifier
        == "example-sdk"
    )


def test_artifact_suffixes_are_required() -> None:
    adapter = TypeScriptTargetAdapter()
    with pytest.raises(ValueError, match="^TS_MODULE_PATH_UNSUPPORTED:"):
        adapter.resolve_module_path(
            ModulePathRequest("src/service.js", provider_artifact="src/user.ts")
        )
    with pytest.raises(ValueError, match="^TS_MODULE_PATH_UNSUPPORTED:"):
        adapter.resolve_module_path(
            ModulePathRequest("src/service.ts", provider_artifact="src/user.js")
        )
