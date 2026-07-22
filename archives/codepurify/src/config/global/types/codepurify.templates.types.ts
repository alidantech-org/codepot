/**
 * Codepurify Template Types
 *
 * Types for template registration.
 */

import { CodepurifyOutputFileName, CodepurifyOutputFolder } from '../helpers/template-paths';

export type {
  CodepurifyPathToken,
  CodepurifyOutputFolderPart,
  CodepurifyOutputFolder,
  CodepurifyOutputFileName,
} from '../helpers/template-paths';

export { paths, file } from '../helpers/template-paths';

/**
 * A user-registered template.
 */
export interface CodepurifyTemplateRegistration {
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
  outputFolder: CodepurifyOutputFolder;

  /**
   * File name definition.
   *
   * Example:
   * file(paths.entity.name.kebab)
   *   .prefix('create-')
   *   .suffix('.dto')
   *   .ext('ts')
   */
  fileName: CodepurifyOutputFileName;

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
export interface CodepurifyTemplatesFile {
  /**
   * Root directory containing template files.
   */
  rootDir: string;

  /**
   * Registered template definitions.
   */
  templates: readonly CodepurifyTemplateRegistration[];
}

/**
 * Resolved template registration.
 */
export interface ResolvedCodepurifyTemplateRegistration extends CodepurifyTemplateRegistration {
  absoluteTemplatePath: string;
  resolvedOutputFolderPattern: string;
  resolvedFileNamePattern: string;
  resolvedOutputPathPattern: string;
}

/**
 * Resolved templates file.
 */
export interface ResolvedCodepurifyTemplatesFile {
  rootDir: string;
  templates: readonly ResolvedCodepurifyTemplateRegistration[];
}
