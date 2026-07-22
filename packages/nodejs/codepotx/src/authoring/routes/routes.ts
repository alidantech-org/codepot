import { EngineIdPart, createEngineId } from '../core/engine-id';
import { normalizeInfo } from '../core/normalize';
import { RefKind } from '../refs/ref-kind';
import type { RouteRef } from '../refs/ref.types';
import { HttpMethod } from './http-method';
import type {
  DefineRoutesBuilderInput,
  DefineRoutesInput,
  DefineRoutesOptions,
  RouteBodyInput,
  RouteCacheBuilder,
  RouteCacheConfig,
  RouteCacheInvalidateBuilder,
  RouteCacheInvalidationConfig,
  RouteDefinition,
  RouteDefinitionInput,
  RouteOperationBuilder,
  RouteOperationFactory,
  RouteParameterRegistry,
  RouteQueryInput,
  RouteRegistry,
  RouteResponseInput,
  RouteSourceInput,
  RouteSourceSelector,
  RoutesDefinitionBuilder,
} from './route.types';
import type { AccessRef } from '../access/access.types';
import type { RuntimeRouteConfig } from '../hooks/hooks.types';
import type { JsonObject } from '@/contract/index';
import type { InfoInput } from '../core/authoring.types';

export function defineRoutes(options: DefineRoutesOptions): RoutesDefinitionBuilder;
export function defineRoutes(options: DefineRoutesOptions, input: DefineRoutesInput): RouteRegistry;
export function defineRoutes(options: DefineRoutesOptions, input?: DefineRoutesInput): RouteRegistry | RoutesDefinitionBuilder {
  if (!input) return new RoutesRootBuilder(options);
  return createRegistry(options, input.params, Object.fromEntries(Object.entries(input.routes).map(([key, value]) => [key, normalizeRoute(value)])));
}
class RoutesRootBuilder implements RoutesDefinitionBuilder {
  #params?: RouteParameterRegistry;
  readonly #options: DefineRoutesOptions;
  constructor(options: DefineRoutesOptions) { this.#options = options; }
  params(parameters: RouteParameterRegistry): RoutesDefinitionBuilder { this.#params = parameters; return this; }
  routes(input: DefineRoutesBuilderInput): RouteRegistry {
    const built = input(new RouteFactory());
    return createRegistry(this.#options, this.#params, Object.fromEntries(Object.entries(built).map(([key, builder]) => [key, builder.build()])));
  }
}
class RouteFactory implements RouteOperationFactory {
  get(path: string): RouteOperationBuilder { return new FluentRouteOperationBuilder(HttpMethod.get, path); }
  post(path: string): RouteOperationBuilder { return new FluentRouteOperationBuilder(HttpMethod.post, path); }
  put(path: string): RouteOperationBuilder { return new FluentRouteOperationBuilder(HttpMethod.put, path); }
  patch(path: string): RouteOperationBuilder { return new FluentRouteOperationBuilder(HttpMethod.patch, path); }
  delete(path: string): RouteOperationBuilder { return new FluentRouteOperationBuilder(HttpMethod.delete, path); }
}
class FluentRouteOperationBuilder implements RouteOperationBuilder {
  #route: RouteDefinition;
  constructor(method: RouteDefinition['method'], path: string) { this.#route = { method, path }; }
  summary(summary: string): RouteOperationBuilder { this.#route = { ...this.#route, summary }; return this; }
  description(description: string): RouteOperationBuilder { this.#route = { ...this.#route, description }; return this; }
  query(query: RouteQueryInput): RouteOperationBuilder { this.#route = { ...this.#route, query }; return this; }
  body(body: RouteBodyInput): RouteOperationBuilder { this.#route = { ...this.#route, body }; return this; }
  response(response: RouteResponseInput): RouteOperationBuilder { this.#route = { ...this.#route, response }; return this; }
  on(status: number, response: RouteResponseInput): RouteOperationBuilder { this.#route = { ...this.#route, responses: { ...(this.#route.responses ?? {}), [status]: response } }; return this; }
  ui(ui: string | JsonObject): RouteOperationBuilder { this.#route = { ...this.#route, ui }; return this; }
  access(access: AccessRef): RouteOperationBuilder { this.#route = { ...this.#route, access }; return this; }
  effects(effects: JsonObject): RouteOperationBuilder { this.#route = { ...this.#route, effects }; return this; }
  runtime(runtime: RuntimeRouteConfig): RouteOperationBuilder { this.#route = { ...this.#route, runtime }; return this; }
  cache(configure: (cache: RouteCacheBuilder) => RouteCacheInvalidateBuilder | RouteCacheBuilder): RouteOperationBuilder { const builder = new FluentRouteCacheBuilder(); configure(builder); this.#route = { ...this.#route, cache: builder.build() }; return this; }
  tags(tags: readonly string[]): RouteOperationBuilder { this.#route = { ...this.#route, codegenTags: [...tags] }; return this; }
  source(responseField: string, configure: (source: RouteSourceSelector) => RouteSourceSelector): RouteOperationBuilder { const source = configure(new FluentRouteSourceSelector()).build(); this.#route = { ...this.#route, sources: { ...(this.#route.sources ?? {}), [responseField]: { responseField, ...source } } }; return this; }
  info(info: InfoInput): RouteOperationBuilder { const normalized = normalizeInfo(info); if (normalized) this.#route = { ...this.#route, info: normalized }; return this; }
  build(): RouteDefinition { return { ...this.#route }; }
}
class FluentRouteCacheBuilder implements RouteCacheBuilder { readonly invalidate = new FluentRouteCacheInvalidateBuilder(); build(): RouteCacheConfig { const invalidate = this.invalidate.build(); return invalidate.operations.length > 0 ? { invalidate } : {}; } }
class FluentRouteCacheInvalidateBuilder implements RouteCacheInvalidateBuilder { #operations: string[] = []; on(operationId: string): RouteCacheInvalidateBuilder { if (!operationId.trim()) throw new Error('Cache invalidation operation ID must be a non-empty string.'); this.#operations.push(operationId); return this; } build(): RouteCacheInvalidationConfig { return { operations: [...new Set(this.#operations)] }; } }
class FluentRouteSourceSelector implements RouteSourceSelector { #key?: string; #label?: string; key(field: string): RouteSourceSelector { this.#key = field; return this; } label(field: string): RouteSourceSelector { this.#label = field; return this; } build(): RouteSourceInput { if (!this.#key || !this.#label) throw new Error('Route source requires both key(...) and label(...).'); return { key: this.#key, label: this.#label }; } }
function normalizeRoute(route: RouteDefinitionInput): RouteDefinition { const info = route.info ? normalizeInfo(route.info) : undefined; const { source: _source, info: _info, ...rest } = route; const codegenTags = route.codegenTags ?? route.tags; return { ...rest, ...(codegenTags ? { codegenTags } : {}), ...(route.source ? { sources: Object.fromEntries(Object.entries(route.source).map(([responseField, value]) => [responseField, { responseField, ...value }])) } : {}), ...(info ? { info } : {}) }; }
function createRegistry(options: DefineRoutesOptions, params: RouteParameterRegistry | undefined, routes: Record<string, RouteDefinition>): RouteRegistry {
  const normalized = Object.fromEntries(Object.entries(routes).map(([key, route]) => [key, { ...route, operationId: key, tags: options.resource ? [options.resource.tag] : [], meta: { kind: 'dto', ...(options.resource ? { resource: { name: options.resource.alias, path: options.resource.folders } } : { shared: true }) } }]));
  const refs = Object.fromEntries(Object.entries(normalized).map(([key, route]) => {
    const sources: Record<string, import('./route.types').RouteSourceDefinitionRef> = {};
    const ref: RouteRef = { id: scopedId(options, EngineIdPart.route, key), name: key, kind: RefKind.route, routeKey: key, method: route.method, path: route.path, sources };
    for (const [name, source] of Object.entries(route.sources ?? {})) sources[name] = { kind: 'route-source', name, route: ref, source };
    if (Object.keys(sources).length === 1) Object.defineProperty(ref, 'defaultSource', { enumerable: true, configurable: true, value: Object.values(sources)[0] });
    return [key, ref];
  }));
  return { name: options.name, routes: normalized, ...(params ? { params } : {}), ref: refs };
}
function scopedId(options: DefineRoutesOptions, ...parts: readonly string[]): string { return options.resource ? createEngineId(EngineIdPart.resource, options.resource.name, ...parts) : createEngineId(...parts); }
