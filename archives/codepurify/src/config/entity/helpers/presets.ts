// ─── codepurify/presets.ts ─────────────────────────────────────────────────

import type { MutationConfig, QueryConfig, ToggleState } from '../types/base';
import type { StringFieldConfig } from '../types';

// ─── Query Builder ─────────────────────────────────────────────────────────────

class QueryBuilder {
  private config: Partial<QueryConfig> = {};

  select(): QueryBuilder {
    this.config.select = true;
    return this;
  }

  defaultSelect(): QueryBuilder {
    this.config.defaultSelect = true;
    return this;
  }

  sort(): QueryBuilder {
    this.config.sort = true;
    return this;
  }

  search(): QueryBuilder {
    this.config.search = true;
    return this;
  }

  filter(): QueryBuilder {
    this.config.filter = true;
    return this;
  }

  dateRange(): QueryBuilder {
    this.config.dateRange = true;
    return this;
  }

  build(): QueryConfig {
    return this.config as QueryConfig;
  }
}

// ─── Mutation Builder ─────────────────────────────────────────────────────────--

class MutationBuilder {
  private config: Partial<MutationConfig> = {};

  create(actor?: 'api' | 'system'): MutationBuilder {
    this.config.create = actor || 'api';
    return this;
  }

  update(actor?: 'api' | 'system' | false): MutationBuilder {
    this.config.update = actor;
    return this;
  }

  edit(actor?: 'api' | 'system' | false): MutationBuilder {
    this.config.edit = actor;
    return this;
  }

  immutable(): MutationBuilder {
    this.config.immutable = true;
    return this;
  }

  immutableAfterCreate(): MutationBuilder {
    this.config.immutable_after_create = true;
    return this;
  }

  generated(): MutationBuilder {
    this.config.generated = true;
    return this;
  }

  computed(): MutationBuilder {
    this.config.computed = true;
    return this;
  }

  persisted(): MutationBuilder {
    this.config.persisted = true;
    return this;
  }

  systemOnly(): MutationBuilder {
    this.config.create = 'system';
    this.config.update = 'system';
    this.config.edit = 'system';
    return this;
  }

  apiWritable(): MutationBuilder {
    this.config.create = 'api';
    this.config.update = 'api';
    this.config.edit = 'api';
    return this;
  }

  apiCreateOnly(): MutationBuilder {
    this.config.create = 'api';
    this.config.update = false;
    this.config.edit = false;
    return this;
  }

  build(): MutationConfig {
    return this.config as MutationConfig;
  }
}

// ─── Helper Functions ─────────────────────────────────────────────────────────

export function query(): QueryBuilder {
  return new QueryBuilder();
}

export function mutation(): MutationBuilder {
  return new MutationBuilder();
}

export function toggle(): ToggleState {
  return { toggle: true };
}

// ─── Special Field Factories ───────────────────────────────────────────────────

export function secretStringField(config: Omit<StringFieldConfig, 'kind'>): StringFieldConfig {
  return {
    kind: 'string',
    ...config,
    security: { level: 'secret', ...config.security },
  };
}
