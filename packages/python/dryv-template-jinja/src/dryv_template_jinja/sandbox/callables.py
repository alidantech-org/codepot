from __future__ import annotations

from jinja2.runtime import BlockReference, Macro

from dryv_template_jinja.context import SafeRecord
from dryv_template_jinja.helpers import RegisteredCallable

_TAG_METHODS = frozenset({"has", "has_any", "has_all", "under"})


def is_allowed_callable(value: object) -> bool:
    """Permit template callables, registered helpers, and verified tag queries only."""

    if isinstance(value, (BlockReference, Macro, RegisteredCallable)):
        return True
    owner = getattr(value, "__self__", None)
    name = getattr(value, "__name__", None)
    return (
        isinstance(owner, SafeRecord)
        and owner.is_tag_set
        and isinstance(name, str)
        and name in _TAG_METHODS
    )
