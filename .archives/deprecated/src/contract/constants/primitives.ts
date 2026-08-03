// src/contract/constants/primitives.ts

import { valueObject } from './values';

export const PrimitiveTypeValues = [
  'string',
  'number',
  'boolean',
  'integer',
] as const;

export const PrimitiveType = valueObject(PrimitiveTypeValues);

export type PrimitiveType = (typeof PrimitiveTypeValues)[number];

export const PrimitiveFormatValues = [
  'date',
  'dateTime',
  'time',
  'email',
  'uri',
  'url',
  'uuid',
  'objectId',
  'phone',
  'password',
  'binary',
  'custom',
] as const;

export const PrimitiveFormat = valueObject(PrimitiveFormatValues);

export type PrimitiveFormat = (typeof PrimitiveFormatValues)[number];
