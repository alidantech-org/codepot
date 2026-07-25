from __future__ import annotations

from contracts.normalized import ResolutionState


def test_real_schema_entity_http_access_and_frontend_contracts(
    real_openapi_contract,
) -> None:
    contract = real_openapi_contract
    schemas = contract.meta["normalized_schemas"]
    entities = contract.meta["normalized_entities"]
    domains = contract.meta["normalized_domains"]
    frontends = contract.meta["normalized_frontends"]

    status = schemas.by_id["AppStatus"]
    assert status.types == ("string",)
    assert status.default.value == "active"
    assert tuple(status.enum.value) == ("active", "suspended", "disabled")

    slug = schemas.by_id["SharedSlug"]
    assert slug.min_length.value == 1
    assert slug.max_length.value == 100
    assert slug.pattern.value == "^[a-z0-9]+(?:-[a-z0-9]+)*$"

    query = schemas.by_id["AppListQuery"]
    assert len(query.all_of) == 2
    assert query.all_of[0].ref is not None
    assert query.all_of[0].ref.state == ResolutionState.RESOLVED
    assert query.all_of[0].ref.name == "BaseQuery"
    assert query.all_of[1].inline

    base = entities.base_entities.by_id["SoftDeletableEntity"]
    assert base.is_base
    assert base.is_abstract
    assert base.extends[0].is_resolved
    assert base.extends[0].name == "BaseEntity"

    app = entities.entities.by_id["App"]
    assert app.resource is not None and app.resource.is_resolved
    assert app.resource.target is not None
    assert app.resource.target.id == "apps"
    assert app.schema.ref is not None and app.schema.ref.is_resolved
    assert app.schema.ref.name == "App"
    assert app.store == "apps"
    assert app.extends[0].is_resolved
    assert app.extends[0].name == "SoftDeletableEntity"
    assert "id" in app.inherited_fields.by_id
    assert app.declared_fields.by_id["slug"].unique.value is True
    assert app.declared_fields.by_id["slug"].immutable.value is True
    assert set(app.declared_fields.by_id["slug"].query.operators) >= {
        "exact",
        "prefix",
        "contains",
        "sortable",
    }
    assert set(app.declared_fields.by_id["status"].query.operators) >= {
        "exact",
        "one_of",
        "sortable",
    }

    api_keys = app.relations.by_id["apiKeys"]
    assert api_keys.cardinality == "one_to_many"
    assert api_keys.target is not None and api_keys.target.is_resolved
    assert api_keys.target.name == "AppApiKey"
    assert api_keys.local_fields == ("id",)
    assert api_keys.foreign_fields == ("appId",)
    assert api_keys.is_to_many

    unique_slug = app.constraints.by_id["uniq_app_slug"]
    assert unique_slug.kind == "unique"
    assert unique_slug.fields == ("slug",)

    api_key = entities.entities.by_id["AppApiKey"]
    key_hash = api_key.backend_fields.by_id["keyHash"]
    assert key_hash.is_backend_only
    assert key_hash.schema_use.ref is not None
    assert key_hash.schema_use.ref.is_resolved
    assert key_hash.schema_use.ref.name == "SharedToken"

    assert "global.public" in domains.access.by_id
    assert "global.authenticated" in domains.access.by_id
    assert "users.admin" in domains.access.by_id
    assert "users.superAdmin" in domains.access.by_id

    find_apps = domains.operations.by_id["findApps"]
    assert find_apps.path == "/platform/apps"
    assert find_apps.method == "get"
    assert find_apps.responses.by_id["200"].is_success

    admin = frontends.by_id["admin"]
    assert admin.route_prefix == "/admin"
    assert admin.components.by_id["AppsTable"].props.ref is not None
    assert admin.components.by_id["AppsTable"].props.ref.is_resolved
    assert admin.screens.by_id["AppsListScreen"].full_route == "/admin/apps"
    assert admin.screens.by_id["AppDetailScreen"].full_route == (
        "/admin/apps/:id"
    )
    assert "findApps" in admin.operations.by_id
    assert "getAppById" in admin.operations.by_id

    assert schemas.loss_count == 0
    assert entities.cycle_count == 0
    assert entities.unresolved_count == 0
    assert contract.meta["loss_count"] == 0
