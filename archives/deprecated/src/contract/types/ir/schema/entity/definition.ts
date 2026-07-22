// src/contract/types/ir/schema/entity/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { ResourceDefinition } from '../../resource/definition';
import type { EntityFieldDefinition } from './field/definition';

// ============================================================================
// ENTITY DEFINITION
// ============================================================================

export interface EntityDefinition extends DefinitionItem {
  /**
   * Optional compiled ownership ref.
   * Useful for codegen placement, but not required for shared/global entities.
   */
  resource?: Ref<ResourceDefinition>;

  /**
   * Optional grouping/search/docs tags.
   */
  tags?: string[];

  /**
   * Real entity inheritance only.
   * One parent max keeps generated classes safe.
   */
  extends?: Ref<EntityDefinition>;

  /**
   * Abstract entities are reusable schema bases, not concrete runtime records.
   * Codegen may skip DB/table emission for abstract entities by default.
   */
  abstract?: boolean;

  /**
   * Entity-owned fields only.
   *
   * Inherited fields are available through `extends` and should not be
   * duplicated here unless the compiler intentionally flattens output.
   */
  fields: Record<string, EntityFieldDefinition>;
}
