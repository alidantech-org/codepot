export interface PropertyResourceContext {
  readonly name: string;
  readonly alias: string;
  readonly folders: readonly string[];
}

export interface DefinePropertiesOptions {
  readonly name: string;
  readonly resource?: PropertyResourceContext;
}
