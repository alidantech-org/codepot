import type {
  TemplatingValidateRequest,
  TemplatingValidateResult,
} from '@/contract/index';
import { success } from '@/internal/results/operation-results';
import type { TemplatingDependencies } from '../templating.types';
import { compileTemplatePack } from './compile-template-pack';

export async function validateTemplatePack(
  dependencies: TemplatingDependencies,
  request: TemplatingValidateRequest,
): Promise<TemplatingValidateResult> {
  const result = await compileTemplatePack(dependencies, {
    ...request,
    cache: 'bypass',
  });
  if (!result.success) return result;
  return success({
    valid: result.diagnostics.every((item) => item.severity !== 'error'),
    diagnostics: result.diagnostics,
  }, result.diagnostics);
}
