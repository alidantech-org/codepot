/**
 * codepot Templates Definition Helper
 *
 * Type-safe helper for defining template registry files.
 */

import type { codepotTemplatesFile, codepotTemplateRegistration } from '../types/codepot.templates.types';

/**
 * Helper type to extract template names from an array of templates
 */
type TemplateNames<T extends readonly codepotTemplateRegistration[]> = T[number]['name'];

/**
 * Enhanced templates interface with strongly typed filtering methods
 */
interface EnhancedcodepotTemplatesFile<T extends readonly codepotTemplateRegistration[]> extends codepotTemplatesFile {
  /**
   * Filter templates by type 'entity'
   */
  entity(): codepotTemplatesFile;

  /**
   * Filter templates by type 'resource'
   */
  resource(): codepotTemplatesFile;

  /**
   * Pick specific templates by name (strongly typed)
   */
  pick<K extends TemplateNames<T>>(names: readonly K[]): codepotTemplatesFile;

  /**
   * Omit specific templates by name (strongly typed)
   */
  omit<K extends TemplateNames<T>>(names: readonly K[]): codepotTemplatesFile;
}

/**
 * Define a codepot templates registry file.
 *
 * Example:
 * ```ts
 * export default definecodepotTemplates({
 *   rootDir: './codepot/templates',
 *   templates: [dtoCreateTemplate, dtoUpdateTemplate],
 * });
 * ```
 *
 * Usage with filtering:
 * ```ts
 * const templates = definecodepotTemplates({
 *   rootDir: './codepot/templates',
 *   templates: [dtoCreateTemplate, dtoUpdateTemplate],
 * });
 *
 * // Get only entity templates
 * const entityTemplates = templates.entity();
 *
 * // Get only resource templates
 * const resourceTemplates = templates.resource();
 *
 * // Pick specific templates
 * const selectedTemplates = templates.pick(['entity', 'controller']);
 *
 * // Omit specific templates
 * const filteredTemplates = templates.omit(['dto.create', 'dto.update']);
 * ```
 */
export function definecodepotTemplates<T extends readonly codepotTemplateRegistration[]>(
  config: codepotTemplatesFile & { templates: T },
): EnhancedcodepotTemplatesFile<T> {
  // Create enhanced templates object with filtering methods
  const enhancedTemplates: EnhancedcodepotTemplatesFile<T> = {
    ...config,

    // Add template filtering methods that return new codepotTemplatesFile objects
    entity() {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: codepotTemplateRegistration) => template.type === 'entity'),
      };
    },

    resource() {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: codepotTemplateRegistration) => template.type === 'resource'),
      };
    },

    pick<K extends TemplateNames<T>>(names: readonly K[]) {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: codepotTemplateRegistration) => names.includes(template.name as K)),
      };
    },

    omit<K extends TemplateNames<T>>(names: readonly K[]) {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: codepotTemplateRegistration) => !names.includes(template.name as K)),
      };
    },
  };

  return enhancedTemplates;
}
