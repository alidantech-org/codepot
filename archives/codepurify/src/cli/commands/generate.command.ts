/**
 * Codepurify Generate Command
 *
 * Generates entity files from discovered entity folders using the Codepurify API.
 */

import { Command } from 'commander';
import { intro, outro, spinner } from '@clack/prompts';
import { consola } from 'consola';
import { Codepurify } from '@/api/codepurify';

/**
 * Creates the generate command
 */
export function createGenerateCommand(): Command {
  const command = new Command('generate')
    .description('Generate entity files from discovered entity folders')
    .option('--dry-run', 'Show what would be generated without writing files')
    .option('-e, --entities <entities>', 'Specify entities to generate (comma-separated)')
    .option('-t, --templates <templates>', 'Specify templates to use (comma-separated)')
    .action(async (options) => {
      try {
        intro('🚀 Codepurify Generate');

        const codepurify = new Codepurify();

        // Generate using Codepurify API
        const s = spinner();
        s.start('Generating entity files...');

        const result = await codepurify.generate({
          dryRun: options.dryRun,
          entity: options.entities ? options.entities.split(',')[0].trim() : undefined,
          templates: options.templates ? options.templates.split(',').map((t: string) => t.trim()) : undefined,
        });

        s.stop('Generation completed');

        if (options.dryRun) {
          consola.info('Dry run completed. Files that would be generated:');
          result.generatedFiles.forEach((file) => {
            consola.info(`  ✓ ${file.path}`);
          });
        } else {
          consola.success(`Generated ${result.generatedFiles.length} files`);
          consola.info(`Processed ${result.entitiesProcessed} entities`);
          consola.info(`Executed ${result.templatesExecuted} templates`);

          result.generatedFiles.forEach((file) => {
            consola.info(`  ✓ ${file.path}`);
          });
        }

        outro('✨ Generation completed successfully');
      } catch (error) {
        consola.error('Generation failed:', error);
        process.exit(1);
      }
    });

  return command;
}
