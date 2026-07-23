import type {
  CodepotFileLoadRequest,
  CodepotFileLoadResult,
} from '@/contract/index';
import { compileCodepotFile } from '../codepot-file';
import type {
  CodepotFileInput,
  GenerationDependencies,
} from '../generation.types';
import { joinPath } from '../planning';
import { diagnostic, error, failure, success } from '../results';

export async function loadCodepotFile(
  dependencies: GenerationDependencies,
  request: CodepotFileLoadRequest,
): Promise<CodepotFileLoadResult> {
  try {
    const located = await locateCodepotFile(dependencies, request);
    const input = dependencies.data.parseYaml<CodepotFileInput>(
      await dependencies.files.readText(located.path),
    );
    const compiled = compileCodepotFile(input, located.path, located.root);
    if (!compiled.allow) {
      return failure([error(
        'GENERATION_NOT_ALLOWED',
        `${located.path} must explicitly set allow: true.`,
      )]);
    }
    return success(compiled);
  } catch (caught) {
    return failure([
      diagnostic('GENERATION_CODEPOT_FILE_LOAD_FAILED', caught),
    ]);
  }
}

async function locateCodepotFile(
  dependencies: GenerationDependencies,
  request: CodepotFileLoadRequest,
): Promise<{ readonly path: string; readonly root: string }> {
  if (request.source) {
    const resolved = await dependencies.sources.resolve(
      request.source,
      request.projectRoot ? { projectRoot: request.projectRoot } : {},
    );
    return {
      path: request.file ? joinPath(resolved.root, request.file) : resolved.entry,
      root: resolved.root,
    };
  }
  const root = request.projectRoot ?? '.';
  return { path: joinPath(root, request.file ?? 'CodepotFile.yml'), root };
}
