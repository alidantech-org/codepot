import { dirname, extname } from 'node:path/posix';

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
  PlannedDependency,
  PlannedFile,
} from '@/contract/index';
import { resolveExpression, resolveOutputTokens } from '@/templating/index';

import { createRelativeImportAdapter } from './imports';
import type { GenerationDependencies } from './generation.types';
import {
  buildOutputIndex,
  dependencyRefs,
  findOutputByRef,
  subjectRefs,
} from './output-index';
import { diagnostic, error } from './results';

interface SelectionInstance {
  readonly context: JsonObject;
  readonly alias?: string;
  readonly index?: number;
}

/**
 * Plan in two passes. All output paths exist before dependency resolution, so
 * imports never depend on template traversal order.
 */
export function planFiles(
  templates: CompiledTemplatePack,
  baseContext: JsonObject,
  diagnostics: Diagnostic[],
  dependencies?: Pick<GenerationDependencies, 'imports'>,
): PlannedFile[] {
  const folders = new Map(templates.folders.map((folder) => [folder.name, folder]));
  const candidates: PlannedFile[] = [];

  for (const template of templates.templates) {
    if (template.kind === 'partial') continue;
    const folder = folders.get(template.group);
    for (const selected of contextsFor(folder, baseContext, diagnostics)) {
      try {
        const initialPath = resolveOutputTokens(template.outputTokens, selected.context as Record<string, unknown>);
        const outputPath = normalizePath(initialPath);
        const refusalReason = unsafeRelativePath(outputPath) ? `Unsafe output path: ${outputPath}` : undefined;
        const context = attachFileContext(selected, template.id, template.group, outputPath);
        candidates.push({
          id: `planned:${template.id}:${candidates.length}`,
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

  refuseDuplicatePaths(candidates, diagnostics);
  const index = buildOutputIndex(candidates);
  const imports = dependencies?.imports ?? createRelativeImportAdapter();
  const planned = candidates.map((file) => {
    if (file.refusalReason) return file;
    const resolved = resolveDependencies(file, index, imports, diagnostics);
    return {
      ...file,
      dependencies: resolved.dependencies,
      context: attachDependencyContext(file.context, resolved.dependencies, resolved.imports),
      ...(resolved.refusalReason ? { refusalReason: resolved.refusalReason } : {}),
    };
  });

  return planned.sort((left, right) => left.outputPath.localeCompare(right.outputPath));
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
): SelectionInstance[] {
  if (!folder?.select || folder.mode === 'once') return [{ context: base }];
  const selected = resolveExpression(base as Record<string, unknown>, folder.select);
  if (selected === undefined) {
    diagnostics.push(error('GENERATION_SELECTION_MISSING', `Template selection "${folder.select}" did not resolve.`));
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
    subjectRefs: subjectRefs(selection.context),
    ...(selection.index === undefined ? {} : { index: selection.index }),
  };
  const context: JsonObject = { ...selection.context, file };
  if (selection.alias) {
    const selected = asObject(context[selection.alias]);
    if (selected) {
      context[selection.alias] = {
        ...selected,
        emit: {
          ...(asObject(selected.emit) ?? {}),
          group,
          path: outputPath,
          fileName: name,
          file_name: name,
          folderPath: directory,
          folder_path: directory,
          ref: subjectRefs({ [selection.alias]: selected })[0] ?? null,
        },
      };
    }
  }
  return context;
}

function resolveDependencies(
  file: PlannedFile,
  index: ReturnType<typeof buildOutputIndex>,
  imports: NonNullable<GenerationDependencies['imports']>,
  diagnostics: Diagnostic[],
): {
  readonly dependencies: readonly PlannedDependency[];
  readonly imports: readonly JsonObject[];
  readonly refusalReason?: string;
} {
  const planned: PlannedDependency[] = [];
  const importFacts: JsonObject[] = [];
  let refusalReason: string | undefined;
  for (const ref of dependencyRefs(file.context)) {
    const targets = findOutputByRef(index, ref).filter((target) => target.plannedFileId !== file.id);
    if (targets.length === 0) {
      diagnostics.push({
        code: 'GENERATION_DEPENDENCY_NOT_EMITTED',
        severity: 'warning',
        layer: 'generation',
        message: `Dependency ${ref} used by ${file.outputPath} is not emitted by this template pack.`,
        details: { ref, outputPath: file.outputPath },
      });
      planned.push({ ref, purpose: 'reference', targetRef: ref });
      continue;
    }
    if (targets.length > 1) {
      refusalReason = `Dependency ${ref} has multiple output targets.`;
      diagnostics.push({
        code: 'GENERATION_DEPENDENCY_AMBIGUOUS',
        severity: 'error',
        layer: 'generation',
        message: `${refusalReason} ${targets.map((item) => item.outputPath).join(', ')}`,
        details: { ref, outputPath: file.outputPath, targets: targets.map((item) => item.outputPath) },
      });
      continue;
    }
    const target = targets[0]!;
    const dependency: PlannedDependency = {
      ref,
      purpose: 'reference',
      targetRef: ref,
      outputPath: target.outputPath,
    };
    const resolved = imports.resolve({
      fromPath: file.outputPath,
      toPath: target.outputPath,
      dependency,
      context: file.context,
    });
    planned.push({
      ...dependency,
      importPath: resolved.importPath,
      ...(resolved.metadata ? { metadata: resolved.metadata } : {}),
    });
    importFacts.push({
      ref,
      purpose: dependency.purpose,
      outputPath: target.outputPath,
      importPath: resolved.importPath,
      ...(resolved.statement ? { statement: resolved.statement } : {}),
      ...(resolved.symbols ? { symbols: resolved.symbols } : {}),
    });
  }
  return {
    dependencies: planned.sort((left, right) => left.ref.localeCompare(right.ref)),
    imports: importFacts.sort((left, right) => String(left.importPath).localeCompare(String(right.importPath))),
    ...(refusalReason ? { refusalReason } : {}),
  };
}

function attachDependencyContext(
  context: JsonObject,
  dependencies: readonly PlannedDependency[],
  imports: readonly JsonObject[],
): JsonObject {
  const file = asObject(context.file) ?? {};
  const next: JsonObject = {
    ...context,
    dependencies: dependencies as unknown as never,
    imports: imports as unknown as never,
    file: { ...file, dependencies: dependencies as unknown as never, imports: imports as unknown as never },
  };
  for (const alias of ['model', 'dto', 'enum', 'schema', 'entity', 'operation', 'resource', 'frontend']) {
    const selected = asObject(next[alias]);
    if (!selected) continue;
    next[alias] = {
      ...selected,
      emit: {
        ...(asObject(selected.emit) ?? {}),
        dependencies: dependencies as unknown as never,
        imports: imports as unknown as never,
      },
    };
  }
  return next;
}

function refuseDuplicatePaths(files: PlannedFile[], diagnostics: Diagnostic[]): void {
  const byPath = new Map<string, PlannedFile[]>();
  for (const file of files) {
    const selected = byPath.get(file.outputPath) ?? [];
    selected.push(file);
    byPath.set(file.outputPath, selected);
  }
  for (const [path, collisions] of byPath) {
    if (collisions.length < 2) continue;
    const reason = `Multiple templates planned the same output path: ${path}`;
    diagnostics.push({
      code: 'GENERATION_DUPLICATE_OUTPUT_PATH',
      severity: 'error',
      layer: 'generation',
      message: reason,
      details: { path, templates: collisions.map((file) => file.templateId) },
    });
    for (const collision of collisions) {
      const index = files.indexOf(collision);
      files[index] = { ...collision, refusalReason: reason };
    }
  }
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

function asObject(value: unknown): JsonObject | undefined {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as JsonObject : undefined;
}
