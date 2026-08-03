// src/contract/types/ir/properties/enum/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { ResourceDefinition } from '../../resource/definition';
import type { EntityDefinition } from '../../schema/entity/definition';

// ============================================================================
// ENUM VALUES
// ============================================================================

export type EnumValuePrimitive = string | number;

export interface EnumValueDefinition extends DefinitionItem {
  value: EnumValuePrimitive;
  label?: string;
}

// ============================================================================
// ENUM DEFINITION
// ============================================================================

export interface EnumDefinition extends DefinitionItem {
  /**
   * Ordered enum values.
   *
   * Array is intentional so the compiled IR does not duplicate keys like:
   * values.owner.value = "owner".
   */
  values: EnumValueDefinition[];

  /**
   * Optional compiled ownership refs.
   * Useful for codegen placement, but not required for shared/global enums.
   */
  resource?: Ref<ResourceDefinition>;
  entity?: Ref<EntityDefinition>;
}
