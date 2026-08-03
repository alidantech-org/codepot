// cli/presentation/cli-logger.ts

import pc from 'picocolors';

import { createLogger, LogLevel, type Logger } from '@/utils/logger';

// ============================================================================
// TYPES
// ============================================================================

export interface CreateCliLoggerOptions {
  readonly verbose?: boolean;
  readonly silent?: boolean;
}

// ============================================================================
// FACTORY
// ============================================================================

/**
 * Creates a styled CLI logger.
 */
export function createCliLogger(options: CreateCliLoggerOptions = {}): Logger {
  const level = options.silent ? LogLevel.silent : options.verbose ? LogLevel.debug : LogLevel.info;

  return createLogger({
    level,
    sink(event) {
      const prefix =
        event.level === LogLevel.success
          ? pc.green('+')
          : event.level === LogLevel.warn
            ? pc.yellow('!')
            : event.level === LogLevel.error
              ? pc.red('x')
              : event.level === LogLevel.debug
                ? pc.gray('-')
                : pc.cyan('*');

      const scope = event.scope ? pc.gray(`[${event.scope}] `) : '';
      const line = `${prefix} ${scope}${event.message}`;

      if (event.level === LogLevel.error) {
        console.error(line);
        return;
      }

      console.log(line);
    },
  });
}
