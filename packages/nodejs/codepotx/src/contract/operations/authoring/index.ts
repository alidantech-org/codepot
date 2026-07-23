import type { CompiledAuthoringArtifact } from '../../artifacts/authoring/index';
import type { OperationResult, ValidationResult } from '../../diagnostics/index';
import type { PortablePath } from '../../protocol/common.types';
import type { SourceDescriptor } from '../../sources/source.types';

export type CacheMode = 'auto' | 'bypass' | 'refresh';

export interface AuthoringCompileRequest {
  readonly source: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly configFile?: PortablePath;
  readonly tsconfigFile?: PortablePath;
  readonly cache?: CacheMode;
  readonly typecheck?: boolean;
  readonly includeDebugMetadata?: boolean;
}

export interface AuthoringValidateRequest {
  readonly source: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly configFile?: PortablePath;
  readonly tsconfigFile?: PortablePath;
  readonly typecheck?: boolean;
}

export interface AuthoringInspectRequest extends AuthoringCompileRequest {
  readonly format?: 'object' | 'json';
  readonly pretty?: boolean;
}

export interface AuthoringArtifactLoadRequest {
  readonly source: SourceDescriptor;
  readonly verifyDigest?: boolean;
}

export interface AuthoringCacheRequest {
  readonly source: SourceDescriptor;
  readonly operation: 'read' | 'write' | 'invalidate';
  readonly artifact?: CompiledAuthoringArtifact;
}

export type AuthoringCompileResult = OperationResult<CompiledAuthoringArtifact>;
export type AuthoringValidateResult = OperationResult<ValidationResult>;
export type AuthoringInspectResult = OperationResult<CompiledAuthoringArtifact | string>;
export type AuthoringArtifactLoadResult = OperationResult<CompiledAuthoringArtifact>;
export type AuthoringCacheResult = OperationResult<CompiledAuthoringArtifact | null>;
