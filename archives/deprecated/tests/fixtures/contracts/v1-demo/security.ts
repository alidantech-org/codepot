import { v1 } from './version';
import { primitives } from './properties';
import { tenant, user } from './entities';

// ============================================================================
// SECURITY
// ============================================================================

export const security = v1.defineSecurity();

export const credentials = security.credentials({
  bearer: security.bearerHeader({
    valueType: primitives.ref.text,
  }),

  session: security.cookie('session_id', {
    format: 'session',
    valueType: primitives.ref.text,
  }),
});

export const principals = security.principals({
  user: security.principal({
    id: user.ref.fields.id,
    roles: user.ref.fields.roles,
    status: user.ref.fields.status,
  }),

  tenant: security.principal({
    id: tenant.ref.fields.id,
    ownerId: tenant.ref.fields.ownerId,
  }),
});

export const policies = security.policies({
  public: security.public(),

  authenticated: security.protected(),

  tenantMember: security.require({
    credential: credentials.ref.bearer,
    principals: {
      user: principals.ref.user,
      tenant: principals.ref.tenant,
    },
    roles: ['owner', 'admin', 'member'],
    intent: 'tenant_role',
  }),

  tenantAdmin: security.require({
    credential: credentials.ref.bearer,
    principals: {
      user: principals.ref.user,
      tenant: principals.ref.tenant,
    },
    roles: ['owner', 'admin'],
    permissions: ['users.read', 'users.write'],
    intent: 'tenant_role',
  }),
});