import { createLogger } from './create-logger';
import { LogLevel } from './log-level';
import type { Logger, LoggerConfig } from './logger.types';

export interface LogContext {
  readonly scope?: string;
  readonly version?: string;
  readonly resource?: string;
  readonly operation?: string;
  readonly component?: string;
  readonly file?: string;
}

export interface SpinnerHandle {
  readonly text: (message: string) => void;
  readonly succeed: (message?: string) => void;
  readonly fail: (message?: string) => void;
  readonly warn: (message?: string) => void;
  readonly stop: () => void;
}

function resolveLogLevel(config?: LoggerConfig): LogLevel {
  if (config?.silent === true) return LogLevel.silent;
  if (config?.debug === true) return LogLevel.debug;
  if (config?.verbose === true) return LogLevel.debug;

  return config?.level ?? LogLevel.info;
}

function formatContext(context?: LogContext): string {
  if (context === undefined) return '';

  const parts = [
    context.scope,
    context.version ? `v:${context.version}` : undefined,
    context.resource ? `r:${context.resource}` : undefined,
    context.operation ? `op:${context.operation}` : undefined,
    context.component ? `c:${context.component}` : undefined,
    context.file ? `file:${context.file}` : undefined,
  ].filter(Boolean);

  return parts.length > 0 ? ` [${parts.join(' ')}]` : '';
}

/**
 * Compatibility logger for older compiler/app call sites.
 *
 * New code should prefer `createLogger()` and the `Logger` interface directly.
 */
export class CompilerLogger {
  private readonly logger: Logger;
  private readonly level: LogLevel;
  private readonly context?: LogContext;

  constructor(config?: LoggerConfig, context?: LogContext) {
    this.level = resolveLogLevel(config);
    this.context = context;
    this.logger = createLogger({
      level: this.level,
    });
  }

  child(context: LogContext): CompilerLogger {
    return new CompilerLogger(
      { level: this.level },
      {
        ...this.context,
        ...context,
      },
    );
  }

  spinner(message: string, context?: LogContext): SpinnerHandle {
    const fullContext = { ...this.context, ...context };
    let current = message;

    this.info(message, fullContext);

    return {
      text: (next) => {
        current = next;
        this.info(next, fullContext);
      },
      succeed: (next) => this.success(next ?? current, fullContext),
      fail: (next) => this.error(next ?? current, fullContext),
      warn: (next) => this.warn(next ?? current, fullContext),
      stop: () => undefined,
    };
  }

  async phase<T>(
    message: string,
    run: (spinner: SpinnerHandle) => Promise<T> | T,
    options?: {
      readonly success?: string | ((result: T) => string);
      readonly fail?: string;
      readonly context?: LogContext;
    },
  ): Promise<T> {
    const spinner = this.spinner(message, options?.context);

    try {
      const result = await run(spinner);
      const successMessage = typeof options?.success === 'function' ? options.success(result) : options?.success;

      spinner.succeed(successMessage ?? message);
      return result;
    } catch (error) {
      spinner.fail(options?.fail ?? message);
      throw error;
    }
  }

  isSilent(): boolean {
    return this.level === LogLevel.silent;
  }

  isVerbose(): boolean {
    return this.level === LogLevel.debug;
  }

  isDebug(): boolean {
    return this.level === LogLevel.debug;
  }

  info(message: string, context?: LogContext): void {
    this.logger.info(`${message}${formatContext({ ...this.context, ...context })}`);
  }

  step(message: string, context?: LogContext): void {
    this.info(message, context);
  }

  success(message: string, context?: LogContext): void {
    this.logger.success(`${message}${formatContext({ ...this.context, ...context })}`);
  }

  warn(message: string, context?: LogContext): void {
    this.logger.warn(`${message}${formatContext({ ...this.context, ...context })}`);
  }

  error(message: string, context?: LogContext): void {
    this.logger.error(`${message}${formatContext({ ...this.context, ...context })}`);
  }

  section(message: string, context?: LogContext): void {
    this.info(message, context);
  }

  item(message: string, context?: LogContext): void {
    this.info(message, context);
  }

  detail(message: string, data?: unknown, context?: LogContext): void {
    this.logger.debug(`${message}${formatContext({ ...this.context, ...context })}`, data);
  }

  trace(message: string, data?: unknown, context?: LogContext): void {
    this.logger.debug(`${message}${formatContext({ ...this.context, ...context })}`, data);
  }

  verbose(message: string, data?: unknown, context?: LogContext): void {
    this.logger.debug(`${message}${formatContext({ ...this.context, ...context })}`, data);
  }

  debug(message: string, data?: unknown, context?: LogContext): void {
    this.logger.debug(`${message}${formatContext({ ...this.context, ...context })}`, data);
  }

  time(label: string, context?: LogContext): () => void {
    const startedAt = performance.now();
    this.debug(`Started ${label}`, undefined, context);

    return () => {
      const duration = Math.round(performance.now() - startedAt);
      this.debug(`Finished ${label} in ${duration}ms`, undefined, context);
    };
  }
}
