"""Real-contract compatibility layer for normalized Codepot metadata.

The sibling module defines the public dataclasses and core builders. This package loads
that implementation and extends operation/access parsing for the authored real-world
Codepot contract without changing the public template objects.
"""

from __future__ import annotations

from pathlib import Path

_SOURCE_PATH = Path(__file__).resolve().parent.parent / "normalized_codegen_contract.py"
_SOURCE = _SOURCE_PATH.read_text(encoding="utf-8")
exec(compile(_SOURCE, str(_SOURCE_PATH), "exec"), globals(), globals())  # noqa: S102

_OPERATION_KEYS = {*_OPERATION_KEYS, "operation"}


def build_normalized_codegen_contract(
    api,
    raw,
    domains,
):
    """Build normalized metadata with hierarchical access-reference aliases."""
    document = _mapping(raw)
    codegen = _mapping(document.get("x-codegen"))
    resources_raw = _mapping(codegen.get("resources"))
    policy_targets = _compat_policy_targets(domains.access.all)
    resource_targets = {item.id: item for item in api.resources}
    operation_targets = {item.id: item for item in api.operations}
    schema_targets = {item.ref: item for item in api.schemas.all}
    schema_targets.update({item.id: item for item in api.schemas.all})

    hook_definitions = tuple(
        hook
        for resource_name, value in resources_raw.items()
        for hook in _resource_hooks(str(resource_name), _mapping(value))
    )
    hook_targets = {}
    for hook in hook_definitions:
        hook_targets[hook.ref] = hook
        hook_targets.setdefault(hook.id, hook)

    resources = tuple(
        _resource(
            resource,
            _mapping(resources_raw.get(resource.id)),
            api=api,
            policy_targets=policy_targets,
            hooks=tuple(
                item
                for item in hook_definitions
                if item.resource == resource.id
            ),
        )
        for resource in api.resources
    )
    resource_ui = {item.id: item.ui for item in resources}
    operations = tuple(
        _operation(
            operation,
            _operation_raw(document, operation),
            resource_ui=resource_ui.get(operation.resource or ""),
            policy_targets=policy_targets,
            resource_targets=resource_targets,
            operation_targets=operation_targets,
            schema_targets=schema_targets,
            hook_targets=hook_targets,
        )
        for operation in api.operations
    )
    return NormalizedCodegenContract(
        resources=contract_collection(resources),
        operations=contract_collection(operations),
        hooks=contract_collection(hook_definitions),
    )


def _operation(
    operation,
    raw,
    *,
    resource_ui,
    policy_targets,
    resource_targets,
    operation_targets,
    schema_targets,
    hook_targets,
):
    source_path = f"paths.{operation.path}.{operation.method}.x-codegen"
    parameter_raw = _mapping(raw.get("parameters"))
    operation_raw = _mapping(raw.get("operation"))
    name_raw = operation_raw if "name" in operation_raw else raw
    name_source_path = (
        f"{source_path}.operation"
        if "name" in operation_raw
        else source_path
    )
    sources = tuple(
        _data_source(
            str(name),
            _mapping(value),
            owner=operation.id,
            source_path=f"{source_path}.sources.{name}",
            schema_targets=schema_targets,
        )
        for name, value in _named_items(raw.get("sources"))
    )
    runtime = _mapping(raw.get("runtime"))
    return NormalizedOperationMetadata(
        id=operation.id,
        name_value=presence_from_mapping(
            name_raw,
            "name",
            source_path=name_source_path,
        ),
        role=_operation_role(operation, raw, source_path=source_path),
        tags=_string_sequence(raw.get("tags")),
        ui=_ui(
            _mapping(raw.get("ui")),
            source_path=f"{source_path}.ui",
            inherited=resource_ui,
        ),
        parameter_target=_schema_use(
            parameter_raw.get("target", raw.get("target")),
            owner=operation.id,
            source_path=f"{source_path}.parameters.target",
            schema_targets=schema_targets,
        ),
        query_schema=_schema_use(
            raw.get("query"),
            owner=operation.id,
            source_path=f"{source_path}.query",
            schema_targets=schema_targets,
        ),
        params_schema=_schema_use(
            raw.get("params"),
            owner=operation.id,
            source_path=f"{source_path}.params",
            schema_targets=schema_targets,
        ),
        body_schema=_schema_use(
            raw.get("body"),
            owner=operation.id,
            source_path=f"{source_path}.body",
            schema_targets=schema_targets,
        ),
        response_schema=_schema_use(
            raw.get("response"),
            owner=operation.id,
            source_path=f"{source_path}.response",
            schema_targets=schema_targets,
        ),
        sources=contract_collection(sources),
        primary_source=next(
            (item for item in sources if item.primary.value is True),
            sources[0] if sources else None,
        ),
        cache=_cache(
            _mapping(raw.get("cache")),
            owner=operation.id,
            source_path=f"{source_path}.cache",
            operation_targets=operation_targets,
            resource_targets=resource_targets,
        ),
        access=_access_use(
            raw.get("access"),
            owner=operation.id,
            source_path=f"{source_path}.access",
            policy_targets=policy_targets,
        ),
        transport=_transport(_mapping(runtime.get("transport"))),
        hooks=_hook_uses(
            _mapping(runtime.get("hooks", raw.get("hooks"))),
            owner=operation.id,
            source_path=f"{source_path}.runtime.hooks",
            resource=operation.resource,
            hook_targets=hook_targets,
        ),
        notes=structured_notes(raw.get("info", raw.get("notes"))),
        source=source_object(
            raw,
            source_path=source_path,
            known_keys=_OPERATION_KEYS,
        ),
    )


def _operation_role(operation, raw, *, source_path):
    operation_raw = _mapping(raw.get("operation"))
    if "role" in operation_raw:
        return PresenceValue.authored(
            operation_raw["role"],
            source_path=f"{source_path}.operation.role",
        )
    if "role" in raw:
        return PresenceValue.authored(
            raw["role"],
            source_path=f"{source_path}.role",
        )
    if operation.target is not None and operation.target.inferred_roles:
        return PresenceValue.inferred(
            operation.target.inferred_roles[0],
            source_path=f"{source_path}.role",
        )
    inferred = {
        "get": "query",
        "post": "create",
        "put": "update",
        "patch": "update",
        "delete": "delete",
    }.get(str(operation.method), "unknown")
    return PresenceValue.inferred(
        inferred,
        source_path=f"{source_path}.role",
    )


def _access_use(
    value,
    *,
    owner,
    source_path,
    policy_targets,
):
    raw = _mapping(value)
    ref = (
        value
        if isinstance(value, str)
        else raw.get("$ref", raw.get("ref", raw.get("policy")))
    )
    known_keys = {"$ref", "ref", "policy"}
    if not isinstance(ref, str) or not ref:
        return NormalizedAccessUse(
            source=source_object(
                raw,
                source_path=source_path,
                known_keys=known_keys,
            )
        )
    return NormalizedAccessUse(
        ref=ref,
        policy=build_reference(
            ref,
            kind=ReferenceKind.ACCESS,
            owner=owner,
            source_path=source_path,
            targets=policy_targets,
        ),
        source=source_object(
            raw,
            source_path=source_path,
            known_keys=known_keys,
        ),
    )


def _compat_policy_targets(policies):
    targets = {}
    for policy in policies:
        targets[policy.id] = policy
        parts = policy.id.split(".")
        targets[f"#/x-codegen/access/{'/'.join(parts)}"] = policy
        if len(parts) > 1:
            resource, *names = parts
            targets[
                "#/x-codegen/resources/"
                f"{resource}/access/{'/'.join(names)}"
            ] = policy
    return targets


del _SOURCE
del _SOURCE_PATH
