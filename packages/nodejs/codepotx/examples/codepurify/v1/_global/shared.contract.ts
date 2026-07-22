import { z } from 'zod';
import { v1 } from './version.contract.js';

const sharedProps = v1.defineProperties('Shared', {
  mongoId: z.string().regex(/^[a-f\d]{24}$/i),
  dateTime: z.string().datetime(),
  displayName: z.string().min(1).max(100),
  success: z.boolean(),
  message: z.string().min(1).max(500),
  page: z.number().int().positive().max(10000),
  limit: z.number().int().positive().max(100),
  total: z.number().int().nonnegative(),
  pages: z.number().int().nonnegative(),
  search: z.string(),
  field: z.string(),
  errorCode: z.string(),
  min: z.number(),
  max: z.number(),
  gte: z.number(),
  lte: z.number(),
  from: z.string().datetime(),
  to: z.string().datetime(),
});

const baseSchemas = v1.defineSchemas({
  BaseEntity: {
    id: sharedProps.ref.mongoId,
    createdAt: sharedProps.ref.dateTime,
    updatedAt: sharedProps.ref.dateTime,
    deletedAt: sharedProps.ref.dateTime.nullable(),
  },

  PublicBaseEntity: {
    id: sharedProps.ref.mongoId,
    createdAt: sharedProps.ref.dateTime,
    updatedAt: sharedProps.ref.dateTime,
  },

  ApiMessage: {
    success: sharedProps.ref.success,
    message: sharedProps.ref.message,
  },

  ValidationIssue: {
    field: sharedProps.ref.field,
    message: sharedProps.ref.message,
  },
});

const sharedSchemas = v1.defineSchemas({
  ValidationError: baseSchemas.ref.ApiMessage.extendWith({
    errors: baseSchemas.ref.ValidationIssue.array(),
  }),

  PaginationMeta: {
    page: sharedProps.ref.page,
    limit: sharedProps.ref.limit,
    total: sharedProps.ref.total,
    pages: sharedProps.ref.pages,
  },

  BaseQuery: {
    page: sharedProps.ref.page.optional(),
    limit: sharedProps.ref.limit.optional(),
    search: sharedProps.ref.search.optional(),
  },

  DetailsQuery: {},

  NumberRangeQuery: {
    min: sharedProps.ref.min.optional(),
    max: sharedProps.ref.max.optional(),
    gte: sharedProps.ref.gte.optional(),
    lte: sharedProps.ref.lte.optional(),
  },

  DateRangeQuery: {
    from: sharedProps.ref.from.optional(),
    to: sharedProps.ref.to.optional(),
    gte: sharedProps.ref.gte.optional(),
    lte: sharedProps.ref.lte.optional(),
  },

  PaginatedResponse: baseSchemas.ref.ApiMessage.extendWith({}),
});

const baseEntities = v1.defineBaseEntities({
  BaseEntity: {
    kind: 'abstract',
    schema: baseSchemas.ref.BaseEntity,
    fields: {
      id: ($) => $.unique().index().role('primaryKey').query((q) => q.exact()),
      createdAt: ($) => $.role('createdAt').query((q) => q.date().range().sort()),
      updatedAt: ($) => $.role('updatedAt').query((q) => q.date().range().sort()),
      deletedAt: ($) => $.role('softDelete').query((q) => q.date().range()),
    },
  },
});

v1.setDefaultResponses({
  400: baseSchemas.ref.ApiMessage,
  401: baseSchemas.ref.ApiMessage,
  403: baseSchemas.ref.ApiMessage,
  404: baseSchemas.ref.ApiMessage,
  422: {
    schema: sharedSchemas.ref.ValidationError,
    description: 'Validation failed',
  },
  500: baseSchemas.ref.ApiMessage,
});

export const sharedContract = {
  sharedProps,
  sharedSchemas: v1.schemas,
  baseEntity: baseSchemas.ref.BaseEntity,
  publicBaseEntity: baseSchemas.ref.PublicBaseEntity,
  baseEntities: baseEntities.ref,
};
