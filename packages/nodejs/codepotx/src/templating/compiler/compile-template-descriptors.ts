import type {
  CompiledTemplateDescriptor,
  Diagnostic,
  ResolvedSource,
} from '@/contract/index';
import type { NormalizedPathsConfig } from '../config/normalized-paths-config';
import {
  BUILTIN_TEMPLATE_HELPERS,
  createTemplateRenderer,
} from '../helpers';
import { compilePathParts, compilePathTokens } from '../path-tokens';
import {
  isPartialPath,
  matchesTemplateGlob,
  partialNameFor,
  relativeTemplatePath,
} from '../paths/template-paths';
import { collectTemplateReferences } from '../template-references';
import type { TemplatingDependencies } from '../templating.types';

export interface CompiledTemplateDescriptorsResult {
  readonly templates: readonly CompiledTemplateDescriptor[];
  readonly diagnostics: readonly Diagnostic[];
}

export async function compileTemplateDescriptors(
  dependencies: TemplatingDependencies,
  source: ResolvedSource,
  config: NormalizedPathsConfig,
  paths: readonly string[],
): Promise<CompiledTemplateDescriptorsResult> {
  createTemplateRenderer(config.helpers);
  const knownHelpers = new Set([
    ...BUILTIN_TEMPLATE_HELPERS.map((helper) => helper.name),
    ...config.helpers,
    'each',
    'if',
    'unless',
    'with',
    'lookup',
    'log',
  ]);
  const templates: CompiledTemplateDescriptor[] = [];
  const diagnostics: Diagnostic[] = [];

  for (const path of paths) {
    const stat = await dependencies.files.stat(path);
    if (stat.kind !== 'file') continue;
    const relative = relativeTemplatePath(source.root, path);
    if (config.ignore.some((pattern) => matchesTemplateGlob(relative, pattern))) {
      continue;
    }
    const isTemplate = relative.endsWith(config.templateExtension);
    if (!isTemplate && !config.allowRawFiles) continue;
    const isPartial = isTemplate && isPartialPath(relative, config.partials);
    const stripped = isTemplate && config.stripTemplateExtension
      ? relative.slice(0, -config.templateExtension.length)
      : relative;
    const segments = stripped.split('/');
    const marker = segments[0] ?? '';
    const markerMatch = /^\{([^}]+)\}$/.exec(marker);
    const group = isPartial ? 'partials' : markerMatch?.[1] ?? 'root';
    const folder = config.folders[group];
    const templatePath = markerMatch ? segments.slice(1).join('/') : stripped;
    const outputTokens = isPartial
      ? []
      : [
          ...compilePathParts(folder?.parts ?? []),
          ...compilePathTokens(templatePath),
        ];
    const lifecycle = folder?.lifecycle;

    if (isTemplate) {
      const text = await dependencies.files.readText(path);
      const id = `template:${relative}`;
      try {
        templates.push({
          id,
          path: relative,
          kind: isPartial ? 'partial' : 'handlebars',
          group,
          outputTokens,
          ...(isPartial
            ? { partialName: partialNameFor(relative, config.templateExtension) }
            : {}),
          ...(lifecycle ? { lifecycle } : {}),
          compareMode: 'exact',
          references: collectTemplateReferences(id, text, knownHelpers),
          text,
          digest: await dependencies.hashes.text(text),
        });
      } catch (caught) {
        diagnostics.push({
          code: 'TEMPLATING_TEMPLATE_PARSE_FAILED',
          severity: 'error',
          layer: 'templating',
          message: caught instanceof Error ? caught.message : String(caught),
          details: { path: relative },
        });
      }
    } else {
      const dataBase64 = await dependencies.files.readBase64(path);
      templates.push({
        id: `template:${relative}`,
        path: relative,
        kind: 'raw',
        group,
        outputTokens,
        ...(lifecycle ? { lifecycle } : {}),
        compareMode: 'raw',
        references: [],
        dataBase64,
        digest: await dependencies.hashes.base64(dataBase64),
      });
    }
  }

  return { templates, diagnostics };
}
