export class PlatformOperationError extends Error {
  readonly code: string;

  constructor(code: string, message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = 'PlatformOperationError';
    this.code = code;
  }
}

export class OperationCancelledError extends PlatformOperationError {
  constructor(reason = 'Operation cancelled.') {
    super('CODEPOT_CANCELLED', reason);
    this.name = 'OperationCancelledError';
  }
}
