import type {
  FileWriteOutcome,
  VirtualFile,
} from '../../artifacts/generation/index';
import type {
  FileCompareMode,
  FileLifecycleMode,
} from '../../artifacts/templating/index';
import type { ContentDigest, PortablePath } from '../../protocol/common.types';

export interface CompareFileRequest {
  readonly path: PortablePath;
  readonly content: VirtualFile['content'];
  readonly compareMode: FileCompareMode;
}

export interface CompareFileResult {
  readonly exists: boolean;
  readonly changed: boolean;
  readonly previousDigest?: ContentDigest;
  readonly nextDigest: ContentDigest;
}

export interface WriteFileRequest extends CompareFileRequest {
  readonly lifecycle: FileLifecycleMode;
  readonly atomic?: boolean;
  readonly dryRun?: boolean;
}

export interface WriteBatchRequest {
  readonly files: readonly VirtualFile[];
  readonly root: PortablePath;
  readonly atomic?: boolean;
  readonly dryRun?: boolean;
}

/** Changed-aware writer used by generation after in-memory rendering. */
export interface FileWriterPort {
  compare(request: CompareFileRequest): Promise<CompareFileResult>;
  write(request: WriteFileRequest): Promise<FileWriteOutcome>;
  writeBatch(request: WriteBatchRequest): Promise<readonly FileWriteOutcome[]>;
}
