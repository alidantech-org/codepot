import type {
  CompiledOperation,
  CompiledResource,
  Diagnostic,
} from '@/contract/index';
import type { ResourceBuilder } from '../../resource/resource.types';
import type { RouteDefinition } from '../../routes/route.types';
import type { VersionContract } from '../../version/version.types';
import { inlineUse, schemaUse } from '../schema/schema-normalizer';
import {
  accessRef,
  bodySchema,
  docsProperty,
  joinRoutePath,
  jsonObject,
  jsonValue,
  noContent,
  owner,
  required,
  responseSchema,
} from '../shared/compiler-values';

export interface CompiledResourceOperations {
  readonly resource: CompiledResource;
  readonly operations: readonly CompiledOperation[];
}

export function compileResource(
  resource: ResourceBuilder,
  contract: VersionContract,
  diagnostics: Diagnostic[],
): CompiledResourceOperations {
  const operations = resource.routeRegistries.flatMap((registry) =>
    Object.entries(registry.routes).map(([key, route]) =>
      compileOperation(key, route, resource, contract, diagnostics),
    ),
  );
  const resourceAccessRef = accessRef(resource.context.access);

  return {
    resource: {
      id: `resource:${resource.context.name}`,
      key: resource.context.name,
      name: resource.context.alias,
      route: resource.context.route,
      folders: resource.context.folders,
      tags: resource.context.tags,
      operationIds: operations.map((operation) => operation.id),
      ...(resourceAccessRef ? { accessRef: resourceAccessRef } : {}),
      hookRefs: resource.hookComponents.flatMap((registry) =>
        registry.definitions.map((hook) =>
          `hook:${owner(hook.owner)}:${hook.key}`,
        ),
      ),
      ...(resource.context.ui ? { frontend: resource.context.ui } : {}),
      ...docsProperty(resource.context.info),
    },
    operations,
  };
}

function compileOperation(
  key: string,
  route: RouteDefinition,
  resource: ResourceBuilder,
  contract: VersionContract,
  diagnostics: Diagnostic[],
): CompiledOperation {
  const operationId = route.operationId ?? key;
  const path = joinRoutePath(resource.context.route, route.path);
  const responses = new Map<number, unknown>();
  for (const [status, response] of Object.entries(contract.defaultResponses)) {
    responses.set(Number(status), response);
  }
  for (const [status, response] of Object.entries(route.responses ?? {})) {
    responses.set(Number(status), response);
  }
  if (route.response) responses.set(200, route.response);
  if (responses.size === 0) {
    diagnostics.push({
      code: 'AUTHORING_OPERATION_NO_RESPONSE',
      severity: 'warning',
      layer: 'authoring',
      message: `Operation ${operationId} does not declare a response.`,
    });
  }

  return {
    id: `operation:${operationId}`,
    key,
    name: operationId,
    operationId,
    resourceId: `resource:${resource.context.name}`,
    method: route.method,
    path,
    tags: [...new Set([...resource.context.tags, ...(route.tags ?? [])])],
    parameters: pathParameters(path),
    ...(route.body
      ? {
          requestBody: {
            id: `request-body:${operationId}`,
            key: `${operationId}:body`,
            name: `${operationId}:body`,
            required: required(route.body),
            content: [{
              mediaType: 'application/json',
              schema: schemaUse(bodySchema(route.body)),
            }],
          },
        }
      : {}),
    responses: [...responses.entries()]
      .sort(([left], [right]) => left - right)
      .map(([status, response]) => ({
        id: `response:${operationId}:${status}`,
        key: String(status),
        name: String(status),
        status,
        content: noContent(response)
          ? []
          : [{ mediaType: 'application/json', schema: schemaUse(responseSchema(response)) }],
        headers: [],
      })),
    ...(route.access
      ? { accessRef: `access:${owner(route.access.owner)}:${route.access.key}` }
      : {}),
    hookRefs: Object.values(route.runtime?.hooks ?? {}).map((hook) =>
      `hook:${owner(hook.definition.owner)}:${hook.key}`,
    ),
    effects: Object.entries(route.effects ?? {}).map(([kind, value]) => ({
      kind,
      value: jsonValue(value),
    })),
    cacheInvalidates: route.cache?.invalidate?.operations ?? [],
    ...docsProperty(route.info),
    metadata: jsonObject({
      codegenTags: route.codegenTags ?? [],
      meta: route.meta ?? {},
      ui: route.ui ?? null,
      sources: route.sources ?? {},
    }),
  };
}

function pathParameters(path: string): CompiledOperation['parameters'] {
  return Array.from(path.matchAll(/:([A-Za-z_][A-Za-z0-9_]*)/g), (match) => match[1])
    .filter((name): name is string => name !== undefined)
    .map((name) => ({
      id: `parameter:path:${name}`,
      key: name,
      name,
      location: 'path',
      schema: inlineUse({ kind: 'primitive', primitive: 'string', constraints: [] }),
      required: true,
    }));
}
