import type { OpenApiDocument } from "../openapi/openapi.types.js";
import type { ValidationIssue } from "../validation/validation-result.types.js";

export interface CompileSuccessResult {
  readonly success: true;
  readonly document: OpenApiDocument;
  readonly issues: [];
}

export interface CompileFailureResult {
  readonly success: false;
  readonly document?: OpenApiDocument;
  readonly issues: ValidationIssue[];
}

export type CompileResult = CompileSuccessResult | CompileFailureResult;
