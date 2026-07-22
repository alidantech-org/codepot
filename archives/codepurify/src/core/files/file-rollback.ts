import { copyFile, unlink } from 'node:fs/promises';

import { relativeFromRoot } from './file-paths';
import type { CodepurifyFileBackups } from './file-backups';
import type { CodepurifyFileDb } from './file-db';
import type { CodepurifyRollbackResult } from './file-types';

export class CodepurifyFileRollback {
  constructor(
    private readonly rootDir: string,
    private readonly db: CodepurifyFileDb,
    private readonly backups: CodepurifyFileBackups,
  ) {}

  async rollback(sessionId: string): Promise<CodepurifyRollbackResult> {
    const session = await this.backups.loadSession(sessionId);

    if (!session) {
      throw new Error(`Backup session not found: ${sessionId}`);
    }

    const result: CodepurifyRollbackResult = {
      sessionId,
      restoredFiles: [],
      deletedFiles: [],
      skippedFiles: [],
    };

    for (const record of session.records) {
      const relativePath = relativeFromRoot(this.rootDir, record.originalPath);

      if (record.existed && record.backupPath) {
        await copyFile(record.backupPath, record.originalPath);
        await this.db.remove(relativePath);
        result.restoredFiles.push(relativePath);
        continue;
      }

      if (!record.existed) {
        try {
          await unlink(record.originalPath);
          result.deletedFiles.push(relativePath);
        } catch (error) {
          const fsError = error as NodeJS.ErrnoException;

          if (fsError.code === 'ENOENT') {
            result.skippedFiles.push(relativePath);
          } else {
            throw error;
          }
        }

        await this.db.remove(relativePath);
        continue;
      }

      result.skippedFiles.push(relativePath);
    }

    return result;
  }

  async rollbackLatest(): Promise<CodepurifyRollbackResult> {
    const sessions = await this.backups.listSessions();

    if (sessions.length === 0) {
      throw new Error('No Codepurify backup sessions found.');
    }

    return this.rollback(sessions[0].id);
  }
}
