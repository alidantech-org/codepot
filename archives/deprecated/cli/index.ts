#!/usr/bin/env node

import { Command } from 'commander';

import packageJson from '../package.json';
import { runGenerateCommand } from './commands/generate';
import { runInitCommand } from './commands/init';
import { createCliLogger } from './presentation/cli-logger';
import { formatError } from './presentation/format-error';

// ============================================================================
// PROGRAM
// ============================================================================

const program = new Command();

program
  .name('codepot')
  .description('Codepot contract compiler')
  .version(packageJson.version)
  .option('--verbose', 'show verbose logs')
  .option('--silent', 'hide logs');

// ============================================================================
// INIT
// ============================================================================

program
  .command('init')
  .description('create a codepot.config.ts file')
  .option('--force', 'overwrite existing config')
  .action(async (options) => {
    const globalOptions = program.opts();
    const logger = createCliLogger(globalOptions);

    try {
      await runInitCommand({
        force: options.force,
        logger,
      });
    } catch (error) {
      logger.error(formatError(error));
      process.exitCode = 1;
    }
  });

// ============================================================================
// GENERATE
// ============================================================================

program
  .command('generate')
  .alias('gen')
  .description('compile Codepot contracts and write IR files')
  .option('-c, --config <path>', 'path to codepot config')
  .action(async (options) => {
    const globalOptions = program.opts();
    const logger = createCliLogger(globalOptions);

    try {
      await runGenerateCommand({
        config: options.config,
        logger,
      });
    } catch (error) {
      logger.error(formatError(error));
      process.exitCode = 1;
    }
  });

void program.parseAsync(process.argv);
