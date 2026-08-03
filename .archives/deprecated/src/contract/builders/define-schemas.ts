// src/contract/builders/define-schemas.ts

import type { DtoAuthoringRef, EntityFieldAuthoringRef, ParamsAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';

import type {
  EntityAllFields,
  EntityExtendsInput,
  EntityFieldInput,
  EntityFieldInputLike,
  EntityFieldInputMap,
  EntityFieldSetName,
  EntityFieldSetOverrideFactory,
  EntityFieldSetOverrideInput,
  EntityFieldSetOverrides,
  EntityModelOverrideFactory,
  EntityModelOverrideInput,
  EntityModelOverrides,
  EntityOptions,
  EntityPropertiesResult,
  EntityRelationOverrides,
  EntityRelationOverrideFactory,
  FieldBuilder,
  MergeEntityFields,
  RelationFieldSourceInput,
  UnresolvedRelationFieldSourceInput,
} from '@/contract/types/authoring/4.properties-builder';

import { PropertySlotSourceMode } from '@/contract/types/authoring/4.properties-builder';

import type {
  DtoAuthoringDefinition,
  DtoFieldInput,
  DtoFieldInputMap,
  DtoSchemaInput,
  DtoSchemaInputMap,
  DtoSchemasResult,
  EntityAuthoringDefinition,
  ParamsInputMap,
  ParamsResult,
  SchemasAuthoringState,
  SchemasBuilder,
} from '@/contract/types/authoring/5.schemas-builder';

import {
  entityFieldSetOverrideBuilder,
  entityModelOverrideBuilder,
  entityRelationLinkBuilder,
} from '@/contract/helpers/properties/property';

import { dtoRef, entityFieldRef, entityFieldSetRefs, entityRef, modelRefs, paramsRef } from '@/contract/helpers/refs/authoring-ref-builder';

import { isEntityResult, normalizeEntityTarget, resolveEntityTarget } from '@/contract/helpers/refs/normalize-authoring-ref';

import { createInlinePropertyPromotionHint, unwrapPropertySourceInput } from '@/contract/helpers/properties/inline-property';

import { normalizeEntityFieldOptions } from '@/contract/helpers/properties/field-defaults';

// ============================================================================
// OPTIONS
// ============================================================================

export interface DefineSchemasOptions {
  readonly scope: 'version' | 'resource';
  readonly resourceKey?: string;
  readonly state: Partial<SchemasAuthoringState>;
}

// ============================================================================
// STATE
// ============================================================================

function ensureState(state: Partial<SchemasAuthoringState>): Partial<SchemasAuthoringState> {
  state.entities ??= {};
  state.models ??= {};
  state.dtos ??= {};
  state.params ??= {};

  return state;
}

// ============================================================================
// ENTITY FIELD NORMALIZATION
// ============================================================================

function isEntityFieldInputBuilder(value: EntityFieldInputLike): value is FieldBuilder {
  return !!value && typeof value === 'object' && 'input' in value;
}

function withDefaultOptions(field: EntityFieldInput): EntityFieldInput {
  return {
    ...field,
    options: normalizeEntityFieldOptions(field),
  };
}

function normalizeRelationFieldSource(
  source: UnresolvedRelationFieldSourceInput | RelationFieldSourceInput,
): UnresolvedRelationFieldSourceInput | RelationFieldSourceInput {
  if (!('relation' in source) || source.relation === undefined || source.target === undefined) {
    return source;
  }

  return {
    ...source,
    target: normalizeEntityTarget(source.target),
    through: source.through ? normalizeRelationThrough(source.through) : undefined,
    inverse: source.inverse,
  };
}

function normalizeRelationThrough(through: any): any {
  const resolvedJoin = resolveEntityTarget(through.entity);

  const mapping = through.map
    ? through.map(resolvedJoin)
    : {
        from: through.from,
        to: through.to,
      };

  return {
    entity: normalizeEntityTarget(through.entity),
    from: mapping.from,
    to: mapping.to,
  };
}

function normalizeEntityFieldInput(input: {
  readonly entityName: string;
  readonly fieldKey: string;
  readonly field: EntityFieldInput;
}): EntityFieldInput {
  let field = input.field;

  if (field.source.mode === PropertySlotSourceMode.inline) {
    if ('property' in field.source && field.source.property) {
      field = {
        ...field,
        source: {
          mode: PropertySlotSourceMode.inline,
          property: unwrapPropertySourceInput(field.source.property),
          promote: createInlinePropertyPromotionHint({
            ownerKind: 'entity',
            ownerKey: input.entityName,
            fieldKey: input.fieldKey,
          }),
        },
      };
    }
    // Already normalized
  } else if (field.source.mode === PropertySlotSourceMode.relation) {
    field = {
      ...field,
      source: normalizeRelationFieldSource(field.source),
    };
  }

  return withDefaultOptions(field);
}

function toEntityFieldInput(value: EntityFieldInputLike): EntityFieldInput {
  const input = isEntityFieldInputBuilder(value) ? value.input : value;

  return input;
}

function normalizeEntityFieldInputs<TFields extends EntityFieldInputMap>(
  entityName: string,
  fields: TFields,
): Record<keyof TFields & string, EntityFieldInput> {
  const normalized = {} as Record<keyof TFields & string, EntityFieldInput>;

  for (const [key, value] of Object.entries(fields) as [keyof TFields & string, TFields[keyof TFields & string]][]) {
    const input = toEntityFieldInput(value);

    normalized[key] = normalizeEntityFieldInput({
      entityName,
      fieldKey: key,
      field: input,
    });
  }

  return normalized;
}

// ============================================================================
// ENTITY REFS
// ============================================================================

function createEntityFieldInputRefs<TFields extends EntityFieldInputMap>(
  entityName: string,
  fields: TFields,
): Record<keyof TFields & string, EntityFieldAuthoringRef> {
  const refs = {} as Record<keyof TFields & string, EntityFieldAuthoringRef>;

  for (const key of Object.keys(fields) as Array<keyof TFields & string>) {
    refs[key] = entityFieldRef(entityName, key);
  }

  return refs;
}

function createInheritedFieldRefs<TParent extends EntityExtendsInput | undefined>(
  parent: TParent,
): TParent extends EntityExtendsInput ? Record<keyof EntityAllFields<TParent> & string, EntityFieldAuthoringRef> : {} {
  if (!parent) return {} as never;

  return parent.ref.fields as never;
}

function createAllEntityFieldInputRefs<TParent extends EntityExtendsInput | undefined, TOwnFields extends EntityFieldInputMap>(
  entityName: string,
  ownFields: TOwnFields,
  parent: TParent,
): Record<keyof MergeEntityFields<TParent, TOwnFields> & string, EntityFieldAuthoringRef> {
  return {
    ...createInheritedFieldRefs(parent),
    ...createEntityFieldInputRefs(entityName, ownFields),
  } as Record<keyof MergeEntityFields<TParent, TOwnFields> & string, EntityFieldAuthoringRef>;
}

// ============================================================================
// ENTITY MODEL / FIELD SET OVERRIDES
// ============================================================================

function normalizeEntityModelOverride<TFields extends EntityFieldInputMap>(
  value: EntityModelOverrideInput<TFields> | EntityModelOverrideFactory<TFields>,
): EntityModelOverrideInput<TFields> {
  if (typeof value === 'function') {
    return value(entityModelOverrideBuilder<TFields>()).input;
  }

  return value;
}

function normalizeEntityModelOverrides<TFields extends EntityFieldInputMap>(
  models: EntityModelOverrides<TFields>,
): Partial<Record<keyof EntityModelOverrides<TFields> & string, EntityModelOverrideInput<TFields>>> {
  const normalized = {} as Partial<Record<keyof EntityModelOverrides<TFields> & string, EntityModelOverrideInput<TFields>>>;

  for (const [key, value] of Object.entries(models) as [
    keyof EntityModelOverrides<TFields> & string,
    NonNullable<EntityModelOverrides<TFields>[keyof EntityModelOverrides<TFields>]>,
  ][]) {
    normalized[key] = normalizeEntityModelOverride(value);
  }

  return normalized;
}

function normalizeEntityFieldSetOverride<TFields extends EntityFieldInputMap>(
  value: EntityFieldSetOverrideInput<TFields> | EntityFieldSetOverrideFactory<TFields>,
): EntityFieldSetOverrideInput<TFields> {
  if (typeof value === 'function') {
    return value(entityFieldSetOverrideBuilder<TFields>()).input;
  }

  return value;
}

function normalizeEntityFieldSetOverrides<TFields extends EntityFieldInputMap>(
  overrides: EntityFieldSetOverrides<TFields>,
): Partial<Record<EntityFieldSetName, EntityFieldSetOverrideInput<TFields>>> {
  const normalized: Partial<Record<EntityFieldSetName, EntityFieldSetOverrideInput<TFields>>> = {};

  for (const [key, value] of Object.entries(overrides) as [
    keyof EntityFieldSetOverrides<TFields> & string,
    NonNullable<EntityFieldSetOverrides<TFields>[keyof EntityFieldSetOverrides<TFields>]>,
  ][]) {
    normalized[key as EntityFieldSetName] = normalizeEntityFieldSetOverride(value);
  }

  return normalized;
}

function writeEntityModelOverrides<TFields extends EntityFieldInputMap>(
  schemas: Partial<SchemasAuthoringState>,
  name: string,
  models: EntityModelOverrides<TFields>,
): void {
  const state = ensureState(schemas);
  const entity = state.entities?.[name] as
    | (EntityAuthoringDefinition<TFields> & {
        modelOverrides?: Partial<Record<keyof EntityModelOverrides<TFields> & string, EntityModelOverrideInput<TFields>>>;
      })
    | undefined;

  if (!entity) return;

  entity.modelOverrides = normalizeEntityModelOverrides(models);
}

function writeEntityFieldSetOverrides<TFields extends EntityFieldInputMap>(
  schemas: Partial<SchemasAuthoringState>,
  name: string,
  overrides: EntityFieldSetOverrides<TFields>,
): void {
  const state = ensureState(schemas);
  const entity = state.entities?.[name] as
    | (EntityAuthoringDefinition<TFields> & {
        fieldSetOverrides?: Partial<Record<EntityFieldSetName, EntityFieldSetOverrideInput<TFields>>>;
      })
    | undefined;

  if (!entity) return;

  entity.fieldSetOverrides = normalizeEntityFieldSetOverrides(overrides);
}

// ============================================================================
// ENTITY WRITING
// ============================================================================

function writeEntitySource<TFields extends EntityFieldInputMap, TParent extends EntityExtendsInput | undefined>(
  schemas: Partial<SchemasAuthoringState>,
  name: string,
  fields: TFields,
  options: EntityOptions<TParent>,
): void {
  const state = ensureState(schemas);
  const normalizedFields = normalizeEntityFieldInputs(name, fields);

  state.entities![name] = {
    abstract: options.abstract,
    fields: normalizedFields as unknown as Record<string, EntityFieldInput>,
    extends: options.extends ? normalizeEntityTarget(options.extends) : undefined,
    tags: options.tags,
    description: options.description,
    deprecated: options.deprecated,
    meta: options.meta,
  } as unknown as EntityAuthoringDefinition;
}

function writeEntityRelations<TFields extends EntityFieldInputMap>(
  schemas: Partial<SchemasAuthoringState>,
  name: string,
  relations: TFields,
): void {
  const state = ensureState(schemas);
  const entity = state.entities?.[name] as (EntityAuthoringDefinition & { fields: Record<string, EntityFieldInput> }) | undefined;

  if (!entity) return;

  const normalized = normalizeEntityFieldInputs(name, relations);

  entity.fields = {
    ...(entity.fields ?? {}),
    ...(normalized as unknown as Record<string, EntityFieldInput>),
  };
}

function normalizeEntityRelationOverride(baseField: EntityFieldInput, value: EntityRelationOverrideFactory): EntityFieldInput {
  return value(entityRelationLinkBuilder(baseField)).input;
}

function writeEntityRelationOverrides<TFields extends EntityFieldInputMap>(
  schemas: Partial<SchemasAuthoringState>,
  name: string,
  overrides: EntityRelationOverrides<TFields>,
): void {
  const state = ensureState(schemas);

  const entity = state.entities?.[name] as (EntityAuthoringDefinition & { fields: Record<string, EntityFieldInput> }) | undefined;

  if (!entity) return;

  for (const [key, value] of Object.entries(overrides) as [keyof TFields & string, EntityRelationOverrideFactory][]) {
    const existing = entity.fields[key] as unknown as EntityFieldInput | undefined;

    if (!existing) {
      throw new Error(`Relation "${name}.${key}" cannot be configured because the field does not exist.`);
    }

    if (existing.source.mode !== PropertySlotSourceMode.relation) {
      throw new Error(`Relation "${name}.${key}" cannot be configured because the field is not a relation field.`);
    }

    const linked = normalizeEntityRelationOverride(existing, value);

    entity.fields[key] = normalizeEntityFieldInput({
      entityName: name,
      fieldKey: key,
      field: linked,
    }) as unknown as EntityFieldInput;
  }
}

function createEntityResult<TName extends string, TOwnFields extends EntityFieldInputMap, TParent extends EntityExtendsInput | undefined>(
  schemas: Partial<SchemasAuthoringState>,
  name: TName,
  fields: TOwnFields,
  parent: TParent,
  fieldRefs: Record<keyof MergeEntityFields<TParent, TOwnFields> & string, EntityFieldAuthoringRef>,
): EntityPropertiesResult<TName, TOwnFields, MergeEntityFields<TParent, TOwnFields>> {
  const allFields = {
    ...((parent?.allFields ?? {}) as EntityFieldInputMap),
    ...fields,
  } as MergeEntityFields<TParent, TOwnFields>;

  const currentEntityRef = entityRef(name);

  const result: EntityPropertiesResult<TName, TOwnFields, MergeEntityFields<TParent, TOwnFields>> = {
    name,
    fields,
    allFields,
    entity: currentEntityRef,
    ref: {
      entity: currentEntityRef,
      fields: fieldRefs as EntityPropertiesResult<TName, TOwnFields, MergeEntityFields<TParent, TOwnFields>>['ref']['fields'],
      models: modelRefs(name) as EntityPropertiesResult<TName, TOwnFields, MergeEntityFields<TParent, TOwnFields>>['ref']['models'],
      fieldSets: entityFieldSetRefs(name) as EntityPropertiesResult<
        TName,
        TOwnFields,
        MergeEntityFields<TParent, TOwnFields>
      >['ref']['fieldSets'],
    },

    models<TOverrides extends EntityModelOverrides<MergeEntityFields<TParent, TOwnFields>>>(overrides: TOverrides) {
      writeEntityModelOverrides(schemas, name, overrides);
      return result;
    },

    fieldSets<TOverrides extends EntityFieldSetOverrides<MergeEntityFields<TParent, TOwnFields>>>(overrides: TOverrides) {
      writeEntityFieldSetOverrides(schemas, name, overrides);
      return result;
    },

    relations<TOverrides extends EntityRelationOverrides<MergeEntityFields<TParent, TOwnFields>>>(overrides: TOverrides) {
      writeEntityRelationOverrides(schemas, name, overrides);

      return result;
    },
  };

  return result;
}

// ============================================================================
// DTO NORMALIZATION
// ============================================================================

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function isFieldBuilder(value: unknown): value is FieldBuilder {
  return isRecord(value) && 'input' in value;
}

function isAuthoringRefOrUsage(value: unknown): boolean {
  return isRecord(value) && ('id' in value || 'kind' in value || 'ref' in value);
}

function normalizeDtoSchema(value: DtoSchemaInput): unknown {
  // Direct ref/usage - wrap as source for storage
  if (isAuthoringRefOrUsage(value)) {
    return {
      source: normalizeDtoRefUsage(value as DtoFieldInput),
    };
  }

  // Flat field map - wrap in fields
  return {
    fields: normalizeDtoFields(value as DtoFieldInputMap),
  };
}

function isAuthoringRef(value: unknown): value is {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
} {
  return !!value && typeof value === 'object' && 'id' in value && 'kind' in value && 'key' in value;
}

function isRefUsage(value: unknown): value is {
  readonly ref: unknown;
  readonly usage: unknown;
} {
  return !!value && typeof value === 'object' && 'ref' in value && 'usage' in value;
}

function normalizeDtoRefUsage(value: DtoFieldInput): {
  readonly ref: DtoFieldInput;
  readonly usage: Record<string, unknown>;
} {
  if (isRefUsage(value)) {
    return {
      ref: value.ref as DtoFieldInput,
      usage: (value.usage as Record<string, unknown>) ?? {},
    };
  }

  return {
    ref: value,
    usage: {},
  };
}

function normalizeDtoFields(fields: DtoFieldInputMap): Record<
  string,
  {
    readonly ref: DtoFieldInput;
    readonly usage: Record<string, unknown>;
  }
> {
  const normalized: Record<
    string,
    {
      readonly ref: DtoFieldInput;
      readonly usage: Record<string, unknown>;
    }
  > = {};

  for (const [key, value] of Object.entries(fields)) {
    // If value is an entity result, normalize it to entity ref first
    const normalizedValue = isEntityResult(value) ? value.entity : value;
    normalized[key] = normalizeDtoRefUsage(normalizedValue as DtoFieldInput);
  }

  return normalized;
}

function writeDtoSchemas<TSchemas extends DtoSchemaInputMap>(schemasState: Partial<SchemasAuthoringState>, schemas: TSchemas): void {
  const state = ensureState(schemasState);

  for (const [key, value] of Object.entries(schemas) as [keyof TSchemas & string, TSchemas[keyof TSchemas & string]][]) {
    state.dtos![key] = normalizeDtoSchema(value) as unknown as DtoAuthoringDefinition;
  }
}

function createDtoRefs<TSchemas extends DtoSchemaInputMap>(schemas: TSchemas): Record<keyof TSchemas & string, DtoAuthoringRef> {
  const refs = {} as Record<keyof TSchemas & string, DtoAuthoringRef>;

  for (const key of Object.keys(schemas) as Array<keyof TSchemas & string>) {
    refs[key] = dtoRef(key);
  }

  return refs;
}

// ============================================================================
// PARAMS
// ============================================================================

function writeParams<TParams extends ParamsInputMap>(schemasState: Partial<SchemasAuthoringState>, params: TParams): void {
  const state = ensureState(schemasState);

  for (const [key, value] of Object.entries(params) as [keyof TParams & string, TParams[keyof TParams & string]][]) {
    state.params![key] = value;
  }
}

function createParamsRefs<TParams extends ParamsInputMap>(params: TParams): Record<keyof TParams & string, ParamsAuthoringRef> {
  const refs = {} as Record<keyof TParams & string, ParamsAuthoringRef>;

  for (const key of Object.keys(params) as Array<keyof TParams & string>) {
    refs[key] = paramsRef(key);
  }

  return refs;
}

// ============================================================================
// DEFINE SCHEMAS
// ============================================================================

export function defineSchemas(options: DefineSchemasOptions): SchemasBuilder {
  const builder: SchemasBuilder = {
    get state() {
      return options.state;
    },

    entity<TName extends string, TOwnFields extends EntityFieldInputMap, TParent extends EntityExtendsInput | undefined = undefined>(
      name: TName,
      fields: TOwnFields,
      entityOptions: EntityOptions<TParent> = {},
    ): EntityPropertiesResult<TName, TOwnFields, MergeEntityFields<TParent, TOwnFields>> {
      const fieldRefs = createAllEntityFieldInputRefs(name, fields, entityOptions.extends);

      writeEntitySource(options.state, name, fields, entityOptions);

      return createEntityResult(options.state, name, fields, entityOptions.extends, fieldRefs);
    },

    dtos<TSchemas extends DtoSchemaInputMap>(schemas: TSchemas): DtoSchemasResult<TSchemas> {
      writeDtoSchemas(options.state, schemas);

      return {
        schemas,
        ref: createDtoRefs(schemas) as DtoSchemasResult<TSchemas>['ref'],
      };
    },

    params<TParams extends ParamsInputMap>(params: TParams): ParamsResult<TParams> {
      writeParams(options.state, params);

      return {
        params,
        ref: createParamsRefs(params) as ParamsResult<TParams>['ref'],
      };
    },

    snapshot() {
      return options.state;
    },
  };

  return builder;
}
