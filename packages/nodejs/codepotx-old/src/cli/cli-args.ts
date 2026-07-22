import type { LoggerConfig } from '../logger/logger.types.js';

export interface ParsedCliArgs {
  readonly command: string;
  readonly flags: ReadonlySet<string>;
  readonly values: ReadonlyMap<string, string>;
}

export function parseCliArgs(argv: readonly string[]): ParsedCliArgs {
  const [command = 'generate', ...rest] = argv;
  const flags = new Set<string>();
  const values = new Map<string, string>();

  for (let index = 0; index < rest.length; index += 1) {
    const item = rest[index];

    if (!item.startsWith('--')) continue;

    const withoutPrefix = item.slice(2);
    const [key, inlineValue] = withoutPrefix.split('=', 2);

    if (inlineValue !== undefined) {
      values.set(key, inlineValue);
      continue;
    }

    const next = rest[index + 1];

    if (next && !next.startsWith('--')) {
      values.set(key, next);
      index += 1;
    } else {
      flags.add(key);
    }
  }

  return { command, flags, values };
}

export function loggerConfigFromCliArgs(args: ParsedCliArgs): LoggerConfig {
  if (args.flags.has('silent')) return { level: 'silent', silent: true };
  if (args.flags.has('debug')) return { level: 'debug', debug: true };
  if (args.flags.has('verbose')) return { level: 'verbose', verbose: true };

  const level = args.values.get('log-level');

  if (level === 'silent' || level === 'normal' || level === 'verbose' || level === 'debug') {
    return { level };
  }

  return {};
}
