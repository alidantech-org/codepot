"""Compatibility loader for the broad normalized domain view.

The specialized normalized roots classify unresolved plain registry names as internal
``missing`` references. The older broad ``domains`` root historically classified those
plain names as ``external``. Keep that compatibility contract local to this root while
also exposing the hierarchical access registries used by the real Codepot contract.
"""

from __future__ import annotations

from collections.abc import Mapping as _CompatMapping
from dataclasses import replace as _compat_replace
from pathlib import Path
from typing import Any as _CompatAny

_SOURCE_PATH = Path(__file__).resolve().parent.parent / "normalized_domains.py"
_SOURCE = _SOURCE_PATH.read_text(encoding="utf-8")
_IMPORT = (
    "from contracts.normalized_builders import build_reference, build_schema_use"
)
_REPLACEMENT = """from contracts.normalized_builders import (
    build_reference as _strict_build_reference,
    build_schema_use,
)


def build_reference(ref, *, kind, owner, source_path, targets):
    value = _strict_build_reference(
        ref,
        kind=kind,
        owner=owner,
        source_path=source_path,
        targets=targets,
    )
    normalized = __import__(
        'contracts.normalized',
        fromlist=['ResolutionState'],
    )
    if value.state == normalized.ResolutionState.MISSING and not ref.startswith('#/'):
        return __import__('dataclasses').replace(
            value,
            state=normalized.ResolutionState.EXTERNAL,
            diagnostics=(),
        )
    return value
"""

if _SOURCE.count(_IMPORT) != 1:
    raise RuntimeError(
        "Normalized domains compatibility source no longer has the expected "
        "builder import"
    )

_SOURCE = _SOURCE.replace(_IMPORT, _REPLACEMENT, 1)
exec(compile(_SOURCE, str(_SOURCE_PATH), "exec"), globals(), globals())  # noqa: S102

_ORIGINAL_BUILD_NORMALIZED_DOMAIN_VIEW = build_normalized_domain_view


def build_normalized_domain_view(api, raw):
    """Build domains and expose root and resource-scoped access policies."""
    view = _ORIGINAL_BUILD_NORMALIZED_DOMAIN_VIEW(api, raw)
    policies = _compat_access_policies(raw)
    if not policies:
        return view
    return _compat_replace(
        view,
        access=contract_collection(
            _access(policy_id, policy_raw)
            for policy_id, policy_raw in policies
        ),
    )


def _compat_access_policies(
    raw: _CompatMapping[str, _CompatAny] | None,
) -> tuple[tuple[str, _CompatMapping[str, _CompatAny]], ...]:
    if not isinstance(raw, _CompatMapping):
        return ()
    codegen = raw.get("x-codegen")
    if not isinstance(codegen, _CompatMapping):
        return ()

    values: dict[str, _CompatMapping[str, _CompatAny]] = {}
    root_access = codegen.get("access")
    if isinstance(root_access, _CompatMapping):
        _compat_collect_policy_namespace(root_access, prefix="", destination=values)

    resources = codegen.get("resources")
    if isinstance(resources, _CompatMapping):
        for resource_name, resource_value in resources.items():
            if not isinstance(resource_value, _CompatMapping):
                continue
            access = resource_value.get("access")
            if isinstance(access, _CompatMapping):
                _compat_collect_policy_namespace(
                    access,
                    prefix=str(resource_name),
                    destination=values,
                )
    return tuple(values.items())


def _compat_collect_policy_namespace(
    value: _CompatMapping[str, _CompatAny],
    *,
    prefix: str,
    destination: dict[str, _CompatMapping[str, _CompatAny]],
) -> None:
    for name, candidate in value.items():
        if not isinstance(candidate, _CompatMapping):
            continue
        policy_id = f"{prefix}.{name}" if prefix else str(name)
        if _compat_is_policy(candidate):
            destination[policy_id] = candidate
        else:
            _compat_collect_policy_namespace(
                candidate,
                prefix=policy_id,
                destination=destination,
            )


def _compat_is_policy(value: _CompatMapping[str, _CompatAny]) -> bool:
    if any(
        key in value
        for key in ("context", "roles", "permissions", "expression", "tags")
    ):
        return True
    for key in ("public", "authenticated"):
        if key in value and not isinstance(value.get(key), _CompatMapping):
            return True
    return False


del _IMPORT
del _REPLACEMENT
del _SOURCE
del _SOURCE_PATH
