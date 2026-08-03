import { content, error } from '@/index';

import { v1 } from '../version';
import { user } from '../entities';
import { commonDtos, dtos } from '../dtos';
import { errors } from '../errors';
import { policies, security } from '../security';

// ============================================================================
// USERS RESOURCE
// ============================================================================

export const users = v1.defineResource({
  key: 'users',
  folders: ['platform', 'auth'],
  security: security.protected(),
});

export const userSchemas = users.defineSchemas();

export const userParams = userSchemas.params({
  id: user.ref.fields.id,
});

export const userErrors = users.defineErrors({
  emailTaken: error(409, commonDtos.ref.ErrorResponse, {
    intent: 'conflict',
    meta: { reason: 'email_taken' },
  }),
});

users.defineRoutes().define((route) => ({
  listUsers: route
    .get('/')
    .query(dtos.ref.ListUsersQuery)
    .security(policies.ref.tenantAdmin)
    .errors(errors.ref.unauthorized, errors.ref.forbidden)
    .output(dtos.ref.UserListResponse),

  getUser: route
    .get('/:id')
    .params(userParams.ref.id)
    .security(security.protected())
    .errors(errors.ref.unauthorized, errors.ref.notFound)
    .output(dtos.ref.UserResponse),

  createUser: route
    .post('/')
    .body(dtos.ref.CreateUserBody)
    .security(policies.ref.tenantAdmin)
    .errors(errors.ref.validation, userErrors.ref.emailTaken)
    .created(dtos.ref.UserResponse),

  updateProfile: route
    .patch('/:id/profile')
    .params(userParams.ref.id)
    .body(dtos.ref.UpdateProfileBody)
    .security(security.protected())
    .errors(errors.ref.validation, errors.ref.unauthorized, errors.ref.notFound)
    .output(dtos.ref.UserResponse),

  uploadAvatar: route
    .post('/:id/avatar')
    .params(userParams.ref.id)
    .body(dtos.ref.UploadAvatarBody, content.multipart())
    .security(security.protected())
    .errors(errors.ref.validation, errors.ref.unauthorized)
    .created(dtos.ref.UploadAvatarResponse),

  exportUsersCsv: route
    .get('/export.csv')
    .security(policies.ref.tenantAdmin)
    .errors(errors.ref.unauthorized, errors.ref.forbidden)
    .output(dtos.ref.ExportUsersResponse, content.csv()),

  feedXml: route
    .get('/feed.xml')
    .security(policies.ref.public)
    .errors(errors.ref.xmlError)
    .output(dtos.ref.FeedResponse, [content.json(), content.xml()]),

  deleteUser: route
    .delete('/:id')
    .params(userParams.ref.id)
    .security(policies.ref.tenantAdmin)
    .errors(errors.ref.unauthorized, errors.ref.notFound)
    .noContent(),

  legacyRawResponses: route.get('/legacy').responses({
    200: {
      status: 200,
      schema: dtos.ref.UserResponse,
      content: [content.json()],
    },
  }),
}));
