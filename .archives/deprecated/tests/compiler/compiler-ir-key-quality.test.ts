import { describe, expect, it } from 'vitest';

import { compile } from '@/compiler';
import { v1 } from '../fixtures/contracts/v1-demo';

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Returns true when a key is snake_case or dot.scoped_snake_case.
 */
function isSnakeOrDottedSnakeKey(key: string): boolean {
  return /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:_[a-z0-9]+)*)*$/.test(key);
}

/**
 * Asserts all keys in a registry are snake_case or dotted snake_case.
 */
function expectRegistryKeysClean(registryName: string, registry: Record<string, unknown>): void {
  for (const key of Object.keys(registry)) {
    expect(isSnakeOrDottedSnakeKey(key), `${registryName} has invalid key "${key}"`).toBe(true);
  }
}

/**
 * Asserts a registry has no underscore-scoped keys.
 *
 * This prevents old promoted keys like users_email_taken.
 */
function expectNoUnderscoreScopedKeys(registryName: string, registry: Record<string, unknown>, scopes: readonly string[]): void {
  for (const key of Object.keys(registry)) {
    for (const scope of scopes) {
      expect(key.startsWith(`${scope}_`), `${registryName} has old underscore-scoped key "${key}"`).toBe(false);
    }
  }
}

function expectOwnedKeyHasThreeParts(registryName: string, key: string, identity: string): void {
  if (!key.startsWith(`${identity}.`)) return;

  expect(key.split('.'), `${registryName} owned key "${key}" must have identity.owner.item`).toHaveLength(3);
}

// ============================================================================
// TESTS
// ============================================================================

describe('compiler IR key quality', () => {
  it('emits normalized registry keys', () => {
    const ir = compile(v1.snapshot());

    expectRegistryKeysClean('content_types', ir.content_types);
    expectRegistryKeysClean('properties.primitives', ir.properties.primitives);
    expectRegistryKeysClean('properties.enums', ir.properties.enums);
    expectRegistryKeysClean('properties.composites', ir.properties.composites);

    expectRegistryKeysClean('schemas.entities', ir.schemas.entities);
    expectRegistryKeysClean('schemas.field_sets', ir.schemas.field_sets);
    expectRegistryKeysClean('schemas.models', ir.schemas.models);
    expectRegistryKeysClean('schemas.dtos', ir.schemas.dtos);
    expectRegistryKeysClean('schemas.params', ir.schemas.params);

    expectRegistryKeysClean('responses.errors', ir.responses.errors);
    expectRegistryKeysClean('security.credentials', ir.security.credentials);
    expectRegistryKeysClean('security.principals', ir.security.principals);
    expectRegistryKeysClean('security.policies', ir.security.policies);
    expectRegistryKeysClean('resources', ir.resources);
  });

  it('does not emit old underscore-scoped promoted keys', () => {
    const ir = compile(v1.snapshot());
    const scopes = Object.keys(ir.resources);

    expectNoUnderscoreScopedKeys('schemas.dtos', ir.schemas.dtos, scopes);
    expectNoUnderscoreScopedKeys('schemas.params', ir.schemas.params, scopes);
    expectNoUnderscoreScopedKeys('responses.errors', ir.responses.errors, scopes);
    expectNoUnderscoreScopedKeys('schemas.field_sets', ir.schemas.field_sets, scopes);
  });

  it('uses dotted keys for scoped root registries', () => {
    const ir = compile(v1.snapshot());

    expect(ir.responses.errors['resource.users.email_taken']).toBeDefined();
    expect(ir.schemas.params['resource.users.id']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.list_select']).toBeDefined();
    expect(ir.properties.primitives['entity.user.nickname']).toBeDefined();
    expect(ir.properties.primitives['composite.inline_money.amount']).toBeDefined();
  });

  it('uses three-part owned keys for owned registries', () => {
    const ir = compile(v1.snapshot());

    for (const key of Object.keys(ir.responses.errors)) {
      expectOwnedKeyHasThreeParts('responses.errors', key, 'resource');
    }

    for (const key of Object.keys(ir.schemas.params)) {
      expectOwnedKeyHasThreeParts('schemas.params', key, 'resource');
    }

    for (const key of Object.keys(ir.schemas.field_sets)) {
      expectOwnedKeyHasThreeParts('schemas.field_sets', key, 'entity');
    }

    for (const key of Object.keys(ir.properties.primitives)) {
      expectOwnedKeyHasThreeParts('properties.primitives', key, 'entity');
      expectOwnedKeyHasThreeParts('properties.primitives', key, 'composite');
    }
  });
});
