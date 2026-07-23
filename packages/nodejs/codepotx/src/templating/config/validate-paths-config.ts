import type { Diagnostic } from '@/contract/index';
import type { NormalizedPathsConfig } from './normalized-paths-config';
import { unsafeTemplatePath } from '../paths/template-paths';

export function validatePathsConfig(
  config: NormalizedPathsConfig,
): readonly Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  for (const root of [...config.write.protectedRoots, ...config.write.cleanRoots]) {
    if (unsafeTemplatePath(root)) diagnostics.push({
      code: 'TEMPLATING_UNSAFE_ROOT',
      severity: 'error',
      layer: 'templating',
      message: `Unsafe template write root: ${root}`,
    });
  }
  for (const [name, folder] of Object.entries(config.folders)) {
    if ((folder.mode === 'each' || folder.mode === 'group') && !folder.select) {
      diagnostics.push({
        code: 'TEMPLATING_SELECTION_REQUIRED',
        severity: 'error',
        layer: 'templating',
        message: `Template folder "${name}" uses mode ${folder.mode} and requires select.`,
      });
    }
  }
  return diagnostics;
}
