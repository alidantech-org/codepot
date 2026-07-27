from __future__ import annotations

from jinja2.runtime import BlockReference, Macro

from codepotg_template_jinja.helpers import RegisteredCallable


def is_allowed_callable(value: object) -> bool:
    """Permit only template-owned callables and explicitly registered host helpers."""

    return isinstance(value, (BlockReference, Macro, RegisteredCallable))
