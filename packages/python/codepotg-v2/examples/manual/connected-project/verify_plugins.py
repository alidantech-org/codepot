from __future__ import annotations

from importlib.metadata import entry_points

from codepotg.runtime import RuntimePlugins


def _names(group: str) -> tuple[str, ...]:
    return tuple(sorted(item.name for item in entry_points(group=group)))


def main() -> int:
    source_entries = _names("codepotg.source_adapters")
    target_entries = _names("codepotg.language_adapters")
    engine_entries = _names("codepotg.template_engines")

    print("entry points")
    print(f"  sources: {source_entries}")
    print(f"  targets: {target_entries}")
    print(f"  engines: {engine_entries}")

    plugins = RuntimePlugins.discover()
    source_ids = tuple(item.plugin.id for item in plugins.source_adapters)
    target_ids = tuple(item.plugin.id for item in plugins.target_adapters)
    engine_ids = tuple(item.plugin.id for item in plugins.template_engines)

    print("loaded plugins")
    print(f"  sources: {source_ids}")
    print(f"  targets: {target_ids}")
    print(f"  engines: {engine_ids}")

    required = {
        "ir source": "ir" in source_ids,
        "OpenAPI source": "openapi" in source_ids,
        "TypeScript target": "typescript" in target_ids,
        "Dart target": "dart" in target_ids,
        "Jinja engine": "jinja" in engine_ids,
    }
    missing = tuple(name for name, present in required.items() if not present)
    if missing:
        raise SystemExit(f"missing required manual-test plugins: {missing}")

    all_ids = (*source_ids, *target_ids, *engine_ids)
    duplicates = tuple(sorted({identifier for identifier in all_ids if all_ids.count(identifier) > 1}))
    if duplicates:
        raise SystemExit(f"duplicate loaded plugin IDs: {duplicates}")

    print("plugin graph is ready for IR, Python authoring, OpenAPI, TypeScript, and Dart tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
