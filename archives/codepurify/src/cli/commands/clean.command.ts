/**
 * codepot Clean Command
 *
 * Clears the .codepot/cache directory.
 */
import { Command } from 'commander';
import { intro, outro, confirm, spinner, isCancel } from '@clack/prompts';
import { consola } from 'consola';

import { codepot } from '@/api/codepot';
import { CLEAN_PATHS, CLEAN_LOG_MESSAGES } from '@/api/constants';

export function createCleanCommand(): Command {
  return new Command('clean')
    .description('Clear the .codepot/cache directory')
    .option('-f, --force', 'Force clean without confirmation')
    .action(async (options: { force?: boolean }) => {
      intro('🧹 codepot Clean');

      try {
        const codepot = new codepot({
          cwd: process.cwd(),
        });

        const cacheDir = CLEAN_PATHS.cacheDir;
        const cacheExists = await codepot.files.exists(cacheDir);

        if (!cacheExists) {
          consola.warn(CLEAN_LOG_MESSAGES.cacheNotFound);
          outro(CLEAN_LOG_MESSAGES.nothingToClean);
          return;
        }

        if (!options.force) {
          const shouldContinue = await confirm({
            message: `Clear ${cacheDir}?`,
          });

          if (isCancel(shouldContinue) || !shouldContinue) {
            outro(CLEAN_LOG_MESSAGES.cancelled);
            return;
          }
        }

        const s = spinner();
        s.start('Clearing cache');

        await codepot.files.deletePath(cacheDir);

        s.stop('Cache cleared');

        consola.success(CLEAN_LOG_MESSAGES.cacheCleared);
        consola.info(`Removed: ${cacheDir}`);

        outro('✨ Clean complete');
      } catch (error) {
        consola.error('Clean failed:', error);
        process.exit(1);
      }
    });
}
