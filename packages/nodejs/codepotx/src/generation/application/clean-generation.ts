import type {
  Diagnostic,
  GenerationCleanRequest,
  GenerationCleanResult,
  PortablePath,
} from '@/contract/index';
import type { GenerationDependencies } from '../generation.types';
import { diagnostic, error, failure, success } from '../results';

/** Direct clean calls refuse recursive directories; task cleanup uses manifests. */
export async function cleanGeneration(
  dependencies: GenerationDependencies,
  request: GenerationCleanRequest,
): Promise<GenerationCleanResult> {
  try {
    const cleaned: PortablePath[] = [];
    const diagnostics: Diagnostic[] = [];
    for (const item of request.plan.clean) {
      request.signal?.throwIfAborted();
      if (!item.allowed || !await dependencies.files.exists(item.path)) continue;
      const stat = await dependencies.files.stat(item.path);
      if (stat.kind !== 'file') {
        diagnostics.push(error(
          'GENERATION_BROAD_CLEAN_REFUSED',
          `Refusing recursive directory cleanup without a managed manifest: ${item.path}`,
        ));
        continue;
      }
      if (!request.dryRun) {
        await dependencies.files.remove(item.path, { force: true });
      }
      cleaned.push(item.path);
    }
    return diagnostics.some((item) => item.severity === 'error')
      ? failure(diagnostics)
      : success(cleaned, diagnostics);
  } catch (caught) {
    return failure([diagnostic('GENERATION_CLEAN_FAILED', caught)]);
  }
}
