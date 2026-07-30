from __future__ import annotations

from dryv import DryvRuntime, RuntimePlugins, create_runtime


def test_runtime_snapshot_is_deterministic_without_optional_plugins() -> None:
    runtime = DryvRuntime(plugins=RuntimePlugins())

    snapshot = runtime.snapshot()

    assert snapshot.core_version
    assert snapshot.plugins == ()


def test_create_runtime_uses_the_injected_plugin_graph() -> None:
    plugins = RuntimePlugins()

    runtime = create_runtime(plugins=plugins)

    assert runtime.plugins is plugins
