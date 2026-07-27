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

    if "openapi" in source_entries:
        raise SystemExit(
            "codepotg-openapi is installed, but its source-adapter facade is currently incomplete; "
            "use a clean manual-test environment without it"
        )

    plugins = RuntimePlugins.discover()
    source_ids = tuple(item.plugin.id for item in plugins.source_adapters)
    target_ids = tuple(item.plugin.id for item in plugins.target_adapters)
    engine_ids = tuple(item.plugin.id for item in plugins.template_engines)

    print("loaded plugins")
    print(f"  sources: {source_ids}")
    print(f"  targets: {target_ids}")
    print(f"  engines: {engine_ids}")

    required = {
        "source": "ir" in source_ids,
        "typescript": "typescript" in target_ids,
        "dart": "dart" in target_ids,
        "jinja": "jinja" in engine_ids,
    }
    missing = tuple(name for name, present in required.items() if not present)
    if missing:
        raise SystemExit(f"missing required manual-test plugins: {missing}")

    print("plugin graph is ready for the connected manual project")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
