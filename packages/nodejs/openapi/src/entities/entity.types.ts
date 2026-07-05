import type { ComponentRef, PropertyRef } from '../refs/ref.types.js';
import type { RefUsage } from '../refs/ref-usage.types.js';
import type { XCodegenResourceMeta } from '../codegen/codegen-extension.types.js';
import type { InfoInput, NormalizedInfo } from '../info/info.types.js';

export type EntityOwner = { readonly global: true } | { readonly resource: XCodegenResourceMeta };

export interface EntityRef {
  readonly id: string;
  readonly name: string;
  readonly kind: 'entity';
  readonly entityKey: string;
  readonly owner: EntityOwner;
  readonly abstract: boolean;
}

export type EntitySearchQueryOptions = {
  readonly prefix?: boolean;
  readonly contains?: boolean;
  readonly fuzzy?: boolean;
};

export type EntityFieldRole = 'primaryKey' | 'createdAt' | 'updatedAt' | 'softDelete' | 'auditActor';

export type EntityGeneratedStrategy = 'uuid' | 'increment' | 'cuid';

export interface EntityFieldQueryMetadata {
  readonly exact?: true;
  readonly oneOf?: true;
  readonly range?: true;
  readonly date?: true;
  readonly search?: EntitySearchQueryOptions;
  readonly sort?: true;
}

export interface EntityFieldMetadata {
  readonly index?: true;
  readonly unique?: true;
  readonly readonly?: true;
  readonly managed?: true;
  readonly immutable?: true;
  readonly select?: false;
  readonly edit?: false;
  readonly role?: EntityFieldRole;
  readonly generated?: EntityGeneratedStrategy;
  readonly query?: EntityFieldQueryMetadata;
  readonly info?: NormalizedInfo;
}

export interface EntityFieldBuilder {
  index(): EntityFieldBuilder;
  unique(): EntityFieldBuilder;
  readonly(): EntityFieldBuilder;
  managed(): EntityFieldBuilder;
  immutable(): EntityFieldBuilder;
  select(enabled: false): EntityFieldBuilder;
  edit(enabled: false): EntityFieldBuilder;
  role(role: EntityFieldRole): EntityFieldBuilder;
  generated(strategy: EntityGeneratedStrategy): EntityFieldBuilder;
  query(callback: (query: EntityFieldQueryBuilder) => EntityFieldQueryBuilder): EntityFieldBuilder;
  info(info: InfoInput): EntityFieldBuilder;
}

export interface EntityFieldQueryBuilder {
  exact(): EntityFieldQueryBuilder;
  oneOf(): EntityFieldQueryBuilder;
  range(): EntityFieldQueryBuilder;
  date(): EntityFieldQueryBuilder;
  search(options: EntitySearchQueryOptions): EntityFieldQueryBuilder;
  sort(): EntityFieldQueryBuilder;
}

export type EntityFieldDefinition = (field: EntityFieldBuilder) => EntityFieldBuilder;

export type EntityBackendField = PropertyRef | RefUsage<PropertyRef>;

export type EntityBackendFields = Record<string, EntityBackendField>;

export type EntityFieldsDefinition = Record<string, EntityFieldDefinition>;

export type EntityConstraintValue =
  | string
  | number
  | boolean
  | null
  | readonly EntityConstraintValue[]
  | EntityFieldValueRef;

export interface EntityFieldValueRef {
  readonly $field: string;
}

export interface EntityConstraintRule {
  readonly op: string;
  readonly [key: string]: unknown;
}

export interface EntityConstraintBuilder {
  index(fields: readonly string[]): EntityConstraintDefinition;
  unique(fields: readonly string[]): EntityConstraintDefinition;
  check(rule: EntityConstraintRule): EntityConstraintDefinition;
  gt(field: string, value: EntityConstraintValue): EntityConstraintRule;
  gte(field: string, value: EntityConstraintValue): EntityConstraintRule;
  lt(field: string, value: EntityConstraintValue): EntityConstraintRule;
  lte(field: string, value: EntityConstraintValue): EntityConstraintRule;
  eq(field: string, value: EntityConstraintValue): EntityConstraintRule;
  neq(field: string, value: EntityConstraintValue): EntityConstraintRule;
  notNull(field: string): EntityConstraintRule;
  oneOf(field: string, values: readonly EntityConstraintValue[]): EntityConstraintRule;
  range(field: string, min: EntityConstraintValue, max: EntityConstraintValue): EntityConstraintRule;
  when(condition: EntityConstraintRule, thenCondition: EntityConstraintRule): EntityConstraintRule;
  and(...conditions: EntityConstraintRule[]): EntityConstraintRule;
  or(...conditions: EntityConstraintRule[]): EntityConstraintRule;
  field(fieldName: string): EntityFieldValueRef;
}

export type EntityConstraintKind = 'index' | 'unique' | 'check';

export interface EntityConstraintDefinition {
  readonly kind: EntityConstraintKind;
  readonly fields?: readonly string[];
  readonly rule?: EntityConstraintRule;
}

export type EntityConstraintsDefinition = (constraints: EntityConstraintBuilder) => Record<string, EntityConstraintDefinition>;

export interface BaseEntityDefinitionInput {
  readonly kind: 'abstract';
  readonly schema: ComponentRef;
  readonly extends?: EntityRef;
  readonly fields?: EntityFieldsDefinition;
  readonly info?: InfoInput;
}

export interface ConcreteEntityDefinitionInput {
  readonly kind?: 'entity';
  readonly schema: ComponentRef;
  readonly extends?: EntityRef;
  readonly store: string;
  readonly backend?: EntityBackendFields;
  readonly fields?: EntityFieldsDefinition;
  readonly constraints?: EntityConstraintsDefinition;
  readonly info?: InfoInput;
}

export type EntityDefinitionInput = BaseEntityDefinitionInput | ConcreteEntityDefinitionInput;

export interface EntityDefinition {
  readonly key: string;
  readonly kind: 'abstract' | 'entity';
  readonly schema: ComponentRef;
  readonly extends?: EntityRef;
  readonly store?: string;
  readonly backend?: EntityBackendFields;
  readonly fields: Record<string, EntityFieldMetadata>;
  readonly constraints?: Record<string, EntityConstraintDefinition>;
  readonly info?: NormalizedInfo;
  readonly owner: EntityOwner;
  readonly ref: EntityRef;
}

export type EntityRegistryRefs<TInput extends Record<string, EntityDefinitionInput>> = {
  readonly [Key in keyof TInput & string]: EntityRef & { readonly name: Key };
};

export interface EntityRegistry<TInput extends Record<string, EntityDefinitionInput> = Record<string, EntityDefinitionInput>> {
  readonly name: string;
  readonly owner: EntityOwner;
  readonly abstract: boolean;
  readonly definitions: EntityDefinition[];
  readonly ref: EntityRegistryRefs<TInput>;
}

export type EntityRelationCardinality = 'belongsTo' | 'hasOne' | 'hasMany' | 'manyToMany';

export type EntityRelationDeleteBehavior = {
  readonly cascade?: boolean;
  readonly restrict?: boolean;
  readonly setNull?: boolean;
  readonly noAction?: boolean;
};

export interface EntityRelationRef {
  readonly cardinality: EntityRelationCardinality;
  readonly target: EntityRef;
  readonly localField?: string;
  readonly foreignField?: string;
  readonly deleteBehavior?: EntityRelationDeleteBehavior;
  local(field: string): EntityRelationRef;
  foreign(field: string): EntityRelationRef;
  onDelete(behavior: EntityRelationDeleteBehavior): EntityRelationRef;
}

export type EntityRelationDefinition = (relation: EntityRelationBuilder) => EntityRelationRef;

export interface EntityRelationBuilder {
  belongsTo(target: EntityRef): EntityRelationRef;
  hasOne(target: EntityRef): EntityRelationRef;
  hasMany(target: EntityRef): EntityRelationRef;
  manyToMany(target: EntityRef): EntityRelationRef;
}

export type EntityRelationsInput = Record<string, Record<string, EntityRelationDefinition>>;

export interface EntityRelation {
  readonly source: string;
  readonly name: string;
  readonly cardinality: EntityRelationCardinality;
  readonly target: EntityRef;
  readonly local: string;
  readonly foreign: string;
  readonly onDelete?: EntityRelationDeleteBehavior;
}

export interface EntityRelationRegistry {
  readonly owner: EntityOwner;
  readonly definitions: EntityRelation[];
}
