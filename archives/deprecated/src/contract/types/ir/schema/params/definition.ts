// src/contract/types/ir/schema/params/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { EntityFieldDefinition } from '../entity/field/definition';

// ============================================================================
// PARAMS
// ============================================================================

export interface ParamsDefinition extends DefinitionItem {
  readonly ref: Ref<EntityFieldDefinition>;
}
