// src/compiler/resolvers/authoring-ref-resolver.ts

import { createOwnedKey } from '../naming/owned-key';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// AUTHORING REF-LIKE TYPE
// ============================================================================

export interface AuthoringRefLike {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
}

// ============================================================================
// TYPE GUARD
// ============================================================================

/**
 * Checks whether a value looks like a Codepot authoring ref.
 */
export function isAuthoringRefLike(input: unknown): input is AuthoringRefLike {
  return (
    input !== null &&
    typeof input === 'object' &&
    'id' in input &&
    typeof input.id === 'string' &&
    'kind' in input &&
    typeof input.kind === 'string' &&
    'key' in input &&
    typeof input.key === 'string'
  );
}

/**
 * Ensures a value is a Codepot authoring ref.
 */
export function assertAuthoringRefLike(input: unknown): AuthoringRefLike {
  if (isAuthoringRefLike(input)) return input;

  throw new Error('Expected Codepot authoring ref.');
}

// ============================================================================
// MODEL REF PARSING
// ============================================================================

export interface ParsedModelRef {
  readonly entity_key: string;
  readonly variant_key: string;
  readonly model_key: string;
}

/**
 * Parses model refs like:
 * - schema:model:User:public
 * - key: User:public
 *
 * Into:
 * - entity_key: user
 * - variant_key: public
 * - model_key: entity.user.user_public
 */
export function parseModelRef(input: AuthoringRefLike): ParsedModelRef {
  if (input.kind !== 'schema.model') {
    throw new Error(`Expected schema.model ref, got "${input.kind}".`);
  }

  const raw = input.key.includes(':') ? input.key : input.id.replace(/^schema:model:/, '');

  const [entityName, variantName] = raw.split(':');

  if (!entityName || !variantName) {
    throw new Error(`Invalid model ref "${input.id}". Expected schema:model:Entity:variant.`);
  }

  const entityKey = toSnakeCaseKey(entityName);
  const variantKey = toSnakeCaseKey(variantName);
  const localModelKey = toSnakeCaseKey(`${entityKey}_${variantKey}`);

  return {
    entity_key: entityKey,
    variant_key: variantKey,
    model_key: createOwnedKey('entity', entityKey, localModelKey),
  };
}

// ============================================================================
// ENTITY REF PARSING
// ============================================================================

export interface ParsedEntityRef {
  readonly entity_key: string;
}

/**
 * Parses entity refs like:
 * - schema:entity:User
 */
export function parseEntityRef(input: AuthoringRefLike): ParsedEntityRef {
  if (input.kind !== 'schema.entity') {
    throw new Error(`Expected schema.entity ref, got "${input.kind}".`);
  }

  return {
    entity_key: toSnakeCaseKey(input.key),
  };
}

// ============================================================================
// ENTITY FIELD REF PARSING
// ============================================================================

export interface ParsedEntityFieldRef {
  readonly entity_key: string;
  readonly field_key: string;
}

/**
 * Parses entity field refs like:
 * - schema:entity:Profile:field:user
 *
 * Do not use `input.key` as the entity name. For field refs, `input.key` is
 * only the field key. The entity key must come from the id.
 */
export function parseEntityFieldRef(input: AuthoringRefLike): ParsedEntityFieldRef {
  if (input.kind !== 'schema.entity.field') {
    throw new Error(`Expected schema.entity.field ref, got "${input.kind}".`);
  }

  const parts = input.id.split(':');
  const entityIndex = parts.indexOf('entity');
  const fieldIndex = parts.indexOf('field');

  if (entityIndex < 0 || fieldIndex < 0) {
    throw new Error(`Invalid entity field ref "${input.id}".`);
  }

  const entityName = parts[entityIndex + 1];
  const fieldName = parts[fieldIndex + 1];

  if (!entityName || !fieldName) {
    throw new Error(`Invalid entity field ref "${input.id}".`);
  }

  return {
    entity_key: toSnakeCaseKey(entityName),
    field_key: toSnakeCaseKey(fieldName),
  };
}

// ============================================================================
// ERROR REF PARSING
// ============================================================================

export interface ParsedErrorRef {
  readonly error_key: string;
}

/**
 * Parses error refs into normalized local error keys.
 *
 * Resource scoping is handled by the resource/route compiler because only that
 * layer knows which resource the ref came from.
 */
export function parseErrorRef(input: AuthoringRefLike): ParsedErrorRef {
  if (input.kind !== 'error') {
    throw new Error(`Expected error ref, got "${input.kind}".`);
  }

  return {
    error_key: toSnakeCaseKey(input.key),
  };
}
