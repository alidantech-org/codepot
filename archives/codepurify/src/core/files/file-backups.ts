import { copyFile, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';

import { FILE_BACKUP_CONSTANTS, createBackupSessionId, formatBackupSessionJson } from './file.constants';
import { hashContent } from './file-hash';
import { relativeFromRoot, resolveInsideRoot } from './file-paths';
import type { CodepurifyBackupRecord, CodepurifyBackupSession } from './file-types';

export class CodepurifyFileBackups {
  readonly backupDir: string;

  constructor(
    private readonly rootDir: string,
    backupDir?: string,
  ) {
    this.backupDir = resolve(rootDir, backupDir ?? FILE_BACKUP_CONSTANTS.defaultDirName);
  }

  async createSession(reason?: string): Promise<CodepurifyBackupSession> {
    const session: CodepurifyBackupSession = {
      id: createBackupSessionId(),
      reason,
      createdAt: new Date().toISOString(),
      records: [],
    };

    await this.saveSession(session);

    return session;
  }

  async backupFile(session: CodepurifyBackupSession, path: string): Promise<CodepurifyBackupRecord> {
    const absolutePath = resolveInsideRoot(this.rootDir, path);
    const relativePath = relativeFromRoot(this.rootDir, absolutePath);

    let content: Buffer | null = null;

    try {
      content = await readFile(absolutePath);
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;

      if (fsError.code !== 'ENOENT') {
        throw error;
      }
    }

    const record: CodepurifyBackupRecord = {
      originalPath: absolutePath,
      backupPath: null,
      existed: Boolean(content),
      hash: content ? hashContent(content) : undefined,
      sizeBytes: content?.byteLength,
    };

    if (content) {
      const backupPath = join(this.backupDir, session.id, relativePath);
      await mkdir(dirname(backupPath), { recursive: true });
      await copyFile(absolutePath, backupPath);
      record.backupPath = backupPath;
    }

    session.records = session.records.filter((item) => item.originalPath !== record.originalPath);
    session.records.push(record);

    await this.saveSession(session);

    return record;
  }

  async saveSession(session: CodepurifyBackupSession): Promise<void> {
    const sessionPath = this.getSessionPath(session.id);
    await mkdir(dirname(sessionPath), { recursive: true });
    await writeFile(sessionPath, formatBackupSessionJson(session), 'utf-8');
  }

  async loadSession(sessionId: string): Promise<CodepurifyBackupSession | null> {
    try {
      const content = await readFile(this.getSessionPath(sessionId), 'utf-8');
      return JSON.parse(content) as CodepurifyBackupSession;
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;
      if (fsError.code === 'ENOENT') return null;
      throw error;
    }
  }

  async listSessions(): Promise<CodepurifyBackupSession[]> {
    try {
      const entries = await readdir(this.backupDir, { withFileTypes: true });
      const sessions: CodepurifyBackupSession[] = [];

      for (const entry of entries) {
        if (!entry.isDirectory()) continue;

        const session = await this.loadSession(entry.name);
        if (session) sessions.push(session);
      }

      return sessions.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;
      if (fsError.code === 'ENOENT') return [];
      throw error;
    }
  }

  private getSessionPath(sessionId: string): string {
    return join(this.backupDir, sessionId, FILE_BACKUP_CONSTANTS.sessionFileName);
  }
}
