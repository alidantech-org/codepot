// src/contract/constants/ir-ref-paths.ts

import { valueObject } from './values';

// ============================================================================
// IR REF ROOT
// ============================================================================

export const IrRefRoot = '#';

// ============================================================================
// IR REF SECTIONS
// ============================================================================

export const IrRefSectionValues = [
  'content_types',
  'properties',
  'primitives',
  'enums',
  'composites',
  'schemas',
  'entities',
  'fields',
  'field_sets',
  'models',
  'dtos',
  'params',
  'responses',
  'errors',
  'security',
  'credentials',
  'principals',
  'policies',
  'resources',
  'operations',
] as const;

export const IrRefSection = valueObject(IrRefSectionValues);

export type IrRefSection = (typeof IrRefSectionValues)[number];

// ============================================================================
// IR REF PATH HELPERS
// ============================================================================

/**
 * Builds a stable JSON/YAML `$ref` path for compiled Codepot IR.
 */
export function createIrRefPath(...segments: readonly string[]): string {
  return `${IrRefRoot}/${segments.join('/')}`;
}
