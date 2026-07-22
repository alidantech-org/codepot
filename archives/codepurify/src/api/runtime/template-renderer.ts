/**
 * Template Renderer Service
 *
 * Handles rendering of templates using Codepurify or other template engines.
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import * as Eta from 'eta';

import type { CodepurifyRuntime } from './codepurify-runtime';
import type { TemplateExecution } from './template-resolver';

export interface RenderedTemplate {
  /** Template execution that was rendered */
  execution: TemplateExecution;
  /** Rendered content */
  content: string;
  /** Output file path */
  outputPath: string;
  /** Template metadata */
  metadata: {
    /** Template name */
    templateName: string;
    /** Entity key */
    entityKey: string;
    /** Render timestamp */
    renderedAt: string;
    /** Content length */
    contentLength: number;
  };
}

export interface TemplateRendererOptions {
  /** Template engine to use */
  engine?: 'eta' | 'codepurify';
  /** Cache compiled templates */
  cache?: boolean;
}

export class TemplateRenderer {
  private readonly templateCache = new Map<string, Function>();
  private readonly engine: 'eta' | 'codepurify';

  constructor(
    private readonly runtime: CodepurifyRuntime,
    options: TemplateRendererOptions = {},
  ) {
    this.engine = options.engine ?? 'eta';
  }

  /**
   * Renders multiple template executions.
   *
   * @param executions - Array of template executions to render
   * @param options - Rendering options
   * @returns Array of rendered templates
   */
  async renderTemplates(executions: TemplateExecution[], options: TemplateRendererOptions = {}): Promise<RenderedTemplate[]> {
    const { cache = true } = options;
    const renderedTemplates: RenderedTemplate[] = [];

    for (const execution of executions) {
      try {
        const rendered = await this.renderSingleTemplate(execution, { cache });
        renderedTemplates.push(rendered);
      } catch (error) {
        throw new Error(
          `Failed to render template '${execution.template.name}' for entity '${execution.entityContext.entity.key}': ${error instanceof Error ? error.message : String(error)}`,
        );
      }
    }

    return renderedTemplates;
  }

  /**
   * Renders a single template execution.
   *
   * @param execution - Template execution to render
   * @param options - Rendering options
   * @returns Rendered template
   */
  private async renderSingleTemplate(execution: TemplateExecution, options: { cache: boolean }): Promise<RenderedTemplate> {
    const { cache } = options;

    // Load template content
    const templateContent = await this.loadTemplateContent(execution.source.absoluteTemplatePath);

    // Prepare template data
    const templateData = this.prepareTemplateData(execution);

    // Render template directly
    const content = await this.executeTemplate(templateContent, templateData);

    return {
      execution,
      content,
      outputPath: execution.outputPath,
      metadata: {
        templateName: execution.template.name,
        entityKey: execution.entityContext.entity.key,
        renderedAt: new Date().toISOString(),
        contentLength: Buffer.byteLength(content, 'utf-8'),
      },
    };
  }

  /**
   * Loads template content from file.
   *
   * @param templatePath - Absolute path to template file
   * @returns Template content
   */
  private async loadTemplateContent(templatePath: string): Promise<string> {
    try {
      return await readFile(templatePath, 'utf-8');
    } catch (error) {
      throw new Error(`Failed to load template file '${templatePath}': ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Executes a template with data.
   *
   * @param templateContent - Template content
   * @param templateData - Template data
   * @returns Rendered content
   */
  private async executeTemplate(templateContent: string, templateData: unknown): Promise<string> {
    try {
      // For now, use basic string replacement - will be enhanced later
      let result = templateContent;

      // Basic template variable replacement
      if (typeof templateData === 'object' && templateData !== null) {
        const data = templateData as Record<string, unknown>;

        // Replace {{entity.key}} with actual entity key
        if (data.entity && typeof data.entity === 'object' && (data.entity as any).key) {
          result = result.replace(/\{\{entity\.key\}\}/g, (data.entity as any).key);
        }

        // Add more basic replacements as needed
      }

      return result;
    } catch (error) {
      throw new Error(`Template execution failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Prepares template data from execution context.
   *
   * @param execution - Template execution
   * @returns Template data object
   */
  private prepareTemplateData(execution: TemplateExecution): unknown {
    const { entityContext, template } = execution;

    return {
      // Entity information
      entity: {
        key: entityContext.entity.key,
        groupKey: entityContext.entity.group_key,
        fields: entityContext.entity.fields,
        relations: entityContext.entity.relations,
        indexes: entityContext.entity.indexes,
        checks: entityContext.entity.checks,
        options: entityContext.entity.options,
        transitions: entityContext.entity.transitions,
        workflows: entityContext.entity.workflows,
      },

      // Computed entity metadata
      entityMeta: entityContext.metadata,

      // Template information
      template: {
        name: template.name,
        type: template.type,
        description: template.description,
      },

      // Helper functions for naming conventions
      names: entityContext.metadata.keys,

      // Group information
      group: entityContext.metadata.group,
    };
  }

  /**
   * Creates a simple hash for content caching.
   *
   * @param content - Content to hash
   * @returns Simple hash string
   */
  private createContentHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * Clears the template cache.
   */
  clearCache(): void {
    this.templateCache.clear();
  }

  /**
   * Gets cache statistics.
   *
   * @returns Cache statistics
   */
  getCacheStats(): { size: number; entries: string[] } {
    return {
      size: this.templateCache.size,
      entries: Array.from(this.templateCache.keys()),
    };
  }
}
