// src/contract/types/ir/schema/entity/field/definition.ts

import type { DefinitionItem } from '../../../definition';
import type { Ref } from '../../../ref';
import type { RefProperty } from '../../../properties/definition';
import type { EntityDefinition } from '../definition';

// ============================================================================
// CAPABILITY
// ============================================================================

export const QueryOperator = {
  eq: 'eq',
  neq: 'neq',
  in: 'in',
  not_in: 'not_in',
  contains: 'contains',
  starts_with: 'starts_with',
  ends_with: 'ends_with',
  gt: 'gt',
  gte: 'gte',
  lt: 'lt',
  lte: 'lte',
  between: 'between',
  exists: 'exists',
} as const;

export type QueryOperator = (typeof QueryOperator)[keyof typeof QueryOperator];

export interface FieldCapabilityConfig extends DefinitionItem {
  filter?: boolean;
  sort?: boolean;
  select?: boolean;
  operators?: QueryOperator[];
}

// ============================================================================
// VISIBILITY
// ============================================================================

export const FieldVisibilityLevel = {
  public: 'public',
  internal: 'internal',
  secret: 'secret',
  auth: 'auth',
} as const;

export type FieldVisibilityLevel = (typeof FieldVisibilityLevel)[keyof typeof FieldVisibilityLevel];

export interface FieldVisibilityConfig extends DefinitionItem {
  read?: FieldVisibilityLevel;
  write?: FieldVisibilityLevel;
  sensitive?: boolean;
}

// ============================================================================
// LIFECYCLE
// ============================================================================

export interface FieldLifecycleConfig extends DefinitionItem {
  create?: boolean;
  update?: boolean;
  immutable?: boolean;
  generated?: boolean;
  read_only?: boolean;
}

// ============================================================================
// PERSISTENCE
// ============================================================================

export const FieldPersistenceMode = {
  stored: 'stored',
  virtual: 'virtual',
  computed: 'computed',
} as const;

export type FieldPersistenceMode = (typeof FieldPersistenceMode)[keyof typeof FieldPersistenceMode];

export interface FieldPersistenceConfig extends DefinitionItem {
  mode: FieldPersistenceMode;
  generated?: boolean;
  immutable?: boolean;
}

// ============================================================================
// ARRAY
// ============================================================================

export interface ArrayDefinition extends DefinitionItem {
  min_items?: number;
  max_items?: number;
  unique_items?: boolean;
}

// ============================================================================
// RELATION
// ============================================================================

export const EntityRelationKind = {
  belongs_to: 'belongs_to',
  has_one: 'has_one',
  has_many: 'has_many',
  many_to_many: 'many_to_many',
} as const;

export type EntityRelationKind = (typeof EntityRelationKind)[keyof typeof EntityRelationKind];

export interface EntityRelationThroughDefinition {
  entity: Ref<EntityDefinition>;
  from: Ref<EntityFieldDefinition>;
  to: Ref<EntityFieldDefinition>;
}

export interface EntityRelationDefinition {
  relation: EntityRelationKind;
  target: Ref<EntityDefinition>;
  inverse?: Ref<EntityFieldDefinition>;
  through?: EntityRelationThroughDefinition;
}

// ============================================================================
// FIELD OPTIONS
// ============================================================================

export interface EntityFieldOptionsDefinition extends DefinitionItem {
  required?: boolean;
  nullable?: boolean;
  array?: true | ArrayDefinition;
  default?: unknown;

  capability?: FieldCapabilityConfig;
  visibility?: FieldVisibilityConfig;
  lifecycle?: FieldLifecycleConfig;
  persistence?: FieldPersistenceConfig;
}

// ============================================================================
// ENTITY FIELD
// ============================================================================

export type EntityPropertyFieldDefinition = Ref<RefProperty> & EntityFieldOptionsDefinition;

export type EntityRelationFieldDefinition = EntityRelationDefinition & EntityFieldOptionsDefinition;

export type EntityFieldDefinition = EntityPropertyFieldDefinition | EntityRelationFieldDefinition;
