"""Dart language adapter."""

from __future__ import annotations

from archives.codepot.src.contracts.language.context import (
    LanguageField,
    LanguageItem,
    LanguageOperation,
    LanguageRoute,
)
from archives.codepot.src.contracts.language.interface import (
    LanguageExportRequest,
    LanguageFieldRequest,
    LanguageImportRequest,
    LanguageItemRequest,
    LanguageOperationRequest,
    LanguageRouteRequest,
    LanguageRuntimeRequest,
    LanguageTypeRequest,
)
from archives.codepot.src.contracts.language.runtime import (
    LanguageImportRules,
    LanguageImportStrategy,
    LanguageNamingRules,
    LanguageRuntime,
)
from archives.codepot.src.contracts.spec.names import resolve_name_case
from archives.codepot.src.languages.dart.constants import DART_LANGUAGE_KEY
from archives.codepot.src.languages.dart.exports import create_dart_exports
from archives.codepot.src.languages.dart.imports import create_dart_imports
from archives.codepot.src.languages.dart.names import make_dart_name
from archives.codepot.src.languages.dart.types import make_dart_type

DEFAULT_DART_EXTENSIONS = ("dart",)


class DartLanguageAdapter:
    """Dart implementation of the Codepotx language adapter contract."""

    key = DART_LANGUAGE_KEY

    def create_runtime(self, request: LanguageRuntimeRequest) -> LanguageRuntime:
        """Create Dart runtime context."""

        naming = request.naming
        imports = request.imports
        extensions = request.extensions or DEFAULT_DART_EXTENSIONS

        return LanguageRuntime(
            name=request.language,
            extensions=extensions,
            package_name=request.package_name,
            package_manager=request.package_manager,
            source_root=request.source_root,
            naming=LanguageNamingRules(
                class_case=naming.class_name,
                interface_case=naming.interface,
                enum_case=naming.enum,
                enum_value_case=naming.enum_value,
                field_case=naming.field,
                method_case=naming.method,
                function_case=naming.function,
                constant_case=naming.constant,
                variable_case=naming.variable,
                file_case=naming.file,
                folder_case=naming.folder,
                module_case=naming.module,
                package_case=naming.package,
            ),
            imports=LanguageImportRules(
                strategy=LanguageImportStrategy(imports.strategy),
                root=imports.root,
                alias=imports.alias,
                package=imports.package,
                include_extension=imports.extension,
                type_only=imports.type_only,
            ),
        )

    def enrich_item(self, request: LanguageItemRequest) -> LanguageItem:
        """Create generic Dart item `.lang` context."""

        runtime = request.runtime
        record = request.record

        lang_name = make_dart_name(
            record.name,
            class_name=resolve_name_case(record.name, runtime.naming.class_case),
            interface_name=resolve_name_case(
                record.name,
                runtime.naming.interface_case,
            ),
            enum_name=resolve_name_case(record.name, runtime.naming.enum_case),
            enum_value_name=resolve_name_case(
                record.name,
                runtime.naming.enum_value_case,
            ),
            field_name=resolve_name_case(record.name, runtime.naming.field_case),
            method_name=resolve_name_case(record.name, runtime.naming.method_case),
            function_name=resolve_name_case(
                record.name,
                runtime.naming.function_case,
            ),
            constant_name=resolve_name_case(
                record.name,
                runtime.naming.constant_case,
            ),
            file_name=resolve_name_case(record.name, runtime.naming.file_case),
            module_name=resolve_name_case(record.name, runtime.naming.module_case),
            package_name=resolve_name_case(
                record.name,
                runtime.naming.package_case,
            ),
        )

        return LanguageItem(name=lang_name)

    def enrich_field(self, request: LanguageFieldRequest) -> LanguageField:
        """Create Dart field `.lang` context."""

        runtime = request.runtime
        flags = request.flags

        lang_name = make_dart_name(
            request.name,
            class_name=resolve_name_case(request.name, runtime.naming.class_case),
            interface_name=resolve_name_case(
                request.name,
                runtime.naming.interface_case,
            ),
            enum_name=resolve_name_case(request.name, runtime.naming.enum_case),
            enum_value_name=resolve_name_case(
                request.name,
                runtime.naming.enum_value_case,
            ),
            field_name=resolve_name_case(request.name, runtime.naming.field_case),
            method_name=resolve_name_case(request.name, runtime.naming.method_case),
            function_name=resolve_name_case(
                request.name,
                runtime.naming.function_case,
            ),
            constant_name=resolve_name_case(
                request.name,
                runtime.naming.constant_case,
            ),
            file_name=resolve_name_case(request.name, runtime.naming.file_case),
            module_name=resolve_name_case(request.name, runtime.naming.module_case),
            package_name=resolve_name_case(
                request.name,
                runtime.naming.package_case,
            ),
        )

        lang_type = self.create_type(
            LanguageTypeRequest(
                facts=request.type_facts,
                is_required=flags.is_required,
                is_nullable=flags.is_nullable,
                is_array=flags.is_array,
            ),
            runtime,
        )

        return LanguageField(
            name=lang_name,
            type=lang_type,
            annotation=lang_type.annotation,
            is_optional=flags.is_optional,
            is_nullable=flags.is_nullable,
            is_array=flags.is_array,
        )

    def enrich_operation(self, request: LanguageOperationRequest) -> LanguageOperation:
        """Create Dart operation `.lang` context."""

        item = self.enrich_item(
            LanguageItemRequest(
                record=request.record,
                runtime=request.runtime,
            )
        )

        return LanguageOperation(name=item.name)

    def enrich_route(self, request: LanguageRouteRequest) -> LanguageRoute:
        """Create Dart route `.lang` context."""

        item = self.enrich_item(
            LanguageItemRequest(
                record=request.record,
                runtime=request.runtime,
            )
        )

        return LanguageRoute(
            name=item.name,
            method_name=item.name.method_name,
        )

    def create_type(self, request: LanguageTypeRequest, runtime: LanguageRuntime):
        """Create a Dart type annotation."""

        return make_dart_type(
            request.facts,
            is_array=request.is_array,
            is_nullable=request.is_nullable,
            is_dynamic=request.is_dynamic,
            is_void=request.is_void,
        )

    def create_imports(self, request: LanguageImportRequest):
        """Create Dart file-level imports."""

        return create_dart_imports(request)

    def create_exports(self, request: LanguageExportRequest):
        """Create Dart file-level exports."""

        return create_dart_exports(request)


dart_language_adapter = DartLanguageAdapter()