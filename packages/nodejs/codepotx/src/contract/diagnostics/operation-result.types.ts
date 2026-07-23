import type { Diagnostic } from './diagnostic.types';

export interface OperationSuccess<T> {
  readonly success: true;
  readonly value: T;
  readonly diagnostics: readonly Diagnostic[];
}

export interface OperationFailure {
  readonly success: false;
  readonly diagnostics: readonly Diagnostic[];
}

/** Explicit success/failure result suitable for runtime and frontend boundaries. */
export type OperationResult<T> = OperationSuccess<T> | OperationFailure;
