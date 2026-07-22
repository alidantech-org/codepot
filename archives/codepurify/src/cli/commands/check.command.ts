/**
 * Codepurify Check Command
 *
 * Checks generated files against the Codepurify file DB for drift detection.
 * Reports clean, changed, and missing files.
 */

import { Command } from 'commander';
import { intro, outro, spinner } from '@clack/prompts';
import { consola } from 'consola';
import Table from 'cli-table3';

import { Codepurify } from '@/api/codepurify';

export function createCheckCommand(): Command {
  return new Command('check')
    .description('Check generated files against the Codepurify file DB for drift')
    .option('--json', 'Output result as JSON')
    .action(async (options: { json?: boolean }) => {
      intro('🔍 Codepurify Check');

      const s = spinner();
      s.start('Checking generated files...');

      try {
        const codepurify = new Codepurify({
          cwd: process.cwd(),
        });

        const results = await codepurify.files.validate();

        const clean = results.filter((result) => result.exists && result.hashMatches);

        const changed = results.filter((result) => result.exists && result.hashMatches === false);

        const missing = results.filter((result) => !result.exists);

        s.stop('Check completed');

        if (options.json) {
          consola.log(
            JSON.stringify(
              {
                success: changed.length === 0 && missing.length === 0,
                total: results.length,
                clean: clean.length,
                changed: changed.length,
                missing: missing.length,
                results,
              },
              null,
              2,
            ),
          );

          return;
        }

        const table = new Table({
          head: ['Status', 'File', 'Template'],
          colWidths: [12, 50, 24],
          wordWrap: true,
        });

        for (const result of clean) {
          table.push(['clean', result.record.path, result.record.template ?? '-']);
        }

        for (const result of changed) {
          table.push(['changed', result.record.path, result.record.template ?? '-']);
        }

        for (const result of missing) {
          table.push(['missing', result.record.path, result.record.template ?? '-']);
        }

        consola.log(table.toString());

        consola.info(`Total: ${results.length}`);
        consola.success(`Clean: ${clean.length}`);

        if (changed.length > 0) {
          consola.warn(`Changed: ${changed.length}`);
        }

        if (missing.length > 0) {
          consola.error(`Missing: ${missing.length}`);
        }

        const isValid = changed.length === 0 && missing.length === 0;

        if (isValid) {
          outro('✅ Generated files are in sync');
          return;
        }

        outro('⚠️ Generated files have drift');
        process.exit(1);
      } catch (error) {
        s.stop('Check failed');
        consola.error('Check failed:', error);
        process.exit(1);
      }
    });
}
