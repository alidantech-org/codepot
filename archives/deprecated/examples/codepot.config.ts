// examples/codepot.config.ts

import { content, defineCodepotConfig, defineVersionContract, error, field, property } from 'codepot';

// ============================================================================
// VERSION
// ============================================================================

const v1 = defineVersionContract({
  codepot: '1.0',
  key: 'demo_api',
  version: 1,
  info: {
    title: 'Demo API',
    version: '1.0.0',
  },
});

const properties = v1.defineProperties();
const schemas = v1.defineSchemas();

// ============================================================================
// PROPERTIES
// ============================================================================

const primitives = properties.primitives({
  id: property.uuid(),
  text: property.string(),
  email: property.email(),
  displayName: property.string().minLength(2).maxLength(80),
  message: property.string().maxLength(1000),
});

const enums = properties.enums({
  UserRole: property.enum({
    admin: {
      value: 'admin',
      label: 'Admin',
    },
    member: {
      value: 'member',
      label: 'Member',
    },
  }),
});

// ============================================================================
// SCHEMAS
// ============================================================================

const baseEntity = schemas.entity(
  'BaseEntity',
  {
    id: field(primitives.ref.id)
      .required()
      .capability((capability) => capability.filter().sort().select())
      .lifecycle((lifecycle) => lifecycle.generated().immutable())
      .persistence((persistence) => persistence.stored()),
  },
  {
    abstract: true,
  },
);

const user = schemas
  .entity(
    'User',
    {
      name: field(primitives.ref.displayName)
        .required()
        .capability((capability) => capability.filter().sort().select())
        .visibility((visibility) => visibility.public())
        .persistence((persistence) => persistence.stored()),

      email: field(primitives.ref.email)
        .required()
        .capability((capability) => capability.filter().select(false))
        .visibility((visibility) => visibility.internal().sensitive())
        .persistence((persistence) => persistence.stored()),

      role: field(enums.ref.UserRole)
        .required()
        .capability((capability) => capability.filter().sort())
        .visibility((visibility) => visibility.public())
        .persistence((persistence) => persistence.stored()),
    },
    {
      extends: baseEntity,
    },
  )
  .fieldSets({
    listSelect: (set) => set.only('id', 'name', 'role'),
    listFilter: (set) => set.only('id', 'role'),
  })
  .models({
    public: (model) => model.pick('id', 'name', 'role'),
    create: (model) => model.omit('id'),
    patch: (model) => model.partial().omit('id'),
  });

const dtos = schemas.dtos({
  ErrorResponse: {
    message: primitives.ref.message.required(),
    code: primitives.ref.text.optional(),
  },

  UserResponse: {
    user: user.ref.models.public.required(),
  },

  ListUsersQuery: {
    search: primitives.ref.text.optional(),
    role: user.ref.fields.role.optional(),
  },
});

const params = schemas.params({
  id: baseEntity.ref.fields.id,
});

// ============================================================================
// SECURITY
// ============================================================================

const security = v1.defineSecurity();

const credentials = security.credentials({
  accessToken: security.bearerHeader({
    valueType: primitives.ref.text,
  }),
});

const principals = security.principals({
  user: security.principal({
    id: user.ref.fields.id,
    roles: user.ref.fields.role,
  }),
});

const policies = security.policies({
  public: security.public(),
  protected: security.require({
    credential: credentials.ref.accessToken,
    principals: {
      user: principals.ref.user,
    },
  }),
});

// ============================================================================
// ERRORS
// ============================================================================

const errors = v1.defineErrors({
  unauthorized: error(401, dtos.ref.ErrorResponse, {
    intent: 'unauthorized',
  }),

  forbidden: error(403, dtos.ref.ErrorResponse, {
    intent: 'forbidden',
  }),
});

// ============================================================================
// RESOURCE
// ============================================================================

const users = v1.defineResource({
  key: 'users',
  folders: ['platform', 'auth'],
  security: policies.ref.protected,
});

const userSchemas = users.defineSchemas();

const userParams = userSchemas.params({
  id: baseEntity.ref.fields.id,
});

const userErrors = users.defineErrors({
  emailTaken: error(409, dtos.ref.ErrorResponse, {
    intent: 'conflict',
    meta: {
      reason: 'email_taken',
    },
  }),
});

users.defineRoutes().define((route) => ({
  listUsers: route
    .get('/')
    .query(dtos.ref.ListUsersQuery)
    .security(policies.ref.protected)
    .errors(errors.ref.unauthorized, errors.ref.forbidden)
    .output(dtos.ref.UserResponse, content.json()),

  getUser: route
    .get('/:id')
    .params(userParams.ref.id)
    .security(policies.ref.protected)
    .errors(errors.ref.unauthorized, errors.ref.forbidden, userErrors.ref.emailTaken)
    .output(dtos.ref.UserResponse, content.json()),
}));

// ============================================================================
// CONFIG
// ============================================================================

export default defineCodepotConfig({
  output: {
    folder: 'codepot.generated',
  },
  contracts: [v1],
});
