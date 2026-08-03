import { content, error } from '@/index';

import { v1 } from './version';
import { commonDtos } from '.';

// ============================================================================
// ERRORS
// ============================================================================


export const errors = v1.defineErrors({
  unauthorized: error(401, commonDtos.ref.ErrorResponse, {
    intent: 'unauthorized',
  }),

  forbidden: error(403, commonDtos.ref.ErrorResponse, {
    intent: 'forbidden',
  }),

  notFound: error(404, commonDtos.ref.ErrorResponse, {
    intent: 'not_found',
  }),

  validation: error(422, commonDtos.ref.ValidationErrorResponse, {
    intent: 'validation',
  }),

  xmlError: error(400, commonDtos.ref.ErrorResponse, content.xml()),
});
