// src/contract/constants/entity-models.ts

import { valueObject } from './values';

export const EntityModelVariantValues = [
  'read',
  'create',
  'patch',
  'query',
  'public',
  'publicList',
  'admin',
  'internal',
  'summary',
  'option',
  'relation',
  'projection',
  'redacted',
] as const;

export const EntityModelVariant = valueObject(EntityModelVariantValues);

export type EntityModelVariant = (typeof EntityModelVariantValues)[number];
