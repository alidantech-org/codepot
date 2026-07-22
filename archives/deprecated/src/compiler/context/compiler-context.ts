// src/compiler/context/compiler-context.ts

import type { VersionAuthoringState } from '@/contract/types/authoring/2.version-builder';
import type { CodepotDefinition } from '@/contract/types/ir/definition';

import type { CompilerDiagnostic } from './diagnostics';

// ============================================================================
// CONTEXT
// ============================================================================

export interface CompilerContext {
  readonly authoring: VersionAuthoringState;
  readonly diagnostics: CompilerDiagnostic[];
  readonly ir: CodepotDefinition;
}

// ============================================================================
// EMPTY IR FACTORY
// ============================================================================

function createEmptyIr(authoring: VersionAuthoringState): CodepotDefinition {
  return {
    codepot: authoring.codepot,
    key: authoring.key,
    version: authoring.version,

    info: authoring.info,

    urls: [],

    content_types: {},

    properties: {
      primitives: {},
      enums: {},
      composites: {},
    },

    schemas: {
      entities: {},
      field_sets: {},
      models: {},
      dtos: {},
      params: {},
    },

    responses: {
      errors: {},
    },

    security: {
      credentials: {},
      principals: {},
      policies: {},
    },

    resources: {},

    ...(authoring.description !== undefined ? { description: authoring.description } : {}),

    ...(authoring.deprecated !== undefined ? { deprecated: authoring.deprecated } : {}),

    ...(authoring.meta !== undefined ? { meta: authoring.meta } : {}),
  };
}

// ============================================================================
// CREATE CONTEXT
// ============================================================================

export function createCompilerContext(authoring: VersionAuthoringState): CompilerContext {
  return {
    authoring,
    diagnostics: [],
    ir: createEmptyIr(authoring),
  };
}
