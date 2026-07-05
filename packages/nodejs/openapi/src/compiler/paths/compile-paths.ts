import type { OpenApiPaths, OpenApiOperation } from '../../openapi/openapi.types.js';
import type { VersionContract } from '../../version/version-contract.types.js';
import type { CompilerContext } from '../compiler-context.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';
import { expressPathToOpenApi, normalizeOpenApiPath } from './express-path-to-openapi.js';
import { resolveCodegenUi } from '../../codegen/codegen-ui.js';
import type { RouteDefinition, RouteParameterMap, RouteParameterRegistry } from '../../routes/route.types.js';
import type { InferredRouteComponents } from './inferred-route-components.types.js';
import { inferRouteComponents } from './infer-route-components.js';
import { compileRouteOperation } from './compile-route-operation.js';
import { extractPathParamNames } from '../../routes/route.types.js';
import type { ComponentRef } from '../../refs/ref.types.js';
import { isRefUsage } from '../../validation/ref-usage-guards.js';
import { isComponentRef } from '../../validation/ref-guards.js';
import { createOperationParameterTargetMeta } from './parameter-target-metadata.js';
import type { AccessRef } from '../../access/access.types.js';
import type { RouteSourceDefinition } from '../../routes/route.types.js';
import type {
  RuntimeHookPhase,
  RuntimeHookRef,
  RuntimeRouteConfig,
  RuntimeTransport,
  RuntimeTransportSideInbound,
  RuntimeTransportSideOutbound,
} from '../../hooks/runtime-hooks.types.js';
import { compactOperationAccess, compileAccessRegistryMetadata } from '../access-registry-metadata.js';

export function compilePaths(
  contract: VersionContract,
  resolver: RefResolver,
  context: CompilerContext,
): {
  paths: OpenApiPaths;
  inferredComponents: InferredRouteComponents;
} {
  const paths: OpenApiPaths = {};
  const allInferredComponents: InferredRouteComponents = {
    parameters: new Map(),
    requestBodies: new Map(),
    responses: new Map(),
  };

  // Create reusable response components for default responses
  if (contract.defaultResponses) {
    for (const [status, response] of Object.entries(contract.defaultResponses)) {
      const componentName = `Default${status}Response`;
      allInferredComponents.responses.set(componentName, {
        name: componentName,
        status: parseInt(status),
        description:
          typeof response === 'object' && response !== null && 'description' in response
            ? (response as { description: string }).description
            : `Default ${status}`,
        schema:
          typeof response === 'object' && response !== null && 'schema' in response
            ? (response as { schema: unknown }).schema
            : (response as any),
        contentType: 'application/json',
        noContent: false,
        operationId: '',
      });
    }
  }

  // First pass: collect all operations and inferred components
  const pathOperations = new Map<
    string,
    Array<{ method: string; operation: OpenApiOperation; inferred: InferredRouteComponents; resourceContext: any; route: RouteDefinition }>
  >();
  const operationIds = collectOperationIds(contract);
  const accessRegistryMetadata = compileAccessRegistryMetadata(contract, resolver);
  const hookRegistry = createHookRegistry(contract);

  for (const resource of contract.resources) {
    for (const registry of resource.routeRegistries) {
      for (const route of Object.values(registry.routes)) {
        const routePath = `${resource.context.route}${route.path}`;
        const fullPath = expressPathToOpenApi(routePath);
        const resourcePath = expressPathToOpenApi(resource.context.route);
        const pathParams = resolvePathParameters(registry.params, routePath, route.operationId, contract);

        // Infer components for this route
        const inferred = inferRouteComponents(
          route,
          pathParams,
          resource.context.name,
          contract.defaultResponses,
          contract.defaults,
          context,
          contract,
        );

        // Merge inferred components
        mergeInferredComponents(allInferredComponents, inferred);

        const operation = compileRouteOperationWithRefs(route, resolver, inferred, context, contract);
        const ui = resolveCodegenUi({
          operationUi: typeof route.ui === 'object' ? route.ui : undefined,
          resourceUi: resource.context.ui,
          method: route.method,
          fullPath,
          resourcePath,
        });
        const access = route.access ?? resource.context.access;
        const resolvedAccess = compactOperationAccess(access, resolver, accessRegistryMetadata.policies);

        mergeOperationCodegen(operation, {
          operation: {
            name: route.operationId,
            role: ui.role,
          },
          ui,
          access: resolvedAccess,
          effects: route.effects,
          runtime: resolveOperationRuntime(route.operationId, route.runtime, hookRegistry),
          cache: resolveOperationCache(route, operationIds),
          tags: mergeTags(contract.tags, resource.context.tags, route.codegenTags),
          sources: resolveOperationSources(route, resolver, contract),
          info: route.info,
        });

        if (isPublicAccess(access)) {
          operation.security = [];
        }

        if (!pathOperations.has(fullPath)) {
          pathOperations.set(fullPath, []);
        }
        pathOperations.get(fullPath)!.push({ method: route.method, operation, inferred, resourceContext: resource.context, route });
      }
    }
  }

  // Second pass: extract common path parameters and build final paths
  for (const [fullPath, operations] of pathOperations.entries()) {
    const pathItem: Record<string, unknown> = {};

    // Add resource metadata to path item
    if (operations.length > 0) {
      const firstOperation = operations[0];
      if (firstOperation.resourceContext) {
        const xCodegen: Record<string, unknown> = {
          resource: {
            $ref: resourceRef(firstOperation.resourceContext.alias || firstOperation.resourceContext.name || firstOperation.resourceContext.key || 'unknown'),
          },
        };

        pathItem['x-codegen'] = xCodegen;
      }
    }

    // Add operations. Keep route parameters operation-level so each operation is self-contained.
    for (const { method, operation } of operations) {
      const filteredOperation = { ...operation };

      // Replace default responses with $ref
      if (contract.defaultResponses) {
        for (const status of Object.keys(contract.defaultResponses)) {
          if (filteredOperation.responses && filteredOperation.responses[status]) {
            const componentName = `Default${status}Response`;
            filteredOperation.responses[status] = { $ref: `#/components/responses/${componentName}` };
          }
        }
      }

      // Remove empty parameters array
      if (filteredOperation.parameters && Array.isArray(filteredOperation.parameters) && filteredOperation.parameters.length === 0) {
        delete filteredOperation.parameters;
      }

      pathItem[method] = filteredOperation;
    }

    paths[normalizeOpenApiPath(fullPath)] = pathItem;
  }

  return { paths, inferredComponents: allInferredComponents };
}

function resourceRef(resourceKey: string): string {
  return `#/x-codegen/resources/${resourceKey}`;
}

function collectOperationIds(contract: VersionContract): ReadonlySet<string> {
  const operationIds = new Set<string>();

  for (const resource of contract.resources) {
    for (const registry of resource.routeRegistries) {
      for (const route of Object.values(registry.routes)) {
        if (route.operationId) {
          operationIds.add(route.operationId);
        }
      }
    }
  }

  return operationIds;
}

function resolveOperationCache(route: RouteDefinition, operationIds: ReadonlySet<string>): Record<string, unknown> | undefined {
  const operations = route.cache?.invalidate?.operations;
  if (!operations || operations.length === 0) return undefined;

  for (const operationId of operations) {
    if (!operationIds.has(operationId)) {
      throw new Error(`Operation "${route.operationId || 'unknown'}" invalidates unknown operation "${operationId}".`);
    }
  }

  return {
    invalidate: {
      operations: [...operations],
    },
  };
}

function mergeOperationCodegen(operation: OpenApiOperation, metadata: Record<string, unknown>): void {
  const current = isRecord(operation['x-codegen']) ? operation['x-codegen'] : {};
  const next = cleanObject({
    ...current,
    ...metadata,
  });

  if (Object.keys(next).length > 0) {
    operation['x-codegen'] = next;
  }
}

function resolveOperationSources(
  route: RouteDefinition,
  resolver: RefResolver,
  contract: VersionContract,
): Record<string, unknown> | undefined {
  if (!route.sources || Object.keys(route.sources).length === 0) return undefined;

  return Object.fromEntries(
    Object.entries(route.sources).map(([name, source]) => [
      name,
      cleanObject({
        responseField: source.responseField,
        item: resolveSourceItem(route, source, resolver, contract),
        key: source.key,
        label: source.label,
      }),
    ]),
  );
}

function resolveSourceItem(
  route: RouteDefinition,
  source: RouteSourceDefinition,
  resolver: RefResolver,
  contract: VersionContract,
): unknown {
  const responseRef = unwrapComponentRefFromRouteValue(route.response);
  if (!responseRef) return undefined;

  const definition = findSchemaDefinition(responseRef.id, contract);
  const field = resolveFieldFromSchemaValue(definition?.value, source.responseField, contract);
  if (!field) {
    throw new Error(`Route "${route.operationId || 'unknown'}" source "${source.responseField}" does not exist on the response schema.`);
  }

  const itemRef = unwrapArrayItemComponentRef(field);

  if (!itemRef) {
    throw new Error(`Route "${route.operationId || 'unknown'}" source "${source.responseField}" must be an array of schema refs.`);
  }

  validateSourceItemFields(route, source, itemRef, contract);

  const schemaName = resolver.schemas.get(itemRef.id) ?? itemRef.name;
  return { $ref: `#/components/schemas/${schemaName}` };
}

function validateSourceItemFields(
  route: RouteDefinition,
  source: RouteSourceDefinition,
  itemRef: ComponentRef,
  contract: VersionContract,
): void {
  const definition = findSchemaDefinition(itemRef.id, contract);
  const fields = resolveSchemaObjectFields(definition?.value, contract);

  if (!fields) return;

  if (!(source.key in fields)) {
    throw new Error(`Route "${route.operationId || 'unknown'}" source "${source.responseField}" key "${source.key}" was not found on "${itemRef.name}".`);
  }

  if (!(source.label in fields)) {
    throw new Error(`Route "${route.operationId || 'unknown'}" source "${source.responseField}" label "${source.label}" was not found on "${itemRef.name}".`);
  }
}

function resolveSchemaObjectFields(value: unknown, contract: VersionContract): Record<string, unknown> | undefined {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined;

  if (isRefUsage(value) && isComponentRef(value.ref)) {
    const definition = findSchemaDefinition(value.ref.id, contract);
    const baseFields = resolveSchemaObjectFields(definition?.value, contract) ?? {};
    const extensionFields = value.usage.extendWith;

    if (extensionFields && typeof extensionFields === 'object' && !Array.isArray(extensionFields) && !('kind' in extensionFields)) {
      return {
        ...baseFields,
        ...(extensionFields as Record<string, unknown>),
      };
    }

    return baseFields;
  }

  if ('kind' in value || 'ref' in value) return undefined;

  return value as Record<string, unknown>;
}

function unwrapComponentRefFromRouteValue(value: unknown): ComponentRef | undefined {
  const unwrapped = isRefUsage(value) ? value.ref : value;
  return isComponentRef(unwrapped) ? unwrapped : undefined;
}

function resolveFieldFromSchemaValue(value: unknown, fieldName: string, contract: VersionContract): unknown {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return undefined;

  if (isRefUsage(value) && isComponentRef(value.ref)) {
    const definition = findSchemaDefinition(value.ref.id, contract);
    const baseField = resolveFieldFromSchemaValue(definition?.value, fieldName, contract);
    const extensionFields = value.usage.extendWith;

    if (extensionFields && typeof extensionFields === 'object' && !Array.isArray(extensionFields) && !(isRefUsage(extensionFields))) {
      return (extensionFields as Record<string, unknown>)[fieldName] ?? baseField;
    }

    return baseField;
  }

  if ('kind' in value || 'ref' in value) return undefined;

  return (value as Record<string, unknown>)[fieldName];
}

function unwrapArrayItemComponentRef(value: unknown): ComponentRef | undefined {
  if (!value) return undefined;

  if (isRefUsage(value)) {
    if (value.usage.array && isComponentRef(value.ref)) return value.ref;
    return undefined;
  }

  return undefined;
}

function resolveOperationRuntime(
  operationId: string | undefined,
  runtime: RuntimeRouteConfig | undefined,
  hookRegistry: ReadonlyMap<string, RuntimeHookRef>,
): Record<string, unknown> | undefined {
  if (!runtime) return undefined;

  const hooks = normalizeRuntimeHooks(operationId, runtime.hooks, hookRegistry);
  const hookRefs = Object.values(hooks).flat();
  const transport = mergeRuntimeTransports(runtime.transport, ...hookRefs.map((hook) => hook.definition.transport));

  return cleanObject({
    transport,
    hooks: Object.fromEntries(
      Object.entries(hooks).map(([phase, phaseHooks]) => [
        phase,
        phaseHooks.map((hook) => ({ $ref: hookRefPointer(hook) })),
      ]),
    ),
  });
}

function normalizeRuntimeHooks(
  operationId: string | undefined,
  hooks: RuntimeRouteConfig['hooks'],
  hookRegistry: ReadonlyMap<string, RuntimeHookRef>,
): Partial<Record<RuntimeHookPhase, RuntimeHookRef[]>> {
  const normalized: Partial<Record<RuntimeHookPhase, RuntimeHookRef[]>> = {};

  for (const [phase, value] of Object.entries(hooks ?? {}) as Array<[RuntimeHookPhase, RuntimeHookRef | readonly RuntimeHookRef[]]>) {
    const phaseHooks = Array.isArray(value) ? value : [value];

    for (const hook of phaseHooks) {
      if (hook.phase !== phase) {
        throw new Error(`Runtime hook "${hook.key}" declares phase "${hook.phase}" but was used in phase "${phase}".`);
      }

      const rootHook = hookRegistry.get(hookRefId(hook));
      if (!rootHook) {
        throw new Error(`Operation "${operationId || 'unknown'}" uses hook "${hookRefId(hook)}", but root hook registry does not define it.`);
      }

      if (
        rootHook.phase !== phase ||
        JSON.stringify(rootHook.definition.transport ?? {}) !== JSON.stringify(hook.definition.transport ?? {}) ||
        rootHook.definition.description !== hook.definition.description
      ) {
        throw new Error(`Operation "${operationId || 'unknown'}" uses hook "${hookRefId(hook)}" under phase "${phase}", but root hook registry defines it with different metadata.`);
      }
    }

    normalized[phase] = phaseHooks as RuntimeHookRef[];
  }

  return normalized;
}

function createHookRegistry(contract: VersionContract): Map<string, RuntimeHookRef> {
  const registry = new Map<string, RuntimeHookRef>();

  for (const resource of contract.resources) {
    for (const hooks of resource.hookComponents) {
      for (const hook of Object.values(hooks.ref)) {
        registry.set(hookRefId(hook), hook);
      }
    }
  }

  return registry;
}

function hookRefId(hook: RuntimeHookRef): string {
  return `${hook.owner.resource.name}.${hook.key}`;
}

function hookRefPointer(hook: RuntimeHookRef): string {
  return `#/x-codegen/resources/${hook.owner.resource.name}/hooks/${hook.key}`;
}

function mergeRuntimeTransports(...transports: Array<RuntimeTransport | undefined>): RuntimeTransport | undefined {
  let inbound: true | RuntimeTransportSideInbound | undefined;
  let outbound: true | RuntimeTransportSideOutbound | undefined;

  for (const transport of transports) {
    inbound = mergeRuntimeTransportSide(inbound, transport?.inbound);
    outbound = mergeRuntimeTransportSide(outbound, transport?.outbound);
  }

  return cleanObject({ inbound, outbound }) as RuntimeTransport | undefined;
}

function mergeRuntimeTransportSide<TSide extends object>(
  current: true | TSide | undefined,
  next: true | TSide | undefined,
): true | TSide | undefined {
  if (current === true || next === true) return true;
  if (!current) return next;
  if (!next) return current;

  return {
    ...current,
    ...Object.fromEntries(Object.entries(next).filter(([, enabled]) => enabled === true)),
  } as TSide;
}

function isPublicAccess(access: AccessRef | undefined): boolean {
  if (!access) return false;
  if (access.definition.context === null) return true;

  const normalizedKey = access.key.toLowerCase();
  return normalizedKey.startsWith('public') || normalizedKey === 'refreshtoken' || normalizedKey === 'refreshsession';
}

function cleanObject(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(input)
      .map(([key, value]) => [key, cleanValue(value)] as const)
      .filter(([, value]) => value !== undefined),
  );
}

function mergeTags(...groups: Array<readonly string[] | undefined>): string[] | undefined {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const group of groups) {
    for (const tag of group ?? []) {
      if (!tag || seen.has(tag)) continue;
      seen.add(tag);
      result.push(tag);
    }
  }

  return result.length > 0 ? result : undefined;
}

function cleanValue(value: unknown): unknown {
  if (value === undefined) return undefined;

  if (Array.isArray(value)) {
    const items = value.map(cleanValue).filter((item) => item !== undefined);
    return items.length > 0 ? items : undefined;
  }

  if (isRecord(value)) {
    const cleaned = cleanObject(value);
    return Object.keys(cleaned).length > 0 ? cleaned : undefined;
  }

  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function resolvePathParameters(
  parameters: RouteParameterRegistry | undefined,
  routePath: string,
  operationId?: string,
  contract?: VersionContract,
): RouteParameterMap | undefined {
  if (!parameters) return undefined;

  const paramNames = extractPathParamNames(routePath);
  if (paramNames.length === 0) return undefined;

  const result: RouteParameterMap = {};
  const availableParams = resolveParameterSchemaFields(parameters, contract);

  for (const paramName of paramNames) {
    const paramRef = availableParams[paramName];
    if (!paramRef) {
      throw new Error(
        `Route "${operationId || 'unknown'}" path "${routePath}" declares path parameter "${paramName}" but it was not declared in defineRoutes().params(...).`,
      );
    }
    result[paramName] = paramRef;
  }

  return result;
}

function resolveParameterSchemaFields(parameters: RouteParameterRegistry, contract?: VersionContract): RouteParameterMap {
  const ref = isRefUsage(parameters) ? parameters.ref : parameters;

  if (!isComponentRef(ref)) {
    return {};
  }

  const definition = findSchemaDefinition(ref.id, contract);

  if (!definition || !isRecord(definition.value) || 'kind' in definition.value || 'ref' in definition.value) {
    return {};
  }

  return definition.value as RouteParameterMap;
}

function findSchemaDefinition(refId: string, contract?: VersionContract): { value: unknown } | undefined {
  if (!contract) return undefined;

  for (const registry of contract.schemaComponents) {
    for (const definition of registry.definitions) {
      if (registry.ref[definition.name]?.id === refId) return definition;
    }
  }

  for (const resource of contract.resources) {
    for (const registry of resource.schemaComponents) {
      for (const definition of registry.definitions) {
        if (registry.ref[definition.name]?.id === refId) return definition;
      }
    }
  }

  return undefined;
}

function mergeInferredComponents(target: InferredRouteComponents, source: InferredRouteComponents): void {
  for (const [key, value] of source.parameters.entries()) {
    target.parameters.set(key, value);
  }
  for (const [key, value] of source.requestBodies.entries()) {
    target.requestBodies.set(key, value);
  }
  for (const [key, value] of source.responses.entries()) {
    target.responses.set(key, value);
  }
}

function compileRouteOperationWithRefs(
  route: RouteDefinition,
  resolver: RefResolver,
  inferred: InferredRouteComponents,
  context: CompilerContext,
  contract?: VersionContract,
): OpenApiOperation {
  const operation = compileRouteOperation(route, resolver, contract?.defaultResponses ?? {}, contract, context);

  // Replace inline requestBody with $ref if inferred component exists
  for (const [key, body] of inferred.requestBodies.entries()) {
    if (body.operationId === route.operationId && operation.requestBody) {
      operation.requestBody = { $ref: `#/components/requestBodies/${body.name}` };
      break;
    }
  }

  // Replace inline responses with $ref if inferred components exist
  for (const [key, response] of inferred.responses.entries()) {
    if (response.operationId === route.operationId && operation.responses) {
      const status = response.status.toString();
      if (operation.responses[status]) {
        operation.responses[status] = { $ref: `#/components/responses/${response.name}` };
      }
    }
  }

  // Add inferred parameters to the operation
  const parameterRefs = getParameterRefsForRoute(route, inferred);
  if (parameterRefs.length > 0) {
    operation.parameters = [...(operation.parameters || []), ...parameterRefs];
  }

  // Add parameters.target if route.query is a ComponentRef or RefUsage<ComponentRef>
  // This happens after inferred params are added so we have the full parameter list
  if (route.query) {
    let queryRef: ComponentRef | undefined;
    if (isComponentRef(route.query)) {
      queryRef = route.query;
    } else if (isRefUsage(route.query) && isComponentRef(route.query.ref)) {
      queryRef = route.query.ref;
    }

    if (queryRef) {
      const schemaName = resolver.schemas.get(queryRef.id);
      // Use schemaName from resolver, or fallback to queryRef.id
      const finalSchemaName = schemaName || queryRef.id;
      if (finalSchemaName) {
        const querySchemaRef = `#/components/schemas/${finalSchemaName}`;
        const operationParameterRefs = (operation.parameters || [])
          .map((p) => {
            if (typeof p === 'object' && p !== null && '$ref' in p) {
              return (p as { $ref: string }).$ref;
            }
            return undefined;
          })
          .filter(Boolean) as string[];

        const parameterTargetMeta = createOperationParameterTargetMeta({
          querySchemaRef,
          operationParameterRefs,
        });

        if (parameterTargetMeta) {
          // Directly set x-codegen with parameters.target
          (operation as unknown as Record<string, unknown>)['x-codegen'] = {
            parameters: parameterTargetMeta,
          };
        }
      }
    }
  }

  return operation;
}

function getParameterRefsForRoute(route: RouteDefinition, inferred: InferredRouteComponents): unknown[] {
  const refs: unknown[] = [];

  // Get parameters that belong to this route's operationId
  for (const param of inferred.parameters.values()) {
    if (param.operationId === route.operationId) {
      refs.push({ $ref: `#/components/parameters/${param.name}` });
    }
  }

  return refs;
}

