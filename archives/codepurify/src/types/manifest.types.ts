/**
 * Codepurify Manifest Types
 *
 * Types for Codepurify manifest tracking and backup/session management.
 * Provides contracts for file tracking and generation metadata.
 */

export interface CodepurifyManifest {
  version: 1;
  generator: 'codepurify';
  generatedAt: string | null;
  entries: CodepurifyManifestEntry[];
}

export interface CodepurifyManifestEntry {
  path: string;
  absolutePath: string;
  source: string;
  template: string;
  hash: string;
  immutable: boolean;
  generatedAt: string;
}
