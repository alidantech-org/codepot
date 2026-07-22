import type { OpenApiVersion } from './openapi-version.js';

export interface OpenApiDocument {
  openapi: OpenApiVersion;
  info: OpenApiInfo;
  servers?: OpenApiServer[];
  security?: Array<Record<string, string[]>>;
  paths: OpenApiPaths;
  components: OpenApiComponents;
  [extension: `x-${string}`]: unknown;
}

export interface OpenApiInfo {
  title: string;
  version: string;
  description?: string;
  license?: {
    name: string;
    identifier?: string;
    url?: string;
  };
}

export type OpenApiPaths = Record<string, OpenApiPathItem>;

export type OpenApiPathItem = Partial<Record<OpenApiOperationMethod, OpenApiOperation>> & {
  parameters?: unknown[];
  summary?: string;
  description?: string;
};

export type OpenApiOperationMethod = 'get' | 'post' | 'put' | 'patch' | 'delete';

export interface OpenApiOperation {
  operationId?: string;
  tags?: string[];
  summary?: string;
  description?: string;
  parameters?: unknown[];
  requestBody?: unknown;
  responses: Record<string, unknown>;
  security?: Array<Record<string, string[]>>;
  [extension: `x-${string}`]: unknown;
}

export interface OpenApiComponents {
  schemas: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  requestBodies?: Record<string, unknown>;
  responses?: Record<string, unknown>;
  securitySchemes?: Record<string, unknown>;
}

export interface OpenApiServer {
  url: string;
  description?: string;
}
