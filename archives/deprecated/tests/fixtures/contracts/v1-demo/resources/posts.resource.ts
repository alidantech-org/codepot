import { error } from '@/index';

import { v1 } from '../version';
import { post, user } from '../entities';
import { commonDtos, dtos } from '../dtos';
import { errors } from '../errors';
import { policies, security } from '../security';

// ============================================================================
// POSTS RESOURCE
// ============================================================================

export const posts = v1.defineResource({
  key: 'posts',
  folders: ['content'],
  security: security.protected(),
});

export const postSchemas = posts.defineSchemas();

export const postParams = postSchemas.params({
  id: post.ref.fields.id,
});

export const postErrors = posts.defineErrors({
  postLocked: error(423, commonDtos.ref.ErrorResponse, {
    intent: 'conflict',
    meta: { reason: 'post_locked' },
  }),
});

export const postDtos = postSchemas.dtos({
  PostResponse: dtos.ref.PostResponse.extendWith({
    authorName: user.ref.fields.name,
  }),

  PostListResponse: dtos.ref.PostListResponse.extendWith({
    items: post.ref.models.public.array().extendWith({
      authorName: user.ref.fields.name,
    }),
  }),
});

posts.defineRoutes().define((route) => ({
  listPosts: route
    .get('/')
    .query(dtos.ref.ListPostsQuery)
    .security(policies.ref.authenticated)
    .errors(errors.ref.unauthorized)
    .output(dtos.ref.PostListResponse),

  getPost: route
    .get('/:id')
    .params(postParams.ref.id)
    .security(policies.ref.authenticated)
    .errors(errors.ref.unauthorized, errors.ref.notFound)
    .output(dtos.ref.PostResponse),

  createPost: route
    .post('/')
    .body(dtos.ref.CreatePostBody)
    .security(policies.ref.tenantMember)
    .errors(errors.ref.validation, errors.ref.unauthorized)
    .created(dtos.ref.PostResponse),

  deletePost: route
    .delete('/:id')
    .params(postParams.ref.id)
    .security(policies.ref.tenantAdmin)
    .errors(errors.ref.unauthorized, errors.ref.forbidden, errors.ref.notFound)
    .noContent(),
}));
