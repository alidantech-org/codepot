// src/contract/types/ir/response/definition.ts

import type { ErrorResponseDefinition } from './errors/definition';

// ============================================================================
// RESPONSES
// ============================================================================

export interface ResponsesDefinition {
  errors: Record<string, ErrorResponseDefinition>;
}
