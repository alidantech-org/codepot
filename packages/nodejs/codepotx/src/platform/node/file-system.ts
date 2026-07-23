import {
  access,
  glob as nodeGlob,
  lstat,
  mkdir,
  readFile,
  readdir,
  realpath,
  rename,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises';
import { dirname, isAbsolute, join, resolve } from 'node:path';
import type {
  DirectoryEntry,
  FileKind,
  FileStat,
  FileSystemPort,
  GlobOptions,
  PortablePath,
  RemoveOptions,
} from '@/contract/index';
import { normalizePortablePath } from '@/internal/paths/portable-path';

function fileKind(value: Awaited<ReturnType<typeof stat>>): FileKind {
  if (value.isFile()) return 'file';
  if (value.isDirectory()) return 'directory';
  if (value.isSymbolicLink()) return 'symbolicLink';
  return 'other';
}

export class NodeFileSystem implements FileSystemPort {
  async readText(path: PortablePath): Promise<string> {
    return readFile(path, 'utf8');
  }

  async readBase64(path: PortablePath): Promise<string> {
    return (await readFile(path)).toString('base64');
  }

  async writeText(path: PortablePath, content: string): Promise<void> {
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, content, 'utf8');
  }

  async writeBase64(path: PortablePath, content: string): Promise<void> {
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, Buffer.from(content, 'base64'));
  }

  async exists(path: PortablePath): Promise<boolean> {
    try {
      await access(path);
      return true;
    } catch {
      return false;
    }
  }

  async stat(path: PortablePath): Promise<FileStat> {
    const value = await lstat(path);
    return { kind: fileKind(value), size: value.size, modifiedAt: value.mtime.toISOString() };
  }

  async list(path: PortablePath): Promise<readonly DirectoryEntry[]> {
    const entries = await readdir(path, { withFileTypes: true });
    return entries.map((entry): DirectoryEntry => ({
      name: entry.name,
      path: normalizePortablePath(join(path, entry.name)),
      kind: entry.isFile()
        ? 'file'
        : entry.isDirectory()
          ? 'directory'
          : entry.isSymbolicLink()
            ? 'symbolicLink'
            : 'other',
    })).sort((left, right) => left.name.localeCompare(right.name));
  }

  async glob(
    patterns: readonly string[],
    options: GlobOptions = {},
  ): Promise<readonly PortablePath[]> {
    const cwd = options.cwd ?? process.cwd();
    const results: PortablePath[] = [];
    for await (const entry of nodeGlob([...patterns], {
      cwd,
      exclude: options.ignore ? [...options.ignore] : undefined,
    })) {
      const absolutePath = isAbsolute(entry) ? entry : resolve(cwd, entry);
      if (!options.includeDirectories && (await stat(absolutePath)).isDirectory()) continue;
      results.push(normalizePortablePath(options.absolute ? absolutePath : entry));
    }
    return [...new Set(results)].sort((left, right) => left.localeCompare(right));
  }

  async mkdir(
    path: PortablePath,
    options: { readonly recursive?: boolean } = {},
  ): Promise<void> {
    await mkdir(path, { recursive: options.recursive ?? false });
  }

  async remove(path: PortablePath, options: RemoveOptions = {}): Promise<void> {
    await rm(path, {
      recursive: options.recursive ?? false,
      force: options.force ?? false,
    });
  }

  async move(
    from: PortablePath,
    to: PortablePath,
    options: { readonly overwrite?: boolean } = {},
  ): Promise<void> {
    await mkdir(dirname(to), { recursive: true });
    if (options.overwrite && await this.exists(to)) {
      await rm(to, { recursive: true, force: true });
    }
    await rename(from, to);
  }

  async realpath(path: PortablePath): Promise<PortablePath> {
    const resolved = isAbsolute(path) ? await realpath(path) : await realpath(resolve(path));
    return normalizePortablePath(resolved);
  }
}
