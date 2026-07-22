import { parseArgs } from 'node:util';

import type { CliCommand, CliOptions } from './cli.types';

const COMMANDS = new Set<CliCommand>(['generate', 'plan', 'validate', 'inspect', 'features', 'help', 'version']);

export function parseCliArguments(argv: readonly string[], cwd = process.cwd()): CliOptions {
  const commandValue = argv[0] ?? 'help';
  const command = COMMANDS.has(commandValue as CliCommand) ? commandValue as CliCommand : 'help';
  const parsed = parseArgs({
    args: argv.slice(1),
    allowPositionals: true,
    strict: true,
    options: {
      root: { type: 'string', short: 'r' },
      file: { type: 'string', short: 'f' },
      config: { type: 'string', short: 'c' },
      task: { type: 'string', short: 't' },
      all: { type: 'boolean' },
      'dry-run': { type: 'boolean' },
      refresh: { type: 'boolean' },
      'skip-before': { type: 'boolean' },
      'skip-after': { type: 'boolean' },
      json: { type: 'boolean' },
      pretty: { type: 'boolean' },
      verbose: { type: 'boolean', short: 'v' },
    },
  });
  const task = parsed.values.task ?? parsed.positionals[0];
  return {
    command,
    projectRoot: parsed.values.root ?? cwd,
    ...(parsed.values.file ? { file: parsed.values.file } : {}),
    ...(parsed.values.config ? { config: parsed.values.config } : {}),
    ...(task ? { task } : {}),
    allTasks: parsed.values.all ?? false,
    dryRun: parsed.values['dry-run'] ?? false,
    refresh: parsed.values.refresh ?? false,
    skipBefore: parsed.values['skip-before'] ?? false,
    skipAfter: parsed.values['skip-after'] ?? false,
    json: parsed.values.json ?? false,
    pretty: parsed.values.pretty ?? true,
    verbose: parsed.values.verbose ?? false,
  };
}
