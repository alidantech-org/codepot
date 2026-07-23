import type {
  TemplatingCompileRequest,
  TemplatingCompileResult,
} from '@/contract/index';
import {
  caughtDiagnostic,
  failure,
  success,
} from '@/internal/results/operation-results';
import { assembleTemplatePack } from '../compiler/assemble-template-pack';
import { compileTemplateDescriptors } from '../compiler/compile-template-descriptors';
import { discoverTemplateFiles } from '../compiler/discover-template-files';
import { validateCompiledTemplatePack } from '../compiler/validate-template-pack';
import { normalizePathsConfig } from '../config/normalized-paths-config';
import type { PathsFileInput } from '../config/paths-input.types';
import { validatePathsConfig } from '../config/validate-paths-config';
import { joinTemplatePath } from '../paths/template-paths';
import type { TemplatingDependencies } from '../templating.types';

export async function compileTemplatePack(
  dependencies: TemplatingDependencies,
  request: TemplatingCompileRequest,
): Promise<TemplatingCompileResult> {
  try {
    const source = await dependencies.sources.resolve(request.source, {
      ...(request.projectRoot ? { projectRoot: request.projectRoot } : {}),
      cache: request.cache ?? 'auto',
    });
    const pathsPath = request.pathsFile
      ? joinTemplatePath(source.root, request.pathsFile)
      : joinTemplatePath(source.root, 'paths.yaml');
    const input = dependencies.data.parseYaml<PathsFileInput>(
      await dependencies.files.readText(pathsPath),
    );
    const config = normalizePathsConfig(input);
    const diagnostics = [...validatePathsConfig(config)];
    const paths = await discoverTemplateFiles(dependencies, source, config);
    const compiled = await compileTemplateDescriptors(
      dependencies,
      source,
      config,
      paths,
    );
    diagnostics.push(...compiled.diagnostics);
    diagnostics.push(...validateCompiledTemplatePack(config, compiled.templates));
    const artifact = await assembleTemplatePack(
      dependencies,
      source,
      config,
      compiled.templates,
      diagnostics,
    );
    return diagnostics.some((item) => item.severity === 'error')
      ? failure(diagnostics)
      : success(artifact, diagnostics);
  } catch (caught) {
    return failure([
      caughtDiagnostic('templating', 'TEMPLATING_COMPILE_FAILED', caught),
    ]);
  }
}
