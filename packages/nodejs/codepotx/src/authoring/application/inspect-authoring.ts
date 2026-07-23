import type {
  AuthoringInspectRequest,
  AuthoringInspectResult,
} from '@/contract/index';
import { success } from '@/internal/results/operation-results';
import type { AuthoringEngineDependencies } from '../engine/authoring-engine.types';
import { compileAuthoring } from './compile-authoring';

export async function inspectAuthoring(
  dependencies: AuthoringEngineDependencies,
  request: AuthoringInspectRequest,
): Promise<AuthoringInspectResult> {
  const result = await compileAuthoring(dependencies, request);
  if (!result.success) return result;
  return request.format === 'json'
    ? success(
        dependencies.data.stringifyJson(result.value, {
          pretty: request.pretty !== false,
        }),
        result.diagnostics,
      )
    : result;
}
