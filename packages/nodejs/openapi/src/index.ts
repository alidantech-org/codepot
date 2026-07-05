/* =========================================================
 * Core contract builders
 * ========================================================= */

import { PropertyRegistry } from './properties/property.types.js';
import {
  ProjectionFieldSelection,
  RefUsage,
  SchemaExtendedRefUsage,
  SchemaProjection,
  SchemaProjectionDefinition,
  SchemaProjectionStep,
} from './refs/ref-usage.types.js';
import { ArrayRef, ExtendedRef } from './refs/ref-wrapper.types.js';
import { CompositeSchemaField, PrimitiveSchemaField, RefSchemaField } from './schema/schema.types.js';
import { VersionBuilder } from './version/define-version-contract.js';

export { defineVersionContract } from './version/define-version-contract.js';
export { defineResource } from './resource/define-resource.js';
export { defineFrontend } from './frontend/define-frontend.js';
export { defineAccess } from './access/define-access.js';
export { defineHooks } from './hooks/define-hooks.js';
export { defineBaseEntities, defineEntities, defineEntityRelations } from './entities/define-entities.js';
export type { EntityDefinitionFactory } from './entities/define-entities.js';

export type { VersionContract as OpenApiVersionContract } from './version/version-contract.types.js';
export type { ResourceBuilder as OpenApiResourceContract } from './resource/define-resource.js';
export type { FrontendBuilder as OpenApiFrontendContract } from './frontend/frontend.types.js';
export type {
  AccessAllowMap,
  AccessDefinition,
  AccessDefinitionInput,
  AccessDefinitionObject,
  AccessOwner,
  AccessRef,
  AccessRegistry,
  AccessRoleSource,
  AccessRoleSources,
} from './access/access.types.js';
export type { AccessBuilder } from './access/access-builder.js';
export type {
  RuntimeHookDefinition,
  RuntimeHookOwner,
  RuntimeHookPhase,
  RuntimeHookRef,
  RuntimeHookRefMap,
  RuntimeHookRegistry,
  RuntimeHookUsage,
  RuntimeHookUsageMap,
  RuntimeRouteConfig,
  RuntimeTransport,
  RuntimeTransportSideInbound,
  RuntimeTransportSideOutbound,
} from './hooks/runtime-hooks.types.js';
export type {
  BaseEntityDefinitionInput,
  ConcreteEntityDefinitionInput,
  EntityBackendField,
  EntityBackendFields,
  EntityConstraintBuilder,
  EntityConstraintDefinition,
  EntityConstraintKind,
  EntityConstraintRule,
  EntityConstraintsDefinition,
  EntityDefinition,
  EntityDefinitionInput,
  EntityFieldBuilder,
  EntityFieldDefinition,
  EntityFieldMetadata,
  EntityFieldQueryBuilder,
  EntityFieldQueryMetadata,
  EntityFieldRole,
  EntityGeneratedStrategy,
  EntityOwner,
  EntityRef,
  EntityRegistry,
  EntityRelation,
  EntityRelationBuilder,
  EntityRelationCardinality,
  EntityRelationDeleteBehavior,
  EntityRelationDefinition,
  EntityRelationRef,
  EntityRelationRegistry,
  EntityRelationsInput,
  EntitySearchQueryOptions,
} from './entities/entity.types.js';

/* =========================================================
 * Public API facade
 * ========================================================= */

export { OpenApiTs } from './api/codepot-openapi.js';

export type { GenerateInput, GenerateResult, InitConfigInput, InitConfigResult, OpenApiTsApi } from './api/codepot-openapi.types.js';

/* =========================================================
 * Schema DSL
 * ========================================================= */

export { schema } from './schema/schema.js';

/* =========================================================
 * Routes
 * ========================================================= */

export { HttpMethod } from './routes/http-method.js';

export type {
  DefineRoutesBuilderInput,
  DefineRoutesInput,
  DefineRoutesInputLike,
  RouteBodyInput,
  RouteCacheBuilder,
  RouteCacheConfig,
  RouteCacheInvalidationConfig,
  RouteCacheInvalidateBuilder,
  RouteDefinition,
  RouteDefinitionInput,
  RouteFieldSource,
  RouteOperationBuilder,
  RouteOperationFactory,
  RouteParameterMap,
  RouteParameterRegistry,
  RouteQueryInput,
  RouteRegistry,
  RouteResponseInput,
  RouteSourceDefinition,
  RouteSourceInput,
  RouteSourceMapInput,
  RouteSourceRef,
  RouteSourceSelector,
  RoutesDefinitionBuilder,
} from './routes/route.types.js';

/* =========================================================
 * Components
 * ========================================================= */

export { ComponentBucket } from './components/component-bucket.js';

export type { ComponentFieldMap } from './components/component.types.js';

export { defineSchemas } from './components/schemas/define-schemas.js';

export type { SchemaComponentDefinition, SchemaComponentRegistry } from './components/schemas/schema-component.types.js';

export { ParameterLocation } from './components/parameters/parameter-location.js';
export { defineParameters } from './components/parameters/define-parameters.js';

export type {
  ParameterComponentDefinition,
  ParameterComponentRegistry,
  ParameterSchemaRef,
} from './components/parameters/parameter-component.types.js';

export { defineRequestBodies } from './components/request-bodies/define-request-bodies.js';

export type {
  RequestBodyComponentDefinition,
  RequestBodyComponentRegistry,
  RequestBodySchemaRef,
} from './components/request-bodies/request-body-component.types.js';

export { defineResponses } from './components/responses/define-responses.js';

export type {
  ResponseComponentDefinition,
  ResponseComponentRegistry,
  ResponseSchemaRef,
} from './components/responses/response-component.types.js';

/* =========================================================
 * Properties and refs
 * ========================================================= */

export type { PropertyRefGroup } from './properties/property.types.js';

export type {
  ComponentRef,
  EngineRef,
  ModelRef,
  OperationRef,
  ParameterRef,
  PropertyRef,
  RequestBodyRef,
  ResponseRef,
  RouteRef,
} from './refs/ref.types.js';

/* =========================================================
 * Codegen metadata
 * ========================================================= */

export { CODEGEN_EXTENSION_KEY } from './codegen/codegen-extension.keys.js';
export type { CodegenExtensionKey } from './codegen/codegen-extension.keys.js';

export { XCodegenAccess, XCodegenDtoRole, XCodegenEntityVariant, XCodegenKind } from './codegen/codegen-extension.types.js';

export type {
  CodegenKind,
  CodegenCookieEffects,
  CodegenMetadata,
  CodegenOperationEffects,
  CodegenUiInput,
  CodegenUiMeta,
  CodegenUiRole,
  XCodegenAccess as XCodegenAccessType,
  XCodegenBaseMeta,
  XCodegenDtoMeta,
  XCodegenDtoRole as XCodegenDtoRoleType,
  XCodegenEntityMeta,
  XCodegenEntityVariant as XCodegenEntityVariantType,
  XCodegenEnumMeta,
  // XCodegenMeta,
  XCodegenModelMeta,
  XCodegenPrimitiveMeta,
  XCodegenQueryMeta,
  XCodegenRefPointer,
  XCodegenResourceMeta,
  ResolvedCodegenUiMeta,
} from './codegen/codegen-extension.types.js';

export {
  isDtoSchema,
  isEnumSchema,
  isModelSchema,
  isObjectSchema,
  isPrimitiveSchema,
  resolveCodegenKind,
  stripEnumInheritanceMetadata,
  stripNonObjectInheritanceMetadata,
} from './codegen/resolve-codegen-kind.js';

export { applyCodegenMetadata } from './codegen/apply-codegen-extensions.js';

export type { CodegenExtensionTarget } from './codegen/apply-codegen-extensions.js';

/* =========================================================
 * OpenAPI types and constants
 * ========================================================= */

export { OpenApiVersion } from './openapi/openapi-version.js';
export { ContentType as OpenApiContentType } from './openapi/content-type.js';
export { OpenApiRefPattern } from './openapi/ref-patterns.js';

export type { ContentTypeInput } from './openapi/content-type.js';

export type {
  OpenApiComponents,
  OpenApiDocument,
  OpenApiInfo,
  OpenApiOperation,
  OpenApiPaths,
  OpenApiServer,
} from './openapi/openapi.types.js';

/* =========================================================
 * Compiler
 * ========================================================= */

export { compileOpenApi } from './compiler/compile-openapi.js';

export type { CompileOptions } from './compiler/compile-options.types.js';

export type { CompileFailureResult, CompileResult, CompileSuccessResult } from './compiler/compile-result.types.js';

/* =========================================================
 * Validation
 * ========================================================= */

export { validateContract } from './validation/validate-contract.js';

export type { ValidationIssue, ValidationResult } from './validation/validation-result.types.js';

export { validateOpenApiDocument, type OpenApiValidationResult } from './validator/validate-openapi-document.js';

/* =========================================================
 * Config
 * ========================================================= */

export { definePackageConfig } from './config/define-package-config.js';
export { PackageOutputFormat } from './config/package-config.types.js';
export { resolveCompileOptions } from './config/resolve-compile-options.js';
export { resolvePackageConfig } from './config/resolve-package-config.js';

export type { PackageConfig, PackageOutputConfig, PackageServerConfig } from './config/package-config.types.js';
export type {
  VersionBuilder,
  ArrayRef,
  ProjectionFieldSelection,
  RefUsage,
  SchemaExtendedRefUsage,
  SchemaProjection,
  SchemaProjectionDefinition,
  SchemaProjectionStep,
  PropertyRegistry,
  ExtendedRef,
  RefSchemaField,
  CompositeSchemaField,
  PrimitiveSchemaField,
};

/* =========================================================
 * Frontend authoring
 * ========================================================= */

export type {
  DefineFrontendOptions,
  DefineFrontendComponentsInput,
  DefineFrontendScreensInput,
  FrontendBuilder,
  FrontendComponentBuilder,
  FrontendComponentBuilderMap,
  FrontendComponentDefinition,
  FrontendComponentFactoryRoot,
  FrontendComponentRef,
  FrontendComponentRegistry,
  FrontendComponentsDefinitionBuilder,
  FrontendScreenBuilder,
  FrontendScreenBuilderMap,
  FrontendScreenDefinition,
  FrontendScreenFactoryRoot,
  FrontendScreenRef,
  FrontendScreenRegistry,
  FrontendScreensDefinitionBuilder,
} from './frontend/frontend.types.js';

export { createInfoBuilder, normalizeInfo } from './info/normalize-info.js';

export type { InfoBuilder, InfoInput, InfoObject, InfoValue, NormalizedInfo } from './info/info.types.js';

/* =========================================================
 * Output and writer
 * ========================================================= */

export { ContentType, DefaultOutputConfig } from './output/output.constants.js';
export type { ContentType as ContentTypeValue } from './output/output.constants.js';
export { createDebugFileName, createOpenApiFileName } from './output/openapi-file-name.js';
export { resolveOutputConfig } from './output/resolve-output-config.js';

export type { OutputFileResult, ResolvedOutputConfig } from './output/output.types.js';

export { writeOpenApiFiles } from './writer/write-openapi-files.js';

export type { WriteOpenApiFilesInput } from './writer/write-openapi-files.js';

/* =========================================================
 * Generator
 * ========================================================= */

export { generateOpenApi, type GenerateOpenApiResult } from './generator/generate-openapi.js';

/* =========================================================
 * Naming helpers
 * ========================================================= */

export { toSchemaName } from './naming/schema-name.js';

export { componentRefToSchemaName, modelRefToSchemaName } from './naming/ref-schema-name.js';

/* =========================================================
 * Logger
 * ========================================================= */

export { CompilerLogger } from './logger/index.js';
export type { LogLevel } from './logger/index.js';
