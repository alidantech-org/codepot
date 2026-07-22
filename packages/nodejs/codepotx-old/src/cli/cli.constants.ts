export const CliCommand = {
  init: 'init',
  generate: 'generate',
  validate: 'validate',
  help: 'help',
} as const;

export type CliCommand = (typeof CliCommand)[keyof typeof CliCommand];

export const DefaultConfigFileName = 'package.config.ts';

export const CliMessage = {
  initialized: (path: string) => `✓ Created config file: ${path}`,
  skipped: (path: string) => `✓ Config already exists: ${path}`,
  generated: (path: string) => `✓ Generated ${path}`,
  done: '✓ Done',
  failed: '✗ Failed',
} as const;
