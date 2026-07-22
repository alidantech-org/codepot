/**
 * Codepurify Templates Definition Helper
 *
 * Type-safe helper for defining template registry files.
 */

import type { CodepurifyTemplatesFile, CodepurifyTemplateRegistration } from '../types/codepurify.templates.types';

/**
 * Helper type to extract template names from an array of templates
 */
type TemplateNames<T extends readonly CodepurifyTemplateRegistration[]> = T[number]['name'];

/**
 * Enhanced templates interface with strongly typed filtering methods
 */
interface EnhancedCodepurifyTemplatesFile<T extends readonly CodepurifyTemplateRegistration[]> extends CodepurifyTemplatesFile {
  /**
   * Filter templates by type 'entity'
   */
  entity(): CodepurifyTemplatesFile;

  /**
   * Filter templates by type 'resource'
   */
  resource(): CodepurifyTemplatesFile;

  /**
   * Pick specific templates by name (strongly typed)
   */
  pick<K extends TemplateNames<T>>(names: readonly K[]): CodepurifyTemplatesFile;

  /**
   * Omit specific templates by name (strongly typed)
   */
  omit<K extends TemplateNames<T>>(names: readonly K[]): CodepurifyTemplatesFile;
}

/**
 * Define a Codepurify templates registry file.
 *
 * Example:
 * ```ts
 * export default defineCodepurifyTemplates({
 *   rootDir: './codepurify/templates',
 *   templates: [dtoCreateTemplate, dtoUpdateTemplate],
 * });
 * ```
 *
 * Usage with filtering:
 * ```ts
 * const templates = defineCodepurifyTemplates({
 *   rootDir: './codepurify/templates',
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
export function defineCodepurifyTemplates<T extends readonly CodepurifyTemplateRegistration[]>(
  config: CodepurifyTemplatesFile & { templates: T },
): EnhancedCodepurifyTemplatesFile<T> {
  // Create enhanced templates object with filtering methods
  const enhancedTemplates: EnhancedCodepurifyTemplatesFile<T> = {
    ...config,

    // Add template filtering methods that return new CodepurifyTemplatesFile objects
    entity() {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: CodepurifyTemplateRegistration) => template.type === 'entity'),
      };
    },

    resource() {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: CodepurifyTemplateRegistration) => template.type === 'resource'),
      };
    },

    pick<K extends TemplateNames<T>>(names: readonly K[]) {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: CodepurifyTemplateRegistration) => names.includes(template.name as K)),
      };
    },

    omit<K extends TemplateNames<T>>(names: readonly K[]) {
      return {
        rootDir: this.rootDir,
        templates: this.templates.filter((template: CodepurifyTemplateRegistration) => !names.includes(template.name as K)),
      };
    },
  };

  return enhancedTemplates;
}
