import type {
  GenerationWriteRequest,
  GenerationWriteResult,
} from '@/contract/index';
import type { GenerationDependencies } from '../generation.types';
import { joinPath } from '../planning';
import { diagnostic, failure, success } from '../results';

export async function writeGeneration(
  dependencies: GenerationDependencies,
  request: GenerationWriteRequest,
): Promise<GenerationWriteResult> {
  try {
    request.signal?.throwIfAborted();
    const files = request.rendered.files.map((file) => ({
      ...file,
      path: joinPath(request.outputRoot, file.path),
    }));
    const outcomes = await dependencies.writer.writeBatch({
      files,
      root: request.outputRoot,
      atomic: request.atomic ?? true,
      dryRun: request.dryRun ?? false,
    });
    request.signal?.throwIfAborted();
    return success(outcomes);
  } catch (caught) {
    return failure([diagnostic('GENERATION_WRITE_FAILED', caught)]);
  }
}
