import type { LogLevel } from './log-level.js';

export interface LogContext {
  readonly scope?: string;
  readonly version?: string;
  readonly operation?: string;
}

export interface Logger {
  child(context: LogContext): Logger;
  task(message: string): LogTask;
  info(message: string): void;
  warn(message: string): void;
  error(message: string, error?: unknown): void;
  verbose(message: string): void;
  debug(message: string): void;
}

export interface LogTask {
  update(message: string): void;
  succeed(message?: string): void;
  fail(message?: string): void;
}

export interface LoggerOptions {
  readonly level?: LogLevel;
}
