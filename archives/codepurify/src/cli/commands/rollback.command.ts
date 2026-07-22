/**
 * Codepurify Rollback Command
 *
 * Restores files from backup sessions using the Codepurify API.
 */

import { Command } from 'commander';
import { intro, outro, confirm, spinner } from '@clack/prompts';
import { consola } from 'consola';
import { Codepurify } from '@/api/codepurify';

/**
 * Creates the rollback command
 */
export function createRollbackCommand(): Command {
  const command = new Command('rollback')
    .description('Rollback to a backup session')
    .option('-f, --force', 'Force rollback without confirmation')
    .option('-i, --id <sessionId>', 'Rollback to specific session ID')
    .option('-t, --timestamp <timestamp>', 'Rollback to session before timestamp')
    .action(async (options) => {
      try {
        intro('🔄 Codepurify Rollback');

        const codepurify = new Codepurify();

        // Confirm rollback
        if (!options.force) {
          const shouldContinue = await confirm({
            message: 'This will restore files from a backup session. Continue?',
          });

          if (!shouldContinue) {
            outro('Rollback cancelled');
            return;
          }
        }

        // Perform rollback using Codepurify API
        const s = spinner();
        s.start('Rolling back files...');

        const result = await codepurify.rollback({
          backupId: options.id,
          timestamp: options.timestamp,
        });

        s.stop('Rollback completed');

        consola.success('Rollback completed successfully!');
        consola.info(`Session ID: ${result.backupId}`);
        consola.info(`Timestamp: ${result.backupTimestamp.toISOString()}`);

        if (result.restoredFiles.length > 0) {
          consola.info(`Restored ${result.restoredFiles.length} files:`);
          result.restoredFiles.forEach((file) => {
            consola.info(`  ✓ ${file}`);
          });
        }

        if (result.errors.length > 0) {
          consola.warn(`${result.errors.length} errors occurred:`);
          result.errors.forEach((error) => {
            consola.error(`  ✗ ${error}`);
          });
        }

        if (result.warnings.length > 0) {
          consola.warn(`${result.warnings.length} warnings:`);
          result.warnings.forEach((warning) => {
            consola.warn(`  ⚠ ${warning}`);
          });
        }

        outro('✨ Rollback complete');
      } catch (error) {
        consola.error('Rollback failed:', error);
        process.exit(1);
      }
    });

  return command;
}
