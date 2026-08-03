/**
 * codepot
 *
 * Semantic metadata inference engine + template compiler for generating architecture artifacts from typed domain configs.
 */

// Public API - Main API
export { codepot } from './api/codepot';
export * as API from './api';

// Public API - Configuration
export { definecodepotConfig } from '@/config/global/helpers/define-config';
export { definecodepotTemplates } from '@/config/global/helpers/define-templates';

// Public API - Template utilities
export { paths, file } from '@/config/global/helpers/template-paths';

// Public API - Entity Configuration
export * from '@/config/entity';

// Public API - Configuration types
export type { codepotConfig, ResolvedcodepotConfig } from '@/config/global/types/codepot.config.types';

export type {
  codepotPathToken,
  codepotOutputFolderPart,
  codepotOutputFolder,
  codepotOutputFileName,
  codepotTemplateRegistration,
  codepotTemplatesFile,
} from '@/config/global/types/codepot.templates.types';

// Public API - Core functionality
export * as Core from '@/core';

// Public API - Types
export * as Types from '@/types';

// Public API - Utilities
export * from '@/utils';
