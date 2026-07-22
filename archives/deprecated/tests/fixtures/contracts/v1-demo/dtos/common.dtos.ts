import { schemas } from '../version';
import { primitives } from '../properties';

// ============================================================================
// COMMON DTOS
// ============================================================================

export const commonDtos = schemas.dtos({
  ErrorResponse: {
    message: primitives.ref.message.required(),
    code: primitives.ref.text.optional(),
  },

  ValidationErrorResponse: {
    message: primitives.ref.message.required(),
    field: primitives.ref.text.optional(),
  },

  ApiResponse: {
    success: primitives.ref.boolean.required(),
    message: primitives.ref.message.optional(),
  },

  PaginatedResponse: {
    page: primitives.ref.integer.required(),
    limit: primitives.ref.integer.required(),
    total: primitives.ref.integer.required(),
  },
});