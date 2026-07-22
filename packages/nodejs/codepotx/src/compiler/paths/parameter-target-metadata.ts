import type { XCodegenParameterTargetMeta } from '../../codegen/codegen-extension.types.js';

export interface ParameterTargetInput {
  readonly querySchemaRef?: string;
  readonly sharedPathParameterRefs?: readonly string[];
  readonly operationParameterRefs?: readonly string[];
  readonly excludedParameterRefs?: readonly string[];
}

export interface XCodegenOperationMeta {
  readonly resource?: {
    readonly name: string;
    readonly path?: readonly string[];
  };
  readonly parameters?: {
    readonly target: XCodegenParameterTargetMeta;
  };
}

export interface XCodegenPathMeta {
  readonly resource?: {
    readonly name: string;
    readonly path?: readonly string[];
  };
  readonly parameters?: {
    readonly target: XCodegenParameterTargetMeta;
  };
}

export function createOperationParameterTargetMeta(input: {
  readonly querySchemaRef?: string;
  readonly operationParameterRefs: readonly string[];
  readonly excludedParameterRefs?: readonly string[];
}): XCodegenOperationMeta['parameters'] | undefined {
  if (!input.querySchemaRef) return undefined;
  if (input.operationParameterRefs.length === 0) return undefined;

  return {
    target: {
      $ref: input.querySchemaRef,
      ...(input.excludedParameterRefs?.length ? { exclude: input.excludedParameterRefs } : {}),
    },
  };
}

export function createPathParameterTargetMeta(input: {
  readonly sharedPathParameterRefs: readonly string[];
}): XCodegenPathMeta['parameters'] | undefined {
  if (input.sharedPathParameterRefs.length === 0) return undefined;

  if (input.sharedPathParameterRefs.length === 1) {
    return {
      target: {
        $ref: input.sharedPathParameterRefs[0],
      },
    };
  }

  // For multiple shared path params, use the first one with empty exclude
  // This can be enhanced later to support a targets array if needed
  return {
    target: {
      $ref: input.sharedPathParameterRefs[0],
      exclude: [],
    },
  };
}
