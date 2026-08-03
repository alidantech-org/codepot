import type { DefinitionItem } from './4.properties-builder';

import type {
  DtoAuthoringRef,
  EntityAuthoringRef,
  EntityFieldAuthoringRef,
  MaybeUsage,
  ModelAuthoringRef,
  ParamsAuthoringRef,
  PropertyAuthoringRef,
} from './3.authoring-ref';

import type {
  EntityExtendsInput,
  EntityFieldInput,
  EntityFieldInputMap,
  EntityFieldSetName,
  EntityFieldSetOverrideInput,
  EntityModelOverrideInput,
  EntityModelOverrides,
  EntityOptions,
  EntityPropertiesResult,
  MergeEntityFields,
} from './4.properties-builder';

// ============================================================================
// DTO FIELD INPUTS
// ============================================================================

export type DtoRef = PropertyAuthoringRef | EntityFieldAuthoringRef | ModelAuthoringRef | DtoAuthoringRef | ParamsAuthoringRef;

export type DtoFieldInput = DtoRef | MaybeUsage<DtoRef>;

export type DtoFieldInputMap = Record<string, DtoFieldInput>;

export type DtoSchemaInput = DtoFieldInputMap | DtoRef | MaybeUsage<DtoRef>;

export type DtoSchemaInputMap = Record<string, DtoSchemaInput>;

// ============================================================================
// PARAM INPUTS
// ============================================================================

export type ParamSourceRef = PropertyAuthoringRef | EntityFieldAuthoringRef;

export type ParamsInputMap = Record<string, ParamSourceRef>;

// ============================================================================
// AUTHORING STORAGE SHAPES
// ============================================================================

export interface DtoFieldAuthoringDefinition {
  readonly ref: DtoFieldInput;
  readonly usage: Record<string, unknown>;
}

export interface DtoSourceAuthoringDefinition {
  readonly source: {
    readonly ref: DtoFieldInput;
    readonly usage: Record<string, unknown>;
  };
}

export interface DtoFieldsAuthoringDefinition {
  readonly fields: Record<string, DtoFieldAuthoringDefinition>;
}

export type DtoAuthoringDefinition = DtoSourceAuthoringDefinition | DtoFieldsAuthoringDefinition;

export interface EntityAuthoringDefinition<TFields extends EntityFieldInputMap = EntityFieldInputMap> extends DefinitionItem {
  readonly abstract?: boolean;
  readonly extends?: EntityAuthoringRef;
  readonly tags?: readonly string[];

  /**
   * Authoring/debug fields.
   * These are not compiled IR fields.
   */
  fields: Record<keyof TFields & string, EntityFieldInput>;

  /**
   * Authoring model overrides.
   * Compiler later turns these into compiled models.
   */
  modelOverrides?: Partial<Record<keyof EntityModelOverrides<TFields> & string, EntityModelOverrideInput<TFields>>>;

  /**
   * Authoring field-set overrides.
   * Compiler later turns these into compiled field_sets.
   */
  fieldSetOverrides?: Partial<Record<EntityFieldSetName, EntityFieldSetOverrideInput<TFields>>>;
}

export type ParamsAuthoringDefinition = ParamsInputMap;

// ============================================================================
// SCHEMAS AUTHORING STATE MUTABLE
// ============================================================================

export interface SchemasAuthoringState {
  entities: Record<string, EntityAuthoringDefinition>;
  models: Record<string, unknown>;
  dtos: Record<string, DtoAuthoringDefinition>;
  params: ParamsAuthoringDefinition;
}

// ============================================================================
// BUILDER RESULTS
// ============================================================================

export interface DtoSchemasResult<TSchemas extends DtoSchemaInputMap> {
  readonly schemas: TSchemas;

  readonly ref: {
    readonly [K in keyof TSchemas & string]: DtoAuthoringRef;
  };
}

export interface ParamsResult<TParams extends ParamsInputMap> {
  readonly params: TParams;

  readonly ref: {
    readonly [K in keyof TParams & string]: ParamsAuthoringRef;
  };
}

// ============================================================================
// SCHEMAS BUILDER
// ============================================================================

export interface SchemasBuilder {
  readonly state: Partial<SchemasAuthoringState>;

  entity<TName extends string, TOwnFields extends EntityFieldInputMap, TParent extends EntityExtendsInput | undefined = undefined>(
    name: TName,
    fields: TOwnFields,
    options?: EntityOptions<TParent>,
  ): EntityPropertiesResult<TName, TOwnFields, MergeEntityFields<TParent, TOwnFields>>;

  dtos<TSchemas extends DtoSchemaInputMap>(schemas: TSchemas): DtoSchemasResult<TSchemas>;

  params<TParams extends ParamsInputMap>(params: TParams): ParamsResult<TParams>;

  snapshot(): Partial<SchemasAuthoringState>;
}
