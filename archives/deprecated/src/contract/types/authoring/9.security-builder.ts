import type {
  EntityFieldAuthoringRef,
  PropertyAuthoringRef,
  SecurityCredentialAuthoringRef,
  SecurityPolicyAuthoringRef,
  SecurityPrincipalAuthoringRef,
} from './3.authoring-ref';

import type { DefinitionItem } from './4.properties-builder';

// ============================================================================
// AUTHORING SECURITY TYPES
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

// ============================================================================
// CREDENTIAL INPUTS
// ============================================================================

export type SecurityCredentialValueType = PropertyAuthoringRef;

export interface SecurityCredentialOptions extends DefinitionItem {
  readonly format?: SecurityCredentialFormat;
  readonly valueType?: SecurityCredentialValueType;
}

export interface SecurityCredentialInput extends DefinitionItem {
  readonly source: SecurityCredentialSource;
  readonly key: string;
  readonly format?: SecurityCredentialFormat;
  readonly valueType?: SecurityCredentialValueType;
}

export type SecurityCredentialInputMap = Record<string, SecurityCredentialInput>;

export interface SecurityCredentialsResult<TInput extends SecurityCredentialInputMap> {
  readonly credentials: TInput;

  readonly ref: {
    readonly [K in keyof TInput & string]: SecurityCredentialAuthoringRef;
  };
}

// ============================================================================
// PRINCIPAL INPUTS
// ============================================================================

export type SecurityPrincipalInput = Record<string, EntityFieldAuthoringRef>;

export type SecurityPrincipalInputMap = Record<string, SecurityPrincipalInput>;

export interface SecurityPrincipalsResult<TInput extends SecurityPrincipalInputMap> {
  readonly principals: TInput;

  readonly ref: {
    readonly [K in keyof TInput & string]: SecurityPrincipalAuthoringRef;
  };
}

// ============================================================================
// POLICY INPUTS
// ============================================================================

export const SecurityPolicyMode = {
  public: 'public',
  protected: 'protected',
} as const;

export type SecurityPolicyMode = (typeof SecurityPolicyMode)[keyof typeof SecurityPolicyMode];

export type SecurityPrincipalRefMap = Record<string, SecurityPrincipalAuthoringRef>;

export interface SecurityRequirePolicyInput extends DefinitionItem {
  readonly credential?: SecurityCredentialAuthoringRef;
  readonly principals?: SecurityPrincipalRefMap;
  readonly roles?: readonly string[];
  readonly permissions?: readonly string[];
  readonly intent?: string;
}

export interface SecurityPolicyInput extends DefinitionItem {
  readonly mode: 'public' | 'protected';
  readonly credential?: SecurityCredentialAuthoringRef;
  readonly principals?: SecurityPrincipalRefMap;
  readonly roles?: readonly string[];
  readonly permissions?: readonly string[];
  readonly intent?: string;
}

export type SecurityPolicyInputMap = Record<string, SecurityPolicyInput>;

export interface SecurityPoliciesResult<TInput extends SecurityPolicyInputMap> {
  readonly policies: TInput;

  readonly ref: {
    readonly [K in keyof TInput & string]: SecurityPolicyAuthoringRef;
  };
}

// ============================================================================
// SECURITY AUTHORING STATE (mutable, not compiled IR)
// ============================================================================

export interface SecurityAuthoringState {
  credentials: Record<string, SecurityCredentialInput>;
  principals: Record<string, SecurityPrincipalInput>;
  policies: Record<string, SecurityPolicyInput>;
}

// ============================================================================
// SECURITY BUILDER
// ============================================================================

export interface SecurityBuilder {
  readonly state: Partial<SecurityAuthoringState>;

  header(key: string, options?: SecurityCredentialOptions): SecurityCredentialInput;

  cookie(key: string, options?: SecurityCredentialOptions): SecurityCredentialInput;

  query(key: string, options?: SecurityCredentialOptions): SecurityCredentialInput;

  bearerHeader(options?: Omit<SecurityCredentialOptions, 'format'>): SecurityCredentialInput;

  principal(fields: SecurityPrincipalInput): SecurityPrincipalInput;

  public(options?: DefinitionItem): SecurityPolicyInput;

  protected(options?: DefinitionItem): SecurityPolicyInput;

  require(input: SecurityRequirePolicyInput): SecurityPolicyInput;

  credentials<TInput extends SecurityCredentialInputMap>(credentials: TInput): SecurityCredentialsResult<TInput>;

  principals<TInput extends SecurityPrincipalInputMap>(principals: TInput): SecurityPrincipalsResult<TInput>;

  policies<TInput extends SecurityPolicyInputMap>(policies: TInput): SecurityPoliciesResult<TInput>;

  snapshot(): Partial<SecurityAuthoringState>;
}

export type RouteSecurityInput = SecurityPolicyAuthoringRef | SecurityPolicyInput;
export type RouteSecurityRefsInput = RouteSecurityInput;
