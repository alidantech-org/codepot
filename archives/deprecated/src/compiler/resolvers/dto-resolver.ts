// src/compiler/resolvers/dto-resolver.ts

import type {
  DtoAuthoringDefinition,
  DtoFieldAuthoringDefinition,
  DtoFieldInput,
  DtoFieldsAuthoringDefinition,
  DtoSourceAuthoringDefinition,
  ParamsAuthoringDefinition,
} from '@/contract/types/authoring/5.schemas-builder';

import type {
  DtoAuthoringRef,
  EntityFieldAuthoringRef,
  ModelAuthoringRef,
  ParamsAuthoringRef,
  PropertyAuthoringRef,
} from '@/contract/types/authoring/3.authoring-ref';

import type { RefProperty } from '@/contract/types/ir/properties/definition';
import type { DtoDefinition } from '@/contract/types/ir/schema/dto/definition';
import type { ParamsDefinition } from '@/contract/types/ir/schema/params/definition';
import type { EntityFieldDefinition } from '@/contract/types/ir/schema/entity/field/definition';
import type { Ref } from '@/contract/types/ir/ref';

import { dtoRef, entityFieldRef, modelRef, paramsRef, propertyCompositeRef, propertyEnumRef, propertyPrimitiveRef } from './ref-resolver';
import { assertAuthoringRefLike, parseEntityFieldRef, parseModelRef } from './authoring-ref-resolver';
import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// DTO INPUT
// ============================================================================

export interface ResolveDtoInput {
  readonly key: string;
  readonly dto: DtoAuthoringDefinition;
}

// ============================================================================
// PARAM INPUT
// ============================================================================

export interface ResolveParamsInput {
  readonly key: string;
  readonly ref: ParamsAuthoringDefinition[string];
}

// ============================================================================
// AUTHORING REF GUARDS
// ============================================================================

/**
 * Checks whether an input value is an authoring ref-like object.
 */
function isAuthoringRef(input: unknown): input is {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
} {
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
 * Checks whether a value is a ref usage wrapper with a nested ref.
 */
function isUsageWrapper(input: unknown): input is {
  readonly ref: unknown;
} {
  return input !== null && typeof input === 'object' && 'ref' in input;
}

/**
 * Checks whether a value is a plain object-like record.
 */
function isObject(input: unknown): input is Record<string, unknown> {
  return input !== null && typeof input === 'object';
}

/**
 * Unwraps usage values into their underlying authoring ref when possible.
 */
function unwrapDtoFieldInput(input: DtoFieldInput): unknown {
  if (isUsageWrapper(input)) {
    return input.ref;
  }

  return input;
}

// ============================================================================
// REF RESOLUTION
// ============================================================================

/**
 * Resolves a property authoring ref into an IR property ref.
 */
function resolvePropertyAuthoringRef(input: PropertyAuthoringRef): Ref<RefProperty> {
  const key = toSnakeCaseKey(input.key);

  if (input.kind === 'property.primitive') {
    return propertyPrimitiveRef(key);
  }

  if (input.kind === 'property.enum') {
    return propertyEnumRef(key);
  }

  return propertyCompositeRef(key);
}

/**
 * Resolves an entity field authoring ref into an IR entity field ref.
 *
 * Authoring field refs encode entity and field in the id:
 * schema:entity:{Entity}:field:{field}
 */
function resolveEntityFieldAuthoringRef(input: EntityFieldAuthoringRef): Ref<EntityFieldDefinition> {
  const parsed = parseEntityFieldRef(assertAuthoringRefLike(input));

  return entityFieldRef(parsed.entity_key, parsed.field_key);
}

/**
 * Resolves any DTO field input into an IR ref.
 */
function resolveDtoFieldRef(input: DtoFieldInput): Ref {
  const value = unwrapDtoFieldInput(input);

  if (!isAuthoringRef(value)) {
    throw new Error('DTO field input must be an authoring ref or usage wrapper.');
  }

  if (value.kind.startsWith('property.')) {
    return resolvePropertyAuthoringRef(value as PropertyAuthoringRef);
  }

  if (value.kind === 'schema.entity.field') {
    return resolveEntityFieldAuthoringRef(value as EntityFieldAuthoringRef);
  }

  if (value.kind === 'schema.model') {
    return modelRef(parseModelRef(assertAuthoringRefLike(value)).model_key);
  }

  if (value.kind === 'schema.dto') {
    return dtoRef(toSnakeCaseKey((value as DtoAuthoringRef).key));
  }

  if (value.kind === 'schema.params') {
    return paramsRef(toSnakeCaseKey((value as ParamsAuthoringRef).key));
  }

  throw new Error(`Unsupported DTO field ref kind "${value.kind}".`);
}

/**
 * Converts DTO field usage metadata into IR DTO field metadata.
 */
function resolveDtoFieldUsage(usage: Record<string, unknown> | undefined): Record<string, unknown> {
  if (usage === undefined) return {};

  return {
    ...(usage.required !== undefined ? { required: usage.required } : {}),
    ...(usage.nullable !== undefined ? { nullable: usage.nullable } : {}),
    ...(usage.array !== undefined ? { array: usage.array } : {}),
    ...(usage.default !== undefined ? { default: usage.default } : {}),
  };
}

/**
 * Resolves a DTO field input into an IR field with ref + usage metadata.
 */
function resolveDtoField(input: DtoFieldInput): DtoDefinition['fields'][string] {
  const value = unwrapDtoFieldInput(input);
  const ref = resolveDtoFieldRef(input);

  if (isObject(value) && isObject(value.usage)) {
    return {
      ...ref,
      ...resolveDtoFieldUsage(value.usage),
    };
  }

  if (isObject(input) && isObject(input.usage)) {
    return {
      ...ref,
      ...resolveDtoFieldUsage(input.usage),
    };
  }

  return ref;
}

// ============================================================================
// DTO SHAPE GUARDS
// ============================================================================

/**
 * Checks whether the authoring DTO is source-backed.
 */
function isDtoSourceDefinition(input: DtoAuthoringDefinition): input is DtoSourceAuthoringDefinition {
  return 'source' in input;
}

/**
 * Checks whether the authoring DTO is field-map-backed.
 */
function isDtoFieldsDefinition(input: DtoAuthoringDefinition): input is DtoFieldsAuthoringDefinition {
  return 'fields' in input;
}

// ============================================================================
// DTO FIELDS
// ============================================================================

/**
 * Resolves authoring DTO fields into IR DTO fields.
 */
function resolveDtoFields(fields: Record<string, DtoFieldAuthoringDefinition>): DtoDefinition['fields'] {
  const output: DtoDefinition['fields'] = {};

  for (const [key, field] of Object.entries(fields)) {
    output[toSnakeCaseKey(key)] = {
      ...resolveDtoField(field.ref),
      ...resolveDtoFieldUsage(field.usage),
    };
  }

  return output;
}

/**
 * Extracts DTO extendWith field maps from source usage.
 *
 * Supports both:
 * - usage.extendWith
 * - usage.extendWith.extendWith
 */
function getExtendWithFields(usage: Record<string, unknown> | undefined): Record<string, DtoFieldInput> {
  if (usage === undefined) return {};

  const direct = usage.extendWith;

  if (isObject(direct) && !('extendWith' in direct)) {
    return direct as Record<string, DtoFieldInput>;
  }

  if (isObject(direct) && isObject(direct.extendWith)) {
    return direct.extendWith as Record<string, DtoFieldInput>;
  }

  return {};
}

/**
 * Resolves source DTO extendWith fields into IR DTO fields.
 */
function resolveDtoExtendWithFields(usage: Record<string, unknown> | undefined): DtoDefinition['fields'] {
  const fields = getExtendWithFields(usage);
  const output: DtoDefinition['fields'] = {};

  for (const [key, value] of Object.entries(fields)) {
    output[toSnakeCaseKey(key)] = resolveDtoField(value);
  }

  return output;
}

// ============================================================================
// DTO RESOLVE
// ============================================================================

/**
 * Converts one authoring DTO into an IR DTO definition.
 *
 * IR DTO fields are required, so source-backed DTOs emit an empty field map
 * plus `extends`.
 */
export function resolveDto(input: ResolveDtoInput): DtoDefinition {
  const { dto } = input;

  if (isDtoSourceDefinition(dto)) {
    return {
      extends: resolveDtoFieldRef(dto.source.ref) as DtoDefinition['extends'],
      fields: resolveDtoExtendWithFields(dto.source.usage),
    };
  }

  if (isDtoFieldsDefinition(dto)) {
    return {
      fields: resolveDtoFields(dto.fields),
    };
  }

  throw new Error(`Unable to resolve DTO "${input.key}".`);
}

// ============================================================================
// PARAMS RESOLVE
// ============================================================================

/**
 * Converts one params authoring ref into an IR params definition.
 */
export function resolveParams(input: ResolveParamsInput): ParamsDefinition {
  const ref = input.ref;

  if (!isAuthoringRef(ref)) {
    throw new Error(`Params "${input.key}" must reference a property or entity field.`);
  }

  if (ref.kind.startsWith('property.')) {
    return {
      ref: resolvePropertyAuthoringRef(ref as PropertyAuthoringRef) as ParamsDefinition['ref'],
    };
  }

  if (ref.kind === 'schema.entity.field') {
    return {
      ref: resolveEntityFieldAuthoringRef(ref as EntityFieldAuthoringRef) as ParamsDefinition['ref'],
    };
  }

  throw new Error(`Unsupported params ref kind "${ref.kind}".`);
}
