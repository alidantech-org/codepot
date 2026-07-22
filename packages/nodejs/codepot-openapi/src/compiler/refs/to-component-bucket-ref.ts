import { OpenApiRefPattern } from '../../openapi/ref-patterns.js';
import type { ParameterRef, RequestBodyRef, ResponseRef } from '../../refs/ref.types.js';
import type { RefResolver } from './ref-resolver.types.js';

export function toParameterOpenApiRef(ref: ParameterRef, resolver: RefResolver) {
  const name = resolver.parameters.get(ref.id);
  if (!name) throw new Error(`Unable to resolve parameter ref: ${ref.id}`);
  return { $ref: `${OpenApiRefPattern.parameters}${name}` };
}

export function toRequestBodyOpenApiRef(ref: RequestBodyRef, resolver: RefResolver) {
  const name = resolver.requestBodies.get(ref.id);
  if (!name) throw new Error(`Unable to resolve request body ref: ${ref.id}`);
  return { $ref: `${OpenApiRefPattern.requestBodies}${name}` };
}

export function toResponseOpenApiRef(ref: ResponseRef, resolver: RefResolver) {
  const name = resolver.responses.get(ref.id);
  if (!name) throw new Error(`Unable to resolve response ref: ${ref.id}`);
  return { $ref: `${OpenApiRefPattern.responses}${name}` };
}
