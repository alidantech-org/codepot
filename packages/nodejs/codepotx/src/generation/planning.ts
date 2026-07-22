import type {
  ArtifactReference,
  CodepotCommandConfig,
  CodepotTaskConfig,
  CompiledTemplateFolder,
  CompiledTemplatePack,
  Diagnostic,
  JsonObject,
  PlannedCleanOperation,
  PlannedCommand,
  PlannedFile,
} from '@/contract/index';
import { resolveExpression, resolveOutputTokens } from '@/templating/index';
import type { GenerationDependencies } from './generation.types';
import { diagnostic, error } from './results';

export function planFiles(
  templates: CompiledTemplatePack,
  baseContext: JsonObject,
  diagnostics: Diagnostic[],
): PlannedFile[] {
  const folders = new Map(templates.folders.map((folder) => [folder.name, folder]));
  const files: PlannedFile[] = [];
  for (const template of templates.templates) {
    const folder = folders.get(template.group);
    for (const context of contextsFor(folder, baseContext, diagnostics)) {
      try {
        const outputPath = resolveOutputTokens(template.outputTokens, context as Record<string, unknown>);
        const refusalReason = unsafeRelativePath(outputPath) ? `Unsafe output path: ${outputPath}` : undefined;
        files.push({
          id: `planned:${template.id}:${files.length}`,
          templateId: template.id,
          outputPath,
          group: template.group,
          lifecycle: template.lifecycle ?? templates.writePolicy.defaultMode,
          compareMode: template.compareMode,
          context,
          dependencies: [],
          ...(refusalReason ? { refusalReason } : {}),
        });
      } catch (caught) {
        diagnostics.push(diagnostic('GENERATION_PATH_RESOLUTION_FAILED', caught));
      }
    }
  }
  return files.sort((left, right) => left.outputPath.localeCompare(right.outputPath));
}

export function planCommands(
  task: CodepotTaskConfig,
  root: string,
  skipBefore: boolean | undefined,
  skipAfter: boolean | undefined,
  ids: GenerationDependencies['ids'],
): PlannedCommand[] {
  const output: PlannedCommand[] = [];
  if (!skipBefore) output.push(...task.before.map((command) => commandPlan('before', command, task, root, ids)));
  if (!skipAfter) output.push(...task.after.map((command) => commandPlan('after', command, task, root, ids)));
  return output;
}

export function planClean(
  task: CodepotTaskConfig,
  outputRoot: string,
  templates: CompiledTemplatePack,
  ids: GenerationDependencies['ids'],
): PlannedCleanOperation[] {
  return task.clean.map((path) => {
    const full = joinPath(outputRoot, path);
    const relative = normalizePath(path);
    const protectedRoot = templates.writePolicy.protectedRoots.some((root) => containsPath(relative, normalizePath(root)));
    const cleanAllowed = templates.writePolicy.cleanRoots.length === 0
      || templates.writePolicy.cleanRoots.some((root) => containsPath(relative, normalizePath(root)));
    const allowed = !unsafeRelativePath(relative) && !protectedRoot && cleanAllowed;
    return {
      id: ids.create('clean'),
      path: full,
      allowed,
      ...(allowed ? {} : { refusalReason: `Clean path is not allowed: ${path}` }),
    };
  });
}

export function artifactReference(value: {
  readonly header: {
    readonly kind: string;
    readonly contentDigest: string;
    readonly sourceDigest: string;
  };
}): ArtifactReference {
  return {
    kind: value.header.kind as ArtifactReference['kind'],
    contentDigest: value.header.contentDigest,
    sourceDigest: value.header.sourceDigest,
  };
}

export function joinPath(root: string, path: string): string {
  if (path === '.' || path === '') return root;
  return `${root.replace(/[\\/]$/, '')}/${path.replace(/^[\\/]/, '')}`;
}

function contextsFor(
  folder: CompiledTemplateFolder | undefined,
  base: JsonObject,
  diagnostics: Diagnostic[],
): JsonObject[] {
  if (!folder?.select || folder.mode === 'once') return [base];
  const selected = resolveExpression(base as Record<string, unknown>, folder.select);
  if (selected === undefined) {
    diagnostics.push(error('GENERATION_SELECTION_MISSING', `Template selection "${folder.select}" did not resolve.`));
    return [];
  }
  const alias = folder.alias ?? folder.name;
  if (folder.mode === 'group') return [{ ...base, [alias]: selected as never, items: selected as never }];
  const values = Array.isArray(selected) ? selected : [selected];
  return values.map((value, index) => ({ ...base, [alias]: value as never, index }));
}

function commandPlan(
  phase: 'before' | 'after',
  command: CodepotCommandConfig,
  task: CodepotTaskConfig,
  root: string,
  ids: GenerationDependencies['ids'],
): PlannedCommand {
  return {
    id: ids.create('command'),
    phase,
    ...(command.name ? { name: command.name } : {}),
    command: command.run,
    cwd: joinPath(root, command.cwd ?? '.'),
    optional: command.optional ?? false,
    environment: { ...task.environment, ...(command.environment ?? {}) },
  };
}

function unsafeRelativePath(path: string): boolean {
  const value = normalizePath(path);
  return value.startsWith('/') || value === '..' || value.startsWith('../') || value.includes('/../');
}
function containsPath(path: string, root: string): boolean {
  return path === root || path.startsWith(`${root}/`);
}
function normalizePath(path: string): string {
  return path.replaceAll('\\', '/').replace(/^\.\//, '').replace(/\/+/g, '/');
}
