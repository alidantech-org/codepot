import type {
  AuthoringArtifactLoadRequest,
  AuthoringArtifactLoadResult,
  AuthoringCacheRequest,
  AuthoringCacheResult,
  AuthoringCompileRequest,
  AuthoringCompileResult,
  AuthoringInspectRequest,
  AuthoringInspectResult,
  AuthoringValidateRequest,
  AuthoringValidateResult,
} from '../../operations/authoring/index';

export interface AuthoringPort {
  compile(request: AuthoringCompileRequest): Promise<AuthoringCompileResult>;
  validate(request: AuthoringValidateRequest): Promise<AuthoringValidateResult>;
  inspect(request: AuthoringInspectRequest): Promise<AuthoringInspectResult>;
  loadArtifact(request: AuthoringArtifactLoadRequest): Promise<AuthoringArtifactLoadResult>;
  cache(request: AuthoringCacheRequest): Promise<AuthoringCacheResult>;
}
