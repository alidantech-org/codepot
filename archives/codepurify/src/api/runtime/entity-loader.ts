/**
 * Entity Loader Service
 *
 * Handles loading and instantiation of entity configuration classes.
 */

import type { CodepurifyRuntime } from './codepurify-runtime';
import type { IEntityConfig } from '@/config/entity/types/entity';
import type { DiscoveredEntity } from './entity-discovery';
import { writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { importTsModule } from './ts-importer';

export interface EntityLoaderOptions {
  /** Validate entity configs during loading */
  validate?: boolean;
  /** Cache loaded entities */
  cache?: boolean;
}

export interface LoadedEntity {
  /** Discovered entity metadata */
  discovered: DiscoveredEntity;
  /** Loaded entity configuration instance */
  config: IEntityConfig;
  /** Loading metadata */
  metadata: {
    /** Load timestamp */
    loadedAt: string;
    /** Module path used for dynamic import */
    modulePath: string;
  };
}

export class EntityLoader {
  private readonly entityCache = new Map<string, LoadedEntity>();

  constructor(private readonly runtime: CodepurifyRuntime) {}

  /**
   * Loads entity configuration instances from discovered files.
   *
   * @param discoveredEntities - Array of discovered entity files
   * @param options - Loading options
   * @returns Array of loaded entity configurations
   */
  async loadEntityConfigs(discoveredEntities: DiscoveredEntity[], options: EntityLoaderOptions = {}): Promise<LoadedEntity[]> {
    const { validate = true, cache = true } = options;
    const loadedEntities: LoadedEntity[] = [];

    console.debug(`Entity loader - Loading ${discoveredEntities.length} entities`);

    for (const discovered of discoveredEntities) {
      try {
        console.debug(`Entity loader - Loading entity: ${discovered.path}`);

        // Check cache first if enabled
        if (cache && this.entityCache.has(discovered.absolutePath)) {
          console.debug(`Entity loader - Found cached entity: ${discovered.path}`);
          const cached = this.entityCache.get(discovered.absolutePath)!;
          loadedEntities.push(cached);
          continue;
        }

        const loaded = await this.loadSingleEntity(discovered, validate);
        console.debug(`Entity loader - Successfully loaded entity: ${discovered.path}`);

        if (cache) {
          this.entityCache.set(discovered.absolutePath, loaded);
        }

        loadedEntities.push(loaded);
      } catch (error) {
        console.error(`Entity loader - Error loading entity ${discovered.path}:`, error);
        throw new Error(`Failed to load entity config from ${discovered.path}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    console.debug(`Entity loader - Successfully loaded ${loadedEntities.length} entities`);
    // Save entity context dumps for audit
    await this.saveEntityContextDumps(loadedEntities);

    return loadedEntities;
  }

  /**
   * Saves JSON dumps of discovered entity contexts to .codepurify folder for audit.
   *
   * @param loadedEntities - Array of loaded entities
   */
  private async saveEntityContextDumps(loadedEntities: LoadedEntity[]): Promise<void> {
    try {
      const auditDir = join(this.runtime.cwd, '.codepurify', 'audit');

      for (const loadedEntity of loadedEntities) {
        // Create directory structure matching entity path
        let entityAuditDir = auditDir;
        if (loadedEntity.discovered.groupKey) {
          entityAuditDir = join(auditDir, loadedEntity.discovered.groupKey);
        }
        await mkdir(entityAuditDir, { recursive: true });

        const dumpData = {
          discovered: {
            path: loadedEntity.discovered.path,
            absolutePath: loadedEntity.discovered.absolutePath,
            key: loadedEntity.discovered.key,
            groupKey: loadedEntity.discovered.groupKey,
          },
          config: {
            key: loadedEntity.config.key,
            group_key: loadedEntity.config.group_key,
            base: loadedEntity.config.base,
            workflows: loadedEntity.config.workflows,
            fields: loadedEntity.config.fields,
            relations: this.serializeRelations(loadedEntity.config.relations),
            indexes: this.serializeIndexes(loadedEntity.config.indexes),
            checks: this.serializeChecks(loadedEntity.config.checks),
            transitions: this.serializeTransitions(loadedEntity.config.transitions),
            options: loadedEntity.config.options,
            templates: loadedEntity.config.templates,
          },
          metadata: loadedEntity.metadata,
        };

        // Use entity name as filename (without timestamp for consistency)
        const fileName = `${loadedEntity.discovered.key}.json`;
        const filePath = join(entityAuditDir, fileName);

        await writeFile(filePath, JSON.stringify(dumpData, null, 2), 'utf-8');
        console.debug(`Entity loader - Saved audit dump: ${filePath}`);
      }
    } catch (error) {
      console.warn(`Entity loader - Failed to save audit dumps: ${error}`);
    }
  }

  /**
   * Loads a single entity configuration from file.
   *
   * @param discovered - Discovered entity metadata
   * @param validate - Whether to validate the loaded config
   * @returns Loaded entity configuration
   */
  private async loadSingleEntity(discovered: DiscoveredEntity, validate: boolean): Promise<LoadedEntity> {
    try {
      // Dynamic import of the entity config module using jiti TypeScript transpiler
      console.debug(`Entity loader - Importing from: ${discovered.absolutePath}`);
      const entityModule = await importTsModule(discovered.absolutePath);

      console.debug('Entity loader - module keys:', Object.keys(entityModule));
      console.debug('Entity loader - default export:', entityModule.default);

      // Support all reasonable export forms
      const exported =
        entityModule.default ??
        entityModule.entityConfig ??
        entityModule.config ??
        Object.values(entityModule).find((value) => value && typeof value === 'function');

      if (!exported) {
        throw new Error(
          `Entity config export not found in ${discovered.absolutePath}. Expected default export, entityConfig, config, or exported class.`,
        );
      }

      // Handle both class constructors and instances
      let configInstance;
      if (typeof exported === 'function') {
        try {
          configInstance = new exported();
        } catch (error) {
          // If constructor fails, assume it's already an instance
          configInstance = exported;
        }
      } else {
        configInstance = exported;
      }

      if (!configInstance?.key) {
        throw new Error(`Invalid entity config: ${discovered.absolutePath}`);
      }

      // Validate the config if requested
      if (validate) {
        this.validateEntityConfig(configInstance, discovered);
      }

      return {
        discovered,
        config: configInstance,
        metadata: {
          loadedAt: new Date().toISOString(),
          modulePath: discovered.absolutePath,
        },
      };
    } catch (error) {
      if (error instanceof Error && error.message.includes('Cannot find module')) {
        throw new Error(
          `Failed while importing entity config ${discovered.absolutePath}. ` +
            `A dependency inside this file could not be resolved. Original error: ${error.message}`,
        );
      }
      throw new Error(`Failed to load entity config ${discovered.absolutePath}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Finds the entity configuration class in a module.
   *
   * @param module - Imported module
   * @returns Entity configuration class constructor
   */
  private findEntityConfigClass(module: any): (new () => IEntityConfig) | null {
    // Check default export first
    if (module.default && this.isEntityConfigClass(module.default)) {
      return module.default;
    }

    // Check named exports
    for (const exportName of Object.keys(module)) {
      if (exportName !== 'default' && this.isEntityConfigClass(module[exportName])) {
        return module[exportName];
      }
    }

    return null;
  }

  /**
   * Type guard to check if a class implements IEntityConfig.
   *
   * @param cls - Class constructor
   * @returns True if class implements IEntityConfig
   */
  private isEntityConfigClass(cls: any): cls is new () => IEntityConfig {
    // Check if it's a constructor function
    if (typeof cls !== 'function' || !cls.prototype) {
      return false;
    }

    // Check for required IEntityConfig properties
    const instance = new cls();
    return typeof instance.key === 'string' && typeof instance.fields === 'object' && instance.fields !== null;
  }

  /**
   * Validates a loaded entity configuration.
   *
   * @param configInstance - Entity configuration instance
   * @param discovered - Discovered entity metadata
   */
  private validateEntityConfig(configInstance: IEntityConfig, discovered: DiscoveredEntity): void {
    // Basic validation
    if (!configInstance.key) {
      throw new Error('Entity config must have a key property');
    }

    if (!configInstance.fields || Object.keys(configInstance.fields).length === 0) {
      throw new Error('Entity config must have fields defined');
    }

    // Validate key matches filename
    const expectedKey = discovered.key;
    if (configInstance.key !== expectedKey) {
      throw new Error(`Entity key '${configInstance.key}' does not match expected key '${expectedKey}' from filename`);
    }

    // Validate group key if present
    if (configInstance.group_key && discovered.groupKey && configInstance.group_key !== discovered.groupKey) {
      throw new Error(`Entity group_key '${configInstance.group_key}' does not match directory group '${discovered.groupKey}'`);
    }
  }

  /**
   * Serializes relations with resolved field callbacks for audit dumps.
   *
   * @param relations - Relations object from entity config
   * @returns Serialized relations with resolved field metadata
   */
  private serializeRelations(relations: any = {}) {
    return Object.fromEntries(
      Object.entries(relations).map(([key, value]: [string, any]) => {
        const relation = value.relation ?? value;

        return [
          key,
          {
            ...value,
            relation: {
              ...relation,
              local_field: this.serializeFieldGetter(relation.local_field),
              remote_field: this.serializeFieldGetter(relation.remote_field),
            },
          },
        ];
      }),
    );
  }

  /**
   * Safely serializes a field getter function with error handling.
   *
   * @param getter - Field getter function
   * @returns Serialized field metadata or error info if getter fails
   */
  private safeSerializeFieldGetter(getter?: () => any) {
    if (typeof getter !== 'function') return undefined;

    try {
      const field = getter();
      return this.serializeField(field);
    } catch (error) {
      return {
        unresolved: true,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Serializes a field object to field metadata.
   *
   * @param field - Field configuration object
   * @returns Serialized field metadata
   */
  private serializeField(field: any) {
    if (!field) return undefined;

    return {
      key: field.key,
      names: field.names,
      kind: field.kind,
      nullable: field.nullable ?? false,
      length: field.length,
      query: field.query,
      mutation: field.mutation,
      value_list: field.value_list,
      values: field.values,
      business: field.business,
      system: field.system,
    };
  }

  /**
   * @deprecated Use safeSerializeFieldGetter instead
   */
  private serializeFieldGetter(getter?: () => any) {
    return this.safeSerializeFieldGetter(getter);
  }

  /**
   * Serializes indexes with resolved field getters.
   *
   * @param indexes - Indexes array from entity config
   * @returns Serialized indexes with resolved field metadata
   */
  private serializeIndexes(indexes: readonly any[] = []) {
    return indexes.map((index) => ({
      ...index,
      fields: index.fields?.map((getter: () => any) => this.serializeFieldGetter(getter)),
    }));
  }

  /**
   * Serializes checks with resolved field getters.
   *
   * @param checks - Checks array from entity config
   * @returns Serialized checks with resolved field metadata
   */
  private serializeChecks(checks: readonly any[] = []) {
    return checks.map((check) => ({
      ...check,
      fields: check.fields?.map((getter: () => any) => this.serializeFieldGetter(getter)),
    }));
  }

  /**
   * Serializes transitions with resolved field getters.
   *
   * @param transitions - Transitions array from entity config
   * @returns Serialized transitions with resolved field metadata
   */
  private serializeTransitions(transitions: readonly any[] = []) {
    return transitions.map((transition) => ({
      ...transition,
      fields: transition.fields?.map((getter: () => any) => this.serializeFieldGetter(getter)),
    }));
  }

  /**
   * Clears the entity cache.
   */
  clearCache(): void {
    this.entityCache.clear();
  }

  /**
   * Gets cache statistics.
   *
   * @returns Cache statistics
   */
  getCacheStats(): { size: number; entries: string[] } {
    return {
      size: this.entityCache.size,
      entries: Array.from(this.entityCache.keys()),
    };
  }
}
