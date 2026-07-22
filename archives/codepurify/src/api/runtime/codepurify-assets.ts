/**
 * Codepurify Assets
 *
 * Handles reading package-embedded starter assets.
 */

import { readFile, readdir } from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { ASSET_PATHS, INIT_ASSET_PATHS } from '@/api/constants';

const currentDir = dirname(fileURLToPath(import.meta.url));

const packageRoot = resolve(currentDir, ASSET_PATHS.distRoot);

const initAssetsRoot = join(packageRoot, ASSET_PATHS.initRoot);

export interface CodepurifyAssetFile {
  path: string;
  content: string;
}

export class CodepurifyAssets {
  async listInitFiles(dir = INIT_ASSET_PATHS.rootDir): Promise<CodepurifyAssetFile[]> {
    const root = this.getInitAssetDirectory(dir);

    return this.walkDirectory({
      absoluteRoot: root,
      absoluteDir: root,
    });
  }

  private getInitAssetDirectory(dir: string): string {
    return ASSET_PATHS.initRoot ? join(initAssetsRoot, dir) : initAssetsRoot;
  }

  private async walkDirectory(input: { absoluteRoot: string; absoluteDir: string }): Promise<CodepurifyAssetFile[]> {
    const files: CodepurifyAssetFile[] = [];
    const entries = await readdir(input.absoluteDir, {
      withFileTypes: true,
    });

    for (const entry of entries) {
      const absolutePath = join(input.absoluteDir, entry.name);

      if (entry.isDirectory()) {
        files.push(
          ...(await this.walkDirectory({
            absoluteRoot: input.absoluteRoot,
            absoluteDir: absolutePath,
          })),
        );

        continue;
      }

      if (!entry.isFile()) {
        continue;
      }

      files.push({
        path: this.toPosixPath(relative(input.absoluteRoot, absolutePath)),
        content: await readFile(absolutePath, 'utf-8'),
      });
    }

    return files;
  }

  private toPosixPath(path: string): string {
    return path.replace(/\\/g, '/');
  }
}
