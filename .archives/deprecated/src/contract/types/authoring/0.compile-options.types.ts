export const CompileMode = {
  strict: 'strict',
  loose: 'loose',
} as const;

export type CompileMode = (typeof CompileMode)[keyof typeof CompileMode];

export interface CompileDebugOptions {
  readonly enabled?: boolean;
  readonly includeSourceMaps?: boolean;
  readonly includeInference?: boolean;
  readonly includeResolvedRefs?: boolean;
}

export interface CompileValidationOptions {
  readonly enabled?: boolean;
  readonly mode?: CompileMode;
  readonly failOnWarnings?: boolean;
}

export interface CompileOutputOptions {
  readonly includeMeta?: boolean;
  readonly includeDeprecated?: boolean;
}

export interface CompileOptions {
  /**
   * Validation behavior during compilation.
   */
  readonly validation?: CompileValidationOptions;

  /**
   * Debug artifacts produced during compilation.
   */
  readonly debug?: CompileDebugOptions;

  /**
   * Final compiled output behavior.
   */
  readonly output?: CompileOutputOptions;

  /**
   * Reserved for future compiler plugins/extensions.
   */
  readonly extensions?: Record<string, unknown>;
}
