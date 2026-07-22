import { readFile, stat } from 'node:fs/promises';

import { hashContent } from './file-hash';
import { relativeFromRoot, resolveInsideRoot } from './file-paths';
import type { CodepurifyFileInfo, CodepurifyReadResult } from './file-types';
import type { CodepurifyFileDb } from './file-db';

export class CodepurifyFileReader {
  constructor(
    private readonly rootDir: string,
    private readonly db: CodepurifyFileDb,
  ) {}

  async exists(path: string): Promise<boolean> {
    const absolutePath = resolveInsideRoot(this.rootDir, path);

    try {
      await stat(absolutePath);
      return true;
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;
      if (fsError.code === 'ENOENT') return false;
      throw error;
    }
  }

  async read(path: string, options: { hash?: boolean } = {}): Promise<CodepurifyReadResult> {
    const absolutePath = resolveInsideRoot(this.rootDir, path);
    const relativePath = relativeFromRoot(this.rootDir, absolutePath);
    const record = await this.db.get(relativePath);

    try {
      const content = await readFile(absolutePath, 'utf-8');

      return {
        path: relativePath,
        absolutePath,
        exists: true,
        content,
        hash: options.hash ? hashContent(content) : undefined,
        sizeBytes: Buffer.byteLength(content),
        record,
      };
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;

      if (fsError.code === 'ENOENT') {
        return {
          path: relativePath,
          absolutePath,
          exists: false,
          content: '',
          sizeBytes: 0,
          record,
        };
      }

      throw error;
    }
  }

  async info(path: string): Promise<CodepurifyFileInfo> {
    const absolutePath = resolveInsideRoot(this.rootDir, path);
    const relativePath = relativeFromRoot(this.rootDir, absolutePath);
    const record = await this.db.get(relativePath);

    try {
      const info = await stat(absolutePath);

      return {
        path: relativePath,
        absolutePath,
        exists: true,
        sizeBytes: info.size,
        record,
      };
    } catch (error) {
      const fsError = error as NodeJS.ErrnoException;

      if (fsError.code === 'ENOENT') {
        return {
          path: relativePath,
          absolutePath,
          exists: false,
          sizeBytes: 0,
          record,
        };
      }

      throw error;
    }
  }
}
