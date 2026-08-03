import { dirname, resolve } from 'node:path';
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises';

import type { codepotFileRecord, codepotFilesDb } from './file-types';
import { FILE_DB_CONSTANTS, createTempFilePath, formatDbJson, createEmptyFileDb } from './file.constants';

export class codepotFileDb {
  readonly dbPath: string;

  constructor(rootDir: string, dbPath?: string) {
    this.dbPath = resolve(rootDir, dbPath ?? FILE_DB_CONSTANTS.defaultFileName);
  }

  createEmpty(): codepotFilesDb {
    return createEmptyFileDb();
  }

  async load(): Promise<codepotFilesDb> {
    try {
      const content = await readFile(this.dbPath, 'utf-8');
      const parsed = JSON.parse(content) as codepotFilesDb;

      if (
        parsed.version !== FILE_DB_CONSTANTS.version ||
        parsed.generator !== FILE_DB_CONSTANTS.generator ||
        !Array.isArray(parsed.records)
      ) {
        throw new Error('Invalid codepot file DB structure.');
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

  async save(db: codepotFilesDb): Promise<void> {
    const nextDb: codepotFilesDb = {
      ...db,
      updatedAt: new Date().toISOString(),
    };

    await mkdir(dirname(this.dbPath), { recursive: true });

    const tempPath = createTempFilePath(this.dbPath);
    await writeFile(tempPath, formatDbJson(nextDb), 'utf-8');
    await rename(tempPath, this.dbPath);
  }

  async get(path: string): Promise<codepotFileRecord | null> {
    const db = await this.load();
    return db.records.find((record) => record.path === path) ?? null;
  }

  async list(): Promise<codepotFileRecord[]> {
    const db = await this.load();
    return db.records;
  }

  async upsert(record: codepotFileRecord): Promise<void> {
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
