import type {
  AuthoringCompileRequest,
  AuthoringCompileResult,
} from '@/contract/index';
import {
  caughtDiagnostic,
  failure,
  success,
} from '@/internal/results/operation-results';
import type { AuthoringEngineDependencies } from '../engine/authoring-engine.types';
import {
  authoringCacheKey,
  readAuthoringCache,
  writeAuthoringCache,
} from '../infrastructure/authoring-cache';
import {
  extractAuthoringConfig,
  resolveAuthoringSource,
} from '../infrastructure/authoring-source';
import { loadAuthoringArtifact } from './load-authoring-artifact';

export async function compileAuthoring(
  dependencies: AuthoringEngineDependencies,
  request: AuthoringCompileRequest,
): Promise<AuthoringCompileResult> {
  try {
    if (request.source.kind === 'artifact') {
      return loadAuthoringArtifact(dependencies, {
        source: request.source,
        verifyDigest: true,
      });
    }
    const resolved = await resolveAuthoringSource(dependencies, request);
    const cacheKey = authoringCacheKey(resolved.digest);
    if (request.cache !== 'bypass' && request.cache !== 'refresh') {
      const cached = await readAuthoringCache(dependencies, cacheKey);
      if (cached) return success(cached);
    }
    const loaded = await dependencies.modules.load<Record<string, unknown>>(
      resolved.entry,
      {
        projectRoot: resolved.root,
        ...(request.tsconfigFile ? { tsconfigFile: request.tsconfigFile } : {}),
        cache: request.cache !== 'bypass',
      },
    );
    const config = extractAuthoringConfig(loaded);
    const compiled = await dependencies.compiler.compile({
      config,
      source: resolved,
      ...(request.includeDebugMetadata === undefined
        ? {}
        : { includeDebugMetadata: request.includeDebugMetadata }),
    });
    if (request.cache !== 'bypass') {
      await writeAuthoringCache(dependencies, cacheKey, compiled.artifact);
    }
    return compiled.diagnostics.some((item) => item.severity === 'error')
      ? failure(compiled.diagnostics)
      : success(compiled.artifact, compiled.diagnostics);
  } catch (caught) {
    return failure([
      caughtDiagnostic('authoring', 'AUTHORING_COMPILE_FAILED', caught),
    ]);
  }
}
