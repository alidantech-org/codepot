/**
 * Generate Pipeline Service
 *
 * Orchestrates the entire code generation pipeline from config loading to file writing.
 */

import type { CodepurifyRuntime } from './codepurify-runtime';
import type { ResolvedCodepurifyConfig } from '@/config/global/types/codepurify.config.types';
import type { WriteGeneratedFileInput } from '@/core/files/file-types';
import type { FileAction } from '@/api/types';
import type { CodepurifyBackupSession } from '@/core/files/file-types';
import { ConfigLoader } from './config-loader';
import { EntityDiscovery } from './entity-discovery';
import { EntityLoader } from './entity-loader';
import { TemplateResolver, type EntityContext } from './template-resolver';
import { TemplateRenderer } from './template-renderer';

/**
 * Resolves lazy relation field callbacks to field metadata.
 */
function resolveRelationField(fieldGetter?: () => any) {
  if (!fieldGetter) return undefined;

  const field = fieldGetter();

  return {
    key: field.key,
    snake_case_key: field.snake_case_key,
    camel_case_key: field.camel_case_key,
    pascal_case_key: field.pascal_case_key,
    kind: field.kind,
    nullable: field.nullable ?? false,
    typescript_type: field.typescript_type,
  };
}

/**
 * Normalizes relation configuration by resolving lazy field callbacks.
 */
function normalizeRelation(name: string, relationConfig: any) {
  const relation = relationConfig.relation ?? relationConfig;

  return {
    key: name,
    kind: relation.kind,
    on_delete: relation.on_delete,
    cascade: relation.cascade ?? false,
    local_field: resolveRelationField(relation.local_field),
    remote_field: resolveRelationField(relation.remote_field),
    query: relationConfig.query ?? {},
  };
}

export interface GeneratePipelineOptions {
  /** Configuration loading options */
  config?: {
    configPath?: string;
  };
  /** Entity discovery options */
  discovery?: {
    pattern?: string;
    recursive?: boolean;
    keyPattern?: RegExp;
  };
  /** Entity loading options */
  loading?: {
    validate?: boolean;
    cache?: boolean;
  };
  /** Template rendering options */
  rendering?: {
    engine?: 'eta' | 'codepurify';
    cache?: boolean;
  };
  /** File writing options */
  writing?: {
    backupSession?: CodepurifyBackupSession;
    dryRun?: boolean;
  };
}

export interface GeneratePipelineResult {
  /** Pipeline execution metrics */
  metrics: {
    /** Total entities processed */
    entitiesProcessed: number;
    /** Total templates rendered */
    templatesRendered: number;
    /** Total files written */
    filesWritten: number;
    /** Total execution time in milliseconds */
    executionTimeMs: number;
  };
  /** Generated file results */
  generatedFiles: WriteGeneratedFileInput[];
  /** Pipeline execution warnings */
  warnings: string[];
}

export class GeneratePipeline {
  private readonly configLoader: ConfigLoader;
  private readonly entityDiscovery: EntityDiscovery;
  private readonly entityLoader: EntityLoader;
  private readonly templateResolver: TemplateResolver;
  private readonly templateRenderer: TemplateRenderer;

  constructor(private readonly runtime: CodepurifyRuntime) {
    this.configLoader = new ConfigLoader(runtime);
    this.entityDiscovery = new EntityDiscovery(runtime);
    this.entityLoader = new EntityLoader(runtime);
    this.templateResolver = new TemplateResolver(runtime);
    this.templateRenderer = new TemplateRenderer(runtime);
  }

  /**
   * Executes the complete generation pipeline.
   *
   * @param options - Pipeline execution options
   * @returns Generation pipeline result
   */
  async execute(options: GeneratePipelineOptions = {}): Promise<GeneratePipelineResult> {
    const startTime = Date.now();
    const warnings: string[] = [];

    try {
      console.debug('Pipeline - Starting generation pipeline');

      // Step 1: Load global configuration
      const globalConfig = await this.configLoader.loadGlobalConfig(options.config);

      console.debug('Pipeline - Config loaded, discovering entities...');

      // Step 2: Discover entity configuration files
      const discoveredEntities = await this.entityDiscovery.discoverEntityConfigs(globalConfig, options.discovery);

      console.debug(`Pipeline - Discovered ${discoveredEntities.length} entities`);

      if (discoveredEntities.length === 0) {
        warnings.push('No entity configuration files found');
        return this.createResult([], warnings, startTime);
      }

      // Step 3: Load entity configuration instances
      console.debug('Pipeline - Loading entity configurations...');
      const loadedEntities = await this.entityLoader.loadEntityConfigs(discoveredEntities, options.loading);
      console.debug(`Pipeline - Loaded ${loadedEntities.length} entity configurations`);

      // Step 4: Build entity contexts
      console.debug('Pipeline - Building entity contexts...');
      const entityContexts = loadedEntities.map((loadedEntity) => this.createEntityContext(loadedEntity.config, loadedEntity.discovered));
      console.debug(`Pipeline - Built ${entityContexts.length} entity contexts`);

      // Step 5: Resolve template executions
      console.debug('Pipeline - Resolving template executions...');
      const templateExecutions = await this.templateResolver.resolveTemplateExecutions({
        globalConfig,
        entityConfigs: loadedEntities,
        entityContexts,
      });
      console.debug(`Pipeline - Resolved ${templateExecutions.length} template executions`);

      if (templateExecutions.length === 0) {
        warnings.push('No template executions resolved');
        return this.createResult([], warnings, startTime);
      }

      // Step 6: Render templates
      const renderedTemplates = await this.templateRenderer.renderTemplates(templateExecutions, options.rendering);

      // Step 7: Prepare file inputs for writing
      const fileInputs = renderedTemplates.map((rendered) => ({
        path: rendered.outputPath,
        content: rendered.content,
        source: 'generate',
        template: rendered.metadata.templateName,
        immutable: false,
        backupSession: options.writing?.backupSession,
        metadata: {
          entityKey: rendered.metadata.entityKey,
          templateName: rendered.metadata.templateName,
          renderedAt: rendered.metadata.renderedAt,
        },
      }));

      // Step 8: Write files (if not dry run)
      const generatedFiles: WriteGeneratedFileInput[] = [];
      if (!options.writing?.dryRun) {
        for (const fileInput of fileInputs) {
          try {
            await this.runtime.files.writeGenerated(fileInput);
            generatedFiles.push(fileInput);
          } catch (error) {
            warnings.push(`Failed to write file ${fileInput.path}: ${error instanceof Error ? error.message : String(error)}`);
          }
        }
      } else {
        // In dry run mode, include all files as if they were written
        generatedFiles.push(...fileInputs);
      }

      return this.createResult(generatedFiles, warnings, startTime);
    } catch (error) {
      throw new Error(`Pipeline execution failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Creates an entity context for template rendering.
   *
   * @param config - Entity configuration
   * @param discovered - Discovered entity metadata
   * @returns Entity context
   */
  private createEntityContext(config: any, discovered: any): EntityContext {
    // Normalize relations with resolved field callbacks
    const relationsArray = Object.entries(config.relations ?? {}).map(([name, relation]) => normalizeRelation(name, relation));

    // Convert array back to record for compatibility
    const relations = relationsArray.reduce(
      (acc, relation) => {
        acc[relation.key] = relation;
        return acc;
      },
      {} as Record<string, any>,
    );

    // Create a copy of the config with resolved relations
    const configWithResolvedRelations = {
      ...config,
      relations,
    };

    const context: EntityContext = {
      entity: configWithResolvedRelations,
      discovered,
      metadata: {
        keys: {
          camel: this.toCamelCase(config.key),
          pascal: this.toPascalCase(config.key),
          kebab: this.toKebabCase(config.key),
          snake: this.toSnakeCase(config.key),
        },
        group: {
          key: config.group_key || discovered.groupKey || 'default',
          pascal: this.toPascalCase(config.group_key || discovered.groupKey || 'default'),
        },
      },
    };

    return context;
  }

  /**
   * Creates pipeline result with metrics.
   *
   * @param generatedFiles - Generated files
   * @param warnings - Pipeline warnings
   * @param startTime - Pipeline start time
   * @returns Pipeline result
   */
  private createResult(generatedFiles: WriteGeneratedFileInput[], warnings: string[], startTime: number): GeneratePipelineResult {
    const executionTimeMs = Date.now() - startTime;

    return {
      metrics: {
        entitiesProcessed: new Set(generatedFiles.map((f) => f.metadata?.entityKey)).size,
        templatesRendered: new Set(generatedFiles.map((f) => f.template)).size,
        filesWritten: generatedFiles.length,
        executionTimeMs,
      },
      generatedFiles,
      warnings,
    };
  }

  /**
   * Converts string to camelCase.
   */
  private toCamelCase(str: string): string {
    return str.replace(/[-_](.)/g, (_, char) => char.toUpperCase()).replace(/^[A-Z]/, (char) => char.toLowerCase());
  }

  /**
   * Converts string to PascalCase.
   */
  private toPascalCase(str: string): string {
    return str.replace(/[-_](.)/g, (_, char) => char.toUpperCase()).replace(/^[a-z]/, (char) => char.toUpperCase());
  }

  /**
   * Converts string to kebab-case.
   */
  private toKebabCase(str: string): string {
    return str
      .replace(/([A-Z])/g, '-$1')
      .toLowerCase()
      .replace(/^-/, '');
  }

  /**
   * Converts string to snake_case.
   */
  private toSnakeCase(str: string): string {
    return str
      .replace(/([A-Z])/g, '_$1')
      .toLowerCase()
      .replace(/^_/, '');
  }
}
