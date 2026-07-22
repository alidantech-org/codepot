// src/contract/constants/relations.ts

import { valueObject } from './values';

export const EntityRelationKindValues = [
  'belongsTo',
  'hasOne',
  'hasMany',
  'manyToMany',
] as const;

export const EntityRelationKind = valueObject(EntityRelationKindValues);

export type EntityRelationKind = (typeof EntityRelationKindValues)[number];

export const RelationShapeValues = [
  'expand',
  'idOnly',
  'omit',
] as const;

export const RelationShape = valueObject(RelationShapeValues);

export type RelationShape = (typeof RelationShapeValues)[number];
