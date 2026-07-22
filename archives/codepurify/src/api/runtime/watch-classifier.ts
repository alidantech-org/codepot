/**
 * Watch File Classifier
 *
 * Determines the type of file change based on path patterns.
 */

import type { CodepurifyWatchEvent } from '@/api/types';
import { FilePatternUtils } from './file-pattern-utils';

/**
 * Classify file change type based on path patterns.
 *
 * Uses specific pattern matching to avoid false positives.
 * Global config files are checked first to prevent them being
 * misclassified as regular config files.
 */
export function classifyWatchEvent(path: string): CodepurifyWatchEvent['type'] {
  // Check for global config files first (most specific)
  if (FilePatternUtils.isGlobalConfig(path)) {
    return 'global';
  }

  // Check for template registry files
  if (FilePatternUtils.isTemplateRegistry(path)) {
    return 'template';
  }

  // Check for entity config files
  if (FilePatternUtils.isEntityConfig(path)) {
    return 'config';
  }

  // Default to entity files
  return 'entity';
}
