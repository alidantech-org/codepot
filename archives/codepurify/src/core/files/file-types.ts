import { FileAction } from '@/api/types';

/**
 * Codepurify file management types.
 *
 * This module defines the internal JSON DB shape and the public file-system API
 * result/input types.
 */

/**
 * File kind enum for type safety.
 */
export enum CodepurifyFileKind {
  GENERATED = 'generated',
  CONFIG = 'config',
  TEMPLATE = 'template',
  BACKUP = 'backup',
  UNKNOWN = 'unknown',
}

export interface CodepurifyFilesOptions {
  /**
   * Project root directory.
   */
  rootDir: string;

  /**
   * File DB path relative to rootDir.
   *
   * Recommended:
   * '.codepurify/files.json'
   */
  dbPath?: string;

  /**
   * Backup directory path relative to rootDir.
   *
   * Recommended:
   * '.codepurify/backups'
   */
  backupDir?: string;
}

export interface CodepurifyFileBackupRef {
  sessionId: string;
  path: string;
  createdAt: string;
}

export interface CodepurifyFileRecord {
  /**
   * POSIX relative path from rootDir.
   */
  path: string;

  /**
   * Absolute file path.
   */
  absolutePath: string;

  kind: CodepurifyFileKind;

  /**
   * Source config/entity/template that produced this file.
   */
  source?: string;

  /**
   * Template name that produced this file.
   */
  template?: string;

  hash: string;

  sizeBytes: number;

  createdAt: string;

  updatedAt: string;

  lastGeneratedAt?: string;

  immutable?: boolean;

  backup?: CodepurifyFileBackupRef;

  metadata?: Record<string, unknown>;
}

export interface CodepurifyFilesDb {
  version: 1;
  generator: 'codepurify';
  updatedAt: string | null;
  records: CodepurifyFileRecord[];
}

export interface CodepurifyReadResult {
  path: string;
  absolutePath: string;
  exists: boolean;
  content: string;
  hash?: string;
  sizeBytes: number;
  record?: CodepurifyFileRecord | null;
}

export interface CodepurifyFileInfo {
  path: string;
  absolutePath: string;
  exists: boolean;
  sizeBytes: number;
  record?: CodepurifyFileRecord | null;
}

export interface WriteGeneratedFileInput {
  path: string;
  content: string;
  source: string;
  template: string;
  immutable?: boolean;
  metadata?: Record<string, unknown>;
  backupSession?: CodepurifyBackupSession;
}

export interface WriteGeneratedFileResult {
  path: string;
  absolutePath: string;
  hash: string;
  sizeBytes: number;
  action: FileAction;
  backupPath?: string;
}

export interface CodepurifyBackupRecord {
  originalPath: string;
  backupPath: string | null;
  existed: boolean;
  hash?: string;
  sizeBytes?: number;
}

export interface CodepurifyBackupSession {
  id: string;
  reason?: string;
  createdAt: string;
  records: CodepurifyBackupRecord[];
}

export interface CodepurifyRollbackResult {
  sessionId: string;
  restoredFiles: string[];
  deletedFiles: string[];
  skippedFiles: string[];
}

export interface CodepurifyFileValidationResult {
  record: CodepurifyFileRecord;
  exists: boolean;
  hashMatches?: boolean;
  actualHash?: string;
  error?: string;
}
