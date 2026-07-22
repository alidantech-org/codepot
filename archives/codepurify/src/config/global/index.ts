/**
 * Codepurify Global Configuration
 *
 * Exports all configuration types and utilities for the Codepurify system.
 */

// Template types and utilities
export {
  paths,
  file,
  type CodepurifyPathToken,
  type CodepurifyOutputFolderPart,
  type CodepurifyOutputFolder,
  type CodepurifyOutputFileName,
  type CodepurifyTemplateRegistration,
  type CodepurifyTemplatesFile,
  type ResolvedCodepurifyTemplateRegistration,
  type ResolvedCodepurifyTemplatesFile,
} from './types/codepurify.templates.types';

// Global config types
export { type CodepurifyConfig, type ResolvedCodepurifyConfig } from './types/codepurify.config.types';
