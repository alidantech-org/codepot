import type { JsonObject } from '@/contract/index';
import type { AccessRef } from '../access/access.types';
import type { InfoInput, NormalizedInfo, ResourceContext } from '../core/authoring.types';
import type { RuntimeRouteConfig } from '../hooks/hooks.types';
import type { ComponentRef, ModelRef, PropertyRef, RequestBodyRef, ResponseRef, RouteRef } from '../refs/ref.types';
import type {
  RefUsage,
  RefWithUsageMethods,
  SchemaProjectionStep,
} from '../refs/ref-usage.types';
import type { SchemaField } from '../schema/schema.types';
import type { HttpMethod } from './http-method';

export interface RouteCacheInvalidationConfig { readonly operations: readonly string[]; }
export interface RouteCacheConfig { readonly invalidate?: RouteCacheInvalidationConfig; }
export interface RouteCacheInvalidateBuilder { on(operationId: string): RouteCacheInvalidateBuilder; build(): RouteCacheInvalidationConfig; }
export interface RouteCacheBuilder { readonly invalidate: RouteCacheInvalidateBuilder; build(): RouteCacheConfig; }
export type RouteParameterRegistry = RefWithUsageMethods<ComponentRef> | RefUsage<ComponentRef> | ComponentRef;
export type RouteParameterFieldValue = PropertyRef | RefUsage<PropertyRef>;
export type RouteParameterMap = Readonly<Record<string, RouteParameterFieldValue>>;
export type RouteQueryInput = RouteParameterMap | RefWithUsageMethods<ComponentRef> | RefUsage<ComponentRef>;

/**
 * Structural route-facing projection shape. Typed projection builders may keep
 * richer generic methods without becoming invariant at the route boundary.
 */
export interface RouteSchemaProjection {
  readonly kind: 'schema-projection-definition';
  readonly source: string;
  readonly sourceRefId: string;
  readonly mode: 'partial' | 'pick' | 'omit';
  readonly fields?: readonly string[];
  readonly steps?: readonly SchemaProjectionStep[];
}

export type RouteSchemaInput =
  | PropertyRef
  | ComponentRef
  | ModelRef
  | RefUsage<PropertyRef>
  | RefUsage<ComponentRef>
  | RefUsage<ModelRef>
  | SchemaField
  | RouteSchemaProjection;

export interface RouteBodyObjectInput { readonly schema: RouteSchemaInput; readonly required?: boolean; readonly description?: string; readonly contentType?: string | readonly string[]; }
export type RouteBodyInput = RouteSchemaInput | RequestBodyRef | RouteBodyObjectInput;
export interface RouteResponseObjectInput { readonly schema: RouteSchemaInput; readonly description?: string; readonly contentType?: string | readonly string[]; }
export type RouteResponseInput = RouteSchemaInput | ResponseRef | RouteResponseObjectInput;
export interface RouteSourceInput { readonly key: string; readonly label: string; }
export interface RouteSourceDefinition extends RouteSourceInput { readonly responseField: string; }
export interface RouteSourceDefinitionRef { readonly kind: 'route-source'; readonly name: string; readonly route: RouteRef; readonly source: RouteSourceDefinition; }
export interface RouteDefinition { readonly method: HttpMethod; readonly path: string; readonly summary?: string; readonly description?: string; readonly query?: RouteQueryInput; readonly body?: RouteBodyInput; readonly response?: RouteResponseInput; readonly responses?: Readonly<Record<number, RouteResponseInput>>; readonly operationId?: string; readonly tags?: readonly string[]; readonly codegenTags?: readonly string[]; readonly meta?: JsonObject; readonly ui?: string | JsonObject; readonly access?: AccessRef; readonly effects?: JsonObject; readonly runtime?: RuntimeRouteConfig; readonly cache?: RouteCacheConfig; readonly sources?: Readonly<Record<string, RouteSourceDefinition>>; readonly info?: NormalizedInfo; }
export type RouteDefinitionInput = Omit<RouteDefinition, 'operationId' | 'meta' | 'sources' | 'info'> & { readonly source?: Readonly<Record<string, RouteSourceInput>>; readonly info?: InfoInput };
export type DefineRoutesInput = { readonly params?: RouteParameterRegistry; readonly routes: Readonly<Record<string, RouteDefinitionInput>> };
export type DefineRoutesBuilderInput = (builder: RouteOperationFactory) => Readonly<Record<string, RouteOperationBuilder>>;
export interface RouteSourceSelector { key(field: string): RouteSourceSelector; label(field: string): RouteSourceSelector; build(): RouteSourceInput; }
export interface RouteOperationBuilder { summary(summary: string): RouteOperationBuilder; description(description: string): RouteOperationBuilder; query(query: RouteQueryInput): RouteOperationBuilder; body(body: RouteBodyInput): RouteOperationBuilder; response(response: RouteResponseInput): RouteOperationBuilder; on(status: number, response: RouteResponseInput): RouteOperationBuilder; ui(roleOrMeta: string | JsonObject): RouteOperationBuilder; access(access: AccessRef): RouteOperationBuilder; effects(effects: JsonObject): RouteOperationBuilder; runtime(runtime: RuntimeRouteConfig): RouteOperationBuilder; cache(configure: (cache: RouteCacheBuilder) => RouteCacheInvalidateBuilder | RouteCacheBuilder): RouteOperationBuilder; tags(tags: readonly string[]): RouteOperationBuilder; source(responseField: string, configure: (source: RouteSourceSelector) => RouteSourceSelector): RouteOperationBuilder; info(info: InfoInput): RouteOperationBuilder; build(): RouteDefinition; }
export interface RouteOperationFactory { get(path: string): RouteOperationBuilder; post(path: string): RouteOperationBuilder; put(path: string): RouteOperationBuilder; patch(path: string): RouteOperationBuilder; delete(path: string): RouteOperationBuilder; }
export interface RoutesDefinitionBuilder { params(parameters: RouteParameterRegistry): RoutesDefinitionBuilder; routes(input: DefineRoutesBuilderInput): RouteRegistry; }
export interface RouteRegistry { readonly name: string; readonly routes: Readonly<Record<string, RouteDefinition>>; readonly params?: RouteParameterRegistry; readonly ref: Readonly<Record<string, RouteRef>>; }
export interface DefineRoutesOptions { readonly name: string; readonly resource?: ResourceContext; }
export function extractPathParamNames(path: string): readonly string[] { return Array.from(path.matchAll(/:([A-Za-z_][A-Za-z0-9_]*)/g), (match) => match[1]).filter((value): value is string => value !== undefined); }
