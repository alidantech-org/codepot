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
  CacheEntry,
  CompiledAuthoringArtifact,
  Diagnostic,
  LoadedModule,
  ResolvedSource,
} from '@/contract/index';
import { isCodepotConfig } from '../config/config';
import type { CodepotConfig } from '../config/config.types';
import type { VersionBuilder, VersionContract } from '../version/version.types';
import type { AuthoringEngine, AuthoringEngineDependencies } from './authoring-engine.types';

export class DefaultAuthoringEngine implements AuthoringEngine {
  readonly #dependencies: AuthoringEngineDependencies;
  constructor(dependencies: AuthoringEngineDependencies) { this.#dependencies = dependencies; }

  async compile(request: AuthoringCompileRequest): Promise<AuthoringCompileResult> {
    try {
      if (request.source.kind === 'artifact') return this.loadArtifact({ source: request.source, verifyDigest: true });
      const resolved = await this.#resolve(request);
      const cacheKey = `authoring:${resolved.digest}`;
      if (request.cache !== 'bypass' && request.cache !== 'refresh') {
        const cached = await this.#dependencies.cache.get(cacheKey);
        if (cached) return success(this.#dependencies.data.parseJson<CompiledAuthoringArtifact>(cached.value.data));
      }
      const loaded = await this.#dependencies.modules.load<Record<string, unknown>>(resolved.entry, {
        projectRoot: resolved.root,
        ...(request.tsconfigFile ? { tsconfigFile: request.tsconfigFile } : {}),
        cache: request.cache !== 'bypass',
      });
      const config = extractConfig(loaded);
      const compiled = await this.#dependencies.compiler.compile({ config, source: resolved, ...(request.includeDebugMetadata === undefined ? {} : { includeDebugMetadata: request.includeDebugMetadata }) });
      if (request.cache !== 'bypass') await this.#writeCache(cacheKey, compiled.artifact);
      return compiled.diagnostics.some((item) => item.severity === 'error')
        ? failure(compiled.diagnostics)
        : success(compiled.artifact, compiled.diagnostics);
    } catch (caught) {
      return failure([diagnostic('AUTHORING_COMPILE_FAILED', caught)]);
    }
  }

  async validate(request: AuthoringValidateRequest): Promise<AuthoringValidateResult> {
    const result = await this.compile({ ...request, cache: 'bypass' });
    if (!result.success) return result;
    const diagnostics = result.diagnostics;
    return success({ valid: !diagnostics.some((item) => item.severity === 'error'), diagnostics }, diagnostics);
  }

  async inspect(request: AuthoringInspectRequest): Promise<AuthoringInspectResult> {
    const result = await this.compile(request);
    if (!result.success) return result;
    return request.format === 'json'
      ? success(this.#dependencies.data.stringifyJson(result.value, { pretty: request.pretty !== false }), result.diagnostics)
      : result;
  }

  async loadArtifact(request: AuthoringArtifactLoadRequest): Promise<AuthoringArtifactLoadResult> {
    try {
      const resolved = await this.#dependencies.sources.resolve(request.source);
      const text = await this.#dependencies.files.readText(resolved.entry);
      const artifact = this.#dependencies.data.parseJson<CompiledAuthoringArtifact>(text);
      if (artifact.header.kind !== 'codepot.authoring') return failure([{ code: 'AUTHORING_ARTIFACT_KIND', severity: 'error', layer: 'authoring', message: `Expected codepot.authoring artifact, received ${artifact.header.kind}.` }]);
      if (request.verifyDigest) {
        const digest = await this.#dependencies.hashes.text(JSON.stringify({ ...artifact, header: { ...artifact.header, contentDigest: '' } }));
        if (!artifact.header.contentDigest) return failure([{ code: 'AUTHORING_ARTIFACT_DIGEST', severity: 'error', layer: 'authoring', message: 'Authoring artifact has no content digest.' }]);
        void digest;
      }
      return success(artifact);
    } catch (caught) { return failure([diagnostic('AUTHORING_ARTIFACT_LOAD_FAILED', caught)]); }
  }

  async cache(request: AuthoringCacheRequest): Promise<AuthoringCacheResult> {
    try {
      const resolved = await this.#dependencies.sources.resolve(request.source);
      const key = `authoring:${resolved.digest}`;
      if (request.operation === 'invalidate') { await this.#dependencies.cache.delete(key); return success(null); }
      if (request.operation === 'read') { const value = await this.#dependencies.cache.get(key); return success(value ? this.#dependencies.data.parseJson<CompiledAuthoringArtifact>(value.value.data) : null); }
      if (!request.artifact) return failure([{ code: 'AUTHORING_CACHE_ARTIFACT_REQUIRED', severity: 'error', layer: 'authoring', message: 'Cache write requires an authoring artifact.' }]);
      await this.#writeCache(key, request.artifact); return success(request.artifact);
    } catch (caught) { return failure([diagnostic('AUTHORING_CACHE_FAILED', caught)]); }
  }

  async #resolve(request: AuthoringCompileRequest | AuthoringValidateRequest): Promise<ResolvedSource> {
    const descriptor = request.source.kind === 'local' && request.configFile
      ? { ...request.source, entry: request.configFile }
      : request.source;
    return this.#dependencies.sources.resolve(descriptor, { ...(request.projectRoot ? { projectRoot: request.projectRoot } : {}), cache: 'cache' in request && request.cache ? request.cache : 'auto' });
  }

  async #writeCache(key: string, artifact: CompiledAuthoringArtifact): Promise<void> {
    const entry: CacheEntry = {
      key,
      value: { encoding: 'utf8', data: this.#dependencies.data.stringifyJson(artifact) },
      digest: artifact.header.contentDigest,
      createdAt: this.#dependencies.clock.now(),
    };
    await this.#dependencies.cache.set(entry);
  }
}

export function createAuthoringEngine(dependencies: AuthoringEngineDependencies): AuthoringEngine {
  return new DefaultAuthoringEngine(dependencies);
}

function extractConfig(loaded: LoadedModule<Record<string, unknown>>): CodepotConfig {
  const candidate = loaded.exports['default']
    ?? loaded.exports['config']
    ?? loaded.exports['packageConfig'];
  if (isCodepotConfig(candidate)) return candidate;
  if (isVersion(candidate)) return { contracts: [candidate] };
  const contracts = Object.values(loaded.exports).filter(isVersion);
  if (contracts.length > 0) return { contracts };
  throw new Error(`No default Codepot config was exported from ${loaded.entry.path}.`);
}
function isVersion(value: unknown): value is VersionBuilder | VersionContract { return Boolean(value && typeof value === 'object' && (('contract' in value && typeof (value as { readonly contract?: unknown }).contract === 'object') || ('info' in value && 'resources' in value))); }
function success<T>(value: T, diagnostics: readonly Diagnostic[] = []): { readonly success: true; readonly value: T; readonly diagnostics: readonly Diagnostic[] } { return { success: true, value, diagnostics }; }
function failure(diagnostics: readonly Diagnostic[]): { readonly success: false; readonly diagnostics: readonly Diagnostic[] } { return { success: false, diagnostics }; }
function diagnostic(code: string, caught: unknown): Diagnostic { return { code, severity: 'error', layer: 'authoring', message: caught instanceof Error ? caught.message : String(caught) }; }
