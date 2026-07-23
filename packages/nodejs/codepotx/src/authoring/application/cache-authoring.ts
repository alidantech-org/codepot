import type {
  AuthoringCacheRequest,
  AuthoringCacheResult,
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

export async function cacheAuthoring(
  dependencies: AuthoringEngineDependencies,
  request: AuthoringCacheRequest,
): Promise<AuthoringCacheResult> {
  try {
    const resolved = await dependencies.sources.resolve(request.source);
    const key = authoringCacheKey(resolved.digest);
    if (request.operation === 'invalidate') {
      await dependencies.cache.delete(key);
      return success(null);
    }
    if (request.operation === 'read') {
      return success(await readAuthoringCache(dependencies, key));
    }
    if (!request.artifact) {
      return failure([{
        code: 'AUTHORING_CACHE_ARTIFACT_REQUIRED',
        severity: 'error',
        layer: 'authoring',
        message: 'Cache write requires an authoring artifact.',
      }]);
    }
    await writeAuthoringCache(dependencies, key, request.artifact);
    return success(request.artifact);
  } catch (caught) {
    return failure([
      caughtDiagnostic('authoring', 'AUTHORING_CACHE_FAILED', caught),
    ]);
  }
}
