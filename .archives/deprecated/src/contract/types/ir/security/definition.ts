// src/contract/types/ir/security/definition.ts

import type { DefinitionItem } from '../definition';
import type { Ref } from '../ref';
import type { PrimitiveDefinition } from '../properties/primitive/definition';
import type { EntityFieldDefinition } from '../schema/entity/field/definition';

// ============================================================================
// CREDENTIALS
// ============================================================================

export const SecurityCredentialSource = {
  header: 'header',
  cookie: 'cookie',
  query: 'query',
} as const;

export type SecurityCredentialSource = (typeof SecurityCredentialSource)[keyof typeof SecurityCredentialSource];

export const SecurityCredentialFormat = {
  raw: 'raw',
  bearer: 'bearer',
  basic: 'basic',
  apiKey: 'api_key',
  session: 'session',
} as const;

export type SecurityCredentialFormat = (typeof SecurityCredentialFormat)[keyof typeof SecurityCredentialFormat];

export interface SecurityCredentialDefinition extends DefinitionItem {
  source: SecurityCredentialSource;
  key: string;
  format?: SecurityCredentialFormat;
  value_type?: Ref<PrimitiveDefinition>;
}

// ============================================================================
// PRINCIPALS
// ============================================================================

export type SecurityPrincipalFields = Record<string, Ref<EntityFieldDefinition>>;

export interface SecurityPrincipalDefinition extends DefinitionItem {
  fields: SecurityPrincipalFields;
}

// ============================================================================
// POLICIES
// ============================================================================

export const SecurityPolicyMode = {
  public: 'public',
  protected: 'protected',
} as const;

export type SecurityPolicyMode = (typeof SecurityPolicyMode)[keyof typeof SecurityPolicyMode];

export interface SecurityPolicyDefinition extends DefinitionItem {
  mode: SecurityPolicyMode;

  credential?: Ref<SecurityCredentialDefinition>;
  principals?: Record<string, Ref<SecurityPrincipalDefinition>>;

  roles?: string[];
  permissions?: string[];

  /**
   * Generator-facing intent, not runtime logic.
   * Examples: "authenticated", "tenant_role", "owner_only", "api_key".
   */
  intent?: string;
}

// ============================================================================
// ROOT SECURITY
// ============================================================================

export interface SecurityDefinition {
  credentials: Record<string, SecurityCredentialDefinition>;
  principals: Record<string, SecurityPrincipalDefinition>;
  policies: Record<string, SecurityPolicyDefinition>;
}
