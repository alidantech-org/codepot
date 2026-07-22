import { schemas } from './version';
import { post, tenant, user } from './entities';

// ============================================================================
// PARAMS
// ============================================================================

export const params = schemas.params({
  id: user.ref.fields.id,
  tenantId: tenant.ref.fields.id,
  postId: post.ref.fields.id,
});