// src/compiler/resolvers/security-resolver.ts

import type {
  SecurityCredentialDefinition,
  SecurityPrincipalDefinition,
  SecurityPolicyDefinition,
} from '@/contract/types/ir/security/definition';

import type {
  SecurityAuthoringState,
  SecurityCredentialInput,
  SecurityPrincipalInput,
  SecurityPolicyInput,
} from '@/contract/types/authoring/9.security-builder';

import type { EntityFieldAuthoringRef, PrimitiveAuthoringRef, PropertyAuthoringRef } from '@/contract/types/authoring/3.authoring-ref';

import type { Ref } from '@/contract/types/ir/ref';
import type { EntityFieldDefinition } from '@/contract/types/ir/schema/entity/field/definition';
import type { PrimitiveDefinition } from '@/contract/types/ir/properties/primitive/definition';

import { entityFieldRef, propertyPrimitiveRef, securityCredentialRef, securityPrincipalRef } from './ref-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// INPUTS
// ============================================================================

export interface ResolveSecurityCredentialInput {
  readonly key: string;
  readonly credential: SecurityCredentialInput;
}

export interface ResolveSecurityPrincipalInput {
  readonly key: string;
  readonly principal: SecurityPrincipalInput;
}

export interface ResolveSecurityPolicyInput {
  readonly key: string;
  readonly policy: SecurityPolicyInput;
}

// ============================================================================
// DEFINITION ITEM
// ============================================================================

/**
 * Copies shared definition metadata from authoring into IR.
 */
function resolveDefinitionItem(input: {
  readonly description?: string;
  readonly deprecated?: boolean;
  readonly meta?: Record<string, unknown>;
}): Record<string, unknown> {
  return {
    ...(input.description !== undefined ? { description: input.description } : {}),
    ...(input.deprecated !== undefined ? { deprecated: input.deprecated } : {}),
    ...(input.meta !== undefined ? { meta: input.meta } : {}),
  };
}

// ============================================================================
// AUTHORING REF GUARDS
// ============================================================================

/**
 * Checks whether an input value is an authoring ref-like object.
 */
function isAuthoringRef(input: unknown): input is {
  readonly id: string;
  readonly kind: string;
  readonly key: string;
} {
  return (
    input !== null &&
    typeof input === 'object' &&
    'id' in input &&
    typeof input.id === 'string' &&
    'kind' in input &&
    typeof input.kind === 'string' &&
    'key' in input &&
    typeof input.key === 'string'
  );
}

// ============================================================================
// FIELD REFS
// ============================================================================

/**
 * Resolves an entity field authoring ref into an IR entity field ref.
 */
function resolveEntityFieldAuthoringRef(input: EntityFieldAuthoringRef): Ref<EntityFieldDefinition> {
  const parts = input.id.split(':');
  const entityIndex = parts.indexOf('entity');
  const fieldIndex = parts.indexOf('field');

  if (entityIndex < 0 || fieldIndex < 0) {
    throw new Error(`Invalid entity field ref id "${input.id}".`);
  }

  return entityFieldRef(toSnakeCaseKey(parts[entityIndex + 1]), toSnakeCaseKey(parts[fieldIndex + 1]));
}

/**
 * Resolves a primitive/property authoring ref into a primitive IR ref.
 */
function resolvePrimitiveValueTypeRef(input: PrimitiveAuthoringRef | PropertyAuthoringRef): Ref<PrimitiveDefinition> {
  if (input.kind === 'property.primitive') {
    return propertyPrimitiveRef(toSnakeCaseKey(input.key));
  }

  throw new Error(`Security credential value_type must reference a primitive property. Got "${input.kind}".`);
}

// ============================================================================
// CREDENTIALS
// ============================================================================

/**
 * Converts an authoring security credential into an IR security credential.
 */
export function resolveSecurityCredential(input: ResolveSecurityCredentialInput): SecurityCredentialDefinition {
  const credential = input.credential;

  return {
    ...resolveDefinitionItem(credential),

    source: credential.source,
    key: credential.key,

    ...(credential.format !== undefined ? { format: credential.format } : {}),

    ...(credential.valueType !== undefined
      ? {
          value_type: resolvePrimitiveValueTypeRef(credential.valueType),
        }
      : {}),
  };
}

// ============================================================================
// PRINCIPALS
// ============================================================================

/**
 * Normalizes principal input into a field map.
 *
 * Authoring may store principals either as:
 * - { fields: { id: ref } }
 * - { id: ref, roles: ref }
 */
function getPrincipalFields(principal: SecurityPrincipalInput): Record<string, unknown> {
  if (
    principal !== null &&
    typeof principal === 'object' &&
    'fields' in principal &&
    principal.fields !== undefined &&
    principal.fields !== null
  ) {
    return principal.fields as unknown as Record<string, unknown>;
  }

  return principal as unknown as Record<string, unknown>;
}

/**
 * Converts authoring principal fields into IR field refs.
 */
function resolvePrincipalFields(principal: SecurityPrincipalInput): SecurityPrincipalDefinition['fields'] {
  const fields = getPrincipalFields(principal);
  const output: SecurityPrincipalDefinition['fields'] = {};

  for (const [key, ref] of Object.entries(fields)) {
    if (!isAuthoringRef(ref) || ref.kind !== 'schema.entity.field') {
      throw new Error(`Security principal field "${key}" must reference an entity field.`);
    }

    output[toSnakeCaseKey(key)] = resolveEntityFieldAuthoringRef(ref as EntityFieldAuthoringRef);
  }

  return output;
}

/**
 * Converts an authoring security principal into an IR security principal.
 */
export function resolveSecurityPrincipal(input: ResolveSecurityPrincipalInput): SecurityPrincipalDefinition {
  return {
    ...resolveDefinitionItem(input.principal),
    fields: resolvePrincipalFields(input.principal),
  };
}

// ============================================================================
// POLICIES
// ============================================================================

/**
 * Resolves a credential value into an IR credential ref.
 */
function resolvePolicyCredential(credential: SecurityPolicyInput['credential']): SecurityPolicyDefinition['credential'] {
  if (credential === undefined) return undefined;

  if (!isAuthoringRef(credential)) {
    throw new Error('Security policy credential must be an authoring ref.');
  }

  return securityCredentialRef(toSnakeCaseKey(credential.key));
}

/**
 * Resolves policy principals into IR principal refs.
 */
function resolvePolicyPrincipals(principals: SecurityPolicyInput['principals']): SecurityPolicyDefinition['principals'] {
  if (principals === undefined) return undefined;

  const output: NonNullable<SecurityPolicyDefinition['principals']> = {};

  for (const [key, principal] of Object.entries(principals)) {
    if (!isAuthoringRef(principal)) {
      throw new Error(`Security policy principal "${key}" must be an authoring ref.`);
    }

    output[toSnakeCaseKey(key)] = securityPrincipalRef(toSnakeCaseKey(principal.key));
  }

  return output;
}

/**
 * Converts an authoring security policy into an IR security policy.
 */
export function resolveSecurityPolicy(input: ResolveSecurityPolicyInput): SecurityPolicyDefinition {
  const policy = input.policy;

  return {
    ...resolveDefinitionItem(policy),

    mode: policy.mode,

    ...(policy.credential !== undefined ? { credential: resolvePolicyCredential(policy.credential) } : {}),

    ...(policy.principals !== undefined ? { principals: resolvePolicyPrincipals(policy.principals) } : {}),

    ...(policy.roles !== undefined ? { roles: [...policy.roles] } : {}),
    ...(policy.permissions !== undefined ? { permissions: [...policy.permissions] } : {}),

    ...(policy.intent !== undefined ? { intent: policy.intent } : {}),
  };
}

// ============================================================================
// STATE HELPERS
// ============================================================================

/**
 * Returns a complete security authoring state shape.
 */
export function getSecurityState(state: Partial<SecurityAuthoringState>): SecurityAuthoringState {
  return {
    credentials: state.credentials ?? {},
    principals: state.principals ?? {},
    policies: state.policies ?? {},
  };
}
