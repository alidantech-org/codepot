import { unlink, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

import { codepotFileBackups } from './file-backups';
import { codepotFileDb } from './file-db';
import { codepotFileReader } from './file-reader';
import { codepotFileRollback } from './file-rollback';
import { codepotFileValidator } from './file-validator';
import { codepotFileWriter } from './file-writer';
import { relativeFromRoot, resolveInsideRoot } from './file-paths';
import { FILE_DB_CONSTANTS, FILE_BACKUP_CONSTANTS } from './file.constants';

import type {
  codepotBackupSession,
  codepotFileInfo,
  codepotFileRecord,
  codepotFilesOptions,
  codepotFileValidationResult,
  codepotReadResult,
  codepotRollbackResult,
  WriteGeneratedFileInput,
  WriteGeneratedFileResult,
} from './file-types';

/**
 * One public file-management API for codepot.
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
export class codepotFiles {
  readonly rootDir: string;

  readonly db: codepotFileDb;
  readonly reader: codepotFileReader;
  readonly backups: codepotFileBackups;
  readonly writer: codepotFileWriter;
  readonly rollbacker: codepotFileRollback;
  readonly validator: codepotFileValidator;

  constructor(options: codepotFilesOptions) {
    this.rootDir = resolve(options.rootDir);

    this.db = new codepotFileDb(this.rootDir, options.dbPath ?? FILE_DB_CONSTANTS.defaultFileName);
    this.reader = new codepotFileReader(this.rootDir, this.db);
    this.backups = new codepotFileBackups(this.rootDir, options.backupDir ?? FILE_BACKUP_CONSTANTS.defaultDirName);
    this.writer = new codepotFileWriter(this.rootDir, this.db, this.reader, this.backups);
    this.rollbacker = new codepotFileRollback(this.rootDir, this.db, this.backups);
    this.validator = new codepotFileValidator(this.db, this.reader);
  }

  read(path: string): Promise<codepotReadResult> {
    return this.reader.read(path, { hash: true });
  }

  exists(path: string): Promise<boolean> {
    return this.reader.exists(path);
  }

  info(path: string): Promise<codepotFileInfo> {
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

  async listGenerated(): Promise<codepotFileRecord[]> {
    const records = await this.db.list();
    return records.filter((record) => record.kind === 'generated');
  }

  validate(): Promise<codepotFileValidationResult[]> {
    return this.validator.validate();
  }

  createBackupSession(reason?: string): Promise<codepotBackupSession> {
    return this.backups.createSession(reason);
  }

  rollback(sessionId: string): Promise<codepotRollbackResult> {
    return this.rollbacker.rollback(sessionId);
  }

  rollbackLatest(): Promise<codepotRollbackResult> {
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
