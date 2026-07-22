// src/contract/builders/define-errors.ts

import type {
  ErrorInput,
  ErrorInputMap,
  ErrorsAuthoringState,
  ErrorsBuilder,
  ErrorsResult,
} from '@/contract/types/authoring/8.errors-builder';

import { content } from '@/contract/helpers/content/content';
import { error } from '@/contract/helpers/errors/error';
import { errorRef } from '@/contract/helpers/refs/authoring-ref-builder';

// ============================================================================
// OPTIONS
// ============================================================================

export interface DefineErrorsOptions {
  readonly state: Partial<ErrorsAuthoringState>;
}

// ============================================================================
// STATE HELPERS
// ============================================================================

function ensureState(state: Partial<ErrorsAuthoringState>): Partial<ErrorsAuthoringState> {
  return state;
}

function createErrorRefs<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput>['ref'] {
  const refs = {} as Record<keyof TInput & string, ReturnType<typeof errorRef>>;

  for (const key of Object.keys(input) as Array<keyof TInput & string>) {
    refs[key] = errorRef(key);
  }

  return refs as ErrorsResult<TInput>['ref'];
}

function writeErrors<TInput extends ErrorInputMap>(state: Partial<ErrorsAuthoringState>, input: TInput): void {
  for (const [key, value] of Object.entries(input) as [keyof TInput & string, TInput[keyof TInput & string]][]) {
    state[key] = value as ErrorInput;
  }
}

// ============================================================================
// DEFINE ERRORS
// ============================================================================

export function defineErrors(options: DefineErrorsOptions): ErrorsBuilder {
  const builder: ErrorsBuilder = {
    get state() {
      return options.state;
    },

    content,

    error,

    define<TInput extends ErrorInputMap>(input: TInput): ErrorsResult<TInput> {
      const state = ensureState(options.state);

      writeErrors(state, input);

      return {
        errors: input,
        ref: createErrorRefs(input),
      };
    },

    snapshot() {
      return options.state;
    },
  };

  return builder;
}
