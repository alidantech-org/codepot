"""Jinja template renderer for emission."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from contracts.emission import TemplateContext
from contracts.normalized_document_contract import build_normalized_document_contract

_NORMALIZED_ROOTS = {
    "normalized": "normalized",
    "domains": "normalized_domains",
    "schema_contract": "normalized_schemas",
    "codegen_contract": "normalized_codegen",
    "entity_contract": "normalized_entities",
    "frontend_contract": "normalized_frontends",
}


def create_environment(template_root: Path) -> Environment:
    """Create a strict Jinja environment for one generation run."""
    resolved_root = resolve_renderer_template_root(template_root)
    environment = Environment(
        loader=FileSystemLoader(str(resolved_root)),
        undefined=StrictUndefined,
        autoescape=select_autoescape(default=False),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        cache_size=2_048,
        # Environments are cleared after every generation. Avoid one source mtime
        # stat per rendered output while still picking up edits on the next run.
        auto_reload=False,
    )

    environment.filters["dash"] = dash
    environment.filters["yesno"] = yesno
    environment.filters["csv"] = csv
    environment.filters["value"] = value
    environment.filters["info_comment"] = info_comment

    return environment


def cached_environment(template_root: Path) -> Environment:
    """Return one reusable environment per resolved template root."""
    resolved_root = resolve_renderer_template_root(template_root)
    return _cached_environment(str(resolved_root))


@lru_cache(maxsize=32)
def _cached_environment(resolved_root: str) -> Environment:
    return create_environment(Path(resolved_root))


def clear_environment_cache() -> None:
    """Release cached environments, compiled templates, and loader state."""
    _cached_environment.cache_clear()


def resolve_renderer_template_root(template_root: Path) -> Path:
    """Resolve a renderer root without hiding invalid custom paths.

    Historical source-checkout callers used ``<project>/templates/<language>``.
    Built-in packs now live under ``src/codepotg/templates`` so they are included
    in wheels. Only that exact missing legacy shape falls back to the bundled
    pack; every other missing custom path raises a clear error.
    """
    root = template_root.expanduser().resolve()
    if root.is_dir():
        return root

    if root.parent.name == "templates":
        bundled = Path(__file__).resolve().parents[2] / "codepotg" / "templates" / root.name
        if bundled.is_dir():
            return bundled

    raise FileNotFoundError(f"Template directory does not exist: {root}")


def render_template(
    template_root: Path,
    relative_path: Path,
    context: TemplateContext,
) -> str:
    """Render a template by relative path using the shared compiled cache."""
    environment = cached_environment(template_root)
    template = environment.get_template(relative_path.as_posix())
    return template.render(**_with_normalized_roots(context))


def _with_normalized_roots(context: TemplateContext) -> TemplateContext:
    """Add stable normalized roots to compatibility render contexts.

    Direct eager and queued legacy contexts include the compatibility ``api`` root.
    Bounded graph contexts intentionally omit it from their public render mapping, so
    this helper cannot leak the full document or hidden selection collections into
    graph templates.
    """

    api = context.get("api")
    if api is None:
        return context

    rendered = dict(context)
    api_meta = getattr(api, "meta", {})
    meta: Mapping[str, Any] = api_meta if isinstance(api_meta, Mapping) else {}

    document = meta.get("normalized_document")
    if document is None:
        document = build_normalized_document_contract(getattr(api, "raw", {}))
    rendered.setdefault("document_contract", document)

    for public_name, meta_name in _NORMALIZED_ROOTS.items():
        value = meta.get(meta_name)
        if value is not None:
            rendered.setdefault(public_name, value)

    return rendered


def value(item: Any, default: str = "-") -> str:
    """Render a safe display value."""
    if item is None:
        return default

    if isinstance(item, Enum):
        return str(item.value)

    if isinstance(item, Path):
        return item.as_posix()

    if isinstance(item, bool):
        return "true" if item else "false"

    text = str(item)
    return text if text else default


def dash(item: Any) -> str:
    """Render a dash for empty values."""
    return value(item, "-")


def yesno(item: Any) -> str:
    """Render a boolean as yes/no."""
    return "yes" if bool(item) else "no"


def csv(items: Any, default: str = "-") -> str:
    """Render an iterable as comma-separated text."""
    if items is None:
        return default

    if isinstance(items, str):
        return items or default

    if not isinstance(items, Iterable):
        return value(items, default)

    values = [value(item, "") for item in items]
    values = [item for item in values if item]
    if not values:
        return default

    return ", ".join(values)


def info_comment(info: Any, prefix: str = " * ") -> str:
    """Render normalized info metadata as comment body lines."""
    if not isinstance(info, dict):
        return ""

    lines: list[str] = []
    for category, items in info.items():
        if not isinstance(items, Iterable) or isinstance(items, str):
            continue
        values = [str(item) for item in items if str(item)]
        if not values:
            continue
        lines.append(f"{prefix}{_info_title(str(category))}:")
        lines.extend(f"{prefix}- {item}" for item in values)
        lines.append(prefix.rstrip())

    while lines and not lines[-1].strip("* "):
        lines.pop()

    return "\n".join(lines)


def _info_title(category: str) -> str:
    return category.replace("_", " ").replace("-", " ").title()
