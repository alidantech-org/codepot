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
} from '@/contract/index';
import { cacheAuthoring } from '../application/cache-authoring';
import { compileAuthoring } from '../application/compile-authoring';
import { inspectAuthoring } from '../application/inspect-authoring';
import { loadAuthoringArtifact } from '../application/load-authoring-artifact';
import { validateAuthoring } from '../application/validate-authoring';
import type {
  AuthoringEngine,
  AuthoringEngineDependencies,
} from './authoring-engine.types';

export class DefaultAuthoringEngine implements AuthoringEngine {
  readonly #dependencies: AuthoringEngineDependencies;

  constructor(dependencies: AuthoringEngineDependencies) {
    this.#dependencies = dependencies;
  }

  compile(request: AuthoringCompileRequest): Promise<AuthoringCompileResult> {
    return compileAuthoring(this.#dependencies, request);
  }

  validate(request: AuthoringValidateRequest): Promise<AuthoringValidateResult> {
    return validateAuthoring(this.#dependencies, request);
  }

  inspect(request: AuthoringInspectRequest): Promise<AuthoringInspectResult> {
    return inspectAuthoring(this.#dependencies, request);
  }

  loadArtifact(
    request: AuthoringArtifactLoadRequest,
  ): Promise<AuthoringArtifactLoadResult> {
    return loadAuthoringArtifact(this.#dependencies, request);
  }

  cache(request: AuthoringCacheRequest): Promise<AuthoringCacheResult> {
    return cacheAuthoring(this.#dependencies, request);
  }
}

export function createAuthoringEngine(
  dependencies: AuthoringEngineDependencies,
): AuthoringEngine {
  return new DefaultAuthoringEngine(dependencies);
}
