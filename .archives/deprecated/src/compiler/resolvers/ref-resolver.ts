// src/compiler/context/ref-resolver.ts

import { createIrRefPath, IrRefSection } from '@/contract/constants';

import type { Ref } from '@/contract/types/ir/ref';

// ============================================================================
// RESOLVER INPUT
// ============================================================================

export interface RefResolverInput {
  readonly path: string;
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Checks whether an unknown value is a direct IR ref path string.
 */
function isRefPathString(input: unknown): input is string {
  return typeof input === 'string' && input.length > 0;
}

/**
 * Checks whether an unknown value is an object containing an IR ref path.
 */
function isRefResolverInput(input: unknown): input is RefResolverInput {
  if (input === null || typeof input !== 'object') return false;

  const value = input as Partial<RefResolverInput>;

  return typeof value.path === 'string' && value.path.length > 0;
}

/**
 * Converts unknown resolver input into a stable IR ref path.
 */
function assertRefPath(input: unknown): string {
  if (isRefPathString(input)) return input;

  if (isRefResolverInput(input)) return input.path;

  throw new Error('Expected IR ref path string or { path } ref resolver input.');
}

// ============================================================================
// BASE RESOLVER
// ============================================================================

/**
 * Resolver-style entry point for creating compiled Codepot refs.
 *
 * All resolvers expose an unknown-input function so passes can pass raw
 * authoring/compiler values while the resolver owns validation.
 */
export function resolveRef<TTarget = unknown>(input: unknown): Ref<TTarget> {
  return {
    $ref: assertRefPath(input),
  };
}

/**
 * Creates a compiled Codepot JSON/YAML reference from a known path.
 */
export function irRef<TTarget = unknown>(path: string): Ref<TTarget> {
  return resolveRef<TTarget>(path);
}

// ============================================================================
// CONTENT TYPE REFS
// ============================================================================

/**
 * Creates a reference to a compiled content type.
 */
export function contentTypeRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.content_types, key));
}

// ============================================================================
// PROPERTY REFS
// ============================================================================

/**
 * Creates a reference to a compiled primitive property.
 */
export function propertyPrimitiveRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.properties, IrRefSection.primitives, key));
}

/**
 * Creates a reference to a compiled enum property.
 */
export function propertyEnumRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.properties, IrRefSection.enums, key));
}

/**
 * Creates a reference to a compiled composite property.
 */
export function propertyCompositeRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.properties, IrRefSection.composites, key));
}

// ============================================================================
// SCHEMA REFS
// ============================================================================

/**
 * Creates a reference to a compiled entity schema.
 */
export function entityRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.schemas, IrRefSection.entities, key));
}

/**
 * Creates a reference to a compiled entity field.
 */
export function entityFieldRef<TTarget = unknown>(entityKey: string, fieldKey: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.schemas, IrRefSection.entities, entityKey, IrRefSection.fields, fieldKey));
}

/**
 * Creates a reference to a compiled field set.
 */
export function fieldSetRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.schemas, IrRefSection.field_sets, key));
}

/**
 * Creates a reference to a compiled model schema.
 */
export function modelRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.schemas, IrRefSection.models, key));
}

/**
 * Creates a reference to a compiled DTO schema.
 */
export function dtoRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.schemas, IrRefSection.dtos, key));
}

/**
 * Creates a reference to a compiled params schema.
 */
export function paramsRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.schemas, IrRefSection.params, key));
}

// ============================================================================
// RESPONSE REFS
// ============================================================================

/**
 * Creates a reference to a compiled error response.
 */
export function errorResponseRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.responses, IrRefSection.errors, key));
}

// ============================================================================
// SECURITY REFS
// ============================================================================

/**
 * Creates a reference to a compiled security credential.
 */
export function securityCredentialRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.security, IrRefSection.credentials, key));
}

/**
 * Creates a reference to a compiled security principal.
 */
export function securityPrincipalRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.security, IrRefSection.principals, key));
}

/**
 * Creates a reference to a compiled security policy.
 */
export function securityPolicyRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.security, IrRefSection.policies, key));
}

// ============================================================================
// RESOURCE REFS
// ============================================================================

/**
 * Creates a reference to a compiled resource.
 */
export function resourceRef<TTarget = unknown>(key: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.resources, key));
}

/**
 * Creates a reference to a compiler-generated operation inside a resource.
 */
export function operationRef<TTarget = unknown>(resourceKey: string, operationKey: string): Ref<TTarget> {
  return irRef(createIrRefPath(IrRefSection.resources, resourceKey, IrRefSection.operations, operationKey));
}
