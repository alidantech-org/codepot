import { OpenApiRefPattern } from "../../openapi/ref-patterns.js";
import type { EngineRef } from "../../refs/ref.types.js";
import type { OpenApiRef, RefResolver } from "./ref-resolver.types.js";

export function toOpenApiSchemaRef(
  ref: EngineRef,
  resolver: RefResolver,
): OpenApiRef {
  const schemaName = resolver.schemas.get(ref.id);

  if (!schemaName) {
    throw new Error(`Unable to resolve OpenAPI schema ref: ${ref.id}`);
  }

  return {
    $ref: `${OpenApiRefPattern.schemas}${schemaName}`,
  };
}
