// src/contract/types/ir/properties/primitive/definition.ts

import type { DefinitionItem } from '../../definition';

// ============================================================================
// PRIMITIVE TYPES
// ============================================================================

export const PrimitiveType = {
  string: 'string',
  number: 'number',
  boolean: 'boolean',
  integer: 'integer',
} as const;

export type PrimitiveType = (typeof PrimitiveType)[keyof typeof PrimitiveType];

// ============================================================================
// PRIMITIVE FORMATS
// ============================================================================

export const PrimitiveFormat = {
  date: 'date',
  date_time: 'date-time',
  time: 'time',
  email: 'email',
  uri: 'uri',
  url: 'url',
  uuid: 'uuid',
  object_id: 'object-id',
  phone: 'phone',
  password: 'password',
  binary: 'binary',
  custom: 'custom',
} as const;

export type PrimitiveFormat = (typeof PrimitiveFormat)[keyof typeof PrimitiveFormat];

// ============================================================================
// VALIDATION
// ============================================================================

export interface PrimitiveValidationDefinition {
  minimum?: number;
  maximum?: number;
  exclusive_minimum?: number;
  exclusive_maximum?: number;

  /**
   * Decimal step/scale validation.
   * Example: 0.01 for two decimal places or 0.5 for half steps.
   */
  multiple_of?: number;

  min_length?: number;
  max_length?: number;
  pattern?: string;
}

// ============================================================================
// PRIMITIVE DEFINITION
// ============================================================================

export interface PrimitiveDefinition extends DefinitionItem {
  type: PrimitiveType;
  format?: PrimitiveFormat;
  validation?: PrimitiveValidationDefinition;
  example?: unknown;
}
