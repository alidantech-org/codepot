import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

export interface WriteTextFileInput {
  readonly path: string;
  readonly content: string;
}

export interface FileSystemManager {
  ensureDirectory(path: string): Promise<void>;
  writeTextFile(input: WriteTextFileInput): Promise<void>;
  joinPath(...parts: readonly string[]): string;
  toPosixPath(path: string): string;
}

export function createFileSystemManager(): FileSystemManager {
  return {
    async ensureDirectory(path: string): Promise<void> {
      await mkdir(path, { recursive: true });
    },

    async writeTextFile(input: WriteTextFileInput): Promise<void> {
      await mkdir(dirname(input.path), { recursive: true });
      await writeFile(input.path, input.content, 'utf8');
    },

    joinPath(...parts: readonly string[]): string {
      return join(...parts);
    },

    toPosixPath(path: string): string {
      return path.replace(/\\/g, '/');
    },
  };
}
