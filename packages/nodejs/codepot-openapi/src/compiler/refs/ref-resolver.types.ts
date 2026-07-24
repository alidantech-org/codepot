export interface RefResolver {
  readonly schemas: Map<string, string>;
  readonly parameters: Map<string, string>;
  readonly requestBodies: Map<string, string>;
  readonly responses: Map<string, string>;
}

export interface OpenApiRef {
  readonly $ref: string;
}
