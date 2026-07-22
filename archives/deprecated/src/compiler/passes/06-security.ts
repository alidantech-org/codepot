// src/compiler/passes/06-security.ts

import type { CompilerContext } from '../context/compiler-context';

import {
  getSecurityState,
  resolveSecurityCredential,
  resolveSecurityPolicy,
  resolveSecurityPrincipal,
} from '../resolvers/security-resolver';

import { toSnakeCaseKey } from '@/utils/naming/normalize-key';

// ============================================================================
// CREDENTIALS
// ============================================================================

/**
 * Compiles security credentials into IR security credentials.
 */
function compileSecurityCredentials(ctx: CompilerContext): void {
  const security = getSecurityState(ctx.authoring.security);

  for (const [key, credential] of Object.entries(security.credentials)) {
    ctx.ir.security.credentials[toSnakeCaseKey(key)] = resolveSecurityCredential({
      key,
      credential,
    });
  }
}

// ============================================================================
// PRINCIPALS
// ============================================================================

/**
 * Compiles security principals into IR security principals.
 */
function compileSecurityPrincipals(ctx: CompilerContext): void {
  const security = getSecurityState(ctx.authoring.security);

  for (const [key, principal] of Object.entries(security.principals)) {
    ctx.ir.security.principals[toSnakeCaseKey(key)] = resolveSecurityPrincipal({
      key,
      principal,
    });
  }
}

// ============================================================================
// POLICIES
// ============================================================================

/**
 * Compiles security policies into IR security policies.
 */
function compileSecurityPolicies(ctx: CompilerContext): void {
  const security = getSecurityState(ctx.authoring.security);

  for (const [key, policy] of Object.entries(security.policies)) {
    ctx.ir.security.policies[toSnakeCaseKey(key)] = resolveSecurityPolicy({
      key,
      policy,
    });
  }
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles authoring security registry into IR security registry.
 */
export function compileSecurity(ctx: CompilerContext): void {
  compileSecurityCredentials(ctx);
  compileSecurityPrincipals(ctx);
  compileSecurityPolicies(ctx);
}
