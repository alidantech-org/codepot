from __future__ import annotations

from .contracts import FrozenObject, FrozenValue, PackConfigurationError, PackManifest, ResolvedPack


def resolve_pack(
    manifest: PackManifest,
    *,
    options: FrozenObject,
    bindings: FrozenObject,
    manifest_resource_id: str,
    manifest_hash: str,
) -> ResolvedPack:
    option_defs = {item.name: item for item in manifest.options}
    provided_options = dict(options)
    unknown_options = sorted(set(provided_options) - set(option_defs))
    if unknown_options:
        raise PackConfigurationError("PACK_UNKNOWN_OPTION", f"unknown pack option {unknown_options[0]!r}")
    resolved_options: list[tuple[str, FrozenValue]] = []
    for name in sorted(option_defs):
        definition = option_defs[name]
        supplied = name in provided_options
        value = provided_options.get(name, definition.default)
        if definition.required and not supplied and definition.default is None:
            raise PackConfigurationError("PACK_REQUIRED_OPTION", f"required pack option {name!r} is missing")
        if definition.choices and value not in definition.choices:
            raise PackConfigurationError("PACK_OPTION_CHOICE", f"pack option {name!r} is not an allowed value")
        resolved_options.append((name, value))

    binding_defs = {item.name: item for item in manifest.bindings}
    provided_bindings = dict(bindings)
    unknown_bindings = sorted(set(provided_bindings) - set(binding_defs))
    if unknown_bindings:
        raise PackConfigurationError("PACK_UNKNOWN_BINDING", f"unknown pack binding {unknown_bindings[0]!r}")
    missing_bindings = sorted(
        name for name, definition in binding_defs.items() if definition.required and name not in provided_bindings
    )
    if missing_bindings:
        raise PackConfigurationError("PACK_REQUIRED_BINDING", f"required pack binding {missing_bindings[0]!r} is missing")

    selection_keys = {item.key for item in manifest.selections}
    binding_keys = set(binding_defs)
    for selection in manifest.selections:
        missing = sorted(set(selection.bindings) - binding_keys)
        if missing:
            raise PackConfigurationError("PACK_MISSING_BINDING", f"selection {selection.key!r} references unknown binding {missing[0]!r}")

    template_keys = {item.key for item in manifest.templates}
    for template in manifest.templates:
        if template.selection not in selection_keys:
            raise PackConfigurationError("PACK_MISSING_SELECTION", f"template {template.key!r} references unknown selection {template.selection!r}")
        missing = sorted(set(template.depends_on) - template_keys)
        if missing:
            raise PackConfigurationError("PACK_MISSING_TEMPLATE", f"template {template.key!r} depends on unknown template {missing[0]!r}")
        if template.key in template.depends_on:
            raise PackConfigurationError("PACK_TEMPLATE_CYCLE", f"template {template.key!r} cannot depend on itself")

    _validate_template_cycles(manifest)
    return ResolvedPack(manifest, tuple(resolved_options), tuple(sorted(provided_bindings.items())), manifest_resource_id, manifest_hash)


def _validate_template_cycles(manifest: PackManifest) -> None:
    graph = {item.key: item.depends_on for item in manifest.templates}
    active: list[str] = []
    done: set[str] = set()

    def visit(key: str) -> None:
        if key in done:
            return
        if key in active:
            cycle = " -> ".join((*active[active.index(key):], key))
            raise PackConfigurationError("PACK_TEMPLATE_CYCLE", f"template dependency cycle: {cycle}")
        active.append(key)
        try:
            for dependency in graph[key]:
                visit(dependency)
        finally:
            active.pop()
        done.add(key)

    for key in sorted(graph):
        visit(key)


__all__ = ["resolve_pack"]
