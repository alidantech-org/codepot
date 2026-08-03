"""TypeScript language adapter."""

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
from archives.codepot.src.languages.typescript.constants import (
    TYPESCRIPT_LANGUAGE_KEY,
)
from archives.codepot.src.languages.typescript.exports import create_typescript_exports
from archives.codepot.src.languages.typescript.imports import create_typescript_imports
from archives.codepot.src.languages.typescript.names import make_typescript_name
from archives.codepot.src.languages.typescript.types import make_typescript_type

DEFAULT_TYPESCRIPT_EXTENSIONS = ("ts", "tsx")


class TypeScriptLanguageAdapter:
    """TypeScript implementation of the Codepotx language adapter contract."""

    key = TYPESCRIPT_LANGUAGE_KEY

    def create_runtime(self, request: LanguageRuntimeRequest) -> LanguageRuntime:
        """Create TypeScript runtime context."""

        naming = request.naming
        imports = request.imports
        extensions = request.extensions or DEFAULT_TYPESCRIPT_EXTENSIONS

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
        """Create generic TypeScript item `.lang` context."""

        runtime = request.runtime
        record = request.record

        lang_name = make_typescript_name(
            record.name,
            class_case=runtime.naming.class_case,
            interface_case=runtime.naming.interface_case,
            enum_case=runtime.naming.enum_case,
            enum_value_case=runtime.naming.enum_value_case,
            field_case=runtime.naming.field_case,
            method_case=runtime.naming.method_case,
            function_case=runtime.naming.function_case,
            constant_case=runtime.naming.constant_case,
            file_case=runtime.naming.file_case,
            module_case=runtime.naming.module_case,
            package_case=runtime.naming.package_case,
        )

        return LanguageItem(name=lang_name)

    def enrich_field(self, request: LanguageFieldRequest) -> LanguageField:
        """Create TypeScript field `.lang` context."""

        runtime = request.runtime
        flags = request.flags

        lang_name = make_typescript_name(
            request.name,
            field_case=runtime.naming.field_case,
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
        """Create TypeScript operation `.lang` context."""

        item = self.enrich_item(
            LanguageItemRequest(
                record=request.record,
                runtime=request.runtime,
            )
        )

        return LanguageOperation(name=item.name)

    def enrich_route(self, request: LanguageRouteRequest) -> LanguageRoute:
        """Create TypeScript route `.lang` context."""

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
        """Create a TypeScript type annotation."""

        return make_typescript_type(
            request.facts,
            is_array=request.is_array,
            is_nullable=request.is_nullable,
            is_dynamic=request.is_dynamic,
            is_void=request.is_void,
        )

    def create_imports(self, request: LanguageImportRequest):
        """Create TypeScript file-level imports."""

        return create_typescript_imports(request)

    def create_exports(self, request: LanguageExportRequest):
        """Create TypeScript file-level exports."""

        return create_typescript_exports(request)


typescript_language_adapter = TypeScriptLanguageAdapter()