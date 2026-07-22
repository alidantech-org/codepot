import type { ComponentRef, RouteRef } from '../refs/ref.types.js';
import { RefKind } from '../refs/ref-kind.js';
import type { RefUsage } from '../refs/ref-usage.types.js';
import type { VersionContract } from '../version/version-contract.types.js';
import { isRefUsage } from '../validation/ref-usage-guards.js';
import { isComponentRef } from '../validation/ref-guards.js';
import { expressPathToOpenApi, normalizeOpenApiPath } from './paths/express-path-to-openapi.js';
import type { RefResolver } from './refs/ref-resolver.types.js';
import type {
  FrontendBuilder,
  FrontendComponentDefinition,
  FrontendComponentRef,
  FrontendOperationUsesInput,
  FrontendScreenDefinition,
} from '../frontend/frontend.types.js';

interface OperationMetadata {
  readonly operationId: string;
  readonly method: string;
  readonly path: string;
  readonly resource?: unknown;
}

export function compileFrontendMetadata(contract: VersionContract, resolver: RefResolver): Record<string, unknown> | undefined {
  if (contract.frontends.length === 0) return undefined;

  validateUniqueFrontendNames(contract.frontends);

  const operations = createOperationRegistry(contract);
  const frontends = Object.fromEntries(
    contract.frontends.map((frontend) => [frontend.context.name, compileFrontend(frontend, resolver, operations)]),
  );

  return Object.keys(frontends).length > 0 ? frontends : undefined;
}

function compileFrontend(
  frontend: FrontendBuilder,
  resolver: RefResolver,
  operations: ReadonlyMap<string, OperationMetadata>,
): Record<string, unknown> {
  return cleanObject({
    name: frontend.context.name,
    title: frontend.context.title,
    description: frontend.context.description,
    routePrefix: frontend.context.routePrefix,
    folders: frontend.context.folders,
    tags: frontend.context.tags,
    info: frontend.context.info,
    components: compileFrontendComponents(frontend, resolver, operations),
    screens: compileFrontendScreens(frontend, resolver, operations),
  });
}

function compileFrontendComponents(
  frontend: FrontendBuilder,
  resolver: RefResolver,
  operations: ReadonlyMap<string, OperationMetadata>,
): Record<string, unknown> | undefined {
  const components = Object.fromEntries(
    frontend.componentRegistries.flatMap((registry) =>
      registry.definitions.map((definition) => [
        definition.key,
        cleanObject({
          name: definition.name,
          title: definition.title,
          description: definition.description,
          props: definition.propsRef ? schemaRef(definition.propsRef, resolver) : undefined,
          schemas: collectSchemaRefs(definition.props, resolver),
          uses: compileUses(definition.uses, operations, `frontend "${frontend.context.name}" component "${definition.key}"`),
          tags: definition.tags,
          info: definition.info,
        }),
      ]),
    ),
  );

  return Object.keys(components).length > 0 ? components : undefined;
}

function compileFrontendScreens(
  frontend: FrontendBuilder,
  resolver: RefResolver,
  operations: ReadonlyMap<string, OperationMetadata>,
): Record<string, unknown> | undefined {
  const routes = new Set<string>();
  const screens = Object.fromEntries(
    frontend.screenRegistries.flatMap((registry) =>
      registry.definitions.map((definition) => {
        validateScreenRoute(frontend, definition, routes);

        return [
          definition.key,
          cleanObject({
            name: definition.name,
            title: definition.title,
            description: definition.description,
            route: definition.route ? normalizeFrontendPath(definition.route) : undefined,
            fullRoute: definition.route ? normalizeFrontendPath(`${frontend.context.routePrefix ?? ''}/${definition.route}`) : undefined,
            params: schemaRefFromValue(definition.params, resolver),
            query: schemaRefFromValue(definition.query, resolver),
            components: compileScreenComponents(frontend, definition.components),
            uses: compileUses(definition.uses, operations, `frontend "${frontend.context.name}" screen "${definition.key}"`),
            tags: definition.tags,
            info: definition.info,
          }),
        ];
      }),
    ),
  );

  return Object.keys(screens).length > 0 ? screens : undefined;
}

function compileScreenComponents(
  frontend: FrontendBuilder,
  components: Record<string, FrontendComponentRef>,
): Record<string, unknown> | undefined {
  const entries = Object.entries(components).map(([slot, component]) => {
    if (!component || component.kind !== 'frontend-component') {
      throw new Error(`Frontend screen component slot "${slot}" must reference a frontend component ref.`);
    }

    if (component.frontend !== frontend.context.name) {
      throw new Error(
        `Frontend "${frontend.context.name}" screen component slot "${slot}" references component "${component.name}" from frontend "${component.frontend}".`,
      );
    }

    if (!frontend.components.ref[component.key]) {
      throw new Error(`Frontend "${frontend.context.name}" screen component slot "${slot}" references unknown component "${component.name}".`);
    }

    return [
      slot,
      {
        $ref: `#/x-codegen/frontends/${frontend.context.name}/components/${component.key}`,
      },
    ] as const;
  });

  return entries.length > 0 ? Object.fromEntries(entries) : undefined;
}

function compileUses(
  uses: FrontendOperationUsesInput,
  operations: ReadonlyMap<string, OperationMetadata>,
  owner: string,
): Record<string, unknown> | undefined {
  const entries = Object.entries(uses).map(([alias, route]) => {
    if (!isRouteRef(route)) {
      throw new Error(`${owner} use "${alias}" must reference a route operation ref.`);
    }

    const operation = operations.get(route.id);
    if (!operation) {
      throw new Error(`${owner} use "${alias}" references unknown route operation "${route.name}".`);
    }

    return [
      alias,
      cleanObject({
        operationId: operation.operationId,
        method: operation.method,
        path: operation.path,
        resource: operation.resource,
      }),
    ] as const;
  });

  return entries.length > 0 ? Object.fromEntries(entries) : undefined;
}

function createOperationRegistry(contract: VersionContract): Map<string, OperationMetadata> {
  const operations = new Map<string, OperationMetadata>();

  for (const resource of contract.resources) {
    for (const registry of resource.routeRegistries) {
      for (const [key, routeRef] of Object.entries(registry.ref)) {
        const route = registry.routes[key];
        if (!route) continue;

        operations.set(routeRef.id, {
          operationId: routeRef.routeKey,
          method: route.method,
          path: normalizeOpenApiPath(expressPathToOpenApi(`${resource.context.route}${route.path}`)),
          resource: {
            $ref: `#/x-codegen/resources/${resource.context.alias}`,
          },
        });
      }
    }
  }

  return operations;
}

function validateUniqueFrontendNames(frontends: readonly FrontendBuilder[]): void {
  const names = new Set<string>();
  for (const frontend of frontends) {
    if (names.has(frontend.context.name)) {
      throw new Error(`Duplicate frontend "${frontend.context.name}". Frontend names must be unique in a version contract.`);
    }
    names.add(frontend.context.name);
  }
}

function validateScreenRoute(frontend: FrontendBuilder, definition: FrontendScreenDefinition, routes: Set<string>): void {
  if (!definition.route) return;

  const route = normalizeFrontendPath(definition.route);
  if (routes.has(route)) {
    throw new Error(`Duplicate frontend screen route "${definition.route}" in frontend "${frontend.context.name}".`);
  }

  routes.add(route);
}

function schemaRefFromValue(value: unknown, resolver: RefResolver): Record<string, string> | undefined {
  if (!value) return undefined;

  const ref = isRefUsage(value) ? value.ref : value;
  if (!isComponentRef(ref)) return undefined;

  return schemaRef(ref, resolver);
}

function schemaRef(ref: ComponentRef, resolver: RefResolver): Record<string, string> {
  const schemaName = resolver.schemas.get(ref.id);
  if (!schemaName) {
    throw new Error(`Unable to resolve frontend schema ref "${ref.name}".`);
  }

  return { $ref: `#/components/schemas/${schemaName}` };
}

function collectSchemaRefs(value: unknown, resolver: RefResolver): readonly Record<string, string>[] | undefined {
  if (!value || typeof value !== 'object') return undefined;

  const refs = new Map<string, Record<string, string>>();
  collectSchemaRefsInternal(value, resolver, refs);
  const values = [...refs.values()];

  return values.length > 0 ? values : undefined;
}

function collectSchemaRefsInternal(value: unknown, resolver: RefResolver, refs: Map<string, Record<string, string>>): void {
  if (!value || typeof value !== 'object') return;

  if (isRefUsage(value)) {
    collectSchemaRefsInternal(value.ref, resolver, refs);
    if (value.usage.extendWith) collectSchemaRefsInternal(value.usage.extendWith, resolver, refs);
    return;
  }

  if (isComponentRef(value)) {
    refs.set(value.id, schemaRef(value, resolver));
    return;
  }

  if (Array.isArray(value)) {
    for (const item of value) collectSchemaRefsInternal(item, resolver, refs);
    return;
  }

  for (const child of Object.values(value)) {
    collectSchemaRefsInternal(child, resolver, refs);
  }
}

function isRouteRef(value: unknown): value is RouteRef {
  return !!value && typeof value === 'object' && (value as { kind?: unknown }).kind === RefKind.route;
}

function normalizeFrontendPath(path: string): string {
  const normalized = path.replace(/\\/g, '/').replace(/\/+/g, '/').replace(/^\/?/, '/');
  return normalized === '/' ? '/' : normalized.replace(/\/$/, '');
}

function cleanObject(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(input)
      .map(([key, value]) => [key, cleanValue(value)] as const)
      .filter(([, value]) => value !== undefined),
  );
}

function cleanValue(value: unknown): unknown {
  if (value === undefined) return undefined;

  if (Array.isArray(value)) {
    const items = value.map(cleanValue).filter((item) => item !== undefined);
    return items.length > 0 ? items : undefined;
  }

  if (value && typeof value === 'object') {
    const cleaned = cleanObject(value as Record<string, unknown>);
    return Object.keys(cleaned).length > 0 ? cleaned : undefined;
  }

  return value;
}
