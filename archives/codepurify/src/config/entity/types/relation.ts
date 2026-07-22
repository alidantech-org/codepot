// ─── codepurify/fields/relation.ts ─────────────────────────────────────────────────

import type { FieldConfig } from './base';
import { IEntityConfig } from './entity';

// ─── Helper Types ─────────────────────────────────────────────────────────────

export type EntityConfigClass<T extends IEntityConfig = IEntityConfig> = new (...args: any[]) => T;

export type EntityInstance<T> = T extends new (...args: any[]) => infer I ? I : never;

// ─── Relation ─────────────────────────────────────────────────────────────────

export type OnDelete = 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';

export type FieldOf<T extends IEntityConfig> = keyof T['fields'] & string;

export interface ManyToOneRelation {
  kind: 'many_to_one';
  local_field: () => FieldConfig;
  remote_field: () => FieldConfig;
  on_delete?: OnDelete;
}

export interface OneToManyRelation {
  kind: 'one_to_many';
  remote_field: () => FieldConfig;
  cascade?: boolean;
}

export interface OneToOneRelation {
  kind: 'one_to_one';
  local_field: () => FieldConfig;
  remote_field: () => FieldConfig;
  on_delete?: OnDelete;
}

export type RelationConfigUnion = ManyToOneRelation | OneToManyRelation | OneToOneRelation;

export type DefineRelation = Record<string, RelationConfigUnion>;

// ─── Relation field ───────────────────────────────────────────────────────────

export interface RelationFieldConfig {
  relation: RelationConfigUnion;
  query?: {
    select?: boolean;
    filter?: boolean;
  };
}
