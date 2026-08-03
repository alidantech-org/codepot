export interface CompilerNameRegistry {
  readonly properties: Map<string, string>;
  readonly entities: Map<string, string>;
  readonly fields: Map<string, Map<string, string>>;
  readonly models: Map<string, string>;
  readonly dtos: Map<string, string>;
  readonly params: Map<string, string>;
  readonly errors: Map<string, string>;
  readonly resources: Map<string, string>;
  readonly operations: Map<string, Map<string, string>>;
}

export function createCompilerNameRegistry(): CompilerNameRegistry {
  return {
    properties: new Map(),
    entities: new Map(),
    fields: new Map(),
    models: new Map(),
    dtos: new Map(),
    params: new Map(),
    errors: new Map(),
    resources: new Map(),
    operations: new Map(),
  };
}
