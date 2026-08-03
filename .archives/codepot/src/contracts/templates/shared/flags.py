"""Template-facing boolean flag contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateDependencyFlags:
    """Dependency flags for a template item."""

    has_dependencies: bool = False
    has_missing_dependencies: bool = False
    has_external_dependencies: bool = False


@dataclass(frozen=True)
class TemplateFieldFlags:
    """Template-friendly field flags."""

    is_required: bool = False
    is_optional: bool = False
    is_nullable: bool = False
    is_not_nullable: bool = False

    is_array: bool = False
    is_scalar: bool = False

    is_primitive: bool = False
    is_enum: bool = False
    is_composite: bool = False
    is_model: bool = False
    is_dto: bool = False
    is_relation: bool = False

    is_string: bool = False
    is_number: bool = False
    is_integer: bool = False
    is_boolean: bool = False

    is_email: bool = False
    is_uuid: bool = False
    is_date: bool = False
    is_datetime: bool = False
    is_binary: bool = False

    has_default: bool = False
    has_validation: bool = False
    has_format: bool = False


@dataclass(frozen=True)
class TemplateContentTypeFlags:
    """Template-friendly content type flags."""

    is_json: bool = False
    is_xml: bool = False
    is_yaml: bool = False
    is_html: bool = False
    is_csv: bool = False
    is_multipart: bool = False
    is_form: bool = False
    is_text: bool = False
    is_binary: bool = False
    is_stream: bool = False
    is_structured: bool = False


@dataclass(frozen=True)
class TemplateOperationFlags:
    """Template-friendly operation flags."""

    has_context: bool = False
    has_params: bool = False
    has_query: bool = False
    has_body: bool = False
    has_result: bool = False
    has_errors: bool = False


@dataclass(frozen=True)
class TemplateRouteFlags:
    """Template-friendly route flags."""

    is_get: bool = False
    is_post: bool = False
    is_put: bool = False
    is_patch: bool = False
    is_delete: bool = False
    is_options: bool = False
    is_head: bool = False

    has_params: bool = False
    has_query: bool = False
    has_body: bool = False
    has_responses: bool = False
    has_security: bool = False


@dataclass(frozen=True)
class TemplateResourceFlags:
    """Template-friendly resource flags."""

    has_defaults: bool = False
    has_security: bool = False
    has_operations: bool = False
    has_route_paths: bool = False
    has_routes: bool = False


@dataclass(frozen=True)
class TemplateSchemaFlags:
    """Template-friendly schema flags."""

    is_partial: bool = False
    is_abstract: bool = False
    has_extends: bool = False
    has_fields: bool = False
    has_field_sets: bool = False