import type {
  SecurityAuthoringState,
  SecurityBuilder,
  SecurityCredentialInputMap,
  SecurityCredentialsResult,
  SecurityPrincipalInputMap,
  SecurityPrincipalsResult,
  SecurityPolicyInputMap,
  SecurityPoliciesResult,
} from '@/contract/types/authoring/9.security-builder';

import {
  bearerHeader,
  cookie,
  header,
  principal,
  publicPolicy,
  protectedPolicy,
  query,
  requirePolicy,
} from '@/contract/helpers/security/security';

import { securityCredentialRef, securityPolicyRef, securityPrincipalRef } from '@/contract/helpers/refs/authoring-ref-builder';

export interface DefineSecurityOptions {
  readonly state: Partial<SecurityAuthoringState>;
}

function ensureState(state: Partial<SecurityAuthoringState>): SecurityAuthoringState {
  state.credentials ??= {};
  state.principals ??= {};
  state.policies ??= {};

  return state as SecurityAuthoringState;
}

function createCredentialRefs<TInput extends SecurityCredentialInputMap>(input: TInput): SecurityCredentialsResult<TInput>['ref'] {
  const refs = {} as Record<keyof TInput & string, ReturnType<typeof securityCredentialRef>>;

  for (const key of Object.keys(input) as Array<keyof TInput & string>) {
    refs[key] = securityCredentialRef(key);
  }

  return refs as SecurityCredentialsResult<TInput>['ref'];
}

function createPrincipalRefs<TInput extends SecurityPrincipalInputMap>(input: TInput): SecurityPrincipalsResult<TInput>['ref'] {
  const refs = {} as Record<keyof TInput & string, ReturnType<typeof securityPrincipalRef>>;

  for (const key of Object.keys(input) as Array<keyof TInput & string>) {
    refs[key] = securityPrincipalRef(key);
  }

  return refs as SecurityPrincipalsResult<TInput>['ref'];
}

function createPolicyRefs<TInput extends SecurityPolicyInputMap>(input: TInput): SecurityPoliciesResult<TInput>['ref'] {
  const refs = {} as Record<keyof TInput & string, ReturnType<typeof securityPolicyRef>>;

  for (const key of Object.keys(input) as Array<keyof TInput & string>) {
    refs[key] = securityPolicyRef(key);
  }

  return refs as SecurityPoliciesResult<TInput>['ref'];
}

export function defineSecurity(options: DefineSecurityOptions): SecurityBuilder {
  const builder: SecurityBuilder = {
    get state() {
      return options.state;
    },

    header,

    cookie,

    query,

    bearerHeader,

    principal,

    public: publicPolicy,

    protected: protectedPolicy,

    require: requirePolicy,

    credentials<TInput extends SecurityCredentialInputMap>(credentials: TInput): SecurityCredentialsResult<TInput> {
      const state = ensureState(options.state);

      for (const [key, value] of Object.entries(credentials) as [keyof TInput & string, TInput[keyof TInput & string]][]) {
        state.credentials[key] = value;
      }

      return {
        credentials,
        ref: createCredentialRefs(credentials),
      };
    },

    principals<TInput extends SecurityPrincipalInputMap>(principals: TInput): SecurityPrincipalsResult<TInput> {
      const state = ensureState(options.state);

      for (const [key, value] of Object.entries(principals) as [keyof TInput & string, TInput[keyof TInput & string]][]) {
        state.principals[key] = value;
      }

      return {
        principals,
        ref: createPrincipalRefs(principals),
      };
    },

    policies<TInput extends SecurityPolicyInputMap>(policies: TInput): SecurityPoliciesResult<TInput> {
      const state = ensureState(options.state);

      for (const [key, value] of Object.entries(policies) as [keyof TInput & string, TInput[keyof TInput & string]][]) {
        state.policies[key] = value;
      }

      return {
        policies,
        ref: createPolicyRefs(policies),
      };
    },

    snapshot() {
      return options.state;
    },
  };

  return builder;
}
