// src/contract/types/ir/schema/field-set/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { EntityFieldDefinition } from '../entity/field/definition';

// ============================================================================
// FIELD SET
// ============================================================================

export interface FieldSetDefinition extends DefinitionItem {
  readonly fields: readonly Ref<EntityFieldDefinition>[];
}
