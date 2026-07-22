export const LogLevel = {
  silent: 'silent',
  normal: 'normal',
  verbose: 'verbose',
  debug: 'debug',
} as const;

export type LogLevel = (typeof LogLevel)[keyof typeof LogLevel];
