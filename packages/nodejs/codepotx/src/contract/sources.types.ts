import type {
  CodepotId,
  ContentDigest,
  JsonObject,
  PortablePath,
  UriString,
} from './common.types';

/** One-based source position for portable diagnostics. */
export interface SourcePosition {
  readonly line: number;
  readonly column: number;
  readonly offset?: number;
}

/** A half-open source range from start to end. */
export interface SourceRange {
  readonly start: SourcePosition;
  readonly end: SourcePosition;
}

/** A source file referenced by an artifact or diagnostic. */
export interface SourceFileReference {
  readonly id: CodepotId;
  readonly uri: UriString;
  readonly path: PortablePath;
  readonly rootRelativePath?: PortablePath;
  readonly language?: string;
  readonly digest?: ContentDigest;
}

/** A source location that remains portable across frontends. */
export interface SourceLocation {
  readonly file: SourceFileReference;
  readonly range?: SourceRange;
}

export interface LocalSourceDescriptor {
  readonly kind: 'local';
  readonly path: PortablePath;
  readonly entry?: PortablePath;
}

export interface PackageSourceDescriptor {
  readonly kind: 'package';
  readonly package: string;
  readonly version?: string;
  readonly path?: PortablePath;
  readonly entry?: PortablePath;
}

export interface GitSourceDescriptor {
  readonly kind: 'git';
  readonly repository: string;
  readonly ref?: string;
  readonly path?: PortablePath;
  readonly entry?: PortablePath;
}

export interface ArtifactSourceDescriptor {
  readonly kind: 'artifact';
  readonly path: PortablePath;
}

export interface MemorySourceDescriptor {
  readonly kind: 'memory';
  readonly id: CodepotId;
  readonly entry?: PortablePath;
}

/** Supported source locations shared by authoring, templating, and generation. */
export type SourceDescriptor =
  | LocalSourceDescriptor
  | PackageSourceDescriptor
  | GitSourceDescriptor
  | ArtifactSourceDescriptor
  | MemorySourceDescriptor;

/** A source after a platform source resolver has made it locally addressable. */
export interface ResolvedSource {
  readonly id: CodepotId;
  readonly descriptor: SourceDescriptor;
  readonly root: PortablePath;
  readonly entry: PortablePath;
  readonly digest: ContentDigest;
  readonly files: readonly SourceFileReference[];
  readonly metadata?: JsonObject;
}
