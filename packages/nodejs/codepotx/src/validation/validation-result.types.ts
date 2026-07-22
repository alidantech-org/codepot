export interface ValidationIssue {
  readonly path: string;
  readonly message: string;
}

export interface ValidationResult {
  readonly valid: boolean;
  readonly issues: ValidationIssue[];
}

export function validResult(): ValidationResult {
  return {
    valid: true,
    issues: [],
  };
}

export function invalidResult(issues: ValidationIssue[]): ValidationResult {
  return {
    valid: issues.length === 0,
    issues,
  };
}
