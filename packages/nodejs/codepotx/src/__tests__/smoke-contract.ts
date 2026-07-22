import { z } from 'zod';
import { ContentType, HttpMethod, defineVersionContract, schema } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Smoke API',
    version: 'v1',
    description: 'Smoke test for the transport-schema API',
  },
  defaults: {
    requestContentType: ContentType.json,
    responseContentType: ContentType.json,
  },
});

const sharedProps = v1.defineProperties('Shared', {
  mongoId: z.string().regex(/^[a-f\d]{24}$/i),
  dateTime: z.string().datetime(),
  success: z.boolean(),
  message: z.string().min(1).max(500),
  page: z.number().int().positive().max(10000),
  limit: z.number().int().positive().max(100),
  total: z.number().int().nonnegative(),
  pages: z.number().int().nonnegative(),
  search: z.string().min(1).max(100),
});

const sharedBaseSchemas = v1.defineSchemas({
  DateRangeQuery: {
    from: sharedProps.ref.dateTime.optional(),
    to: sharedProps.ref.dateTime.optional(),
  },

  ApiMessage: {
    success: sharedProps.ref.success,
    message: sharedProps.ref.message,
  },
});

const sharedSchemas = v1.defineSchemas({
  ValidationError: sharedBaseSchemas.ref.ApiMessage.extendWith({}),

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
});

v1.setDefaultResponses({
  400: sharedBaseSchemas.ref.ApiMessage,
  401: {
    schema: sharedBaseSchemas.ref.ApiMessage,
    description: 'Unauthorized',
  },
  422: {
    schema: v1.schemas.ref.ValidationError,
    description: 'Validation failed',
  },
  500: {
    schema: sharedBaseSchemas.ref.ApiMessage,
    description: 'Internal server error',
  },
});

const users = v1.defineResource({
  name: 'User',
  route: '/users',
});

const userProps = users.defineProperties('User', {
  id: z.string().regex(/^[a-f\d]{24}$/i),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  phone: z.string().min(7).max(20),
  avatar: z.string().url(),
  isOnline: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

const userQueryProps = users.defineProperties('UserQuery', {
  select: z.enum(['email', 'name', 'phone', 'avatar', 'isOnline']),
  sort: z.enum(['+createdAt', '-createdAt', '+name', '-name']),
});

const userPublicSchemas = users.defineSchemas({
  UserPublic: {
    id: userProps.ref.id,
    email: userProps.ref.email,
    name: userProps.ref.name,
    phone: userProps.ref.phone.nullable(),
    avatar: userProps.ref.avatar.nullable(),
    isOnline: userProps.ref.isOnline,
    createdAt: userProps.ref.createdAt,
    updatedAt: userProps.ref.updatedAt,
  },
});

const userFilterSchemas = users.defineSchemas({
  UserFilters: {
    email: userProps.ref.email.optional(),
    name: userProps.ref.name.optional(),
    isOnline: userProps.ref.isOnline.optional(),
    createdAt: sharedBaseSchemas.ref.DateRangeQuery.optional(),
    updatedAt: sharedBaseSchemas.ref.DateRangeQuery.optional(),
  },
});

const userSchemas = users.defineSchemas({
  UserRouteParams: {
    userId: userProps.ref.id,
  },

  UserListQuery: sharedSchemas.ref.BaseQuery.extendWith({
    filters: userFilterSchemas.ref.UserFilters.optional(),
    fields: userQueryProps.ref.select.array().optional(),
    sort: userQueryProps.ref.sort.array().optional(),
  }),

  UserDetailQuery: sharedSchemas.ref.DetailsQuery.extendWith({
    fields: userQueryProps.ref.select.array().optional(),
  }),

  UsersListOk: sharedBaseSchemas.ref.ApiMessage.extendWith({
    users: userPublicSchemas.ref.UserPublic.array(),
    pagination: sharedSchemas.ref.PaginationMeta,
  }),

  UserOk: sharedBaseSchemas.ref.ApiMessage.extendWith({
    user: userPublicSchemas.ref.UserPublic,
  }),

  UserWithExtra: sharedBaseSchemas.ref.ApiMessage.extendWith({
    user: userPublicSchemas.ref.UserPublic.extendWith({
      relatedUsers: userPublicSchemas.ref.UserPublic.array(),
    }),
  }),

  CreateUserBody: {
    email: userProps.ref.email,
    name: userProps.ref.name,
    phone: userProps.ref.phone.optional().nullable(),
  },

  UpdateUserBody: {
    email: userProps.ref.email.optional(),
    name: userProps.ref.name.optional(),
    phone: userProps.ref.phone.optional().nullable(),
    avatar: userProps.ref.avatar.optional().nullable(),
    isOnline: userProps.ref.isOnline.optional(),
  },
});

users.defineRoutes({
  params: userSchemas.ref.UserRouteParams,

  routes: {
    listUsers: {
      method: HttpMethod.get,
      path: '/',
      summary: 'List users',
      query: userSchemas.ref.UserListQuery,
      response: userSchemas.ref.UsersListOk,
    },

    createUser: {
      method: HttpMethod.post,
      path: '/',
      summary: 'Create user',
      body: userSchemas.ref.CreateUserBody,
      responses: {
        201: userSchemas.ref.UserOk,
      },
    },

    getUserById: {
      method: HttpMethod.get,
      path: '/:userId',
      summary: 'Get user by ID',
      query: userSchemas.ref.UserDetailQuery,
      response: userSchemas.ref.UserWithExtra,
    },

    updateUser: {
      method: HttpMethod.patch,
      path: '/:userId',
      summary: 'Update user',
      body: userSchemas.ref.UpdateUserBody,
      response: userSchemas.ref.UserOk,
    },

    deleteUser: {
      method: HttpMethod.delete,
      path: '/:userId',
      summary: 'Delete user',
      responses: {
        204: schema.noContent(),
      },
    },
  },
});

export const smokeContract = {
  v1,
  sharedContract: { sharedProps, sharedBaseSchemas, sharedSchemas },
  userContract: { users, userProps, userQueryProps, userPublicSchemas, userFilterSchemas, userSchemas },
};

export type SmokeContract = typeof smokeContract;
