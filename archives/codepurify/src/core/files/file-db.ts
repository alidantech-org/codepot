import { dirname, resolve } from 'node:path';
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises';

import type { CodepurifyFileRecord, CodepurifyFilesDb } from './file-types';
import { FILE_DB_CONSTANTS, createTempFilePath, formatDbJson, createEmptyFileDb } from './file.constants';

export class CodepurifyFileDb {
  readonly dbPath: string;

  constructor(rootDir: string, dbPath?: string) {
    this.dbPath = resolve(rootDir, dbPath ?? FILE_DB_CONSTANTS.defaultFileName);
  }

  createEmpty(): CodepurifyFilesDb {
    return createEmptyFileDb();
  }

  async load(): Promise<CodepurifyFilesDb> {
    try {
      const content = await readFile(this.dbPath, 'utf-8');
      const parsed = JSON.parse(content) as CodepurifyFilesDb;

      if (
        parsed.version !== FILE_DB_CONSTANTS.version ||
        parsed.generator !== FILE_DB_CONSTANTS.generator ||
        !Array.isArray(parsed.records)
      ) {
        throw new Error('Invalid Codepurify file DB structure.');
      }

      return parsed;
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;

      if (fsError.code === 'ENOENT') {
        return this.createEmpty();
      }

      throw error;
    }
  }

  async save(db: CodepurifyFilesDb): Promise<void> {
    const nextDb: CodepurifyFilesDb = {
      ...db,
      updatedAt: new Date().toISOString(),
    };

    await mkdir(dirname(this.dbPath), { recursive: true });

    const tempPath = createTempFilePath(this.dbPath);
    await writeFile(tempPath, formatDbJson(nextDb), 'utf-8');
    await rename(tempPath, this.dbPath);
  }

  async get(path: string): Promise<CodepurifyFileRecord | null> {
    const db = await this.load();
    return db.records.find((record) => record.path === path) ?? null;
  }

  async list(): Promise<CodepurifyFileRecord[]> {
    const db = await this.load();
    return db.records;
  }

  async upsert(record: CodepurifyFileRecord): Promise<void> {
    const db = await this.load();

    const existing = db.records.find((item) => item.path === record.path);
    const createdAt = existing?.createdAt ?? record.createdAt;

    db.records = db.records.filter((item) => item.path !== record.path);
    db.records.push({
      ...record,
      createdAt,
      updatedAt: new Date().toISOString(),
    });

    await this.save(db);
  }

  async remove(path: string): Promise<void> {
    const db = await this.load();
    const nextRecords = db.records.filter((record) => record.path !== path);

    if (nextRecords.length === db.records.length) {
      return;
    }

    await this.save({
      ...db,
      records: nextRecords,
    });
  }

  async clear(): Promise<void> {
    await this.save(this.createEmpty());
  }
}
