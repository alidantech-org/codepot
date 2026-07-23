import { dirname, extname } from 'node:path/posix';

import type {
  CompiledTemplateFolder,
  CompiledTemplatePack,
  Diagnostic,
  JsonObject,
  JsonValue,
  PlannedFile,
} from '@/contract/index';
import { resolveExpression, resolveOutputTokens } from '@/templating/index';

import { subjectRefs } from './output-index';
import { diagnostic, error } from './results';

interface SelectionInstance {
  readonly context: JsonObject;
  readonly alias?: string;
  readonly index?: number;
}

export function createPlannedFileCandidates(
  templates: CompiledTemplatePack,
  baseContext: JsonObject,
  diagnostics: Diagnostic[],
): PlannedFile[] {
  const folders = new Map(templates.folders.map((folder) => [folder.name, folder]));
  const candidates: PlannedFile[] = [];
  for (const template of templates.templates) {
    if (template.kind === 'partial') continue;
    const folder = folders.get(template.group);
    for (const selected of contextsFor(folder, baseContext, diagnostics)) {
      try {
        const outputPath = normalizeRelativePath(
          resolveOutputTokens(template.outputTokens, selected.context as Record<string, unknown>),
        );
        const refusalReason = unsafeRelativePath(outputPath)
          ? `Unsafe output path: ${outputPath}`
          : undefined;
        candidates.push({
          id: `planned:${template.id}:${candidates.length}`,
          templateId: template.id,
          outputPath,
          group: template.group,
          lifecycle: template.lifecycle ?? templates.writePolicy.defaultMode,
          compareMode: template.compareMode,
          context: attachFileContext(selected, template.id, template.group, outputPath),
          dependencies: [],
          ...(refusalReason ? { refusalReason } : {}),
        });
      } catch (caught) {
        diagnostics.push(diagnostic('GENERATION_PATH_RESOLUTION_FAILED', caught));
      }
    }
  }
  return candidates;
}

function contextsFor(
  folder: CompiledTemplateFolder | undefined,
  base: JsonObject,
  diagnostics: Diagnostic[],
): SelectionInstance[] {
  if (!folder?.select || folder.mode === 'once') return [{ context: base }];
  const selected = resolveExpression(base as Record<string, unknown>, folder.select);
  if (selected === undefined) {
    diagnostics.push(error(
      'GENERATION_SELECTION_MISSING',
      `Template selection "${folder.select}" did not resolve.`,
    ));
    return [];
  }
  const alias = folder.alias ?? folder.name;
  if (folder.mode === 'group') {
    return [{ context: { ...base, [alias]: selected as never, items: selected as never }, alias }];
  }
  const values = Array.isArray(selected) ? selected : [selected];
  return values.map((value, index) => ({
    context: { ...base, [alias]: value as never, index },
    alias,
    index,
  }));
}

function attachFileContext(
  selection: SelectionInstance,
  templateId: string,
  group: string,
  outputPath: string,
): JsonObject {
  const extension = extname(outputPath);
  const name = outputPath.split('/').at(-1) ?? outputPath;
  const directory = dirname(outputPath) === '.' ? '' : dirname(outputPath);
  const subject = subjectRefs(selection.context);
  const file: JsonObject = {
    templateId,
    group,
    path: outputPath,
    outputPath,
    directory,
    name,
    stem: extension ? name.slice(0, -extension.length) : name,
    extension,
    depth: directory ? directory.split('/').length : 0,
    rootPrefix: directory ? '../'.repeat(directory.split('/').length) : './',
    subjectRefs: subject,
    ...(selection.index === undefined ? {} : { index: selection.index }),
  };
  const context: Record<string, JsonValue> = { ...selection.context, file };
  if (!selection.alias) return context;
  const selected = asObject(context[selection.alias]);
  if (!selected) return context;
  return {
    ...context,
    [selection.alias]: {
      ...selected,
      emit: {
        ...(asObject(selected['emit']) ?? {}),
        group,
        path: outputPath,
        fileName: name,
        file_name: name,
        folderPath: directory,
        folder_path: directory,
        ref: subjectRefs({ [selection.alias]: selected })[0] ?? null,
      },
    },
  };
}

export function normalizeRelativePath(path: string): string {
  return path.replaceAll('\\', '/').replace(/^\.\//, '').replace(/\/+/g, '/');
}

export function unsafeRelativePath(path: string): boolean {
  const value = normalizeRelativePath(path);
  return value.startsWith('/') || value === '..' || value.startsWith('../') || value.includes('/../');
}

function asObject(value: JsonValue | undefined): JsonObject | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as JsonObject
    : undefined;
}
