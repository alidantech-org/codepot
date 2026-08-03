// src/compiler/naming/owned-key.ts

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// OWNED KEY
// ============================================================================

/**
 * Creates a three-part searchable ownership key.
 *
 * Format:
 * identity.owner_key.original_key
 *
 * Examples:
 * - resource.users.email_taken
 * - entity.user.nickname
 * - composite.inline_money.amount
 */
export function createOwnedKey(identity: string, ownerKey: string, itemKey: string): string {
  return [toSnakeCaseKey(identity), toSnakeCaseKey(ownerKey), toSnakeCaseKey(itemKey)].join('.');
}
