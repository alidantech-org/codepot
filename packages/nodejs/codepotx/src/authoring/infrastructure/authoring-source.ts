import type {
  AuthoringCompileRequest,
  AuthoringValidateRequest,
  LoadedModule,
  ResolvedSource,
} from '@/contract/index';
import { isCodepotConfig } from '../config/config';
import type { CodepotConfig } from '../config/config.types';
import type { AuthoringEngineDependencies } from '../engine/authoring-engine.types';
import type { VersionBuilder, VersionContract } from '../version/version.types';

export async function resolveAuthoringSource(
  dependencies: AuthoringEngineDependencies,
  request: AuthoringCompileRequest | AuthoringValidateRequest,
): Promise<ResolvedSource> {
  const descriptor = request.source.kind === 'local' && request.configFile
    ? { ...request.source, entry: request.configFile }
    : request.source;
  return dependencies.sources.resolve(descriptor, {
    ...(request.projectRoot ? { projectRoot: request.projectRoot } : {}),
    cache: 'cache' in request && request.cache ? request.cache : 'auto',
  });
}

export function extractAuthoringConfig(
  loaded: LoadedModule<Record<string, unknown>>,
): CodepotConfig {
  const candidate = loaded.exports['default']
    ?? loaded.exports['config']
    ?? loaded.exports['packageConfig'];
  if (isCodepotConfig(candidate)) return candidate;
  if (isVersion(candidate)) return { contracts: [candidate] };
  const contracts = Object.values(loaded.exports).filter(isVersion);
  if (contracts.length > 0) return { contracts };
  throw new Error(`No default Codepot config was exported from ${loaded.entry.path}.`);
}

function isVersion(value: unknown): value is VersionBuilder | VersionContract {
  return Boolean(
    value
    && typeof value === 'object'
    && (
      ('contract' in value
        && typeof (value as { readonly contract?: unknown }).contract === 'object')
      || ('info' in value && 'resources' in value)
    ),
  );
}
