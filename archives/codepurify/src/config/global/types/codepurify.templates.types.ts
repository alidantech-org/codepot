/**
 * codepot Template Types
 *
 * Types for template registration.
 */

import { codepotOutputFileName, codepotOutputFolder } from '../helpers/template-paths';

export type { codepotPathToken, codepotOutputFolderPart, codepotOutputFolder, codepotOutputFileName } from '../helpers/template-paths';

export { paths, file } from '../helpers/template-paths';

/**
 * A user-registered template.
 */
export interface codepotTemplateRegistration {
  /**
   * Unique template name used by entity configs.
   */
  name: string;

  /**
   * Template file path relative to the templates root.
   */
  templatePath: string;

  /**
   * Output folder path segments.
   *
   * Example:
   * [
   *   paths.entity.groupKey,
   *   paths.entity.name.kebab,
   *   'dto',
   * ]
   */
  outputFolder: codepotOutputFolder;

  /**
   * File name definition.
   *
   * Example:
   * file(paths.entity.name.kebab)
   *   .prefix('create-')
   *   .suffix('.dto')
   *   .ext('ts')
   */
  fileName: codepotOutputFileName;

  /**
   * Optional description for tooling/debug output.
   */
  description?: string;

  /**
   * Template type classification.
   */
  type: 'entity' | 'resource';
}

/**
 * Template registry file shape.
 */
export interface codepotTemplatesFile {
  /**
   * Root directory containing template files.
   */
  rootDir: string;

  /**
   * Registered template definitions.
   */
  templates: readonly codepotTemplateRegistration[];
}

/**
 * Resolved template registration.
 */
export interface ResolvedcodepotTemplateRegistration extends codepotTemplateRegistration {
  absoluteTemplatePath: string;
  resolvedOutputFolderPattern: string;
  resolvedFileNamePattern: string;
  resolvedOutputPathPattern: string;
}

/**
 * Resolved templates file.
 */
export interface ResolvedcodepotTemplatesFile {
  rootDir: string;
  templates: readonly ResolvedcodepotTemplateRegistration[];
}
