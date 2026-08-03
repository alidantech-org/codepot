import { v1 } from '../version';
import { dtos } from '../dtos';
import { errors } from '../errors';
import { params } from '../params';
import { policies } from '../security';

// ============================================================================
// TENANTS RESOURCE
// ============================================================================

export const tenants = v1.defineResource({
  key: 'tenants',
  folders: ['platform', 'tenant'],
  security: policies.ref.tenantMember,
});

tenants.defineRoutes().define((route) => ({
  getTenant: route
    .get('/:tenantId')
    .params(params.ref.tenantId)
    .security(policies.ref.tenantMember)
    .errors(errors.ref.unauthorized, errors.ref.forbidden, errors.ref.notFound)
    .output(dtos.ref.UserResponse),

  updateTenant: route
    .patch('/:tenantId')
    .params(params.ref.tenantId)
    .body(dtos.ref.UpdateProfileBody)
    .security(policies.ref.tenantAdmin)
    .errors(errors.ref.validation, errors.ref.forbidden)
    .output(dtos.ref.UserResponse),
}));