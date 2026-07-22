// src/contract/types/core/4.properties-builder.ts

import type {
  ArrayUsageOptions,
  CompositeAuthoringRef,
  EntityAuthoringRef,
  EntityFieldAuthoringRef,
  EntityFieldSetAuthoringRef,
  EnumAuthoringRef,
  ModelAuthoringRef,
  PrimitiveAuthoringRef,
  PropertyAuthoringRef,
} from './3.authoring-ref';

import type {
  EntityFieldSetName,
  EntityModelVariant,
  EntityRelationKind,
  FieldPersistenceMode,
  FieldVisibilityLevel,
  PrimitiveFormat,
  PrimitiveType,
  PropertySlotSourceMode,
  PropertySourceKind,
  QueryOperator,
  RelationShape,
  ValueObject,
} from '@/contract/constants';

// Re-export all constants for backwards compatibility
export {
  EntityFieldSetName,
  EntityFieldSetNameValues,
  EntityModelVariant,
  EntityModelVariantValues,
  EntityRelationKind,
  EntityRelationKindValues,
  FieldPersistenceMode,
  FieldPersistenceModeValues,
  FieldVisibilityLevel,
  FieldVisibilityLevelValues,
  PrimitiveFormat,
  PrimitiveFormatValues,
  PrimitiveType,
  PrimitiveTypeValues,
  PropertySlotSourceMode,
  PropertySlotSourceModeValues,
  PropertySourceKind,
  PropertySourceKindValues,
  QueryOperator,
  QueryOperatorValues,
  RelationShape,
  RelationShapeValues,
  type ValueObject,
  valueObject,
} from '@/contract/constants';

// ============================================================================
// AUTHORING-OWNED BASE TYPES
// ============================================================================

export interface DefinitionItem {
  readonly meta?: Record<string, unknown>;
  readonly description?: string;
  readonly deprecated?: boolean;
}

// ============================================================================
// AUTHORING PRIMITIVE TYPES
// ============================================================================

export interface PrimitiveValidationDefinition {
  readonly minimum?: number;
  readonly maximum?: number;
  readonly exclusiveMinimum?: number;
  readonly exclusiveMaximum?: number;
  readonly multipleOf?: number;
  readonly minLength?: number;
  readonly maxLength?: number;
  readonly pattern?: string;
}

export interface PrimitiveDefinition extends DefinitionItem {
  readonly type: PrimitiveType;
  readonly format?: PrimitiveFormat;
  readonly validation?: PrimitiveValidationDefinition;
  readonly example?: unknown;
}

// ============================================================================
// AUTHORING ENUM TYPES
// ============================================================================

export type EnumValuePrimitive = string | number;

export interface EnumValueDefinition extends DefinitionItem {
  readonly value: EnumValuePrimitive;
  readonly label?: string;
}

export type EnumValuesInput = readonly EnumValuePrimitive[] | Record<string, EnumValuePrimitive | EnumValueDefinition>;

export interface EnumDefinition extends DefinitionItem {
  readonly values: EnumValuesInput;
}

// ============================================================================
// AUTHORING COMPOSITE TYPES
// ============================================================================

export interface CompositeDefinition extends DefinitionItem {
  readonly extends?: CompositeAuthoringRef;
  readonly properties: Record<string, unknown>;
}

// ============================================================================
// AUTHORING FIELD/QUERY TYPES
// ============================================================================

export interface FieldCapabilityConfig extends DefinitionItem {
  readonly filter?: boolean;
  readonly sort?: boolean;
  readonly select?: boolean;
  readonly operators?: readonly QueryOperator[];
}

export interface FieldVisibilityConfig extends DefinitionItem {
  readonly read?: FieldVisibilityLevel;
  readonly write?: FieldVisibilityLevel;
  readonly sensitive?: boolean;
}

export interface FieldLifecycleConfig extends DefinitionItem {
  readonly create?: boolean;
  readonly update?: boolean;
  readonly immutable?: boolean;
  readonly generated?: boolean;
  readonly readOnly?: boolean;
}

export interface FieldPersistenceConfig extends DefinitionItem {
  readonly mode: FieldPersistenceMode;
  readonly generated?: boolean;
  readonly immutable?: boolean;
}

// ============================================================================
// PROPERTY SOURCE INPUTS
// ============================================================================

export interface InlinePropertyPromotionHint {
  readonly ownerKind: 'entity' | 'composite';
  readonly ownerKey: string;
  readonly fieldKey: string;
  readonly suggestedKey: string;
}

export interface PropertySlotRefSource {
  readonly mode: typeof PropertySlotSourceMode.ref;
  readonly ref: PropertyAuthoringRef;
}

export interface PropertySlotInlineSource {
  readonly mode: typeof PropertySlotSourceMode.inline;
  readonly property: PropertySourceInput;
  readonly promote: InlinePropertyPromotionHint;
}

export type PropertySlotSource = PropertySlotRefSource | PropertySlotInlineSource;

export interface PropertyRefMemberInput {
  readonly source: PropertySlotRefSource;
}

export interface InlinePropertyMemberInput {
  readonly source: PropertySlotInlineSource;
}

export type NormalizedPropertyMemberInput = PropertyRefMemberInput | InlinePropertyMemberInput;

export interface BasePropertySourceInput extends DefinitionItem {
  readonly kind: PropertySourceKind;
}

export interface PrimitivePropertySourceInput extends BasePropertySourceInput {
  readonly kind: typeof PropertySourceKind.primitive;
  readonly type: PrimitiveType;
  readonly format?: PrimitiveFormat;
  readonly example?: unknown;
  readonly validation?: PrimitiveValidationDefinition;
}

export interface EnumPropertyValueInput extends DefinitionItem {
  readonly value: EnumValuePrimitive;
  readonly label?: string;
}

export interface EnumPropertySourceInput extends BasePropertySourceInput {
  readonly kind: typeof PropertySourceKind.enum;
  readonly values: EnumValuesInput;
}

export type CompositePropertyValueInput = PropertySourceInput | PropertySourceBuilder<PropertySourceInput> | PropertyAuthoringRef;

export interface CompositePropertySourceInput extends BasePropertySourceInput {
  readonly kind: typeof PropertySourceKind.composite;
  readonly extends?: CompositeAuthoringRef;
  readonly properties: Record<string, CompositePropertyValueInput>;
}

export interface NormalizedCompositePropertySourceInput extends BasePropertySourceInput {
  readonly kind: typeof PropertySourceKind.composite;
  readonly extends?: CompositeAuthoringRef;
  readonly properties: Record<string, NormalizedPropertyMemberInput>;
}

export interface RefPropertySourceInput extends BasePropertySourceInput {
  readonly kind: typeof PropertySourceKind.ref;
  readonly ref: PropertyAuthoringRef;
  readonly overrides?: Partial<PrimitiveDefinition | EnumDefinition | CompositeDefinition>;
}

export type PropertySourceInput =
  | PrimitivePropertySourceInput
  | EnumPropertySourceInput
  | CompositePropertySourceInput
  | NormalizedCompositePropertySourceInput
  | RefPropertySourceInput;

export interface PropertySourceBuilder<TInput extends PropertySourceInput> {
  readonly input: TInput;
}

export type PrimitivePropertySourceInputLike =
  | PrimitivePropertySourceInput
  | PrimitivePropertyBuilder
  | StringPropertyBuilder
  | NumberPropertyBuilder;

export type EnumPropertySourceInputLike = EnumPropertySourceInput | EnumPropertyBuilder;

export type CompositePropertySourceInputLike = CompositePropertySourceInput | CompositePropertyBuilder;

export type RefPropertySourceInputLike = RefPropertySourceInput | RefPropertyBuilder;

export type PropertySourceInputLike = PropertySourceInput | PropertySourceBuilder<PropertySourceInput>;

export type PrimitivePropertySourceMap = Record<string, PrimitivePropertySourceInputLike>;

export type EnumPropertySourceMap = Record<string, EnumPropertySourceInputLike>;

export type CompositePropertySourceMap = Record<string, CompositePropertySourceInputLike>;

export type PropertySourceMap = Record<string, PropertySourceInputLike>;

// ============================================================================
// QUERY / ACCESS / PERSISTENCE BUILDERS
// ============================================================================

export interface QueryOperatorBuilder {
  readonly input: readonly QueryOperator[];

  eq(): QueryOperatorBuilder;
  neq(): QueryOperatorBuilder;
  in(): QueryOperatorBuilder;
  notIn(): QueryOperatorBuilder;
  contains(): QueryOperatorBuilder;
  startsWith(): QueryOperatorBuilder;
  endsWith(): QueryOperatorBuilder;
  gt(): QueryOperatorBuilder;
  gte(): QueryOperatorBuilder;
  lt(): QueryOperatorBuilder;
  lte(): QueryOperatorBuilder;
  between(): QueryOperatorBuilder;
  exists(): QueryOperatorBuilder;
}

export interface CapabilityOptionsBuilder {
  readonly input: FieldCapabilityConfig;

  filter(value?: boolean): CapabilityOptionsBuilder;
  sort(value?: boolean): CapabilityOptionsBuilder;
  select(value?: boolean): CapabilityOptionsBuilder;

  operators(build: (operator: QueryOperatorBuilder) => QueryOperatorBuilder): CapabilityOptionsBuilder;
}

export interface CapabilityHelper {
  operators(): QueryOperatorBuilder;

  filter(value?: boolean): CapabilityOptionsBuilder;
  sort(value?: boolean): CapabilityOptionsBuilder;
  select(value?: boolean): CapabilityOptionsBuilder;

  options(config: FieldCapabilityConfig): CapabilityOptionsBuilder;
}

export interface VisibilityOptionsBuilder {
  readonly input: FieldVisibilityConfig;

  read(level: FieldVisibilityLevel): VisibilityOptionsBuilder;
  write(level: FieldVisibilityLevel): VisibilityOptionsBuilder;

  public(): VisibilityOptionsBuilder;
  internal(): VisibilityOptionsBuilder;
  secret(): VisibilityOptionsBuilder;
  auth(): VisibilityOptionsBuilder;

  sensitive(value?: boolean): VisibilityOptionsBuilder;
}

export interface VisibilityHelper {
  read(level: FieldVisibilityLevel): VisibilityOptionsBuilder;
  write(level: FieldVisibilityLevel): VisibilityOptionsBuilder;

  public(): VisibilityOptionsBuilder;
  internal(): VisibilityOptionsBuilder;
  secret(): VisibilityOptionsBuilder;
  auth(): VisibilityOptionsBuilder;

  sensitive(value?: boolean): VisibilityOptionsBuilder;

  options(config: FieldVisibilityConfig): VisibilityOptionsBuilder;
}

export interface LifecycleOptionsBuilder {
  readonly input: FieldLifecycleConfig;

  create(value?: boolean): LifecycleOptionsBuilder;
  update(value?: boolean): LifecycleOptionsBuilder;
  immutable(value?: boolean): LifecycleOptionsBuilder;
  generated(value?: boolean): LifecycleOptionsBuilder;
  readOnly(value?: boolean): LifecycleOptionsBuilder;
}

export interface LifecycleHelper {
  create(value?: boolean): LifecycleOptionsBuilder;
  update(value?: boolean): LifecycleOptionsBuilder;
  immutable(value?: boolean): LifecycleOptionsBuilder;
  generated(value?: boolean): LifecycleOptionsBuilder;
  readOnly(value?: boolean): LifecycleOptionsBuilder;

  options(config: FieldLifecycleConfig): LifecycleOptionsBuilder;
}

export interface PersistenceOptionsBuilder {
  readonly input: FieldPersistenceConfig;

  mode(mode: FieldPersistenceMode): PersistenceOptionsBuilder;

  stored(): PersistenceOptionsBuilder;
  virtual(): PersistenceOptionsBuilder;
  computed(): PersistenceOptionsBuilder;

  generated(value?: boolean): PersistenceOptionsBuilder;
  immutable(value?: boolean): PersistenceOptionsBuilder;
}

export interface PersistenceHelper {
  mode(mode: FieldPersistenceMode): PersistenceOptionsBuilder;

  stored(): PersistenceOptionsBuilder;
  virtual(): PersistenceOptionsBuilder;
  computed(): PersistenceOptionsBuilder;

  generated(value?: boolean): PersistenceOptionsBuilder;
  immutable(value?: boolean): PersistenceOptionsBuilder;

  options(config: FieldPersistenceConfig): PersistenceOptionsBuilder;
}

// ============================================================================
// PROPERTY BUILDERS
// ============================================================================

export interface PrimitivePropertyBuilder extends PropertySourceBuilder<PrimitivePropertySourceInput> {
  min(value: number): PrimitivePropertyBuilder;
  max(value: number): PrimitivePropertyBuilder;
  exclusiveMin(value: number): PrimitivePropertyBuilder;
  exclusiveMax(value: number): PrimitivePropertyBuilder;
  multipleOf(value: number): PrimitivePropertyBuilder;

  minLength(value: number): PrimitivePropertyBuilder;
  maxLength(value: number): PrimitivePropertyBuilder;
  pattern(value: string): PrimitivePropertyBuilder;

  format(value: PrimitiveFormat): PrimitivePropertyBuilder;

  example(value: unknown): PrimitivePropertyBuilder;
  description(value: string): PrimitivePropertyBuilder;
  deprecated(value?: boolean): PrimitivePropertyBuilder;
  meta(value: Record<string, unknown>): PrimitivePropertyBuilder;
}

export interface StringPropertyBuilder extends PrimitivePropertyBuilder {
  email(): StringPropertyBuilder;
  uri(): StringPropertyBuilder;
  url(): StringPropertyBuilder;
  uuid(): StringPropertyBuilder;
  objectId(): StringPropertyBuilder;
  phone(): StringPropertyBuilder;
  password(): StringPropertyBuilder;
  date(): StringPropertyBuilder;
  dateTime(): StringPropertyBuilder;
  time(): StringPropertyBuilder;
  binary(): StringPropertyBuilder;
}

export interface NumberPropertyBuilder extends PrimitivePropertyBuilder {
  int(): NumberPropertyBuilder;
}

export interface EnumPropertyBuilder extends PropertySourceBuilder<EnumPropertySourceInput> {
  description(value: string): EnumPropertyBuilder;
  deprecated(value?: boolean): EnumPropertyBuilder;
  meta(value: Record<string, unknown>): EnumPropertyBuilder;
}

export interface CompositePropertyBuilder extends PropertySourceBuilder<CompositePropertySourceInput> {
  extends(ref: CompositeAuthoringRef): CompositePropertyBuilder;

  description(value: string): CompositePropertyBuilder;
  deprecated(value?: boolean): CompositePropertyBuilder;
  meta(value: Record<string, unknown>): CompositePropertyBuilder;
}

export interface RefPropertyBuilder extends PropertySourceBuilder<RefPropertySourceInput> {
  description(value: string): RefPropertyBuilder;
  deprecated(value?: boolean): RefPropertyBuilder;
  meta(value: Record<string, unknown>): RefPropertyBuilder;
}

export interface PropertyHelper {
  primitive(type: PrimitiveType): PrimitivePropertyBuilder;

  string(): StringPropertyBuilder;
  number(): NumberPropertyBuilder;
  integer(): NumberPropertyBuilder;
  boolean(): PrimitivePropertyBuilder;

  date(): StringPropertyBuilder;
  dateTime(): StringPropertyBuilder;
  time(): StringPropertyBuilder;
  email(): StringPropertyBuilder;
  uri(): StringPropertyBuilder;
  url(): StringPropertyBuilder;
  uuid(): StringPropertyBuilder;
  objectId(): StringPropertyBuilder;
  phone(): StringPropertyBuilder;
  password(): StringPropertyBuilder;
  binary(): StringPropertyBuilder;

  enum(values: EnumValuesInput): EnumPropertyBuilder;

  composite(properties: Record<string, CompositePropertyValueInput>): CompositePropertyBuilder;

  ref(ref: PropertyAuthoringRef): RefPropertyBuilder;
}

// ============================================================================
// FIELD SOURCES
// ============================================================================

export interface PropertyFieldSourceInput {
  readonly mode: typeof PropertySlotSourceMode.ref;
  readonly ref: PropertyAuthoringRef;
}

export interface InlinePropertyFieldSourceInput {
  readonly mode: typeof PropertySlotSourceMode.inline;
  readonly property?: PropertySourceInputLike;
  readonly promote?: InlinePropertyPromotionHint;
}

export interface ModelFieldSourceInput {
  readonly mode: typeof PropertySlotSourceMode.ref;
  readonly ref: ModelAuthoringRef;
}

export type LazyEntityTargetInput = () => EntityTargetInput;

export type EntityTargetInput =
  | EntityAuthoringRef
  | EntityPropertiesResult<string, EntityFieldInputMap, EntityFieldInputMap>
  | LazyEntityTargetInput;

export type ResolvedEntityTargetInput = EntityAuthoringRef | EntityPropertiesResult<string, EntityFieldInputMap, EntityFieldInputMap>;

export interface RelationFieldThroughInput<TJoin extends EntityTargetInput = EntityTargetInput> {
  readonly entity: TJoin;
  readonly from?: EntityFieldAuthoringRef;
  readonly to?: EntityFieldAuthoringRef;
  readonly map?: (join: AnyEntityResult) => {
    readonly from: EntityFieldAuthoringRef;
    readonly to: EntityFieldAuthoringRef;
  };
}

export type RelationInverseInput = EntityFieldAuthoringRef | ((target: AnyEntityResult) => EntityFieldAuthoringRef);

export interface UnresolvedRelationFieldSourceInput extends DefinitionItem {
  readonly mode: typeof PropertySlotSourceMode.relation;
  readonly relation?: undefined;
  readonly target?: undefined;
  readonly through?: undefined;
  readonly inverse?: undefined;
  readonly expandable?: boolean;
  readonly relationName?: string;
}

export interface RelationFieldSourceInput extends DefinitionItem {
  readonly mode: typeof PropertySlotSourceMode.relation;
  readonly relation: EntityRelationKind;
  readonly target: EntityTargetInput;
  readonly through?: RelationFieldThroughInput;
  readonly inverse?: EntityFieldAuthoringRef;
  readonly expandable?: boolean;
  readonly relationName?: string;
}

export type EntityFieldSourceInput =
  | PropertySlotRefSource
  | PropertySlotInlineSource
  | ModelFieldSourceInput
  | UnresolvedRelationFieldSourceInput
  | RelationFieldSourceInput;

export type FieldSourceValue = PropertyAuthoringRef | ModelAuthoringRef | PropertySourceInputLike;

// ============================================================================
// ENTITY FIELD INPUTS
// ============================================================================

export interface EntityFieldOptions extends DefinitionItem {
  readonly required?: boolean;
  readonly nullable?: boolean;
  readonly default?: unknown;
  readonly array?: true | ArrayUsageOptions | false;
  readonly capability?: FieldCapabilityConfig;
  readonly visibility?: FieldVisibilityConfig;
  readonly lifecycle?: FieldLifecycleConfig;
  readonly persistence?: FieldPersistenceConfig;
}

export interface EntityFieldInput {
  readonly source: EntityFieldSourceInput;
  readonly options?: EntityFieldOptions;
}

export interface BaseFieldBuilder<TInput extends EntityFieldInput> {
  readonly input: TInput;

  required(value?: boolean): this;
  optional(): this;

  description(value: string): this;
  deprecated(value?: boolean): this;
  meta(value: Record<string, unknown>): this;
}

export interface PropertyFieldBuilder extends BaseFieldBuilder<EntityFieldInput> {
  nullable(value?: boolean): PropertyFieldBuilder;
  nonNullable(): PropertyFieldBuilder;

  array(options?: true | ArrayUsageOptions): PropertyFieldBuilder;
  single(): PropertyFieldBuilder;

  default(value: unknown): PropertyFieldBuilder;

  persistence(build: (persistence: PersistenceHelper) => PersistenceOptionsBuilder): PropertyFieldBuilder;

  capability(build: (capability: CapabilityHelper) => CapabilityOptionsBuilder): PropertyFieldBuilder;
  visibility(build: (visibility: VisibilityHelper) => VisibilityOptionsBuilder): PropertyFieldBuilder;
  lifecycle(build: (lifecycle: LifecycleHelper) => LifecycleOptionsBuilder): PropertyFieldBuilder;
}

export interface RelationFieldBuilder extends BaseFieldBuilder<EntityFieldInput> {
  nullable(value?: boolean): RelationFieldBuilder;
  nonNullable(): RelationFieldBuilder;

  array(options?: true | ArrayUsageOptions): RelationFieldBuilder;
  single(): RelationFieldBuilder;

  default(value: unknown): RelationFieldBuilder;

  persistence(build: (persistence: PersistenceHelper) => PersistenceOptionsBuilder): RelationFieldBuilder;

  capability(build: (capability: CapabilityHelper) => CapabilityOptionsBuilder): RelationFieldBuilder;
  visibility(build: (visibility: VisibilityHelper) => VisibilityOptionsBuilder): RelationFieldBuilder;
  lifecycle(build: (lifecycle: LifecycleHelper) => LifecycleOptionsBuilder): RelationFieldBuilder;

  inverse(refOrFactory: RelationInverseInput): RelationFieldBuilder;

  through<TJoin extends EntityTargetInput>(
    entity: TJoin,
    map: {
      readonly from: EntityFieldAuthoringRef;
      readonly to: EntityFieldAuthoringRef;
    },
  ): RelationFieldBuilder;

  expandable(value?: boolean): RelationFieldBuilder;
  relationName(name: string): RelationFieldBuilder;
}

export type FieldBuilder = PropertyFieldBuilder | RelationFieldBuilder;

export type EntityFieldInputLike = EntityFieldInput | PropertyFieldBuilder | RelationFieldBuilder;

export type EntityFieldInputMap = Record<string, EntityFieldInputLike>;

// ============================================================================
// FIELD HELPER
// ============================================================================

export interface FieldHelper {
  (source: FieldSourceValue): PropertyFieldBuilder;

  from(source: FieldSourceValue): PropertyFieldBuilder;

  primitive(type: PrimitiveType): PropertyFieldBuilder;

  string(): PropertyFieldBuilder;
  number(): PropertyFieldBuilder;
  integer(): PropertyFieldBuilder;
  boolean(): PropertyFieldBuilder;

  date(): PropertyFieldBuilder;
  dateTime(): PropertyFieldBuilder;
  time(): PropertyFieldBuilder;
  email(): PropertyFieldBuilder;
  uri(): PropertyFieldBuilder;
  url(): PropertyFieldBuilder;
  uuid(): PropertyFieldBuilder;
  objectId(): PropertyFieldBuilder;
  phone(): PropertyFieldBuilder;
  password(): PropertyFieldBuilder;
  binary(): PropertyFieldBuilder;

  enum(values: EnumValuesInput): PropertyFieldBuilder;

  composite(properties: Record<string, CompositePropertyValueInput>): PropertyFieldBuilder;

  ref(ref: PropertyAuthoringRef): PropertyFieldBuilder;

  relation(): RelationFieldBuilder;

  belongsTo(target: EntityTargetInput): RelationFieldBuilder;
  hasOne(target: EntityTargetInput): RelationFieldBuilder;
  hasMany(target: EntityTargetInput): RelationFieldBuilder;
  manyToMany(target: EntityTargetInput): RelationFieldBuilder;
}

export interface EntityRelationLinkBuilder {
  belongsTo(target: EntityTargetInput): RelationFieldBuilder;
  hasOne(target: EntityTargetInput): RelationFieldBuilder;
  hasMany(target: EntityTargetInput): RelationFieldBuilder;
  manyToMany(target: EntityTargetInput): RelationFieldBuilder;
}

export type EntityRelationOverrideFactory = (relation: EntityRelationLinkBuilder) => RelationFieldBuilder;

export type RelationFieldKeys<TFields extends EntityFieldInputMap> = keyof TFields & string;

export type EntityRelationOverrides<TFields extends EntityFieldInputMap> = Partial<
  Record<RelationFieldKeys<TFields>, EntityRelationOverrideFactory>
>;

// ============================================================================
// ENTITY MODELS / FIELD SETS
// ============================================================================

export type EntityFieldKey<TFields extends EntityFieldInputMap> = keyof TFields & string;

export type EntityFieldSetMode = 'only' | 'include' | 'exclude';

export interface EntityFieldSetOverrideInput<TFields extends EntityFieldInputMap> extends DefinitionItem {
  readonly mode?: EntityFieldSetMode;
  readonly fields?: readonly EntityFieldKey<TFields>[];
}

export interface EntityFieldSetOverrideBuilder<TFields extends EntityFieldInputMap> {
  readonly input: EntityFieldSetOverrideInput<TFields>;

  only(...fields: EntityFieldKey<TFields>[]): EntityFieldSetOverrideBuilder<TFields>;
  include(...fields: EntityFieldKey<TFields>[]): EntityFieldSetOverrideBuilder<TFields>;
  exclude(...fields: EntityFieldKey<TFields>[]): EntityFieldSetOverrideBuilder<TFields>;

  description(value: string): EntityFieldSetOverrideBuilder<TFields>;
  deprecated(value?: boolean): EntityFieldSetOverrideBuilder<TFields>;
  meta(value: Record<string, unknown>): EntityFieldSetOverrideBuilder<TFields>;
}

export type EntityFieldSetOverrideFactory<TFields extends EntityFieldInputMap> = (
  set: EntityFieldSetOverrideBuilder<TFields>,
) => EntityFieldSetOverrideBuilder<TFields>;

export type EntityFieldSetOverrides<TFields extends EntityFieldInputMap> = Partial<
  Record<EntityFieldSetName, EntityFieldSetOverrideInput<TFields> | EntityFieldSetOverrideFactory<TFields>>
>;

export interface EntityModelOverrideInput<TFields extends EntityFieldInputMap> extends DefinitionItem {
  readonly pick?: readonly EntityFieldKey<TFields>[];
  readonly omit?: readonly EntityFieldKey<TFields>[];
  readonly partial?: boolean;
  readonly relations?: RelationShape;
  readonly extendWith?: Record<string, FieldSourceValue | FieldBuilder>;
}

export interface EntityModelOverrideBuilder<TFields extends EntityFieldInputMap> {
  readonly input: EntityModelOverrideInput<TFields>;

  pick(...fields: EntityFieldKey<TFields>[]): EntityModelOverrideBuilder<TFields>;
  omit(...fields: EntityFieldKey<TFields>[]): EntityModelOverrideBuilder<TFields>;
  partial(value?: boolean): EntityModelOverrideBuilder<TFields>;
  relations(shape: RelationShape): EntityModelOverrideBuilder<TFields>;

  extendWith(fields: Record<string, FieldSourceValue | FieldBuilder>): EntityModelOverrideBuilder<TFields>;

  description(value: string): EntityModelOverrideBuilder<TFields>;
  deprecated(value?: boolean): EntityModelOverrideBuilder<TFields>;
  meta(value: Record<string, unknown>): EntityModelOverrideBuilder<TFields>;
}

export type EntityModelOverrideFactory<TFields extends EntityFieldInputMap> = (
  model: EntityModelOverrideBuilder<TFields>,
) => EntityModelOverrideBuilder<TFields>;

export type EntityModelOverrides<TFields extends EntityFieldInputMap> = Partial<
  Record<EntityModelVariant, EntityModelOverrideInput<TFields> | EntityModelOverrideFactory<TFields>>
>;

// ============================================================================
// ENTITY RESULT TYPES
// ============================================================================

export type AnyEntityResult = EntityPropertiesResult<string, EntityFieldInputMap, EntityFieldInputMap>;

export type EntityOwnFields<TEntity> =
  TEntity extends EntityPropertiesResult<string, infer TOwnFields, EntityFieldInputMap> ? TOwnFields : never;

export type EntityAllFields<TEntity> =
  TEntity extends EntityPropertiesResult<string, EntityFieldInputMap, infer TAllFields> ? TAllFields : never;

export type EntityExtendsInput = AnyEntityResult;

export type MergeEntityFields<TParent extends EntityExtendsInput | undefined, TOwnFields extends EntityFieldInputMap> = [TParent] extends [
  EntityExtendsInput,
]
  ? EntityAllFields<TParent> & TOwnFields
  : TOwnFields;

export interface EntityOptions<TParent extends EntityExtendsInput | undefined = undefined> extends DefinitionItem {
  readonly extends?: TParent;
  readonly abstract?: boolean;
  readonly tags?: readonly string[];
}

export type EntityModelRefs = {
  readonly [K in EntityModelVariant]: ModelAuthoringRef;
};

export type EntityFieldSetRefs = {
  readonly [K in EntityFieldSetName]: EntityFieldSetAuthoringRef;
};

export interface EntityPropertiesResult<
  TName extends string,
  TOwnFields extends EntityFieldInputMap,
  TAllFields extends EntityFieldInputMap = TOwnFields,
> {
  readonly name: TName;

  readonly fields: TOwnFields;

  readonly allFields: TAllFields;

  readonly entity: EntityAuthoringRef;

  readonly ref: {
    readonly entity: EntityAuthoringRef;

    readonly fields: {
      readonly [K in keyof TAllFields & string]: EntityFieldAuthoringRef;
    };

    readonly models: EntityModelRefs;

    readonly fieldSets: EntityFieldSetRefs;
  };

  models<TOverrides extends EntityModelOverrides<TAllFields>>(overrides: TOverrides): EntityPropertiesResult<TName, TOwnFields, TAllFields>;

  fieldSets<TOverrides extends EntityFieldSetOverrides<TAllFields>>(
    overrides: TOverrides,
  ): EntityPropertiesResult<TName, TOwnFields, TAllFields>;

  relations<TOverrides extends EntityRelationOverrides<TAllFields>>(
    overrides: TOverrides,
  ): EntityPropertiesResult<TName, TOwnFields, TAllFields>;
}

// ============================================================================
// DEFINE PROPERTIES BUILDER
// ============================================================================

export interface PrimitivePropertiesResult<TFields extends PrimitivePropertySourceMap> {
  readonly fields: TFields;

  readonly ref: {
    readonly [K in keyof TFields & string]: PrimitiveAuthoringRef;
  };
}

export interface EnumPropertiesResult<TFields extends EnumPropertySourceMap> {
  readonly fields: TFields;

  readonly ref: {
    readonly [K in keyof TFields & string]: EnumAuthoringRef;
  };
}

export interface CompositePropertiesResult<TFields extends CompositePropertySourceMap> {
  readonly fields: TFields;

  readonly ref: {
    readonly [K in keyof TFields & string]: CompositeAuthoringRef;
  };
}

export interface PropertyRefsResult<TFields extends PropertySourceMap> {
  readonly fields: TFields;

  readonly ref: {
    readonly [K in keyof TFields & string]: PropertyAuthoringRef;
  };
}

// ============================================================================
// PROPERTIES AUTHORING STATE
// ============================================================================

export interface PropertiesAuthoringState {
  primitives: Record<string, PrimitivePropertySourceInput>;
  enums: Record<string, EnumPropertySourceInput>;
  composites: Record<string, CompositePropertySourceInput>;
}

// ============================================================================
// PROPERTIES BUILDER
// ============================================================================

export interface PropertiesBuilder {
  readonly state: Partial<PropertiesAuthoringState>;

  primitives<TFields extends PrimitivePropertySourceMap>(fields: TFields): PrimitivePropertiesResult<TFields>;

  enums<TFields extends EnumPropertySourceMap>(fields: TFields): EnumPropertiesResult<TFields>;

  composites<TFields extends CompositePropertySourceMap>(fields: TFields): CompositePropertiesResult<TFields>;

  refs<TFields extends PropertySourceMap>(fields: TFields): PropertyRefsResult<TFields>;

  snapshot(): Partial<PropertiesAuthoringState>;
}
