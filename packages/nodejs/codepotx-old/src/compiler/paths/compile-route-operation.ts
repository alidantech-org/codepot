import type { OpenApiOperation } from '../../openapi/openapi.types.js';
import type {
  RouteDefinition,
  RouteBodyInput,
  RouteResponseInput,
  RouteResponseObjectInput,
  RouteBodyObjectInput,
} from '../../routes/route.types.js';
import type { VersionContract } from '../../version/version-contract.types.js';
import type { CompilerContext } from '../compiler-context.js';
import { applyCodegenMetadata } from '../../codegen/apply-codegen-extensions.js';
import type { CodegenMetadata } from '../../codegen/codegen-extension.types.js';
import { ContentType } from '../../output/output.constants.js';
import { RefKind } from '../../refs/ref-kind.js';
import type { RequestBodyRef, ResponseRef, ComponentRef } from '../../refs/ref.types.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';
import { toParameterOpenApiRef, toRequestBodyOpenApiRef, toResponseOpenApiRef } from '../refs/to-component-bucket-ref.js';
import { compileRouteParameters } from './compile-route-parameters.js';
import { compileRouteSchema } from './compile-route-schema.js';
import { isRefUsage } from '../../validation/ref-usage-guards.js';
import { isComponentRef } from '../../validation/ref-guards.js';
import { createOperationParameterTargetMeta } from './parameter-target-metadata.js';

export function compileRouteOperation(
  route: RouteDefinition,
  resolver: RefResolver,
  defaultResponses: Record<number, ResponseRef | RouteResponseInput> = {},
  contract?: VersionContract,
  context?: CompilerContext,
): OpenApiOperation {
  const operation: OpenApiOperation = {
    operationId: route.operationId,
    tags: route.tags,
    summary: route.summary,
    description: route.description,
    responses: compileResponses(route, resolver, defaultResponses),
  };

  const parameters = [
    ...compileRouteParameters(route.query, 'query', resolver, contract),
  ];

  if (parameters.length > 0) {
    operation.parameters = parameters;
  }

  if (route.body) {
    operation.requestBody = compileRequestBody(route.body, resolver);
  }

  // Apply route.meta if present (for other metadata)
  if (route.meta) {
    const codegenMeta: CodegenMetadata = route.meta;
    applyCodegenMetadata(operation as unknown as Record<string, unknown>, codegenMeta);
  }

  return operation;
}

function compileRequestBody(body: RouteBodyInput, resolver: RefResolver): unknown {
  // Handle object-style input
  if (isBodyObjectInput(body)) {
    return {
      required: body.required ?? true,
      description: body.description,
      content: {
        [body.contentType ?? ContentType.json]: {
          schema: compileRouteSchema(body.schema, resolver),
        },
      },
    };
  }

  // Handle legacy RequestBodyRef
  if (isRequestBodyRef(body)) {
    return toRequestBodyOpenApiRef(body, resolver);
  }

  // Handle direct schema input
  return {
    required: true,
    content: {
      [ContentType.json]: {
        schema: compileRouteSchema(body, resolver),
      },
    },
  };
}

function isBodyObjectInput(body: RouteBodyInput): body is RouteBodyObjectInput {
  return typeof body === 'object' && 'schema' in body;
}

function compileResponses(
  route: RouteDefinition,
  resolver: RefResolver,
  defaultResponses: Record<number, ResponseRef | RouteResponseInput>,
): Record<string, unknown> {
  const responses: Record<string, unknown> = {};

  for (const [status, response] of Object.entries(defaultResponses)) {
    if (isResponseRef(response)) {
      responses[status] = toResponseOpenApiRef(response, resolver);
    } else {
      responses[status] = compileResponseValue(`Default ${status}`, response, resolver);
    }
  }

  if (route.response) {
    responses[200] = compileResponseValue('Success', route.response, resolver);
  }

  for (const [status, response] of Object.entries(route.responses ?? {})) {
    responses[status] = compileResponseValue(`Response ${status}`, response, resolver);
  }

  if (Object.keys(responses).length === 0) {
    responses[204] = { description: 'No content' };
  }

  return responses;
}

function compileResponseValue(description: string, response: RouteResponseInput, resolver: RefResolver): unknown {
  // Handle object-style input
  if (isResponseObjectInput(response)) {
    return typedResponse(response.description ?? description, compileRouteSchema(response.schema, resolver), response.contentType);
  }

  // Handle legacy ResponseRef
  if (isResponseRef(response)) {
    return toResponseOpenApiRef(response, resolver);
  }

  // Handle direct schema input
  return typedResponse(description, compileRouteSchema(response, resolver));
}

function isResponseObjectInput(response: RouteResponseInput): response is RouteResponseObjectInput {
  return typeof response === 'object' && 'schema' in response;
}

function typedResponse(description: string, schema: unknown, contentType: string = ContentType.json): Record<string, unknown> {
  return {
    description,
    content: {
      [contentType]: {
        schema,
      },
    },
  };
}

function isRequestBodyRef(value: unknown): value is RequestBodyRef {
  return isRefKind(value, RefKind.requestBody);
}

function isResponseRef(value: unknown): value is ResponseRef {
  return isRefKind(value, RefKind.response);
}

function isRefKind(value: unknown, kind: string): boolean {
  return !!value && typeof value === 'object' && 'kind' in value && value.kind === kind;
}
