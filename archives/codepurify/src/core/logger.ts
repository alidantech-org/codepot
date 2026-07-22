/**
 * Codepurify Logger
 *
 * Provides a simple wrapper around consola for consistent logging
 * throughout the Codepurify application.
 */

import { consola } from 'consola';

/**
 * Codepurify logger instance
 */
export const logger = consola.withTag('codepurify');

/**
 * Log an info message
 *
 * @param message - Message to log
 * @param args - Additional arguments
 */
export function info(message: string, ...args: unknown[]): void {
  logger.info(message, ...args);
}

/**
 * Log a success message
 *
 * @param message - Message to log
 * @param args - Additional arguments
 */
export function success(message: string, ...args: unknown[]): void {
  logger.success(message, ...args);
}

/**
 * Log a warning message
 *
 * @param message - Message to log
 * @param args - Additional arguments
 */
export function warn(message: string, ...args: unknown[]): void {
  logger.warn(message, ...args);
}

/**
 * Log an error message
 *
 * @param message - Message to log
 * @param args - Additional arguments
 */
export function error(message: string, ...args: unknown[]): void {
  logger.error(message, ...args);
}

/**
 * Log a debug message
 *
 * @param message - Message to log
 * @param args - Additional arguments
 */
export function debug(message: string, ...args: unknown[]): void {
  logger.debug(message, ...args);
}

/**
 * Start a spinner or progress indicator
 *
 * @param message - Start message
 * @returns Consola spinner instance
 */
export function start(message: string) {
  return logger.start(message);
}

/**
 * Display a boxed message
 *
 * @param message - Message to display
 * @param title - Optional title
 */
export function box(message: string, title?: string): void {
  logger.box(message, title);
}
