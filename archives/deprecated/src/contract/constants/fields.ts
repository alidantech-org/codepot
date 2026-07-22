// src/contract/constants/fields.ts

import { valueObject } from './values';

export const QueryOperatorValues = [
  'eq',
  'neq',
  'in',
  'notIn',
  'contains',
  'startsWith',
  'endsWith',
  'gt',
  'gte',
  'lt',
  'lte',
  'between',
  'exists',
] as const;

export const QueryOperator = valueObject(QueryOperatorValues);

export type QueryOperator = (typeof QueryOperatorValues)[number];

export const FieldVisibilityLevelValues = [
  'public',
  'internal',
  'secret',
  'auth',
] as const;

export const FieldVisibilityLevel = valueObject(FieldVisibilityLevelValues);

export type FieldVisibilityLevel = (typeof FieldVisibilityLevelValues)[number];

export const FieldPersistenceModeValues = [
  'stored',
  'virtual',
  'computed',
] as const;

export const FieldPersistenceMode = valueObject(FieldPersistenceModeValues);

export type FieldPersistenceMode = (typeof FieldPersistenceModeValues)[number];
