export { createAccessBuilder, defineAccess } from './access/access';
export { DefaultAuthoringCompiler } from './compiler/compiler';
export {
  createSchemaComponentRegistry,
  defineParameters,
  defineRequestBodies,
  defineResponses,
  defineSchemas,
} from './components/components';
export {
  defineCodepotConfig,
  definePackageConfig,
  isCodepotConfig,
} from './config/config';
export { EngineIdPart, createEngineId } from './core/engine-id';
export {
  createAuthoringState,
  normalizeInfo,
  ownerFromResource,
} from './core/normalize';
export {
  createAuthoringEngine,
  DefaultAuthoringEngine,
} from './engine/authoring-engine';
export {
  defineBaseEntities,
  defineEntities,
  defineEntityRelations,
} from './entities/entities';
export { defineFrontend } from './frontend/frontend';
export { defineHooks } from './hooks/hooks';
export { createScopedId, defineProperties } from './properties/define-properties';
export { PropertyKind } from './properties/property-kind';
export { RefKind } from './refs/ref-kind';
export { isRefUsage, withRefMethods } from './refs/ref-methods';
export { defineResource } from './resource/resource';
export { HttpMethod } from './routes/http-method';
export { defineRoutes } from './routes/routes';
export { schema } from './schema/schema';
export { SchemaKind } from './schema/schema-kind';
export { z, ZOD_COMPATIBILITY_FEATURES } from './schema/z-compat';
export { defineVersionContract } from './version/version';

export type {
  AccessAllowMap,
  AccessAllowSelection,
  AccessBuilder,
  AccessDefinitionBuilder,
  AccessDefinitionInput,
  AccessDefinitionObject,
  AccessRef,
  AccessRefMap,
  AccessRegistry,
  AccessRoleSource,
  AccessRoleSources,
  NormalizedAccessDefinition,
} from './access/access.types';
export type {
  AuthoringCompileInput,
  AuthoringCompileOutput,
  AuthoringCompiler,
  AuthoringCompilerDependencies,
} from './compiler/compiler.types';
export type {
  ComponentFieldMap,
  ComponentFieldValue,
  ComponentMetadata,
  DefineComponentOptions,
  ParameterComponentDefinition,
  ParameterComponentInput,
  ParameterComponentRegistry,
  ParameterLocation,
  RequestBodyComponentDefinition,
  RequestBodyComponentInput,
  RequestBodyComponentRegistry,
  ResponseComponentDefinition,
  ResponseComponentInput,
  ResponseComponentRegistry,
  SchemaComponentDefinition,
  SchemaComponentFields,
  SchemaComponentRefMap,
  SchemaComponentRegistry,
  SchemaComponentValue,
} from './components/component.types';
export type { CodepotConfig, PackageConfig } from './config/config.types';
export type {
  AuthoringState,
  DefinitionOwner,
  DefinitionOwnerGlobal,
  DefinitionOwnerResource,
  InfoInput,
  NormalizedInfo,
  ResourceContext,
} from './core/authoring.types';
export type {
  AuthoringEngine,
  AuthoringEngineDependencies,
} from './engine/authoring-engine.types';
export type {
  BaseEntityDefinitionInput,
  ConcreteEntityDefinitionInput,
  DefineEntitiesOptions,
  EntityBackendField,
  EntityBackendFields,
  EntityConstraintBuilder,
  EntityConstraintDefinition,
  EntityConstraintKind,
  EntityConstraintRule,
  EntityConstraintsDefinition,
  EntityConstraintValue,
  EntityDefinition,
  EntityDefinitionFactory,
  EntityDefinitionInput,
  EntityFieldBuilder,
  EntityFieldDefinition,
  EntityFieldMetadata,
  EntityFieldQueryBuilder,
  EntityFieldQueryMetadata,
  EntityFieldRole,
  EntityFieldValueRef,
  EntityFieldsDefinition,
  EntityGeneratedStrategy,
  EntityRef,
  EntityRegistry,
  EntityRegistryRefs,
  EntityRelation,
  EntityRelationBuilder,
  EntityRelationCardinality,
  EntityRelationDefinition,
  EntityRelationDeleteBehavior,
  EntityRelationRef,
  EntityRelationRegistry,
  EntityRelationsInput,
  EntitySearchQueryOptions,
} from './entities/entity.types';
export type {
  DefineFrontendOptions,
  FrontendBuilder,
  FrontendContext,
} from './frontend/frontend.types';
export type {
  NormalizedRuntimeHookDefinition,
  RuntimeHookDefinition,
  RuntimeHookPhase,
  RuntimeHookRef,
  RuntimeHookRegistry,
  RuntimeRouteConfig,
} from './hooks/hooks.types';
export type {
  DefinePropertiesOptions,
  PropertyResourceContext,
} from './properties/define-properties.types';
export type {
  ForRefPropertyDefinition,
  PropertyDefinition,
  PropertyDefinitionBase,
  PropertyFieldRefMap,
  PropertyGroupOptions,
  PropertyGroupRegistry,
  PropertyRefGroup,
  PropertyRegistry,
  PropertyRegistryRef,
  SharedPropertyDefinition,
  ZodPropertyDefinitionFieldMap,
} from './properties/property.types';
export type { RefMethodOptions } from './refs/ref-methods.types';
export type {
  ExtendWithFields,
  ExtendWithInput,
  FieldSourceMetadata,
  FieldSourceOrigin,
  ProjectionFieldSelection,
  RefUsage,
  RefUsageOptions,
  RefWithAccessAllowMethods,
  RefWithUsageMethods,
  SchemaExtendedRefUsage,
  SchemaProjection,
  SchemaProjectionDefinition,
  SchemaProjectionStep,
  SchemaRefWithUsageMethods,
} from './refs/ref-usage.types';
export type { ArrayRef, ExtendedRef } from './refs/ref-wrapper.types';
export type {
  AuthoringCodegenMetadata,
  AuthoringResourceMetadata,
  ComponentRef,
  EngineRef,
  EngineRefBase,
  GeneratedBooleanPropertySchema,
  GeneratedEnumPropertySchema,
  GeneratedPropertySchema,
  ModelRef,
  OperationRef,
  ParameterRef,
  PropertyRef,
  RequestBodyRef,
  ResponseRef,
  RouteFieldSource,
  RouteRef,
  RouteSourceRef,
} from './refs/ref.types';
export type {
  DefineResourceOptions,
  ResourceBuilder,
} from './resource/resource.types';
export type {
  DefineRoutesBuilderInput,
  DefineRoutesInput,
  DefineRoutesOptions,
  RouteBodyInput,
  RouteBodyObjectInput,
  RouteCacheBuilder,
  RouteCacheConfig,
  RouteCacheInvalidateBuilder,
  RouteCacheInvalidationConfig,
  RouteDefinition,
  RouteDefinitionInput,
  RouteOperationBuilder,
  RouteOperationFactory,
  RouteParameterFieldValue,
  RouteParameterMap,
  RouteParameterRegistry,
  RouteQueryInput,
  RouteRegistry,
  RouteResponseInput,
  RouteResponseObjectInput,
  RouteSchemaInput,
  RouteSchemaProjection,
  RouteSourceDefinition,
  RouteSourceDefinitionRef,
  RouteSourceInput,
  RouteSourceSelector,
  RoutesDefinitionBuilder,
} from './routes/route.types';
export type {
  CodepotSchemaHelpers,
  CodepotSchemaNamespace,
  CompositeOptions,
} from './schema/schema';
export type {
  AnyOfSchemaField,
  CompositeSchemaField,
  FileSchemaField,
  LiteralSchemaField,
  NoContentSchemaField,
  OneOfSchemaField,
  PrimitiveSchemaField,
  PropertyDefinitionField,
  PropertyDefinitionFieldMap,
  RecordSchemaField,
  RefSchemaField,
  SchemaBehaviorOptions,
  SchemaField,
  SchemaFieldMap,
  SchemaReferenceInput,
  SchemaReferenceLike,
  SchemaReferenceUsageLike,
} from './schema/schema.types';
export type { CodepotZodCompatibility } from './schema/z-compat';
export type {
  DefineVersionContractOptions,
  VersionBuilder,
  VersionContract,
  VersionDefaults,
  VersionInfo,
  VersionLicense,
} from './version/version.types';
