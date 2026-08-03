import { FileAction } from '@/api/types';

/**
 * codepot file management types.
 *
 * This module defines the internal JSON DB shape and the public file-system API
 * result/input types.
 */

/**
 * File kind enum for type safety.
 */
export enum codepotFileKind {
  GENERATED = 'generated',
  CONFIG = 'config',
  TEMPLATE = 'template',
  BACKUP = 'backup',
  UNKNOWN = 'unknown',
}

export interface codepotFilesOptions {
  /**
   * Project root directory.
   */
  rootDir: string;

  /**
   * File DB path relative to rootDir.
   *
   * Recommended:
   * '.codepot/files.json'
   */
  dbPath?: string;

  /**
   * Backup directory path relative to rootDir.
   *
   * Recommended:
   * '.codepot/backups'
   */
  backupDir?: string;
}

export interface codepotFileBackupRef {
  sessionId: string;
  path: string;
  createdAt: string;
}

export interface codepotFileRecord {
  /**
   * POSIX relative path from rootDir.
   */
  path: string;

  /**
   * Absolute file path.
   */
  absolutePath: string;

  kind: codepotFileKind;

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

  backup?: codepotFileBackupRef;

  metadata?: Record<string, unknown>;
}

export interface codepotFilesDb {
  version: 1;
  generator: 'codepot';
  updatedAt: string | null;
  records: codepotFileRecord[];
}

export interface codepotReadResult {
  path: string;
  absolutePath: string;
  exists: boolean;
  content: string;
  hash?: string;
  sizeBytes: number;
  record?: codepotFileRecord | null;
}

export interface codepotFileInfo {
  path: string;
  absolutePath: string;
  exists: boolean;
  sizeBytes: number;
  record?: codepotFileRecord | null;
}

export interface WriteGeneratedFileInput {
  path: string;
  content: string;
  source: string;
  template: string;
  immutable?: boolean;
  metadata?: Record<string, unknown>;
  backupSession?: codepotBackupSession;
}

export interface WriteGeneratedFileResult {
  path: string;
  absolutePath: string;
  hash: string;
  sizeBytes: number;
  action: FileAction;
  backupPath?: string;
}

export interface codepotBackupRecord {
  originalPath: string;
  backupPath: string | null;
  existed: boolean;
  hash?: string;
  sizeBytes?: number;
}

export interface codepotBackupSession {
  id: string;
  reason?: string;
  createdAt: string;
  records: codepotBackupRecord[];
}

export interface codepotRollbackResult {
  sessionId: string;
  restoredFiles: string[];
  deletedFiles: string[];
  skippedFiles: string[];
}

export interface codepotFileValidationResult {
  record: codepotFileRecord;
  exists: boolean;
  hashMatches?: boolean;
  actualHash?: string;
  error?: string;
}
