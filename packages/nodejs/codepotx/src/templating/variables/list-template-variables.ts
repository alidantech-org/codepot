import type {
  TemplateVariablesRequest,
  TemplateVariablesResult,
} from '@/contract/index';
import {
  caughtDiagnostic,
  failure,
  success,
} from '@/internal/results/operation-results';
import { buildTemplateContext } from '../template-context';
import {
  buildTemplateVariableCatalog,
  formatTemplateVariableCatalog,
} from '../template-variables';
import type { TemplatingDependencies } from '../templating.types';

export async function listTemplateVariables(
  dependencies: TemplatingDependencies,
  request: TemplateVariablesRequest,
): Promise<TemplateVariablesResult> {
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
    return success(
      formatTemplateVariableCatalog(
        catalog,
        request.format ?? 'object',
        request.pretty ?? true,
      ),
      catalog.diagnostics,
    );
  } catch (caught) {
    return failure([
      caughtDiagnostic('templating', 'TEMPLATING_VARIABLES_FAILED', caught),
    ]);
  }
}
