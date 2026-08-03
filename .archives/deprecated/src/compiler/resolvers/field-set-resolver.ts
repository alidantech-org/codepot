// src/compiler/resolvers/field-set-resolver.ts

import type { EntityFieldInput, EntityFieldInputLike, EntityFieldSetOverrideInput } from '@/contract/types/authoring/4.properties-builder';
import type { EntityAuthoringDefinition } from '@/contract/types/authoring/5.schemas-builder';

import type { Ref } from '@/contract/types/ir/ref';
import type { FieldSetDefinition } from '@/contract/types/ir/schema/field-set/definition';

import type { CompilerContext } from '../context/compiler-context';

import { createOwnedKey } from '../naming/owned-key';

import { entityFieldRef, entityRef } from './ref-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// TYPES
// ============================================================================

export interface ResolveFieldSetInput {
  readonly ctx: CompilerContext;
  readonly entity_key: string;
  readonly field_set_key: string;
  readonly override: EntityFieldSetOverrideInput<any>;
}

export interface EntityFieldOwner {
  readonly entity_key: string;
  readonly field_key: string;
  readonly field: EntityFieldInput;
}

export type FieldSetMap = Record<string, FieldSetDefinition>;

// ============================================================================
// FIELD INPUT NORMALIZATION
// ============================================================================

/**
 * Unwraps a field builder into its raw authoring field input.
 */
function unwrapEntityFieldInput(input: EntityFieldInputLike): EntityFieldInput {
  if ('input' in input) {
    return input.input;
  }

  return input;
}

// ============================================================================
// ENTITY LOOKUP
// ============================================================================

/**
 * Returns an authoring entity by compiled snake_case key.
 */
function getAuthoringEntityByCompiledKey(ctx: CompilerContext, compiledEntityKey: string): EntityAuthoringDefinition {
  for (const [rawKey, entity] of Object.entries(ctx.authoring.schemas.entities ?? {})) {
    if (toSnakeCaseKey(rawKey) === compiledEntityKey) {
      return entity;
    }
  }

  throw new Error(`Unable to find authoring entity "${compiledEntityKey}".`);
}

/**
 * Gets the parent entity key for an authoring entity.
 */
function getParentEntityKey(entity: EntityAuthoringDefinition): string | undefined {
  if (entity.extends === undefined) return undefined;

  return toSnakeCaseKey(entity.extends.key);
}

// ============================================================================
// FIELD OWNERSHIP
// ============================================================================

/**
 * Collects fields owned by the inheritance chain.
 *
 * Parent fields are collected first. Child fields override same-name parent
 * fields if a conflict exists.
 */
function collectFieldOwners(ctx: CompilerContext, entityKey: string): Map<string, EntityFieldOwner> {
  const entity = getAuthoringEntityByCompiledKey(ctx, entityKey);
  const parentKey = getParentEntityKey(entity);

  const output = parentKey !== undefined ? collectFieldOwners(ctx, parentKey) : new Map<string, EntityFieldOwner>();

  for (const [rawFieldKey, rawField] of Object.entries(entity.fields)) {
    const field = unwrapEntityFieldInput(rawField);
    const fieldKey = toSnakeCaseKey(rawFieldKey);

    output.set(fieldKey, {
      entity_key: entityKey,
      field_key: fieldKey,
      field,
    });
  }

  return output;
}

/**
 * Converts a collected owner into an entity field ref.
 */
function ownerToRef(owner: EntityFieldOwner): Ref {
  return entityFieldRef(owner.entity_key, owner.field_key);
}

/**
 * Creates a field set definition for an entity.
 */
function createEntityFieldSet(entityKey: string, fields: readonly Ref[]): FieldSetDefinition {
  return {
    ownership: entityRef(entityKey),
    fields,
  };
}

// ============================================================================
// METADATA FILTERS
// ============================================================================

function isStoredField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.persistence?.mode === 'stored';
}

function isRelationField(owner: EntityFieldOwner): boolean {
  return owner.field.source.mode === 'relation';
}

function isFilterField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.capability?.filter === true;
}

function isSortField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.capability?.sort === true;
}

function isSelectField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.capability?.select === true;
}

function isPublicField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.visibility?.read === 'public';
}

function isInternalField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.visibility?.read === 'internal';
}

function isSecretField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.visibility?.read === 'secret';
}

function isCreateField(owner: EntityFieldOwner): boolean {
  return owner.field.options?.lifecycle?.create !== false && owner.field.options?.lifecycle?.generated !== true;
}

function isUpdateField(owner: EntityFieldOwner): boolean {
  return (
    owner.field.options?.lifecycle?.update !== false &&
    owner.field.options?.lifecycle?.immutable !== true &&
    owner.field.options?.lifecycle?.readOnly !== true
  );
}

/**
 * Resolves a field key to the entity that actually owns it.
 */
function resolveFieldOwner(ctx: CompilerContext, entityKey: string, fieldKey: string): EntityFieldOwner {
  const owners = collectFieldOwners(ctx, entityKey);
  const owner = owners.get(toSnakeCaseKey(fieldKey));

  if (owner === undefined) {
    throw new Error(`Field set references unknown field "${entityKey}.${toSnakeCaseKey(fieldKey)}".`);
  }

  return owner;
}

// ============================================================================
// OVERRIDE FIELD SELECTION
// ============================================================================

/**
 * Gets the field names listed in a field-set override.
 */
function getOverrideFields(override: EntityFieldSetOverrideInput<any>): readonly string[] {
  return (override.fields ?? []).map((field) => String(field));
}

/**
 * Applies field-set override mode.
 *
 * For now:
 * - only: use exactly listed fields
 * - exclude: use all fields except listed fields
 * - include: use all fields plus listed fields
 *
 * If mode is missing, treat it as "only".
 */
function selectFieldKeys(ctx: CompilerContext, entityKey: string, override: EntityFieldSetOverrideInput<any>): readonly string[] {
  const owners = collectFieldOwners(ctx, entityKey);
  const allKeys = [...owners.keys()];
  const overrideKeys = getOverrideFields(override).map(toSnakeCaseKey);
  const mode = override.mode ?? 'only';

  if (mode === 'only') {
    return overrideKeys;
  }

  if (mode === 'exclude') {
    const excluded = new Set(overrideKeys);

    return allKeys.filter((key) => !excluded.has(key));
  }

  if (mode === 'include') {
    return [...new Set([...allKeys, ...overrideKeys])];
  }

  throw new Error(`Unsupported field-set override mode "${mode}".`);
}

// ============================================================================
// RESOLVE
// ============================================================================

/**
 * Resolves one authoring field-set override into an owned field-set definition.
 */
export function resolveFieldSet(input: ResolveFieldSetInput): FieldSetDefinition {
  const fieldKeys = selectFieldKeys(input.ctx, input.entity_key, input.override);

  return createEntityFieldSet(
    input.entity_key,
    fieldKeys.map((fieldKey) => {
      const owner = resolveFieldOwner(input.ctx, input.entity_key, fieldKey);

      return ownerToRef(owner);
    }),
  );
}

/**
 * Resolves generated metadata-based field sets for one entity.
 */
export function resolveGeneratedFieldSets(ctx: CompilerContext, entityKey: string): FieldSetMap {
  const owners = [...collectFieldOwners(ctx, entityKey).values()];

  const ownOwners = owners.filter((owner) => owner.entity_key === entityKey);
  const inheritedOwners = owners.filter((owner) => owner.entity_key !== entityKey);

  const groups: Record<string, EntityFieldOwner[]> = {
    all_fields: owners,
    owned_fields: ownOwners,
    inherited_fields: inheritedOwners,
    stored_fields: owners.filter(isStoredField),
    relation_fields: owners.filter(isRelationField),
    filter_fields: owners.filter(isFilterField),
    sort_fields: owners.filter(isSortField),
    select_fields: owners.filter(isSelectField),
    public_fields: owners.filter(isPublicField),
    internal_fields: owners.filter(isInternalField),
    secret_fields: owners.filter(isSecretField),
    create_fields: owners.filter(isCreateField),
    update_fields: owners.filter(isUpdateField),
  };

  return Object.fromEntries(
    Object.entries(groups).map(([fieldSetKey, groupOwners]) => [
      createFieldSetKey(entityKey, fieldSetKey),
      createEntityFieldSet(entityKey, groupOwners.map(ownerToRef)),
    ]),
  );
}

/**
 * Creates the compiled field-set key.
 *
 * Format:
 * entity.entity_key.field_set_key
 */
export function createFieldSetKey(entityKey: string, fieldSetKey: string): string {
  return createOwnedKey('entity', entityKey, fieldSetKey);
}
