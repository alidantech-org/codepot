/**
 * Generate Action
 *
 * Handles semantic artifact generation from entity configurations.
 *
 * This action now serves as a thin orchestration layer that delegates
 * to the GeneratePipeline service for the actual generation work.
 */

import { FileAction, type GenerateOptions, type GenerateResult, type GeneratedFileResult } from '@/api/types';

import type { CodepurifyAction } from '@/api/runtime/action-contract';

import { debug, info, success } from '@/core/logger';

import { GENERATE_ACTION, GENERATE_DEFAULTS, GENERATE_LOG_MESSAGES } from '@/api/constants';

import { GeneratePipeline } from '@/api/runtime/generate-pipeline';

export const generateAction: CodepurifyAction<GenerateOptions, GenerateResult> = {
  name: GENERATE_ACTION.name,

  defaults: (options) => ({
    generatedFiles: GENERATE_DEFAULTS.generatedFiles,
    entitiesProcessed: GENERATE_DEFAULTS.entitiesProcessed,
    templatesExecuted: GENERATE_DEFAULTS.templatesExecuted,
    dryRun: options.dryRun ?? false,
  }),

  async run(runtime, options) {
    info(GENERATE_LOG_MESSAGES.starting);

    // Create backup session for tracking changes
    const backupSession = options.dryRun ? undefined : await runtime.files.createBackupSession(GENERATE_ACTION.name);

    if (backupSession) {
      debug(GENERATE_LOG_MESSAGES.backupCreated(backupSession.id));
    }

    // Initialize and execute the generation pipeline
    const pipeline = new GeneratePipeline(runtime);

    const pipelineResult = await pipeline.execute({
      writing: {
        backupSession,
        dryRun: options.dryRun,
      },
    });

    // Convert pipeline results to action results
    const generatedFiles: GeneratedFileResult[] = pipelineResult.generatedFiles.map((file) => ({
      path: file.path,
      action: FileAction.CREATED,
      templateName: file.template,
      size: Buffer.byteLength(file.content, 'utf-8'),
      changed: true,
    }));

    // Log warnings if any
    if (pipelineResult.warnings.length > 0) {
      for (const warning of pipelineResult.warnings) {
        debug(`Pipeline warning: ${warning}`);
      }
    }

    success(GENERATE_LOG_MESSAGES.completed);

    return {
      generatedFiles,
      entitiesProcessed: pipelineResult.metrics.entitiesProcessed,
      templatesExecuted: pipelineResult.metrics.templatesRendered,
      dryRun: options.dryRun ?? false,
    };
  },
};
