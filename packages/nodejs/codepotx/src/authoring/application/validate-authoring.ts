import type {
  AuthoringValidateRequest,
  AuthoringValidateResult,
} from '@/contract/index';
import { success } from '@/internal/results/operation-results';
import type { AuthoringEngineDependencies } from '../engine/authoring-engine.types';
import { compileAuthoring } from './compile-authoring';

export async function validateAuthoring(
  dependencies: AuthoringEngineDependencies,
  request: AuthoringValidateRequest,
): Promise<AuthoringValidateResult> {
  const result = await compileAuthoring(dependencies, {
    ...request,
    cache: 'bypass',
  });
  if (!result.success) return result;
  const diagnostics = result.diagnostics;
  return success({
    valid: !diagnostics.some((item) => item.severity === 'error'),
    diagnostics,
  }, diagnostics);
}
