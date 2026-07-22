import ora, { type Ora } from 'ora';
import chalk from 'chalk';

import type { LogTask, Logger, LoggerOptions, LogContext } from './logger.types.js';
import { LogLevel } from './log-level.js';

class ConsoleLogTask implements LogTask {
  private message: string;
  private readonly isInteractive: boolean;
  private spinner?: Ora;

  constructor(message: string, isInteractive: boolean) {
    this.message = message;
    this.isInteractive = isInteractive;

    if (isInteractive) {
      this.spinner = ora({
        text: message,
        color: 'cyan',
      }).start();
    } else {
      this.logStart(message);
    }
  }

  update(message: string): void {
    this.message = message;
    if (this.spinner) {
      this.spinner.text = message;
    }
  }

  succeed(message?: string): void {
    const finalMessage = message ?? this.message;
    if (this.spinner) {
      this.spinner.succeed(finalMessage);
      this.spinner = undefined;
    } else {
      this.logSuccess(finalMessage);
    }
  }

  fail(message?: string): void {
    const finalMessage = message ?? this.message;
    if (this.spinner) {
      this.spinner.fail(finalMessage);
      this.spinner = undefined;
    } else {
      this.logError(finalMessage);
    }
  }

  private logStart(message: string): void {
    console.log(chalk.cyan('◼'), message);
  }

  private logSuccess(message: string): void {
    console.log(chalk.green('✓'), message);
  }

  private logError(message: string): void {
    console.log(chalk.red('✗'), message);
  }
}

class ConsoleLogger implements Logger {
  private readonly level: LogLevel;
  private readonly isInteractive: boolean;
  private readonly context?: LogContext;

  constructor(options: LoggerOptions = {}, context?: LogContext) {
    this.level = options.level ?? 'normal';
    this.isInteractive = this.level !== 'silent' && this.level !== 'debug' && process.stdout.isTTY === true;
    this.context = context;
  }

  child(context: LogContext): Logger {
    return new ConsoleLogger({ level: this.level }, { ...this.context, ...context });
  }

  task(message: string): LogTask {
    return new ConsoleLogTask(message, this.isInteractive);
  }

  info(message: string): void {
    if (this.level === 'silent') return;
    console.log(chalk.cyan('•'), message);
  }

  warn(message: string): void {
    if (this.level === 'silent') return;
    console.log(chalk.yellow('⚠'), message);
  }

  error(message: string, error?: unknown): void {
    console.log(chalk.red('✗'), message);
    if (error && this.level === 'debug') {
      console.error(error);
    }
  }

  verbose(message: string): void {
    if (this.level !== 'verbose' && this.level !== 'debug') return;
    console.log(chalk.dim('  '), message);
  }

  debug(message: string): void {
    if (this.level !== 'debug') return;
    console.log(chalk.dim('◆'), message);
  }
}

export function createLogger(options?: LoggerOptions): Logger {
  return new ConsoleLogger(options);
}
