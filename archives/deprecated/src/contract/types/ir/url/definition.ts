// src/contract/types/ir/url/definition.ts

import type { DefinitionItem } from '../definition';

// ============================================================================
// URL ENVIRONMENT
// ============================================================================

export const UrlEnv = {
  local: 'local',
  development: 'development',
  preview: 'preview',
  staging: 'staging',
  production: 'production',
  test: 'test',
} as const;

export type UrlEnv = (typeof UrlEnv)[keyof typeof UrlEnv];

// ============================================================================
// URL KIND
// ============================================================================

export const UrlKind = {
  api: 'api',
  website: 'website',
  admin: 'admin',
  docs: 'docs',
  assets: 'assets',
  cdn: 'cdn',
  websocket: 'websocket',
  webhook: 'webhook',
  auth: 'auth',
  custom: 'custom',
} as const;

export type UrlKind = (typeof UrlKind)[keyof typeof UrlKind];

// ============================================================================
// URL PROTOCOL
// ============================================================================

export const UrlProtocol = {
  http: 'http',
  https: 'https',
  ws: 'ws',
  wss: 'wss',
} as const;

export type UrlProtocol = (typeof UrlProtocol)[keyof typeof UrlProtocol];

// ============================================================================
// URL
// ============================================================================

export interface UrlDefinition extends DefinitionItem {
  /**
   * Stable compiled key/use.
   * Examples: "public_api", "website", "admin", "docs".
   */
  key: string;

  /**
   * What this URL is used for.
   */
  kind: UrlKind;

  /**
   * Environment this URL belongs to.
   */
  env: UrlEnv;

  /**
   * Full URI.
   */
  uri: string;

  /**
   * Optional protocol hint for codegen and validation.
   */
  protocol?: UrlProtocol;

  /**
   * Optional base path for APIs served under a subpath.
   * Example: "/api/v1".
   */
  base_path?: string;

  /**
   * Optional display label.
   */
  label?: string;
}
