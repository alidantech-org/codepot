import { CODEGEN_EXTENSION_KEY } from './codegen-extension.keys.js';
import { XCodegenKind, type CodegenMetadata } from './codegen-extension.types.js';
import { resolveCodegenKind, stripNonObjectInheritanceMetadata } from './resolve-codegen-kind.js';
import type { CompilerContext } from '../compiler/compiler-context.js';

export type CodegenExtensionTarget = Record<string, unknown>;

function cleanCodegenValue(value: unknown, preserveFalse = false): unknown {
  if (value === undefined || value === null) return undefined;
  if (value === false && !preserveFalse) return undefined;
  if (typeof value === 'string' && value.length === 0) return undefined;

  if (Array.isArray(value)) {
    const items = value
      .map((item) => cleanCodegenValue(item, preserveFalse))
      .filter((item): item is Exclude<unknown, undefined> => item !== undefined);

    return items.length > 0 ? items : undefined;
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .map(([key, child]) => {
        // Preserve false for query.select specifically
        const shouldPreserveFalse = key === 'select' && preserveFalse;
        return [key, cleanCodegenValue(child, shouldPreserveFalse)] as const;
      })
      .filter(([, child]) => child !== undefined);

    return entries.length > 0 ? Object.fromEntries(entries) : undefined;
  }

  return value;
}

function isObjectResolvedKind(kind: CodegenMetadata['kind']): boolean {
  return kind === XCodegenKind.model || kind === XCodegenKind.dto;
}

function validateCodegenMetadata(metadata: CodegenMetadata): void {
  // Query metadata is allowed on primitive and enum fields
  if ('query' in metadata) {
    const kind = metadata.kind;
    if (kind !== XCodegenKind.primitive && kind !== XCodegenKind.enum) {
      throw new Error('x-codegen.query is only allowed on primitive and enum model fields.');
    }
  }

  // Role is optional for DTOs - it's determined by route usage
  // if (metadata.kind === XCodegenKind.dto && !metadata.role) {
  //   throw new Error('x-codegen.role is required when x-codegen.kind is "dto".');
  // }

  if (metadata.kind !== XCodegenKind.dto && 'roles' in metadata) {
    throw new Error('x-codegen.role and x-codegen.roles are only allowed when x-codegen.kind is "dto".');
  }

  if (metadata.kind !== XCodegenKind.dto && 'role' in metadata) {
    const role = (metadata as { role?: unknown }).role;
    if ((metadata.kind !== XCodegenKind.primitive && metadata.kind !== XCodegenKind.enum) || role !== 'access-role') {
      throw new Error('x-codegen.role is only allowed on dto schemas, or as "access-role" on primitive/enum schemas.');
    }
  }
}

export function applyCodegenMetadata<TSchema extends Record<string, unknown>>(
  schema: TSchema,
  metadata: CodegenMetadata,
  context?: CompilerContext,
): TSchema {
  const resolvedKind = resolveCodegenKind(schema, metadata.kind);

  let finalMetadata: CodegenMetadata = {
    ...metadata,
    kind: resolvedKind,
  } as CodegenMetadata;

  if (!isObjectResolvedKind(resolvedKind)) {
    finalMetadata = stripNonObjectInheritanceMetadata(finalMetadata) as unknown as CodegenMetadata;
  }

  // Apply DTO role usage from context if this is a DTO component
  if (resolvedKind === XCodegenKind.dto && context?.dtoRoleUsage) {
    // We need the ref id to look up role usage - this is passed separately in the caller
    // For now, we'll handle this in the caller by enriching metadata before calling this function
  }

  validateCodegenMetadata(finalMetadata);

  const cleaned = cleanCodegenValue(finalMetadata);

  if (cleaned && typeof cleaned === 'object') {
    return {
      ...schema,
      [CODEGEN_EXTENSION_KEY]: cleaned,
    };
  }

  return schema;
}
