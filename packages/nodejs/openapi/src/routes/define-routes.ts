import { EngineIdPart, createEngineId } from '../ids/engine-id.js';
import type { OptionalResourceContext } from '../resource/resource-context.types.js';
import { XCodegenDtoRole, XCodegenKind } from '../codegen/codegen-extension.types.js';
import type { CodegenOperationEffects, CodegenUiInput } from '../codegen/codegen-extension.types.js';
import { normalizeCodegenUiInput } from '../codegen/codegen-ui.js';
import type { AccessRef } from '../access/access.types.js';
import type { RuntimeRouteConfig } from '../hooks/runtime-hooks.types.js';
import { RefKind } from '../refs/ref-kind.js';
import type { RouteRef } from '../refs/ref.types.js';
import { HttpMethod } from './http-method.js';
import { normalizeInfo } from '../info/normalize-info.js';
import type { InfoInput } from '../info/info.types.js';
import type {
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
  RouteOperationBuilder,
  RouteOperationFactory,
  RouteParameterRegistry,
  RouteQueryInput,
  RouteRegistry,
  RouteResponseInput,
  RouteSourceInput,
  RouteSourceMapInput,
  RouteSourceRef,
  RouteSourceSelector,
  RoutesDefinitionBuilder,
} from './route.types.js';

type MutableRouteDefinition = {
  -readonly [K in keyof RouteDefinition]: RouteDefinition[K];
};

type NormalizedDefineRoutesInput = {
  readonly params?: RouteParameterRegistry;
  readonly routes: Record<string, RouteDefinition>;
};

export interface DefineRoutesOptions extends OptionalResourceContext {
  name: string;
}

export function defineRoutes(options: DefineRoutesOptions, input?: DefineRoutesInputLike): RouteRegistry | RoutesDefinitionBuilder {
  if (!input) {
    return new RoutesRootBuilder(options);
  }

  return createRouteRegistry(options, normalizeRoutesInput(input));
}

function createRouteRegistry(options: DefineRoutesOptions, normalized: NormalizedDefineRoutesInput): RouteRegistry {
  const normalizedRoutes = Object.fromEntries(
    Object.entries(normalized.routes).map(([key, route]) => [key, withRouteMeta(options, key, route)]),
  );

  const registry: RouteRegistry = {
    name: options.name,
    routes: normalizedRoutes,
    params: normalized.params,
    ref: {},
  };

  Object.assign(registry.ref, createRouteRefs(options, normalizedRoutes));

  return registry;
}

function normalizeRoutesInput(input: DefineRoutesInputLike): NormalizedDefineRoutesInput {
  if ('routes' in input) {
    return {
      params: input.params,
      routes: normalizeObjectRoutes(input.routes),
    };
  }

  return input;
}

function normalizeObjectRoutes(routes: Record<string, RouteDefinitionInput>): Record<string, RouteDefinition> {
  return Object.fromEntries(Object.entries(routes).map(([key, route]) => [key, normalizeRouteDefinition(key, route)]));
}

function normalizeRouteDefinition(key: string, route: RouteDefinitionInput): RouteDefinition {
  if ('operationId' in route) {
    throw new Error(`Route "${key}" must not declare operationId. Operation IDs come from route object keys.`);
  }

  const { tags, ...rest } = route;

  return {
    ...rest,
    codegenTags: route.codegenTags ?? tags,
    sources: normalizeSourceMap(route.source),
    info: normalizeInfo(route.info),
  };
}

class RoutesRootBuilder implements RoutesDefinitionBuilder {
  private rootParams?: RouteParameterRegistry;

  constructor(private readonly options: DefineRoutesOptions) {}

  params(parameters: RouteParameterRegistry): RoutesDefinitionBuilder {
    this.rootParams = parameters;
    return this;
  }

  routes(input: DefineRoutesBuilderInput): RouteRegistry {
    const factory = new RouteFactory();
    const built = input(factory);
    const routes = Object.fromEntries(Object.entries(built).map(([key, builder]) => [key, builder.build()]));

    return createRouteRegistry(this.options, {
      params: this.rootParams,
      routes,
    });
  }
}

class RouteFactory implements RouteOperationFactory {
  get(path: string): RouteOperationBuilder {
    return new FluentRouteOperationBuilder(HttpMethod.get, path);
  }

  post(path: string): RouteOperationBuilder {
    return new FluentRouteOperationBuilder(HttpMethod.post, path);
  }

  put(path: string): RouteOperationBuilder {
    return new FluentRouteOperationBuilder(HttpMethod.put, path);
  }

  patch(path: string): RouteOperationBuilder {
    return new FluentRouteOperationBuilder(HttpMethod.patch, path);
  }

  delete(path: string): RouteOperationBuilder {
    return new FluentRouteOperationBuilder(HttpMethod.delete, path);
  }
}

class FluentRouteOperationBuilder implements RouteOperationBuilder {
  private readonly route: MutableRouteDefinition;

  constructor(method: RouteDefinition['method'], path: string) {
    this.route = {
      method,
      path,
    };
  }

  summary(summary: string): RouteOperationBuilder {
    this.route.summary = summary;
    return this;
  }

  description(description: string): RouteOperationBuilder {
    this.route.description = description;
    return this;
  }

  query(query: RouteQueryInput): RouteOperationBuilder {
    this.route.query = query;
    return this;
  }

  body(body: RouteBodyInput): RouteOperationBuilder {
    this.route.body = body;
    return this;
  }

  response(response: RouteResponseInput): RouteOperationBuilder {
    this.route.response = response;
    return this;
  }

  on(status: number, response: RouteResponseInput): RouteOperationBuilder {
    this.route.responses = {
      ...(this.route.responses ?? {}),
      [status]: response,
    };
    return this;
  }

  ui(roleOrMeta: CodegenUiInput): RouteOperationBuilder {
    this.route.ui = normalizeCodegenUiInput(roleOrMeta);
    return this;
  }

  access(access: AccessRef): RouteOperationBuilder {
    this.route.access = access;
    return this;
  }

  effects(effects: CodegenOperationEffects): RouteOperationBuilder {
    this.route.effects = effects;
    return this;
  }

  runtime(runtime: RuntimeRouteConfig): RouteOperationBuilder {
    this.route.runtime = runtime;
    return this;
  }

  cache(configure: (cache: RouteCacheBuilder) => RouteCacheInvalidateBuilder | RouteCacheBuilder): RouteOperationBuilder {
    const builder = new FluentRouteCacheBuilder();
    configure(builder);
    this.route.cache = builder.build();
    return this;
  }

  tags(tags: readonly string[]): RouteOperationBuilder {
    this.route.codegenTags = tags;
    return this;
  }

  source(responseField: string, configure: (source: RouteSourceSelector) => RouteSourceSelector): RouteOperationBuilder {
    this.route.sources = {
      ...(this.route.sources ?? {}),
      [responseField]: {
        responseField,
        ...configure(new FluentRouteSourceSelector()).build(),
      },
    };
    return this;
  }

  info(info: InfoInput): RouteOperationBuilder {
    this.route.info = normalizeInfo(info);
    return this;
  }

  build(): RouteDefinition {
    return {
      ...this.route,
      sources: normalizeSourceMap(this.route.sources),
    };
  }
}

class FluentRouteCacheBuilder implements RouteCacheBuilder {
  readonly invalidate = new FluentRouteCacheInvalidateBuilder();

  build(): RouteCacheConfig {
    const invalidate = this.invalidate.build();
    return {
      ...(invalidate.operations.length > 0 ? { invalidate } : {}),
    };
  }
}

class FluentRouteCacheInvalidateBuilder implements RouteCacheInvalidateBuilder {
  private readonly operations: string[] = [];

  on(operationId: string): RouteCacheInvalidateBuilder {
    if (!operationId || typeof operationId !== 'string') {
      throw new Error('Cache invalidation operation ID must be a non-empty string.');
    }

    this.operations.push(operationId);
    return this;
  }

  build(): RouteCacheInvalidationConfig {
    return {
      operations: [...new Set(this.operations)],
    };
  }
}

class FluentRouteSourceSelector implements RouteSourceSelector {
  private source: { key?: string; label?: string } = {};

  key(field: string): RouteSourceSelector {
    this.source.key = field;
    return this;
  }

  label(field: string): RouteSourceSelector {
    this.source.label = field;
    return this;
  }

  build(): RouteSourceInput {
    if (!this.source.key || !this.source.label) {
      throw new Error('Route source requires both key(...) and label(...).');
    }

    return {
      key: this.source.key,
      label: this.source.label,
    };
  }
}

function normalizeSourceMap(source: RouteSourceMapInput | RouteDefinition['sources'] | undefined): RouteDefinition['sources'] {
  if (!source) return undefined;

  return Object.fromEntries(
    Object.entries(source).map(([responseField, definition]) => [
      responseField,
      {
        responseField,
        key: definition.key,
        label: definition.label,
      },
    ]),
  );
}

function withRouteMeta(options: DefineRoutesOptions, key: string, route: RouteDefinition): RouteDefinition {
  const operationId = createOperationId(key);

  return {
    ...route,
    operationId,
    ui: normalizeCodegenUiInput(route.ui),
    tags: [options.resource?.tag].filter((tag): tag is string => Boolean(tag)),
    meta: {
      kind: XCodegenKind.dto,
      role: XCodegenDtoRole.body,
      ...(!options.resource ? { shared: true } : {}),
      resource: options.resource
        ? {
            name: options.resource.alias,
            path: options.resource.folders,
          }
        : undefined,
    },
  };
}

function createRouteRefs(options: DefineRoutesOptions, routes: Record<string, RouteDefinition>): Record<string, RouteRef> {
  return Object.fromEntries(
    Object.entries(routes).map(([key, route]) => {
      const sourceRefs: Record<string, RouteSourceRef> = {};
      const routeRef = {
        id: createScopedId(options, EngineIdPart.route, key),
        name: key,
        kind: RefKind.route,
        routeKey: key,
        method: route.method,
        path: route.path,
        resource: options.resource
          ? {
              name: options.resource.alias,
              path: options.resource.folders,
            }
          : undefined,
        query: route.query,
        body: route.body,
        response: route.response,
        access: route.access,
        runtime: route.runtime,
        sources: sourceRefs,
      } as RouteRef;

      for (const [sourceName, source] of Object.entries(route.sources ?? {})) {
        sourceRefs[sourceName] = {
          kind: 'route-source',
          name: sourceName,
          route: routeRef,
          source,
        };
      }

      const sourceValues = Object.values(sourceRefs);
      if (sourceValues.length === 1) {
        Object.defineProperty(routeRef, 'defaultSource', {
          enumerable: true,
          configurable: true,
          value: sourceValues[0],
        });
      }

      return [key, routeRef] as const;
    }),
  );
}

function createOperationId(key: string): string {
  return key;
}

function createScopedId(options: DefineRoutesOptions, ...parts: string[]): string {
  if (!options.resource) return createEngineId(...parts);

  return createEngineId(EngineIdPart.resource, options.resource.name, ...parts);
}
