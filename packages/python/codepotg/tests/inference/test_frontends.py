from __future__ import annotations

import pytest

from core.errors import ConfigError
from emission.templates.resolver import resolve_variable
from inference.frontends import all_template_frontends, template_frontends

X_CODEGEN = {
    "frontends": {
        "admin": {
            "name": "admin",
            "routePrefix": "/admin",
            "info": {"explain": ["Admin frontend."]},
            "components": {
                "AppsTable": {
                    "name": "AppsTable",
                    "props": {"$ref": "#/components/schemas/AdminAppsTableProps"},
                    "schemas": [{"$ref": "#/components/schemas/AppPartial"}],
                    "info": {"ux": ["Support empty state."]},
                }
            },
            "screens": {
                "AppsListScreen": {
                    "name": "AppsListScreen",
                    "route": "/apps",
                    "fullRoute": "/admin/apps",
                    "components": {
                        "table": {"$ref": "#/x-codegen/frontends/admin/components/AppsTable"}
                    },
                    "info": {"implement": ["Render filters above the table."]},
                }
            },
        },
        "customer": {
            "name": "customer",
            "routePrefix": "/customer",
            "components": {},
            "screens": {},
        },
    }
}


def test_frontend_metadata_is_parsed() -> None:
    frontends = all_template_frontends(X_CODEGEN)

    assert len(frontends) == 2
    assert frontends[0].name.raw.o == "admin"
    assert frontends[0].info["explain"] == ("Admin frontend.",)
    assert frontends[0].components[0].props_ref == "#/components/schemas/AdminAppsTableProps"
    assert frontends[0].components[0].info["ux"] == ("Support empty state.",)
    assert frontends[0].screens[0].components["table"]["$ref"] == "#/x-codegen/frontends/admin/components/AppsTable"


def test_named_frontend_selection() -> None:
    selected = template_frontends(X_CODEGEN, selected="admin")

    assert len(selected) == 1
    assert selected[0].name.raw.o == "admin"
    assert selected[0].screens[0].name.raw.o == "AppsListScreen"


def test_wildcard_frontend_selection() -> None:
    selected = template_frontends(X_CODEGEN, selected="*")

    assert [frontend.name.raw.o for frontend in selected] == ["admin", "customer"]


def test_missing_frontend_selection_lists_available_names() -> None:
    with pytest.raises(ConfigError, match="Available frontends: admin, customer"):
        template_frontends(X_CODEGEN, selected="mobile")


def test_selected_frontends_screens_selector_flattens() -> None:
    selected = template_frontends(X_CODEGEN, selected="*")

    screens = resolve_variable({"selected_frontends": selected}, "selected_frontends.screens")

    assert len(screens) == 1
    assert screens[0].name.raw.o == "AppsListScreen"


def test_selected_frontend_components_selector() -> None:
    selected = template_frontends(X_CODEGEN, selected="admin")[0]

    components = resolve_variable({"selected_frontend": selected}, "selected_frontend.components")

    assert len(components) == 1
    assert components[0].name.raw.o == "AppsTable"
