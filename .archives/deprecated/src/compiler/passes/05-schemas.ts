// src/compiler/passes/05-schemas.ts

import type { CompilerContext } from '../context/compiler-context';

import { createOwnedKey } from '../naming/owned-key';
import { resolveDto, resolveParams } from '../resolvers/dto-resolver';
import { resourceRef } from '../resolvers/ref-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// SCOPED KEYS
// ============================================================================

/**
 * Creates a promoted root key for a resource-scoped schema.
 *
 * Format:
 * resource.resource_key.schema_key
 */
function createResourceScopedSchemaKey(resourceKey: string, schemaKey: string): string {
  return createOwnedKey('resource', resourceKey, schemaKey);
}

// ============================================================================
// DTOS
// ============================================================================

/**
 * Compiles authoring DTO schemas into IR DTO schemas.
 */
function compileDtos(ctx: CompilerContext): void {
  for (const [key, dto] of Object.entries(ctx.authoring.schemas.dtos ?? {})) {
    ctx.ir.schemas.dtos[toSnakeCaseKey(key)] = resolveDto({
      key,
      dto,
    });
  }
}

/**
 * Compiles resource-scoped DTOs into root IR DTOs with dotted keys.
 */
function compileResourceDtos(ctx: CompilerContext): void {
  for (const [resourceKey, resource] of Object.entries(ctx.authoring.resources ?? {})) {
    for (const [dtoKey, dto] of Object.entries(resource.schemas.dtos ?? {})) {
      const compiledKey = createResourceScopedSchemaKey(resourceKey, dtoKey);

      ctx.ir.schemas.dtos[compiledKey] = {
        ...resolveDto({
          key: compiledKey,
          dto,
        }),
        ownership: resourceRef(toSnakeCaseKey(resourceKey)),
      };
    }
  }
}

// ============================================================================
// PARAMS
// ============================================================================

/**
 * Compiles authoring params into IR params schemas.
 */
function compileParams(ctx: CompilerContext): void {
  for (const [key, ref] of Object.entries(ctx.authoring.schemas.params ?? {})) {
    ctx.ir.schemas.params[toSnakeCaseKey(key)] = resolveParams({
      key,
      ref,
    });
  }
}

/**
 * Compiles resource-scoped params into root IR params with dotted keys.
 */
function compileResourceParams(ctx: CompilerContext): void {
  for (const [resourceKey, resource] of Object.entries(ctx.authoring.resources ?? {})) {
    for (const [paramKey, ref] of Object.entries(resource.schemas.params ?? {})) {
      const compiledKey = createResourceScopedSchemaKey(resourceKey, paramKey);

      ctx.ir.schemas.params[compiledKey] = {
        ...resolveParams({
          key: compiledKey,
          ref,
        }),
        ownership: resourceRef(toSnakeCaseKey(resourceKey)),
      };
    }
  }
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles non-entity schema artifacts.
 *
 * Entity schemas are handled by `compileEntities`.
 * Entity models are handled by `compileModels`.
 */
export function compileSchemas(ctx: CompilerContext): void {
  compileDtos(ctx);
  compileParams(ctx);
  compileResourceDtos(ctx);
  compileResourceParams(ctx);
}
