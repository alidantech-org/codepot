import { unlink, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

import { CodepurifyFileBackups } from './file-backups';
import { CodepurifyFileDb } from './file-db';
import { CodepurifyFileReader } from './file-reader';
import { CodepurifyFileRollback } from './file-rollback';
import { CodepurifyFileValidator } from './file-validator';
import { CodepurifyFileWriter } from './file-writer';
import { relativeFromRoot, resolveInsideRoot } from './file-paths';
import { FILE_DB_CONSTANTS, FILE_BACKUP_CONSTANTS } from './file.constants';

import type {
  CodepurifyBackupSession,
  CodepurifyFileInfo,
  CodepurifyFileRecord,
  CodepurifyFilesOptions,
  CodepurifyFileValidationResult,
  CodepurifyReadResult,
  CodepurifyRollbackResult,
  WriteGeneratedFileInput,
  WriteGeneratedFileResult,
} from './file-types';

/**
 * One public file-management API for Codepurify.
 *
 * This class is the only file API the rest of the package should use.
 * Internally it delegates to small modules:
 *
 * - FileDb: JSON DB / old manifest replacement
 * - Reader: safe reads
 * - Writer: safe atomic writes
 * - Backups: backup sessions
 * - Rollback: restore/delete from backup sessions
 * - Validator: compare DB records against disk
 */
export class CodepurifyFiles {
  readonly rootDir: string;

  readonly db: CodepurifyFileDb;
  readonly reader: CodepurifyFileReader;
  readonly backups: CodepurifyFileBackups;
  readonly writer: CodepurifyFileWriter;
  readonly rollbacker: CodepurifyFileRollback;
  readonly validator: CodepurifyFileValidator;

  constructor(options: CodepurifyFilesOptions) {
    this.rootDir = resolve(options.rootDir);

    this.db = new CodepurifyFileDb(this.rootDir, options.dbPath ?? FILE_DB_CONSTANTS.defaultFileName);
    this.reader = new CodepurifyFileReader(this.rootDir, this.db);
    this.backups = new CodepurifyFileBackups(this.rootDir, options.backupDir ?? FILE_BACKUP_CONSTANTS.defaultDirName);
    this.writer = new CodepurifyFileWriter(this.rootDir, this.db, this.reader, this.backups);
    this.rollbacker = new CodepurifyFileRollback(this.rootDir, this.db, this.backups);
    this.validator = new CodepurifyFileValidator(this.db, this.reader);
  }

  read(path: string): Promise<CodepurifyReadResult> {
    return this.reader.read(path, { hash: true });
  }

  exists(path: string): Promise<boolean> {
    return this.reader.exists(path);
  }

  info(path: string): Promise<CodepurifyFileInfo> {
    return this.reader.info(path);
  }

  writeGenerated(input: WriteGeneratedFileInput): Promise<WriteGeneratedFileResult> {
    return this.writer.writeGenerated(input);
  }

  writeManyGenerated(inputs: WriteGeneratedFileInput[]): Promise<WriteGeneratedFileResult[]> {
    return this.writer.writeManyGenerated(inputs);
  }

  async deleteGenerated(path: string): Promise<void> {
    const absolutePath = resolveInsideRoot(this.rootDir, path);
    const relativePath = relativeFromRoot(this.rootDir, absolutePath);

    try {
      await unlink(absolutePath);
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;
      if (fsError.code !== 'ENOENT') throw error;
    }

    await this.db.remove(relativePath);
  }

  async listGenerated(): Promise<CodepurifyFileRecord[]> {
    const records = await this.db.list();
    return records.filter((record) => record.kind === 'generated');
  }

  validate(): Promise<CodepurifyFileValidationResult[]> {
    return this.validator.validate();
  }

  createBackupSession(reason?: string): Promise<CodepurifyBackupSession> {
    return this.backups.createSession(reason);
  }

  rollback(sessionId: string): Promise<CodepurifyRollbackResult> {
    return this.rollbacker.rollback(sessionId);
  }

  rollbackLatest(): Promise<CodepurifyRollbackResult> {
    return this.rollbacker.rollbackLatest();
  }

  async deletePath(path: string): Promise<void> {
    const absolutePath = resolveInsideRoot(this.rootDir, path);

    await rm(absolutePath, {
      recursive: true,
      force: true,
    });
  }
}
