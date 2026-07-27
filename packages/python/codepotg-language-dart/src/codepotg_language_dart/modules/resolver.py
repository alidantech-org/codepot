from __future__ import annotations

from codepotg.ports import ModulePathFacts, ModulePathKind, ModulePathRequest

from ..options import DartTargetOptions
from ..validation.paths import contained_parts
from .explicit import validate_explicit
from .package import package_uri, validate_package_name
from .relative import relative_uri


def resolve_module_path(
    request: ModulePathRequest,
    options: DartTargetOptions,
) -> ModulePathFacts:
    _validate_artifact(request.current_artifact, "current")
    if request.explicit_module is not None:
        specifier = validate_explicit(request.explicit_module, request.current_artifact)
        kind = (
            ModulePathKind.PACKAGE if specifier.startswith("package:") else ModulePathKind.EXPLICIT
        )
        return ModulePathFacts(
            kind=kind,
            specifier=specifier,
            current_artifact=request.current_artifact,
            package_path=specifier if kind is ModulePathKind.PACKAGE else None,
        )
    if request.package_name is not None:
        validate_package_name(request.package_name)
        raise ValueError(
            "DART_MODULE_PATH_UNSUPPORTED: package name alone does not identify a Dart library file"
        )
    provider = request.provider_artifact
    if provider is None:
        raise ValueError("DART_MODULE_PATH_INVALID: provider artifact is missing")
    _validate_artifact(provider, "provider")
    if options.package_name is not None and request.project_root is not None:
        specifier = package_uri(provider, request.project_root, options)
        return ModulePathFacts(
            kind=ModulePathKind.PACKAGE,
            specifier=specifier,
            current_artifact=request.current_artifact,
            provider_artifact=provider,
            package_path=specifier,
        )
    if options.prefer_package_uris:
        raise ValueError(
            "DART_MODULE_PATH_UNSUPPORTED: prefer_package_uris requires explicit project_root metadata"
        )
    specifier = relative_uri(request.current_artifact, provider)
    return ModulePathFacts(
        kind=ModulePathKind.RELATIVE,
        specifier=specifier,
        current_artifact=request.current_artifact,
        provider_artifact=provider,
        relative_path=specifier,
    )


def _validate_artifact(path: str, role: str) -> None:
    contained_parts(path)
    if not path.endswith(".dart"):
        raise ValueError(f"DART_MODULE_PATH_UNSUPPORTED: {role} artifact must end with .dart")
