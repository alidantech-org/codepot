import type { IsoTimestamp, PortablePath } from '../../protocol/common.types';

export type FileKind = 'file' | 'directory' | 'symbolicLink' | 'other';

export interface FileStat {
  readonly kind: FileKind;
  readonly size: number;
  readonly modifiedAt?: IsoTimestamp;
}

export interface DirectoryEntry {
  readonly name: string;
  readonly path: PortablePath;
  readonly kind: FileKind;
}

export interface GlobOptions {
  readonly cwd?: PortablePath;
  readonly absolute?: boolean;
  readonly includeDirectories?: boolean;
  readonly ignore?: readonly string[];
}

export interface RemoveOptions {
  readonly recursive?: boolean;
  readonly force?: boolean;
}

/** All engine filesystem access is inverted through this port. */
export interface FileSystemPort {
  readText(path: PortablePath): Promise<string>;
  readBase64(path: PortablePath): Promise<string>;
  writeText(path: PortablePath, content: string): Promise<void>;
  writeBase64(path: PortablePath, content: string): Promise<void>;
  exists(path: PortablePath): Promise<boolean>;
  stat(path: PortablePath): Promise<FileStat>;
  list(path: PortablePath): Promise<readonly DirectoryEntry[]>;
  glob(patterns: readonly string[], options?: GlobOptions): Promise<readonly PortablePath[]>;
  mkdir(path: PortablePath, options?: { readonly recursive?: boolean }): Promise<void>;
  remove(path: PortablePath, options?: RemoveOptions): Promise<void>;
  realpath(path: PortablePath): Promise<PortablePath>;
}
