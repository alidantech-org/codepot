from __future__ import annotations

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

from codepotg_template_jinja.context import SafeRecord
from codepotg_template_jinja.helpers import HelperRegistry
from codepotg_template_jinja.rules import JinjaEngineRules

from .attributes import is_allowed_attribute
from .callables import is_allowed_callable


class StrictSandboxedEnvironment(SandboxedEnvironment):
    def is_safe_attribute(self, obj: object, attr: str, value: object) -> bool:
        return is_allowed_attribute(obj, attr, value)

    def is_safe_callable(self, obj: object) -> bool:
        return is_allowed_callable(obj)

    def getattr(self, obj: object, attribute: str) -> object:
        if isinstance(obj, SafeRecord):
            if attribute.startswith("_"):
                return self.unsafe_undefined(obj, attribute)
            try:
                return obj[attribute]
            except KeyError:
                return self.undefined(obj=obj, name=attribute)
        return super().getattr(obj, attribute)


def create_environment(
    *,
    loader: object,
    rules: JinjaEngineRules,
    helpers: HelperRegistry,
    cache_size: int,
) -> StrictSandboxedEnvironment:
    environment = StrictSandboxedEnvironment(
        loader=loader,
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=rules.trim_blocks,
        lstrip_blocks=rules.lstrip_blocks,
        keep_trailing_newline=rules.keep_trailing_newline,
        newline_sequence=rules.newline_sequence,
        cache_size=cache_size,
        enable_async=False,
    )
    environment.filters.clear()
    environment.tests.clear()
    environment.globals.clear()
    environment.filters.update(helpers.filters())
    environment.tests.update(helpers.tests())
    environment.globals.update(helpers.globals())
    return environment
