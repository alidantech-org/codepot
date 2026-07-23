import type {
  CacheEntry,
  CompiledAuthoringArtifact,
} from '@/contract/index';
import type { AuthoringEngineDependencies } from '../engine/authoring-engine.types';

export function authoringCacheKey(sourceDigest: string): string {
  return `authoring:${sourceDigest}`;
}

export async function readAuthoringCache(
  dependencies: AuthoringEngineDependencies,
  key: string,
): Promise<CompiledAuthoringArtifact | null> {
  const cached = await dependencies.cache.get(key);
  return cached
    ? dependencies.data.parseJson<CompiledAuthoringArtifact>(cached.value.data)
    : null;
}

export async function writeAuthoringCache(
  dependencies: AuthoringEngineDependencies,
  key: string,
  artifact: CompiledAuthoringArtifact,
): Promise<void> {
  const entry: CacheEntry = {
    key,
    value: {
      encoding: 'utf8',
      data: dependencies.data.stringifyJson(artifact),
    },
    digest: artifact.header.contentDigest,
    createdAt: dependencies.clock.now(),
  };
  await dependencies.cache.set(entry);
}
