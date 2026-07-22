// src/utils/logger/logger.types.ts

import type { LogLevel } from './log-level';

// ============================================================================
// LOGGER EVENT
// ============================================================================

export interface LogEvent {
  readonly level: LogLevel;
  readonly message: string;
  readonly scope?: string;
  readonly data?: unknown;
}

// ============================================================================
// LOGGER
// ============================================================================

export interface Logger {
  debug(message: string, data?: unknown): void;
  info(message: string, data?: unknown): void;
  success(message: string, data?: unknown): void;
  warn(message: string, data?: unknown): void;
  error(message: string, data?: unknown): void;
}

// ============================================================================
// LOGGER OPTIONS
// ============================================================================

export interface CreateLoggerOptions {
  readonly scope?: string;
  readonly level?: LogLevel;
  readonly sink?: (event: LogEvent) => void;
}

// ============================================================================
// COMPATIBILITY OPTIONS
// ============================================================================

export interface LoggerConfig {
  readonly level?: LogLevel;
  readonly debug?: boolean;
  readonly verbose?: boolean;
  readonly silent?: boolean;
  readonly interactive?: boolean;
}
