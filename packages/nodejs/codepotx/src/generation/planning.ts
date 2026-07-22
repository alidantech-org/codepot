import type {
  ArtifactReference,
  CodepotCommandConfig,
  CodepotTaskConfig,
  CompiledTemplatePack,
  Diagnostic,
  JsonObject,
  PlannedCleanOperation,
  PlannedCommand,
  PlannedFile,
} from '@/contract/index';

import { resolvePlannedFileDependencies } from './dependency-planning';
import type { GenerationDependencies } from './generation.types';
import {
  createPlannedFileCandidates,
  normalizeRelativePath,
  unsafeRelativePath,
} from './selection-planning';

/**
 * Selection/path planning and dependency/import planning are separate passes so
 * every output is known before a semantic dependency is resolved.
 */
export function planFiles(
  templates: CompiledTemplatePack,
  baseContext: JsonObject,
  diagnostics: Diagnostic[],
  dependencies?: Pick<GenerationDependencies, 'imports'>,
): PlannedFile[] {
  const candidates = createPlannedFileCandidates(templates, baseContext, diagnostics);
  return resolvePlannedFileDependencies(candidates, diagnostics, dependencies?.imports)
    .sort((left, right) => left.outputPath.localeCompare(right.outputPath));
}

/** Command IDs are derived from task content so plan digests are reproducible. */
export function planCommands(
  task: CodepotTaskConfig,
  root: string,
  skipBefore: boolean | undefined,
  skipAfter: boolean | undefined,
  _ids?: GenerationDependencies['ids'],
): PlannedCommand[] {
  const output: PlannedCommand[] = [];
  if (!skipBefore) {
    output.push(...task.before.map((command, index) => commandPlan('before', index, command, task, root)));
  }
  if (!skipAfter) {
    output.push(...task.after.map((command, index) => commandPlan('after', index, command, task, root)));
  }
  return output;
}

/** Clean paths define scopes for manifest-owned stale files, not broad deletes. */
export function planClean(
  task: CodepotTaskConfig,
  outputRoot: string,
  templates: CompiledTemplatePack,
  _ids?: GenerationDependencies['ids'],
): PlannedCleanOperation[] {
  return task.clean.map((path, index) => {
    const full = joinPath(outputRoot, path);
    const relative = normalizeRelativePath(path);
    const protectedRoot = templates.writePolicy.protectedRoots
      .some((root) => containsPath(relative, normalizeRelativePath(root)));
    const cleanAllowed = templates.writePolicy.cleanRoots.length === 0
      || templates.writePolicy.cleanRoots.some((root) => containsPath(relative, normalizeRelativePath(root)));
    const allowed = !unsafeRelativePath(relative) && !protectedRoot && cleanAllowed;
    return {
      id: `clean:${index}:${relative}`,
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

function commandPlan(
  phase: 'before' | 'after',
  index: number,
  command: CodepotCommandConfig,
  task: CodepotTaskConfig,
  root: string,
): PlannedCommand {
  return {
    id: `command:${phase}:${index}:${stableSegment(command.name ?? command.run)}`,
    phase,
    ...(command.name ? { name: command.name } : {}),
    command: command.run,
    cwd: joinPath(root, command.cwd ?? '.'),
    optional: command.optional ?? false,
    environment: { ...task.environment, ...(command.environment ?? {}) },
  };
}

function stableSegment(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'command';
}

function containsPath(path: string, root: string): boolean {
  return path === root || path.startsWith(`${root}/`);
}
