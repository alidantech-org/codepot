from __future__ import annotations

from dryv_template_jinja import JinjaEngineRules
from dryv_template_jinja.helpers import HelperRegistry
from dryv_template_jinja.sandbox import create_environment
from dryv_template_jinja.templates import ImmutableRegistryLoader


def test_environment_is_sandboxed_strict_and_has_no_default_globals() -> None:
    environment = create_environment(
        loader=ImmutableRegistryLoader({"root.jinja": "ok"}),
        rules=JinjaEngineRules(),
        helpers=HelperRegistry.create(),
        cache_size=0,
    )
    assert type(environment).__name__ == "StrictSandboxedEnvironment"
    assert environment.autoescape is False
    assert environment.globals == {}
    assert "attr" not in environment.filters
    assert "map" not in environment.filters
    assert "cycler" not in environment.globals
    assert "namespace" not in environment.globals
    assert "lipsum" not in environment.globals
