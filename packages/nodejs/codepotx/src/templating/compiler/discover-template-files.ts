import type { ResolvedSource } from '@/contract/index';
import type { NormalizedPathsConfig } from '../config/normalized-paths-config';
import type { TemplatingDependencies } from '../templating.types';

export async function discoverTemplateFiles(
  dependencies: TemplatingDependencies,
  source: ResolvedSource,
  config: NormalizedPathsConfig,
): Promise<readonly string[]> {
  const paths = await dependencies.files.glob(
    config.includeHidden ? ['**/*', '**/.*', '**/.*/**/*'] : ['**/*'],
    {
      cwd: source.root,
      absolute: true,
      ignore: config.ignore,
    },
  );
  return [...new Set(paths)].sort();
}
