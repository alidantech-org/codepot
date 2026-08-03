/**
 * Generate Action Constants
 *
 * Data-only constants for generate action operations.
 */

export const GENERATE_ACTION = {
  name: 'generate',
} as const;

export const GENERATE_DEFAULTS = {
  generatedFiles: [],
  entitiesProcessed: 0,
  templatesExecuted: 0,
};

export const GENERATE_LOG_MESSAGES = {
  starting: 'Starting generation...',
  completed: 'Generation completed successfully',
  backupCreated: (sessionId: string) => `Created backup session: ${sessionId}`,
} as const;
