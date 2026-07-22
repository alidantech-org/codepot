import type { CodegenKind, CodegenMetadata } from './codegen-extension.types.js';

/**
 * Resolves the correct x-codegen.kind based on actual schema shape.
 *
 * Important rule:
 * Schema shape wins over requested metadata when the requested metadata is unsafe.
 *
 * New valid kinds:
 * - primitive
 * - enum
 * - model
 * - dto
 *
 * Priority rules:
 * 1. enum schema shape always resolves to kind: enum
 * 2. object/allOf schemas resolve to requested dto/model, otherwise model
 * 3. scalar schemas resolve to primitive
 * 4. array schemas resolve to requested dto/model when object-like usage is requested,
 *    otherwise primitive
 * 5. unknown schemas fall back to requested kind, otherwise primitive
 */
export function resolveCodegenKind(schema: Record<string, unknown>, requestedKind?: CodegenKind): CodegenKind {
  // First, unwrap nullable unions (anyOf/oneOf with null)
  const unwrapped = unwrapNullableUnion(schema);
  if (unwrapped) {
    return resolveCodegenKind(unwrapped, requestedKind);
  }

  if (isEnumShape(schema)) {
    return 'enum';
  }

  if (isObjectShape(schema)) {
    if (requestedKind === 'dto') return 'dto';
    if (requestedKind === 'model') return 'model';

    return 'model';
  }

  if (isScalarShape(schema)) {
    return 'primitive';
  }

  if (isArrayShape(schema)) {
    if (requestedKind === 'dto') return 'dto';
    if (requestedKind === 'model') return 'model';

    return 'primitive';
  }

  return requestedKind ?? 'primitive';
}

/**
 * Checks if a schema is an enum schema based on its shape.
 */
export function isEnumSchema(schema: Record<string, unknown>): boolean {
  return resolveCodegenKind(schema) === 'enum';
}

/**
 * Checks if a schema is a model-like object schema.
 */
export function isModelSchema(schema: Record<string, unknown>): boolean {
  return resolveCodegenKind(schema) === 'model';
}

/**
 * Checks if a schema is a DTO-like object schema.
 */
export function isDtoSchema(schema: Record<string, unknown>, requestedKind?: CodegenKind): boolean {
  return resolveCodegenKind(schema, requestedKind) === 'dto';
}

/**
 * Checks if a schema is any object-like schema.
 */
export function isObjectSchema(schema: Record<string, unknown>): boolean {
  const kind = resolveCodegenKind(schema);
  return kind === 'model' || kind === 'dto';
}

/**
 * Checks if a schema is a primitive schema.
 */
export function isPrimitiveSchema(schema: Record<string, unknown>): boolean {
  return resolveCodegenKind(schema) === 'primitive';
}

/**
 * Strips invalid inheritance metadata from enum and primitive schemas.
 *
 * Enum and primitive schemas should not have model inheritance metadata.
 */
export function stripNonObjectInheritanceMetadata(metadata: Record<string, unknown> | CodegenMetadata): Record<string, unknown> {
  const { inherits, ...rest } = metadata as Record<string, unknown>;
  return rest;
}

/**
 * Backward-compatible alias.
 *
 * Prefer stripNonObjectInheritanceMetadata.
 */
export function stripEnumInheritanceMetadata(metadata: Record<string, unknown> | CodegenMetadata): Record<string, unknown> {
  return stripNonObjectInheritanceMetadata(metadata);
}

function unwrapNullableUnion(schema: Record<string, unknown>): Record<string, unknown> | undefined {
  const union = Array.isArray(schema.anyOf) ? schema.anyOf : Array.isArray(schema.oneOf) ? schema.oneOf : undefined;

  if (!union) return undefined;

  const nonNull = union.filter((item) => {
    return item && typeof item === 'object' && item.type !== 'null';
  });

  // If there's exactly one non-null schema, unwrap it
  return nonNull.length === 1 ? (nonNull[0] as Record<string, unknown>) : undefined;
}

function isEnumShape(schema: Record<string, unknown>): boolean {
  return Array.isArray(schema.enum);
}

function isObjectShape(schema: Record<string, unknown>): boolean {
  return (
    schema.type === 'object' ||
    Boolean(schema.properties) ||
    Array.isArray(schema.allOf) ||
    Array.isArray(schema.anyOf) ||
    Array.isArray(schema.oneOf)
  );
}

function isScalarShape(schema: Record<string, unknown>): boolean {
  // Handle OpenAPI 3.1 type arrays for nullable primitives
  if (Array.isArray(schema.type)) {
    const types = schema.type as unknown[];
    // If the type array contains scalar types, treat as scalar
    const scalarTypes = types.filter((t) => t === 'string' || t === 'number' || t === 'integer' || t === 'boolean' || t === 'null');
    return scalarTypes.length > 0;
  }

  return (
    schema.type === 'string' || schema.type === 'number' || schema.type === 'integer' || schema.type === 'boolean' || schema.type === 'null'
  );
}

function isArrayShape(schema: Record<string, unknown>): boolean {
  return schema.type === 'array';
}
