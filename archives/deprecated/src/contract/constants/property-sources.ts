// src/contract/constants/property-sources.ts

import { valueObject } from './values';

export const PropertySourceKindValues = [
  'primitive',
  'enum',
  'composite',
  'ref',
] as const;

export const PropertySourceKind = valueObject(PropertySourceKindValues);

export type PropertySourceKind = (typeof PropertySourceKindValues)[number];

export const PropertySlotSourceModeValues = [
  'ref',
  'inline',
  'relation',
] as const;

export const PropertySlotSourceMode = valueObject(PropertySlotSourceModeValues);

export type PropertySlotSourceMode = (typeof PropertySlotSourceModeValues)[number];
