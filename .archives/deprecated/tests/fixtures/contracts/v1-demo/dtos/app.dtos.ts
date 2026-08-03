import { post, user } from '../entities';
import { primitives } from '../properties';
import { schemas } from '../version';
import { commonDtos } from './common.dtos';

export const dtos = schemas.dtos({
  // Mode 1: direct model-backed DTOs
  UserPublic: user.ref.models.public,
  UserPatchBody: user.ref.models.patch,
  PostPublic: post.ref.models.public,

  // Mode 2: field-map DTOs
  ListUsersQuery: {
    search: primitives.ref.text.optional(),
    role: user.ref.fields.role.optional(),
    status: user.ref.fields.status.optional(),
    page: primitives.ref.integer.optional(),
    limit: primitives.ref.integer.optional(),
  },

  ListPostsQuery: {
    search: primitives.ref.text.optional(),
    status: post.ref.fields.status.optional(),
    author: post.ref.fields.author.optional(),
    page: primitives.ref.integer.optional(),
    limit: primitives.ref.integer.optional(),
  },

  CreateUserBody: {
    name: user.ref.fields.name.required(),
    email: user.ref.fields.email.required(),
    role: user.ref.fields.role.required(),
    tenant: user.ref.fields.tenant.required(),
  },

  CreatePostBody: {
    title: post.ref.fields.title.required(),
    body: post.ref.fields.body.required(),
    status: post.ref.fields.status.optional(),
  },

  UpdateProfileBody: {
    name: user.ref.fields.name.optional(),
    bio: user.ref.fields.bio.optional().nullable(),
  },

  UploadAvatarBody: {
    file: primitives.ref.fileName.required(),
  },

  FeedResponse: {
    title: primitives.ref.title.required(),
    body: primitives.ref.bio.required(),
  },

  ExportUsersResponse: {
    fileName: primitives.ref.fileName.required(),
  },

  // Mode 3: extendWith composition
  UploadAvatarResponse: commonDtos.ref.ApiResponse.extendWith({
    user: user.ref.models.public.required(),
  }),

  UserResponse: commonDtos.ref.ApiResponse.extendWith({
    user: user.ref.models.public.required(),
  }),

  UserListResponse: commonDtos.ref.PaginatedResponse.extendWith({
    items: user.ref.models.public.array().required(),
  }),

  PostResponse: commonDtos.ref.ApiResponse.extendWith({
    post: post.ref.models.public.required(),
  }),

  PostListResponse: commonDtos.ref.PaginatedResponse.extendWith({
    items: post.ref.models.public.array().required(),
  }),

  // Entity field inheritance/override proofs
  UserBioInheritsEntityOptions: {
    bio: user.ref.fields.bio,
  },

  UserBioRequiredButStillNullable: {
    bio: user.ref.fields.bio.required(),
  },

  UserBioRequiredNonNullable: {
    bio: user.ref.fields.bio.required().nonNullable(),
  },

  UserEmailOptionalOverride: {
    email: user.ref.fields.email.optional(),
  },

  UserRolesInheritArray: {
    roles: user.ref.fields.roles,
  },

  UserPrimaryRoleSingle: {
    role: user.ref.fields.roles.single(),
  },

  UserRoleArrayOverride: {
    roles: user.ref.fields.role.array(),
  },

  UserPrimaryRoleStrict: {
    role: user.ref.fields.roles.required().nonNullable().single(),
  },
});
