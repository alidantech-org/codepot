import type {
  TemplateContextRequest,
  TemplateContextResult,
} from '@/contract/index';
import { success } from '@/internal/results/operation-results';
import { buildTemplateContext } from '../template-context';

export async function createCompiledTemplateContext(
  request: TemplateContextRequest,
): Promise<TemplateContextResult> {
  return success(buildTemplateContext(request));
}
