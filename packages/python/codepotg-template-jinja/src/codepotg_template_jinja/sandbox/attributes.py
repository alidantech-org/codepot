from __future__ import annotations

from jinja2.environment import TemplateModule
from jinja2.runtime import LoopContext, Macro

from codepotg_template_jinja.context import SafeRecord

_SAFE_JINJA_RUNTIME_TYPES = (LoopContext,)


def is_allowed_attribute(value: object, attribute: str, resolved: object) -> bool:
    if not attribute or attribute.startswith("_"):
        return False
    if isinstance(value, SafeRecord):
        return attribute in value or value.is_allowed_tag_attribute(attribute)
    if isinstance(value, TemplateModule):
        return isinstance(resolved, Macro)
    return isinstance(value, _SAFE_JINJA_RUNTIME_TYPES)
