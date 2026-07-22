// src/utils/logger/log-level.ts

export const LogLevel = {
  debug: 'debug',
  info: 'info',
  success: 'success',
  warn: 'warn',
  error: 'error',
  silent: 'silent',
} as const;

export type LogLevel = (typeof LogLevel)[keyof typeof LogLevel];

export const LogLevelWeight: Record<LogLevel, number> = {
  debug: 10,
  info: 20,
  success: 25,
  warn: 30,
  error: 40,
  silent: 100,
};
