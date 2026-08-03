// src/contract/types/ir/properties/definition.ts

import type { PrimitiveDefinition } from './primitive/definition';
import type { EnumDefinition } from './enum/definition';
import type { CompositeDefinition } from './composite/definition';

// ============================================================================
// PROPERTY REFS
// ============================================================================

export type RefProperty = PrimitiveDefinition | EnumDefinition | CompositeDefinition;

// ============================================================================
// PROPERTIES DEFINITION
// ============================================================================

export interface PropertiesDefinition {
  primitives: Record<string, PrimitiveDefinition>;
  enums: Record<string, EnumDefinition>;
  composites: Record<string, CompositeDefinition>;
}
