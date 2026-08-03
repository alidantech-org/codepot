/**
 * codepot Manifest Types
 *
 * Types for codepot manifest tracking and backup/session management.
 * Provides contracts for file tracking and generation metadata.
 */

export interface codepotManifest {
  version: 1;
  generator: 'codepot';
  generatedAt: string | null;
  entries: codepotManifestEntry[];
}

export interface codepotManifestEntry {
  path: string;
  absolutePath: string;
  source: string;
  template: string;
  hash: string;
  immutable: boolean;
  generatedAt: string;
}
