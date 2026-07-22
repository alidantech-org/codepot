/**
 * codepot Global Configuration
 *
 * Exports all configuration types and utilities for the codepot system.
 */

// Template types and utilities
export {
  paths,
  file,
  type codepotPathToken,
  type codepotOutputFolderPart,
  type codepotOutputFolder,
  type codepotOutputFileName,
  type codepotTemplateRegistration,
  type codepotTemplatesFile,
  type ResolvedcodepotTemplateRegistration,
  type ResolvedcodepotTemplatesFile,
} from './types/codepot.templates.types';

// Global config types
export { type codepotConfig, type ResolvedcodepotConfig } from './types/codepot.config.types';
