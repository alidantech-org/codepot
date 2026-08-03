/**
 * codepot Init Command
 *
 * Initializes a codepot project using the codepot API.
 */

import { Command } from 'commander';
import { intro, outro, confirm, spinner } from '@clack/prompts';
import { consola } from 'consola';
import { codepot } from '@/api/codepot';
import { INIT_OUTPUTS } from '@/api/constants';

/**
 * Creates the init command
 */
export function createInitCommand(): Command {
  const command = new Command('init')
    .description('Initialize codepot in your project')
    .option('-f, --force', 'Force initialization even if codepot is already initialized')
    .option('--dry-run', 'Show what would be created without writing files')
    .option('--debug', 'Show debug information for troubleshooting')
    .action(async (options) => {
      try {
        intro('🚀 codepot Init');

        const codepot = new codepot();

        // Check if already initialized using codepot API
        if (!options.force) {
          try {
            const codepot = new codepot();
            const configExists = await codepot.files.exists(INIT_OUTPUTS.codeDir);

            if (configExists) {
              const shouldContinue = await confirm({
                message: 'codepot is already initialized. Re-initialize?',
              });

              if (!shouldContinue) {
                outro('Initialization cancelled');
                return;
              }
            }
          } catch {
            // Continue with initialization if check fails
          }
        }

        // Initialize using codepot API
        const s = spinner();
        s.start('Initializing codepot project...');

        const result = await codepot.init({
          force: options.force,
          dryRun: options.dryRun,
          debug: options.debug,
        });

        // Check if initialization failed
        if (!result.success) {
          s.stop('Initialization failed');

          if (result.errors.length > 0) {
            consola.error('Initialization failed with errors:');
            result.errors.forEach((error, index) => {
              consola.error(`  Error ${index + 1}:`);
              consola.error(`    Message: ${error.message}`);
              consola.error(`    Full error object:`, JSON.stringify(error, null, 2));
              if (error.cause) {
                // Handle different types of error causes
                if (error.cause instanceof Error) {
                  consola.error(`    Cause: ${error.cause.message}`);
                  if (error.cause.stack) {
                    consola.error(`    Stack: ${error.cause.stack}`);
                  }
                } else {
                  consola.error(`    Cause: ${error.cause}`);
                }
              } else {
                consola.error(`    No cause found`);
              }
            });
          } else {
            consola.error('Initialization failed for unknown reasons');
          }

          process.exit(1);
        }

        s.stop('Project initialized successfully');

        if (options.dryRun) {
          consola.info('Dry run completed. Files that would be created:');
          result.createdFiles.forEach((file) => {
            consola.info(`  ✓ ${file.path}`);
          });
        } else {
          consola.success(`codepot initialized successfully!`);
          consola.info(`Created ${result.createdFiles.length} files`);

          result.createdFiles.forEach((file) => {
            consola.info(`  ✓ ${file.path}`);
          });

          if (result.skippedFiles.length > 0) {
            consola.warn(`Skipped ${result.skippedFiles.length} files:`);
            result.skippedFiles.forEach((file) => {
              consola.info(`  ⏭ ${file}`);
            });
          }
        }

        // Show warnings if any
        if (result.warnings.length > 0) {
          consola.warn(`Warnings:`);
          result.warnings.forEach((warning) => {
            consola.warn(`  ${warning}`);
          });
        }

        outro('✨ Ready to generate entities with: codepot generate');
      } catch (error) {
        consola.error('Initialization failed:', error);
        process.exit(1);
      }
    });

  return command;
}
