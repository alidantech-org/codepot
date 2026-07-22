// src/contract/types/ir/response/errors/definition.ts

import type { DefinitionItem } from '../../definition';
import type { Ref } from '../../ref';
import type { ContentTypeDefinition } from '../../content/definition';
import type { DtoDefinition } from '../../schema/dto/definition';

// ============================================================================
// ERROR RESPONSE
// ============================================================================

export interface ErrorResponseDefinition extends DefinitionItem {
  status: number;
  intent?: string;
  schema: Ref<DtoDefinition>;
  content_type: Ref<ContentTypeDefinition>;
  headers?: Record<string, Ref<DtoDefinition>>;
}
