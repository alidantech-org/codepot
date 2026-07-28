from __future__ import annotations

from dryv.ports import ModulePathFacts, ModulePathKind, ModulePathRequest

from ..options import TypeScriptTargetOptions
from ..targets import match_typescript_suffix
from ..validation.paths import contained_parts
from .aliases import alias_specifier
from .explicit import validate_explicit
from .package import provider_package_specifier, validate_package
from .relative import relative_specifier


def resolve_module_path(
    request: ModulePathRequest,
    options: TypeScriptTargetOptions,
) -> ModulePathFacts:
    _validate_artifact(request.current_artifact, "current")
    if request.explicit_module is not None:
        specifier = validate_explicit(
            request.explicit_module,
            request.current_artifact,
            options,
        )
        return ModulePathFacts(
            kind=ModulePathKind.EXPLICIT,
            specifier=specifier,
            current_artifact=request.current_artifact,
        )
    if request.package_name is not None:
        specifier = validate_package(request.package_name)
        return ModulePathFacts(
            kind=ModulePathKind.PACKAGE,
            specifier=specifier,
            current_artifact=request.current_artifact,
            package_path=specifier,
        )
    provider = request.provider_artifact
    if provider is None:
        raise ValueError("TS_MODULE_PATH_INVALID: provider artifact is missing")
    _validate_artifact(provider, "provider")
    alias = alias_specifier(provider, options)
    if alias is not None:
        return ModulePathFacts(
            kind=ModulePathKind.ALIAS,
            specifier=alias,
            current_artifact=request.current_artifact,
            provider_artifact=provider,
        )
    if options.package_name is not None and request.project_root is not None:
        specifier = provider_package_specifier(provider, request.project_root, options)
        return ModulePathFacts(
            kind=ModulePathKind.PACKAGE,
            specifier=specifier,
            current_artifact=request.current_artifact,
            provider_artifact=provider,
            package_path=specifier,
        )
    specifier = relative_specifier(request.current_artifact, provider, options)
    return ModulePathFacts(
        kind=ModulePathKind.RELATIVE,
        specifier=specifier,
        current_artifact=request.current_artifact,
        provider_artifact=provider,
        relative_path=specifier,
    )


def _validate_artifact(path: str, role: str) -> None:
    contained_parts(path)
    if match_typescript_suffix(path) is None:
        raise ValueError(
            f"TS_MODULE_PATH_UNSUPPORTED: {role} artifact has no recognized TypeScript suffix"
        )
