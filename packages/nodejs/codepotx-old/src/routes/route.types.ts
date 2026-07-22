import type { ComponentRef, ModelRef, ParameterRef, RequestBodyRef, ResponseRef, PropertyRef, RouteRef } from '../refs/ref.types.js';
import type { ComponentFieldMap } from '../components/component.types.js';
import type { RefWithUsageMethods, RefUsage } from '../refs/ref-usage.types.js';
import type { SchemaField } from '../schema/schema.types.js';
import type { HttpMethod } from './http-method.js';
import type { CodegenMetadata, CodegenOperationEffects, CodegenUiInput } from '../codegen/codegen-extension.types.js';
import type { AccessRef } from '../access/access.types.js';
import type { ContentTypeInput } from '../openapi/content-type.js';
import type { RuntimeRouteConfig } from '../hooks/runtime-hooks.types.js';
import type { InfoInput, NormalizedInfo } from '../info/info.types.js';

export interface RouteCacheInvalidationConfig {
  readonly operations: readonly string[];
}

export interface RouteCacheConfig {
  readonly invalidate?: RouteCacheInvalidationConfig;
}

export interface RouteCacheInvalidateBuilder {
  on(operationId: string): RouteCacheInvalidateBuilder;
  build(): RouteCacheInvalidationConfig;
}

export interface RouteCacheBuilder {
  readonly invalidate: RouteCacheInvalidateBuilder;
  build(): RouteCacheConfig;
}

export type RouteSchemaRef = ComponentRef | ModelRef | ComponentFieldMap;

export type RouteRequestBodyRef = RequestBodyRef | RouteSchemaRef;

export type RouteResponseRef = ResponseRef | RouteSchemaRef;

export type RouteParameterRef = ParameterRef | ComponentFieldMap;

export type RouteParameterInput = ParameterRef | readonly ParameterRef[] | ComponentFieldMap;

export type RouteParameterRegistry = RefWithUsageMethods<ComponentRef> | RefUsage<ComponentRef> | ComponentRef;

// Route query field values must be property refs, not component/model refs
// A route query can be a ComponentRef at the top level, but expanded fields must be PropertyRef
export type RouteParameterFieldValue = PropertyRef | RefUsage<PropertyRef>;

export type RouteQueryInput = RouteParameterMap | RefWithUsageMethods<ComponentRef> | RefUsage<ComponentRef>;

export type RouteParameterMap = Record<string, RouteParameterFieldValue>;

export type RouteSchemaInput =
  | PropertyRef
  | ComponentRef
  | ModelRef
  | RefUsage<PropertyRef>
  | RefUsage<ComponentRef>
  | RefUsage<ModelRef>
  | SchemaField;

export interface RouteBodyObjectInput {
  readonly schema: RouteSchemaInput;
  readonly required?: boolean;
  readonly description?: string;
  readonly contentType?: ContentTypeInput;
}

export type RouteBodyInput = RouteSchemaInput | RouteBodyObjectInput;

export interface RouteResponseObjectInput {
  readonly schema: RouteSchemaInput;
  readonly description?: string;
  readonly contentType?: ContentTypeInput;
}

export type RouteResponseInput = RouteSchemaInput | RouteResponseObjectInput;

export interface RouteSourceInput {
  readonly key: string;
  readonly label: string;
}

export type RouteSourceMapInput = Record<string, RouteSourceInput>;

export interface RouteSourceDefinition extends RouteSourceInput {
  readonly responseField: string;
}

export interface RouteSourceRef {
  readonly kind: 'route-source';
  readonly name: string;
  readonly route: RouteRef;
  readonly source: RouteSourceDefinition;
}

export interface RouteFieldSource {
  readonly kind: 'route';
  readonly route: RouteRef;
  readonly source?: RouteSourceRef;
}

export interface RouteDefinition {
  readonly method: HttpMethod;
  readonly path: string;
  readonly summary?: string;
  readonly description?: string;

  readonly query?: RouteQueryInput;
  readonly body?: RouteBodyInput;

  readonly response?: RouteResponseInput;
  readonly responses?: Record<number, RouteResponseInput>;

  readonly operationId?: string;
  readonly tags?: string[];
  readonly codegenTags?: readonly string[];
  readonly meta?: CodegenMetadata;
  readonly ui?: CodegenUiInput;
  readonly access?: AccessRef;
  readonly effects?: CodegenOperationEffects;
  readonly runtime?: RuntimeRouteConfig;
  readonly cache?: RouteCacheConfig;
  readonly source?: RouteSourceMapInput;
  readonly sources?: Record<string, RouteSourceDefinition>;
  readonly info?: NormalizedInfo;
}

export type RouteDefinitionInput = Omit<RouteDefinition, 'operationId' | 'meta' | 'sources' | 'info'> & {
  readonly source?: RouteSourceMapInput;
  readonly info?: InfoInput;
};

export type DefineRoutesInput = {
  readonly params?: RouteParameterRegistry;
  readonly routes: Record<string, RouteDefinitionInput>;
};

export type DefineRoutesBuilderInput = (builder: RouteOperationFactory) => Record<string, RouteOperationBuilder>;

export type DefineRoutesInputLike = DefineRoutesInput;

export interface RouteSourceSelector {
  key(field: string): RouteSourceSelector;
  label(field: string): RouteSourceSelector;
  build(): RouteSourceInput;
}

export interface RouteOperationBuilder {
  summary(summary: string): RouteOperationBuilder;
  description(description: string): RouteOperationBuilder;
  query(query: RouteQueryInput): RouteOperationBuilder;
  body(body: RouteBodyInput): RouteOperationBuilder;
  response(response: RouteResponseInput): RouteOperationBuilder;
  on(status: number, response: RouteResponseInput): RouteOperationBuilder;
  ui(roleOrMeta: CodegenUiInput): RouteOperationBuilder;
  access(access: AccessRef): RouteOperationBuilder;
  effects(effects: CodegenOperationEffects): RouteOperationBuilder;
  runtime(runtime: RuntimeRouteConfig): RouteOperationBuilder;
  cache(configure: (cache: RouteCacheBuilder) => RouteCacheInvalidateBuilder | RouteCacheBuilder): RouteOperationBuilder;
  tags(tags: readonly string[]): RouteOperationBuilder;
  source(responseField: string, configure: (source: RouteSourceSelector) => RouteSourceSelector): RouteOperationBuilder;
  info(info: InfoInput): RouteOperationBuilder;
  build(): RouteDefinition;
}

export interface RouteOperationFactory {
  get(path: string): RouteOperationBuilder;
  post(path: string): RouteOperationBuilder;
  put(path: string): RouteOperationBuilder;
  patch(path: string): RouteOperationBuilder;
  delete(path: string): RouteOperationBuilder;
}

export interface RoutesDefinitionBuilder {
  params(parameters: RouteParameterRegistry): RoutesDefinitionBuilder;
  routes(input: DefineRoutesBuilderInput): RouteRegistry;
}

export interface RouteRegistry {
  readonly name: string;
  readonly routes: Record<string, RouteDefinition>;
  readonly params?: RouteParameterRegistry;
  readonly ref: Record<string, RouteRef>;
}

export function extractPathParamNames(path: string): readonly string[] {
  const matches = path.matchAll(/:([A-Za-z_][A-Za-z0-9_]*)/g);
  return Array.from(matches, (match) => match[1]);
}
