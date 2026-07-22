// src/utils/logger/create-logger.ts

import { LogLevel, LogLevelWeight } from './log-level';
import type { CreateLoggerOptions, LogEvent, Logger } from './logger.types';

// ============================================================================
// INTERNAL
// ============================================================================

/**
 * Checks whether a log event should be emitted for the configured level.
 */
function shouldLog(current: LogLevel, event: LogLevel): boolean {
  return LogLevelWeight[event] >= LogLevelWeight[current];
}

/**
 * Default logger sink.
 */
function defaultSink(event: LogEvent): void {
  if (event.level === LogLevel.error) {
    console.error(event.message);
    return;
  }

  console.log(event.message);
}

// ============================================================================
// FACTORY
// ============================================================================

/**
 * Creates a small framework-agnostic logger.
 *
 * CLI can provide a styled sink. Compiler/app code can use the same interface
 * without depending on terminal UI libraries.
 */
export function createLogger(options: CreateLoggerOptions = {}): Logger {
  const level = options.level ?? LogLevel.info;
  const sink = options.sink ?? defaultSink;

  function emit(eventLevel: LogLevel, message: string, data?: unknown): void {
    if (!shouldLog(level, eventLevel)) return;

    sink({
      level: eventLevel,
      message,
      scope: options.scope,
      data,
    });
  }

  return {
    debug(message, data) {
      emit(LogLevel.debug, message, data);
    },

    info(message, data) {
      emit(LogLevel.info, message, data);
    },

    success(message, data) {
      emit(LogLevel.success, message, data);
    },

    warn(message, data) {
      emit(LogLevel.warn, message, data);
    },

    error(message, data) {
      emit(LogLevel.error, message, data);
    },
  };
}
