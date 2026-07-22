#!/usr/bin/env node

/**
 * Codepurify CLI
 *
 * Main entry point for the Codepurify command-line interface.
 * Provides commands for initializing, generating, checking, and rolling back entity files.
 */

import { Command } from 'commander';
import { createInitCommand } from './commands/init.command.js';
import { createGenerateCommand } from './commands/generate.command.js';
import { createCheckCommand } from './commands/check.command.js';
import { createRollbackCommand } from './commands/rollback.command.js';
import { createCleanCommand } from './commands/clean.command.js';

/**
 * Creates and configures the Codepurify CLI program
 */
function createProgram(): Command {
  const program = new Command();

  program.name('codepurify').description('Codepurify - NestJS entity generation tool').version('0.1.0');

  // Register commands
  program.addCommand(createInitCommand());
  program.addCommand(createGenerateCommand());
  program.addCommand(createCheckCommand());
  program.addCommand(createRollbackCommand());
  program.addCommand(createCleanCommand());

  return program;
}

/**
 * Main entry point
 */
async function main() {
  const program = createProgram();
  await program.parseAsync(process.argv);
}

// Run the CLI
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
