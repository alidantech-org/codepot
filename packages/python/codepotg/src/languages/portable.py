"""Shared foundation for production language adapters.

Inference remains language-neutral. Adapters reuse the complete typed contract and
attach deterministic target-language type, package, naming, and layout conventions.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any

from contracts.api import ApiContract, ApiEntityField, ApiField
from contracts.emission import EmissionResult
from contracts.events import ProgressSink, RuntimeEvent
from contracts.language import LanguagePostResult
from contracts.names import make_contract_name
from contracts.template import (
    TemplateContract,
    TemplateDocs,
    TemplateEntity,
    TemplateEntityField,
    TemplateFeatures,
    TemplateField,
    TemplateFramework,
    TemplateLanguage,
    TemplateOperation,
    TemplatePackage,
    TemplateProjectEmit,
    TemplateProjectLang,
    TemplateResource,
    TemplateSchema,
    TemplateSchemaGroups,
)
from languages.debug.adapter import DebugLanguageAdapter
from languages.portable_types import PortableTypeSystem, type_system_for


@dataclass(frozen=True)
class PortableLanguageProfile:
    """Complete target metadata for one production language adapter."""

    name: str
    format: str
    purpose: str
    framework: str = "standard-library"
    package_suffix: str = "client"
    diagnostics: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    package_dependencies: tuple[str, ...] = ()
    package_dev_dependencies: tuple[str, ...] = ()
    type_system: PortableTypeSystem | None = None

    @property
    def resolved_type_system(self) -> PortableTypeSystem:
        """Return the explicit or registered type system for this target."""

        return self.type_system or type_system_for(self.name)


def build_portable_template_contract(
    profile: PortableLanguageProfile,
    *,
    api: ApiContract,
    output_path: Path,
    template_root: Path | None = None,
    dry_run: bool = False,
    frontend: str | None = None,
    progress: ProgressSink | None = None,
) -> TemplateContract:
    """Build a complete typed target contract without re-parsing source dictionaries."""

    _notify(
        progress,
        f"building_{profile.name.replace('-', '_')}_contract",
        f"Building {profile.name} template contract",
    )
    base = DebugLanguageAdapter().build_template_contract(
        api=api,
        output_path=output_path,
        template_root=template_root,
        dry_run=dry_run,
        frontend=frontend,
        progress=None,
    )
    title = api.info.title.strip() if api.info.title else ""
    project_name = make_contract_name(title or f"{profile.name} API")
    description = api.info.description.strip()
    if description == "-":
        description = ""

    type_system = profile.resolved_type_system
    schemas = _target_schema_groups(base.schemas, type_system)
    schema_names = {item.api.ref: item.lang.symbol_name for item in schemas.all}
    operations = tuple(
        _target_operation(item, type_system, schema_names) for item in base.operations
    )
    entities = tuple(
        _target_entity(item, type_system, schema_names) for item in base.entities
    )
    resources = tuple(
        _target_resource(
            item,
            schemas=schemas,
            operations=operations,
            entities=entities,
            type_system=type_system,
        )
        for item in base.resources
    )

    package_name = f"{project_name.snake.o}_{profile.package_suffix}"
    server_urls = tuple(server.url for server in api.servers if server.url)
    common_meta = {
        "api_version": api.info.api_version,
        "openapi_version": api.info.openapi_version,
        "server_urls": server_urls,
        "adapter_family": "production-portable",
        "complete_variable_contract": True,
        "type_system": type_system,
        "scalar_types": type_system.scalar_types,
        "format_types": type_system.format_types,
        "file_extension": type_system.file_extension,
        "package_file": type_system.package_file,
        "source_root": type_system.source_root,
    }

    project = replace(
        base.project,
        name=project_name,
        description=description,
        lang=TemplateProjectLang(name=profile.name, purpose=profile.purpose),
        emit=TemplateProjectEmit(format=profile.format, root_path=output_path),
        docs=TemplateDocs(
            summary=f"Generated {profile.name} API package",
            description=description,
        ),
        meta=common_meta,
    )
    language = TemplateLanguage(
        name=profile.name,
        framework=TemplateFramework(
            name=profile.framework,
            meta={
                "source_root": type_system.source_root,
                "file_extension": type_system.file_extension,
            },
        ),
        package=TemplatePackage(
            name=package_name,
            version="0.1.0",
            dependencies=profile.package_dependencies,
            dev_dependencies=profile.package_dev_dependencies,
            meta={"manifest": type_system.package_file},
        ),
        features=TemplateFeatures(
            text_reports=True,
            schema_groups=True,
            field_reports=True,
            dependency_reports=True,
            file_context_reports=True,
        ),
        meta=common_meta,
    )
    return replace(
        base,
        project=project,
        lang=language,
        resources=resources,
        schemas=schemas,
        operations=operations,
        entities=entities,
        emit=replace(
            base.emit,
            output_path=output_path,
            template_root=template_root,
            dry_run=dry_run,
        ),
        meta=replace(base.meta, debug=False),
    )


def portable_after_emit(
    profile: PortableLanguageProfile,
    *,
    result: EmissionResult,
    progress: ProgressSink | None = None,
) -> LanguagePostResult:
    """Return target-specific hints without executing external tools."""

    _notify(
        progress,
        f"{profile.name.replace('-', '_')}_post_actions",
        f"{profile.name} post-actions are informational",
    )
    return LanguagePostResult(diagnostics=profile.diagnostics)


def _target_schema_groups(
    groups: TemplateSchemaGroups,
    type_system: PortableTypeSystem,
) -> TemplateSchemaGroups:
    converted = {
        item.api.ref: _target_schema(item, type_system)
        for item in groups.all
    }
    values: dict[str, tuple[TemplateSchema, ...]] = {}
    for definition in fields(TemplateSchemaGroups):
        group = getattr(groups, definition.name)
        values[definition.name] = tuple(converted[item.api.ref] for item in group)
    return TemplateSchemaGroups(**values)


def _target_schema(
    schema: TemplateSchema,
    type_system: PortableTypeSystem,
) -> TemplateSchema:
    symbol = schema.name.pascal.o
    fields_value = tuple(
        _target_field(field, type_system, schema_names=None) for field in schema.fields
    )
    if schema.api.kind.value == "primitive":
        target_type = type_system.resolve(
            schema.api.primitive_type,
            format=schema.api.primitive_format,
            nullable=schema.api.nullable,
        )
    elif schema.api.kind.value == "enum":
        target_type = symbol
    else:
        target_type = symbol
    return replace(
        schema,
        fields=fields_value,
        lang=replace(
            schema.lang,
            kind=f"{type_system.language}_{schema.api.kind.value}",
            type=target_type,
            display_name=symbol,
            symbol_name=symbol,
        ),
        emit=(
            replace(
                schema.emit,
                file_name=type_system.model_filename(schema.name),
            )
            if schema.emit is not None
            else None
        ),
    )


def _target_field(
    field: TemplateField,
    type_system: PortableTypeSystem,
    schema_names: dict[str, str] | None,
) -> TemplateField:
    return replace(
        field,
        lang=replace(
            field.lang,
            kind=f"{type_system.language}_field",
            type=_api_field_type(
                field.api,
                type_system,
                schema_names=schema_names,
            ),
            display_name=_field_name(field.name, type_system.language),
            json_key=field.api.id,
        ),
    )


def _target_entity(
    entity: TemplateEntity,
    type_system: PortableTypeSystem,
    schema_names: dict[str, str],
) -> TemplateEntity:
    return replace(
        entity,
        fields=tuple(
            _target_entity_field(item, type_system, schema_names) for item in entity.fields
        ),
        backend_fields=tuple(
            _target_entity_field(item, type_system, schema_names)
            for item in entity.backend_fields
        ),
        meta=replace(
            entity.meta,
            class_name=entity.name.pascal.o,
            file_name=type_system.model_filename(entity.name),
        ),
    )


def _target_entity_field(
    field: TemplateEntityField,
    type_system: PortableTypeSystem,
    schema_names: dict[str, str],
) -> TemplateEntityField:
    return replace(
        field,
        lang=replace(
            field.lang,
            kind=f"{type_system.language}_entity_field",
            type=_api_field_type(
                field.api,
                type_system,
                schema_names=schema_names,
            ),
            display_name=_field_name(field.name, type_system.language),
            json_key=field.api.id,
        ),
    )


def _target_operation(
    operation: TemplateOperation,
    type_system: PortableTypeSystem,
    schema_names: dict[str, str],
) -> TemplateOperation:
    return replace(
        operation,
        lang=replace(
            operation.lang,
            kind=f"{type_system.language}_operation",
            function_name=_function_name(operation.name, type_system.language),
            display_name=operation.name.pascal.o,
            endpoint_path=operation.api.path,
        ),
        parameters=tuple(
            replace(
                item,
                lang=replace(
                    item.lang,
                    kind=f"{type_system.language}_parameter",
                    display_name=_field_name(item.name, type_system.language),
                ),
            )
            for item in operation.parameters
        ),
        meta=replace(
            operation.meta,
            query_type=_target_ref(operation.meta.query_ref, schema_names),
            params_type=_target_ref(operation.meta.params_ref, schema_names),
            body_type=_target_ref(operation.meta.body_ref, schema_names),
            response_type=_target_ref(operation.meta.response_ref, schema_names),
        ),
    )


def _target_resource(
    resource: TemplateResource,
    *,
    schemas: TemplateSchemaGroups,
    operations: tuple[TemplateOperation, ...],
    entities: tuple[TemplateEntity, ...],
    type_system: PortableTypeSystem,
) -> TemplateResource:
    operation_by_id = {item.api.id: item for item in operations}
    schema_by_ref = {item.api.ref: item for item in schemas.all}
    entity_by_id = {item.api.id: item for item in entities}
    return replace(
        resource,
        operations=tuple(operation_by_id[item.api.id] for item in resource.operations),
        models=tuple(schema_by_ref[item.api.ref] for item in resource.models),
        dtos=tuple(schema_by_ref[item.api.ref] for item in resource.dtos),
        enums=tuple(schema_by_ref[item.api.ref] for item in resource.enums),
        schemas=tuple(schema_by_ref[item.api.ref] for item in resource.schemas),
        entities=tuple(entity_by_id.get(item.api.id, item) for item in resource.entities),
        lang=replace(
            resource.lang,
            kind=f"{type_system.language}_resource",
            display_name=resource.name.pascal.o,
        ),
    )


def _api_field_type(
    field: ApiField | ApiEntityField,
    type_system: PortableTypeSystem,
    *,
    schema_names: dict[str, str] | None,
) -> str:
    if field.schema_ref and schema_names and field.schema_ref in schema_names:
        value = schema_names[field.schema_ref]
    elif field.type.raw_type == "array" or field.type.kind.value == "array":
        item = _target_ref(field.item_ref, schema_names) if isinstance(field, ApiField) else None
        if item is None:
            item = type_system.resolve(
                field.type.item_type,
                format=field.type.item_format,
            )
        value = type_system.resolve("array", item_type=item)
    else:
        value = type_system.resolve(
            field.type.type or field.type.raw_type,
            format=field.type.resolved_format or field.type.format,
        )
    if field.nullable or not field.required:
        return type_system.nullable_template.format(value=value)
    return value


def _target_ref(ref: str | None, schema_names: dict[str, str] | None) -> str | None:
    if ref is None or schema_names is None:
        return None
    return schema_names.get(ref)


def _field_name(name: Any, language: str) -> str:
    if language in {"java", "csharp"}:
        return name.camel.o
    return name.snake.o


def _function_name(name: Any, language: str) -> str:
    if language in {"java", "csharp"}:
        return name.camel.o
    return name.snake.o


def _notify(progress: ProgressSink | None, stage: str, message: str) -> None:
    if progress is not None:
        progress(RuntimeEvent(stage=stage, message=message))
