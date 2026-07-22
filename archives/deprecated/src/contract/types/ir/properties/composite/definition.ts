// src/contract/types/ir/properties/composite/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { ResourceDefinition } from '../../resource/definition';
import type { EntityDefinition } from '../../schema/entity/definition';
import type { PrimitiveDefinition } from '../primitive/definition';
import type { EnumDefinition } from '../enum/definition';

// ============================================================================
// COMPOSITE MEMBERS
// ============================================================================

export type CompositePropertyRef = Ref<PrimitiveDefinition> | Ref<EnumDefinition> | Ref<CompositeDefinition>;

// ============================================================================
// COMPOSITE DEFINITION
// ============================================================================

export interface CompositeDefinition extends DefinitionItem {
  /**
   * Real composite inheritance/extension.
   * One parent max keeps merge order predictable.
   */
  extends?: Ref<CompositeDefinition>;

  /**
   * Composite-owned fields.
   *
   * Values must be compiled refs. Inline authoring properties should already be
   * promoted by the compiler before this IR is emitted.
   */
  properties: Record<string, CompositePropertyRef>;

  /**
   * Optional compiled ownership refs.
   * Useful for codegen placement, but not required for shared/global composites.
   */
  resource?: Ref<ResourceDefinition>;
  entity?: Ref<EntityDefinition>;
}
