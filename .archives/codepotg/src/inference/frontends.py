"""Map x-codegen frontend metadata into template contracts."""

from __future__ import annotations

from typing import Any

from archives.codepotg.src.contracts.names import make_contract_name
from archives.codepotg.src.contracts.template import (
    TemplateFrontend,
    TemplateFrontendComponent,
    TemplateFrontendOperationUse,
    TemplateFrontendScreen,
)
from archives.codepotg.src.core.errors import ConfigError


def template_frontends(x_codegen: dict[str, Any], *, selected: str | None = None) -> tuple[TemplateFrontend, ...]:
    raw_frontends = x_codegen.get("frontends")
    if not isinstance(raw_frontends, dict):
        if selected:
            raise ConfigError(f"Frontend '{selected}' was requested, but the OpenAPI document defines no frontends.")
        return ()

    frontends = tuple(_frontend(str(key), value) for key, value in raw_frontends.items() if isinstance(value, dict))

    if selected is None:
        return ()

    if selected == "*":
        return frontends

    for frontend in frontends:
        if frontend.name.raw.o == selected:
            return (frontend,)

    available = ", ".join(frontend.name.raw.o for frontend in frontends) or "(none)"
    raise ConfigError(f"Unknown frontend '{selected}'. Available frontends: {available}")


def all_template_frontends(x_codegen: dict[str, Any]) -> tuple[TemplateFrontend, ...]:
    raw_frontends = x_codegen.get("frontends")
    if not isinstance(raw_frontends, dict):
        return ()
    return tuple(_frontend(str(key), value) for key, value in raw_frontends.items() if isinstance(value, dict))


def _frontend(key: str, raw: dict[str, Any]) -> TemplateFrontend:
    name = str(raw.get("name") or key)
    components = tuple(_component(name, component_name, value) for component_name, value in _dict(raw.get("components")).items())
    screens = tuple(_screen(name, screen_name, value) for screen_name, value in _dict(raw.get("screens")).items())
    operations = _unique_uses(*(component.uses for component in components), *(screen.uses for screen in screens))
    schemas = tuple(dict.fromkeys([schema for component in components for schema in component.schemas]))

    frontend = TemplateFrontend(
        name=make_contract_name(name),
        title=str(raw.get("title") or name),
        route_prefix=str(raw.get("routePrefix") or ""),
        folders=_strings(raw.get("folders")),
        tags=_strings(raw.get("tags")),
        description=str(raw.get("description") or "-"),
        info=_info(raw.get("info")),
        components=components,
        screens=screens,
        operations=operations,
        schemas=schemas,
        meta={"raw": raw},
    )

    components = tuple(_with_component_frontend(component, frontend) for component in components)
    screens = tuple(_with_screen_frontend(screen, frontend) for screen in screens)

    return TemplateFrontend(
        name=frontend.name,
        title=frontend.title,
        route_prefix=frontend.route_prefix,
        folders=frontend.folders,
        tags=frontend.tags,
        description=frontend.description,
        info=frontend.info,
        components=components,
        screens=screens,
        operations=frontend.operations,
        schemas=frontend.schemas,
        meta=frontend.meta,
    )


def _component(frontend_name: str, key: str, raw_value: Any) -> TemplateFrontendComponent:
    raw = raw_value if isinstance(raw_value, dict) else {}
    return TemplateFrontendComponent(
        name=make_contract_name(str(raw.get("name") or key)),
        title=str(raw.get("title") or raw.get("name") or key),
        description=str(raw.get("description") or "-"),
        props_ref=_ref(raw.get("props")),
        uses=_uses(raw.get("uses")),
        schemas=tuple(_ref(item) for item in _list(raw.get("schemas")) if _ref(item)),
        tags=_strings(raw.get("tags")),
        info=_info(raw.get("info")),
        meta={"raw": raw, "frontend_name": frontend_name},
    )


def _screen(frontend_name: str, key: str, raw_value: Any) -> TemplateFrontendScreen:
    raw = raw_value if isinstance(raw_value, dict) else {}
    return TemplateFrontendScreen(
        name=make_contract_name(str(raw.get("name") or key)),
        title=str(raw.get("title") or raw.get("name") or key),
        description=str(raw.get("description") or "-"),
        route=str(raw.get("route") or "-"),
        full_route=str(raw.get("fullRoute") or raw.get("route") or "-"),
        params_ref=_ref(raw.get("params")),
        query_ref=_ref(raw.get("query")),
        components=_dict(raw.get("components")),
        uses=_uses(raw.get("uses")),
        tags=_strings(raw.get("tags")),
        info=_info(raw.get("info")),
        meta={"raw": raw, "frontend_name": frontend_name},
    )


def _with_component_frontend(component: TemplateFrontendComponent, frontend: TemplateFrontend) -> TemplateFrontendComponent:
    return TemplateFrontendComponent(**{**component.__dict__, "frontend": frontend})


def _with_screen_frontend(screen: TemplateFrontendScreen, frontend: TemplateFrontend) -> TemplateFrontendScreen:
    return TemplateFrontendScreen(**{**screen.__dict__, "frontend": frontend})


def _uses(raw_value: Any) -> tuple[TemplateFrontendOperationUse, ...]:
    return tuple(
        TemplateFrontendOperationUse(
            alias=str(alias),
            operation_id=str(raw.get("operationId") or "-"),
            method=str(raw.get("method") or "-"),
            path=str(raw.get("path") or "-"),
            meta={"raw": raw},
        )
        for alias, raw in _dict(raw_value).items()
        if isinstance(raw, dict)
    )


def _unique_uses(*groups: tuple[TemplateFrontendOperationUse, ...]) -> tuple[TemplateFrontendOperationUse, ...]:
    seen: set[str] = set()
    result: list[TemplateFrontendOperationUse] = []
    for group in groups:
        for use in group:
            key = use.operation_id
            if key in seen:
                continue
            seen.add(key)
            result.append(use)
    return tuple(result)


def _info(value: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): tuple(str(item) for item in items)
        for key, items in value.items()
        if isinstance(items, list | tuple)
    }


def _ref(value: Any) -> str | None:
    if isinstance(value, dict) and value.get("$ref"):
        return str(value["$ref"])
    return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in value) if isinstance(value, list | tuple) else ()
