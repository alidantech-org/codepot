// src/contract/builders/define-routes.ts

import type { RouteAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';

import { HttpMethod } from '@/contract/types/authoring/7.routes-builder';

import type {
  RouteContentDefinition,
  RouteDefinitionInput,
  RouteErrorInput,
  RouteHelper,
  RouteMethodChain,
  RouteOutputOptions,
  RouteParamsInput,
  RouteSchemaInput,
  RoutesAuthoringState,
  RoutesBuilder,
  RoutesBuilderResult,
  DefineRoutesFactoryInput,
} from '@/contract/types/authoring/7.routes-builder';

import { content } from '@/contract/helpers/content/content';

import { routeRef } from '@/contract/helpers/refs/authoring-ref-builder';

// ============================================================================
// OPTIONS
// ============================================================================

export interface DefineRoutesOptions {
  readonly resourceKey: string;
  readonly routes: RoutesAuthoringState;
}

// ============================================================================
// DEFAULTS
// ============================================================================

const DEFAULT_CONTENT = [content.json()] as const;

// ============================================================================
// NORMALIZATION HELPERS
// ============================================================================

function normalizeRouteParams(params: RouteParamsInput): RouteParamsInput {
  if (params && typeof params === 'object' && 'params' in params && 'ref' in params) {
    return params.params as RouteParamsInput;
  }

  return params;
}

/**
 * Normalize content - applies default JSON when no content provided and schema exists.
 */
function normalizeContent(
  contentValue?: readonly RouteContentDefinition[] | RouteContentDefinition,
  hasSchema = true,
): readonly RouteContentDefinition[] | undefined {
  // No schema (e.g., 204 no-content) - no content type
  if (!hasSchema) return undefined;

  // No content provided - apply JSON default
  if (contentValue === undefined) return DEFAULT_CONTENT;

  return (Array.isArray(contentValue) ? contentValue : [contentValue]) as readonly RouteContentDefinition[];
}

function isContentDefinition(value: unknown): value is RouteContentDefinition {
  return !!value && typeof value === 'object' && 'type' in value && typeof (value as { type: unknown }).type === 'string';
}

function isContentDefinitionList(value: unknown): value is readonly RouteContentDefinition[] | RouteContentDefinition {
  return isContentDefinition(value) || (Array.isArray(value) && value.every(isContentDefinition));
}

function normalizeOutputOptions(
  contentOrOptions?: readonly RouteContentDefinition[] | RouteContentDefinition | RouteOutputOptions,
): RouteOutputOptions {
  if (contentOrOptions === undefined) return {};

  if (isContentDefinitionList(contentOrOptions)) {
    return {
      content: contentOrOptions,
    };
  }

  return contentOrOptions;
}

function createOutput(
  schema: RouteSchemaInput | undefined,
  status: number,
  contentOrOptions?: readonly RouteContentDefinition[] | RouteContentDefinition | RouteOutputOptions,
) {
  const options = normalizeOutputOptions(contentOrOptions);
  const hasSchema = schema !== undefined;

  return {
    ...options,
    status: options.status ?? status,
    ...(hasSchema ? { schema } : {}),
    content: normalizeContent(options.content, hasSchema),
  };
}

// ============================================================================
// ROUTE CHAIN
// ============================================================================

function createRouteInput(method: HttpMethod, path: string, input: Partial<RouteDefinitionInput> = {}): RouteDefinitionInput {
  return {
    ...input,
    method,
    path,
  };
}

function createRouteChain(method: HttpMethod, path: string, input: Partial<RouteDefinitionInput> = {}): RouteMethodChain {
  const current = createRouteInput(method, path, input);

  return {
    method,
    path,
    description: current.description,
    deprecated: current.deprecated,
    meta: current.meta,

    params(params) {
      return createRouteChain(method, path, {
        ...current,
        params: normalizeRouteParams(params),
      });
    },

    query(query) {
      return createRouteChain(method, path, {
        ...current,
        query,
      });
    },

    body(schema, contentValue) {
      return createRouteChain(method, path, {
        ...current,
        body: {
          schema,
          content: normalizeContent(contentValue, true),
        },
      });
    },

    security(security) {
      return createRouteChain(method, path, {
        ...current,
        security,
      });
    },

    output(schema, contentOrOptions) {
      return {
        ...current,
        output: createOutput(schema, 200, contentOrOptions),
      };
    },

    created(schema, contentOrOptions) {
      return {
        ...current,
        output: createOutput(schema, 201, contentOrOptions),
      };
    },

    noContent(options = {}) {
      return {
        ...current,
        output: {
          ...options,
          status: options.status ?? 204,
        },
      };
    },

    errors(...errors: readonly RouteErrorInput[]) {
      return createRouteChain(method, path, {
        ...current,
        errors,
      });
    },

    responses(responses) {
      return {
        ...current,
        responses,
      };
    },

    operation(operation) {
      return createRouteChain(method, path, {
        ...current,
        operation,
      });
    },
  };
}

const routeHelper: RouteHelper = {
  content,

  get(path) {
    return createRouteChain(HttpMethod.get, path);
  },

  post(path) {
    return createRouteChain(HttpMethod.post, path);
  },

  put(path) {
    return createRouteChain(HttpMethod.put, path);
  },

  patch(path) {
    return createRouteChain(HttpMethod.patch, path);
  },

  delete(path) {
    return createRouteChain(HttpMethod.delete, path);
  },

  options(path) {
    return createRouteChain(HttpMethod.options, path);
  },

  head(path) {
    return createRouteChain(HttpMethod.head, path);
  },
};

// ============================================================================
// STATE HELPERS
// ============================================================================

function createRouteRefs<TInput extends DefineRoutesFactoryInput>(
  resourceKey: string,
  input: TInput,
): Record<keyof TInput & string, RouteAuthoringRef> {
  const refs = {} as Record<keyof TInput & string, RouteAuthoringRef>;

  for (const key of Object.keys(input) as Array<keyof TInput & string>) {
    refs[key] = routeRef(resourceKey, key);
  }

  return refs;
}

function writeRoutes<TInput extends DefineRoutesFactoryInput>(options: DefineRoutesOptions, input: TInput): void {
  for (const [key, value] of Object.entries(input) as [keyof TInput & string, TInput[keyof TInput & string]][]) {
    writeRoute(options, key, value);
  }
}

function writeRoute(options: DefineRoutesOptions, key: string, value: RouteDefinitionInput): void {
  options.routes[key] = value;
}

// ============================================================================
// DEFINE ROUTES
// ============================================================================

export function defineRoutes(options: DefineRoutesOptions): RoutesBuilder {
  const builder: RoutesBuilder = {
    get state() {
      return options.routes;
    },

    define<TInput extends DefineRoutesFactoryInput>(
      routesOrFactory: TInput | ((route: RouteHelper) => TInput),
    ): RoutesBuilderResult<TInput> {
      const input = typeof routesOrFactory === 'function' ? routesOrFactory(routeHelper) : routesOrFactory;

      writeRoutes(options, input);

      return {
        routes: input,
        ref: createRouteRefs(options.resourceKey, input) as RoutesBuilderResult<TInput>['ref'],
      };
    },

    addRoute(key, route) {
      options.routes[key] = route;
      return builder;
    },

    snapshot() {
      return options.routes;
    },
  };

  return builder;
}
