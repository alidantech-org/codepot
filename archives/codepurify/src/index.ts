/**
 * Codepurify
 *
 * Semantic metadata inference engine + template compiler for generating architecture artifacts from typed domain configs.
 */

// Public API - Main API
export { Codepurify } from './api/codepurify';
export * as API from './api';

// Public API - Configuration
export { defineCodepurifyConfig } from '@/config/global/helpers/define-config';
export { defineCodepurifyTemplates } from '@/config/global/helpers/define-templates';

// Public API - Template utilities
export { paths, file } from '@/config/global/helpers/template-paths';

// Public API - Entity Configuration
export * from '@/config/entity';

// Public API - Configuration types
export type { CodepurifyConfig, ResolvedCodepurifyConfig } from '@/config/global/types/codepurify.config.types';

export type {
  CodepurifyPathToken,
  CodepurifyOutputFolderPart,
  CodepurifyOutputFolder,
  CodepurifyOutputFileName,
  CodepurifyTemplateRegistration,
  CodepurifyTemplatesFile,
} from '@/config/global/types/codepurify.templates.types';

// Public API - Core functionality
export * as Core from '@/core';

// Public API - Types
export * as Types from '@/types';

// Public API - Utilities
export * from '@/utils';
