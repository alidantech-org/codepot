// src/compiler/resolvers/route-resolver.ts

import type { RoutePathAuthoringDefinition } from '@/contract/types/authoring/7.routes-builder';

import type { ContentDefinition } from '@/contract/types/authoring/content.types';

import type {
  RouteBodyDefinition,
  RouteInlineResponseDefinition,
  RouteMethodDefinition,
  RouteResponseDefinition,
} from '@/contract/types/ir/resource/route/definition';

import type { OperationDefinition } from '@/contract/types/ir/resource/operation/definition';
import type { Ref } from '@/contract/types/ir/ref';
import type { SecurityPolicyDefinition } from '@/contract/types/ir/security/definition';

import type { CompilerContext } from '../context/compiler-context';

import { createOwnedKey } from '../naming/owned-key';
import { contentTypeRef, dtoRef, errorResponseRef, modelRef, operationRef, paramsRef, securityPolicyRef } from './ref-resolver';
import { resolveSecurityPolicy } from './security-resolver';

import { normalizeContentList, normalizeContentTypeKey, normalizeOptionalContentList, resolveContentType } from './content-type-resolver';
import { assertAuthoringRefLike, parseModelRef } from './authoring-ref-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// DERIVED AUTHORING TYPES
// ============================================================================

type AuthoringRouteBody = NonNullable<RoutePathAuthoringDefinition['body']>;

type AuthoringRouteOutput = NonNullable<RoutePathAuthoringDefinition['output']>;

type AuthoringRouteResponses = NonNullable<RoutePathAuthoringDefinition['responses']>;

type AuthoringRouteResponse = AuthoringRouteResponses[number];

// ============================================================================
// INPUTS
// ============================================================================

export interface ResolveRouteInput {
  readonly ctx: CompilerContext;
  readonly resourceKey: string;
  readonly routeKey: string;
  readonly route: RoutePathAuthoringDefinition;
}

export interface ResolvedRoute {
  readonly operationKey: string;
  readonly operation: OperationDefinition;
  readonly method: RouteMethodDefinition;
}

// ============================================================================
// AUTHORING REF HELPERS
// ============================================================================

interface AuthoringRefLike {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
}

interface UsageWrapperLike {
  readonly ref: AuthoringRefLike;
}

/**
 * Checks whether an input value is an authoring ref-like object.
 */
function isAuthoringRef(input: object | null | undefined): input is AuthoringRefLike {
  return (
    input !== null &&
    input !== undefined &&
    'id' in input &&
    typeof input.id === 'string' &&
    'kind' in input &&
    typeof input.kind === 'string' &&
    'key' in input &&
    typeof input.key === 'string'
  );
}

/**
 * Checks whether an input value is a usage wrapper.
 */
function isUsageWrapper(input: object | null | undefined): input is UsageWrapperLike {
  return input !== null && input !== undefined && 'ref' in input && isAuthoringRef(input.ref as object);
}

/**
 * Unwraps route values that may be plain refs or usage wrappers.
 */
function unwrapRefInput(input: object): AuthoringRefLike {
  if (isAuthoringRef(input)) return input;

  if (isUsageWrapper(input)) return input.ref;

  throw new Error('Expected authoring ref or usage wrapper.');
}

// ============================================================================
// ROUTE BODY / OUTPUT SHAPE HELPERS
// ============================================================================

/**
 * Checks whether a route body has a schema.
 */
function hasBodySchema(body: AuthoringRouteBody | null | undefined): body is AuthoringRouteBody & { readonly schema: object } {
  return (
    body !== null &&
    body !== undefined &&
    typeof body === 'object' &&
    'schema' in body &&
    typeof body.schema === 'object' &&
    body.schema !== null
  );
}

/**
 * Reads optional content from any route body/output/response object.
 *
 * Some narrowed route shapes only prove `schema` or `status`, so this helper
 * must not require the input type to already declare a `content` property.
 */
function getContent(input: object | null | undefined): ContentDefinition | readonly ContentDefinition[] | undefined {
  if (input !== null && input !== undefined && 'content' in input) {
    return input.content as ContentDefinition | readonly ContentDefinition[] | undefined;
  }

  return undefined;
}

/**
 * Checks whether a route output has a schema.
 */
function hasOutputSchema(output: AuthoringRouteOutput | null | undefined): output is AuthoringRouteOutput & {
  readonly status: number;
  readonly schema: object;
} {
  return (
    output !== null &&
    output !== undefined &&
    typeof output === 'object' &&
    'status' in output &&
    typeof output.status === 'number' &&
    'schema' in output &&
    typeof output.schema === 'object' &&
    output.schema !== null
  );
}

/**
 * Checks whether a route output is a valid status-only response.
 */
function hasOutputStatus(output: AuthoringRouteOutput | null | undefined): output is AuthoringRouteOutput & { readonly status: number } {
  return output !== null && output !== undefined && typeof output === 'object' && 'status' in output && typeof output.status === 'number';
}

/**
 * Checks whether an inline response has a schema.
 */
function hasInlineResponseSchema(response: AuthoringRouteResponse): response is AuthoringRouteResponse & {
  readonly schema: object;
  readonly content?: ContentDefinition | readonly ContentDefinition[];
} {
  return (
    response !== null &&
    typeof response === 'object' &&
    'schema' in response &&
    typeof response.schema === 'object' &&
    response.schema !== null
  );
}

/**
 * Reads an inline response status.
 */
function getInlineResponseStatus(response: AuthoringRouteResponse): number | undefined {
  if (response !== null && typeof response === 'object' && 'status' in response && typeof response.status === 'number') {
    return response.status;
  }

  return undefined;
}

/**
 * Reads inline response headers.
 */
function getInlineResponseHeaders(response: AuthoringRouteResponse): Record<string, object> | undefined {
  if (
    response !== null &&
    typeof response === 'object' &&
    'headers' in response &&
    response.headers !== null &&
    typeof response.headers === 'object'
  ) {
    return response.headers as Record<string, object>;
  }

  return undefined;
}

// ============================================================================
// CONTENT TYPES
// ============================================================================

/**
 * Registers a route content descriptor in IR and returns its content type ref.
 */
function registerRouteContentType(ctx: CompilerContext, content: ContentDefinition): Ref {
  const key = normalizeContentTypeKey(content);

  ctx.ir.content_types[key] = resolveContentType(content);

  return contentTypeRef(key);
}

/**
 * Resolves required route content into the primary content type ref.
 */
function resolveRequiredContentType(ctx: CompilerContext, content?: ContentDefinition | readonly ContentDefinition[]): Ref {
  const [first] = normalizeContentList(content);

  return registerRouteContentType(ctx, first);
}

/**
 * Resolves all content descriptors into refs, defaulting to JSON when content
 * is missing.
 */
function resolveRequiredContentTypes(ctx: CompilerContext, content?: ContentDefinition | readonly ContentDefinition[]): readonly Ref[] {
  return normalizeContentList(content).map((item) => registerRouteContentType(ctx, item));
}

/**
 * Resolves optional route content descriptors into content type refs.
 */
function resolveOptionalContentTypes(
  ctx: CompilerContext,
  content?: ContentDefinition | readonly ContentDefinition[],
): readonly Ref[] | undefined {
  const list = normalizeOptionalContentList(content);

  if (list === undefined) return undefined;

  return list.map((item) => registerRouteContentType(ctx, item));
}

// ============================================================================
// SCHEMA REFS
// ============================================================================

/**
 * Creates a resource-owned schema key.
 */
function createScopedSchemaKey(resourceKey: string, schemaKey: string): string {
  return createOwnedKey('resource', resourceKey, schemaKey);
}

/**
 * Resolves an authoring schema ref into an IR schema ref.
 */
function resolveRouteSchemaRef(ctx: CompilerContext, resourceKey: string, input: object): Ref {
  const value = unwrapRefInput(input);

  if (value.kind === 'schema.dto') {
    const globalKey = toSnakeCaseKey(value.key);
    const scopedKey = createScopedSchemaKey(resourceKey, value.key);

    if (ctx.ir.schemas.dtos[globalKey] !== undefined) {
      return dtoRef(globalKey);
    }

    if (ctx.ir.schemas.dtos[scopedKey] !== undefined) {
      return dtoRef(scopedKey);
    }

    throw new Error(`Route references unknown DTO "${value.key}". Checked "${globalKey}" and "${scopedKey}".`);
  }

  if (value.kind === 'schema.model') {
    return modelRef(parseModelRef(assertAuthoringRefLike(value)).model_key);
  }

  throw new Error(`Unsupported route schema ref kind "${value.kind}".`);
}

/**
 * Resolves an authoring params ref into an IR params ref.
 */
function resolveRouteParamsRef(ctx: CompilerContext, resourceKey: string, input: object): Ref {
  const value = unwrapRefInput(input);

  if (value.kind === 'schema.params') {
    const globalKey = toSnakeCaseKey(value.key);
    const scopedKey = createScopedSchemaKey(resourceKey, value.key);
    const hasResourceLocalParam = ctx.authoring.resources?.[resourceKey]?.schemas.params?.[value.key] !== undefined;

    if (hasResourceLocalParam && ctx.ir.schemas.params[scopedKey] !== undefined) {
      return paramsRef(scopedKey);
    }

    if (ctx.ir.schemas.params[globalKey] !== undefined) {
      return paramsRef(globalKey);
    }

    if (ctx.ir.schemas.params[scopedKey] !== undefined) {
      return paramsRef(scopedKey);
    }

    throw new Error(`Route references unknown params "${value.key}". Checked "${globalKey}" and "${scopedKey}".`);
  }

  throw new Error(`Unsupported route params ref kind "${value.kind}".`);
}

/**
 * Checks whether a route security value is an inline security policy.
 */
function isInlineSecurityPolicy(input: object | null | undefined): input is { readonly mode: SecurityPolicyDefinition['mode'] } {
  return input !== null && input !== undefined && 'mode' in input && typeof input.mode === 'string';
}

/**
 * Resolves route security into either a security policy ref or inline policy.
 *
 * Authoring supports both:
 * - security.ref.tenantAdmin
 * - security.protected()
 */
function resolveRouteSecurity(input: object): Ref | SecurityPolicyDefinition {
  if (isAuthoringRef(input) || isUsageWrapper(input)) {
    const value = unwrapRefInput(input);

    if (value.kind === 'security.policy') {
      return securityPolicyRef(toSnakeCaseKey(value.key));
    }

    throw new Error(`Unsupported route security ref kind "${value.kind}".`);
  }

  if (isInlineSecurityPolicy(input)) {
    return resolveSecurityPolicy({
      key: 'inline',
      policy: input as never,
    });
  }

  throw new Error('Route security must be a security policy ref or inline security policy.');
}

/**
 * Creates the promoted key for a resource-scoped error.
 */
function createScopedErrorKey(resourceKey: string, errorKey: string): string {
  return createOwnedKey('resource', resourceKey, errorKey);
}

/**
 * Resolves an authoring error ref into an IR error response ref.
 *
 * Lookup order:
 * 1. global error key, e.g. unauthorized
 * 2. resource-scoped promoted key, e.g. resource.users.email_taken
 */
function resolveRouteErrorRef(ctx: CompilerContext, resourceKey: string, input: object): Ref {
  const value = unwrapRefInput(input);

  if (value.kind !== 'error') {
    throw new Error(`Unsupported route error ref kind "${value.kind}".`);
  }

  const globalKey = toSnakeCaseKey(value.key);
  const scopedKey = createScopedErrorKey(resourceKey, value.key);

  if (ctx.ir.responses.errors[globalKey] !== undefined) {
    return errorResponseRef(globalKey);
  }

  if (ctx.ir.responses.errors[scopedKey] !== undefined) {
    return errorResponseRef(scopedKey);
  }

  throw new Error(`Route references unknown error "${value.key}". Checked "${globalKey}" and "${scopedKey}".`);
}

/**
 * Reads the HTTP status for a compiled error response ref.
 */
function getErrorStatusFromRef(ctx: CompilerContext, ref: Ref): number {
  const key = ref.$ref.split('/').at(-1);

  if (!key) {
    throw new Error(`Invalid error response ref "${ref.$ref}".`);
  }

  const error = ctx.ir.responses.errors[key];

  if (error === undefined) {
    throw new Error(`Missing compiled error for ref "${ref.$ref}".`);
  }

  return error.status;
}

// ============================================================================
// BODY / OUTPUT
// ============================================================================

/**
 * Resolves an authoring route body into an IR route body.
 */
function resolveRouteBody(
  ctx: CompilerContext,
  resourceKey: string,
  body: AuthoringRouteBody | null | undefined,
): RouteBodyDefinition | undefined {
  if (!hasBodySchema(body)) return undefined;

  const content = getContent(body);

  return {
    schema: resolveRouteSchemaRef(ctx, resourceKey, body.schema),
    content_type: resolveRequiredContentType(ctx, content),
    content_types: resolveRequiredContentTypes(ctx, content),
  };
}

/**
 * Resolves an authoring route output into an IR route response-like output.
 */
function resolveRouteOutput(
  ctx: CompilerContext,
  resourceKey: string,
  output: AuthoringRouteOutput | null | undefined,
): RouteInlineResponseDefinition | undefined {
  if (!hasOutputStatus(output)) return undefined;

  if (!hasOutputSchema(output)) {
    return {
      status: output.status,
    };
  }

  const content = getContent(output);

  return {
    status: output.status,
    schema: resolveRouteSchemaRef(ctx, resourceKey, output.schema),
    content_type: resolveRequiredContentType(ctx, content),
    content_types: resolveRequiredContentTypes(ctx, content),
  };
}

/**
 * Resolves an inline authoring response into an IR route response.
 */
function resolveInlineResponse(ctx: CompilerContext, resourceKey: string, response: AuthoringRouteResponse): RouteInlineResponseDefinition {
  const output: RouteInlineResponseDefinition = {
    ...(getInlineResponseStatus(response) !== undefined ? { status: getInlineResponseStatus(response) } : {}),
  };

  if (hasInlineResponseSchema(response)) {
    const content = getContent(response);

    output.schema = resolveRouteSchemaRef(ctx, resourceKey, response.schema);
    output.content_type = resolveRequiredContentType(ctx, content);
    output.content_types = resolveRequiredContentTypes(ctx, content);
  }

  const headers = getInlineResponseHeaders(response);

  if (headers !== undefined) {
    output.headers = Object.fromEntries(
      Object.entries(headers).map(([key, schema]) => [toSnakeCaseKey(key), resolveRouteSchemaRef(ctx, resourceKey, schema)]),
    );
  }

  return output;
}

/**
 * Resolves a route response entry.
 */
function resolveRouteResponse(ctx: CompilerContext, resourceKey: string, response: AuthoringRouteResponse): RouteResponseDefinition {
  if (response !== null && typeof response === 'object' && isAuthoringRef(response)) {
    return resolveRouteErrorRef(ctx, resourceKey, response);
  }

  return resolveInlineResponse(ctx, resourceKey, response);
}

// ============================================================================
// OPERATION
// ============================================================================

/**
 * Creates a stable operation key from the authoring route key.
 */
export function createRouteOperationKey(routeKey: string): string {
  return toSnakeCaseKey(routeKey);
}

/**
 * Derives an IR operation definition from an authoring route.
 */
function resolveOperation(ctx: CompilerContext, resourceKey: string, route: RoutePathAuthoringDefinition): OperationDefinition {
  const input: OperationDefinition['input'] = {};
  const output: OperationDefinition['output'] = {};

  if (route.params !== undefined && route.params !== null) {
    input.params = resolveRouteParamsRef(ctx, resourceKey, route.params as object) as OperationDefinition['input']['params'];
  }

  if (route.query !== undefined && route.query !== null) {
    input.query = resolveRouteSchemaRef(ctx, resourceKey, route.query as object) as OperationDefinition['input']['query'];
  }

  if (hasBodySchema(route.body)) {
    input.body = resolveRouteSchemaRef(ctx, resourceKey, route.body.schema) as OperationDefinition['input']['body'];
  }

  if (hasOutputSchema(route.output)) {
    output.result = resolveRouteSchemaRef(ctx, resourceKey, route.output.schema) as OperationDefinition['output']['result'];
  }

  if (route.errors !== undefined) {
    output.errors = route.errors.map((error) =>
      resolveRouteErrorRef(ctx, resourceKey, error as object),
    ) as OperationDefinition['output']['errors'];
  }

  return {
    input,
    output,
  };
}

// ============================================================================
// RESPONSES
// ============================================================================

/**
 * Builds the route method response map from output, errors, and explicit
 * response overrides.
 */
function resolveResponses(
  ctx: CompilerContext,
  resourceKey: string,
  route: RoutePathAuthoringDefinition,
): RouteMethodDefinition['responses'] {
  const responses: RouteMethodDefinition['responses'] = {};

  const output = resolveRouteOutput(ctx, resourceKey, route.output);

  if (output !== undefined) {
    responses[output.status ?? 200] = output;
  }

  for (const error of route.errors ?? []) {
    const errorRef = resolveRouteErrorRef(ctx, resourceKey, error as object);
    const status = getErrorStatusFromRef(ctx, errorRef);

    responses[status] = errorRef;
  }

  for (const [status, response] of Object.entries(route.responses ?? {})) {
    responses[Number(status)] = resolveRouteResponse(ctx, resourceKey, response as AuthoringRouteResponse);
  }

  return responses;
}

// ============================================================================
// RESOLVE
// ============================================================================

/**
 * Resolves one authoring route into a compiled route method and compiler-created
 * operation definition.
 */
export function resolveRoute(input: ResolveRouteInput): ResolvedRoute {
  const { ctx, resourceKey, routeKey, route } = input;
  const operationKey = createRouteOperationKey(routeKey);
  const body = resolveRouteBody(ctx, resourceKey, route.body);

  return {
    operationKey,
    operation: resolveOperation(ctx, resourceKey, route),
    method: {
      operation: operationRef(toSnakeCaseKey(resourceKey), operationKey),

      ...(route.security !== undefined && route.security !== null ? { security: resolveRouteSecurity(route.security as object) } : {}),

      ...(route.params !== undefined && route.params !== null
        ? { params: resolveRouteParamsRef(ctx, resourceKey, route.params as object) }
        : {}),

      ...(route.query !== undefined && route.query !== null
        ? { query: resolveRouteSchemaRef(ctx, resourceKey, route.query as object) }
        : {}),

      ...(body !== undefined ? { body } : {}),

      responses: resolveResponses(ctx, resourceKey, route),
    },
  };
}
