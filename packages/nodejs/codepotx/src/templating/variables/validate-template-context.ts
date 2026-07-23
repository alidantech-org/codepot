import type {
  TemplateContextValidateRequest,
  TemplateContextValidateResult,
} from '@/contract/index';
import {
  caughtDiagnostic,
  failure,
  success,
} from '@/internal/results/operation-results';
import { buildTemplateContext } from '../template-context';
import {
  buildTemplateVariableCatalog,
  validateTemplateContext,
} from '../template-variables';
import type { TemplatingDependencies } from '../templating.types';

export async function validateCompiledTemplateContext(
  dependencies: TemplatingDependencies,
  request: TemplateContextValidateRequest,
): Promise<TemplateContextValidateResult> {
  try {
    const context = buildTemplateContext(request);
    const catalog = await buildTemplateVariableCatalog(
      context,
      request.templates,
      {
        hashes: dependencies.hashes,
        data: dependencies.data,
      },
    );
    const validation = validateTemplateContext(
      catalog,
      request.templates,
      request.strict ?? true,
    );
    return validation.valid
      ? success(validation, validation.diagnostics)
      : failure(validation.diagnostics);
  } catch (caught) {
    return failure([
      caughtDiagnostic(
        'templating',
        'TEMPLATING_CONTEXT_VALIDATION_FAILED',
        caught,
      ),
    ]);
  }
}
