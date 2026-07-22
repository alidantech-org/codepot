import type {
  Diagnostic,
  FileWriteOutcome,
  GenerationManifest,
  GenerationPlan,
  PortablePath,
  RenderedGeneration,
} from '@/contract/index';

import type { GenerationDependencies } from './generation.types';
import {
  buildGenerationManifest,
  currentFileDigest,
  loadGenerationManifest,
  manifestPath,
  staleManagedFiles,
  writeGenerationManifest,
} from './manifest';
import { artifactReference, joinPath } from './planning';
import { GenerationFileTransaction } from './transaction';

export interface ManagedWriteRequest {
  readonly task: string;
  readonly configuredManifest?: string;
  readonly projectRoot: string;
  readonly outputRoot: string;
  readonly plan: GenerationPlan;
  readonly rendered: RenderedGeneration;
  readonly dryRun: boolean;
  readonly transactional: boolean;
}

export interface ManagedWriteResult {
  readonly manifest: GenerationManifest;
  readonly manifestPath: string;
  readonly files: readonly FileWriteOutcome[];
  readonly cleaned: readonly PortablePath[];
  readonly diagnostics: readonly Diagnostic[];
  readonly transaction?: GenerationFileTransaction;
}

export class ManagedWriteError extends Error {
  readonly rollback: readonly FileWriteOutcome[];

  constructor(message: string, options: { readonly cause?: unknown; readonly rollback?: readonly FileWriteOutcome[] } = {}) {
    super(message, { cause: options.cause });
    this.name = 'ManagedWriteError';
    this.rollback = options.rollback ?? [];
  }
}

/**
 * Apply rendered output as one reversible task. The function never recursively
 * deletes a configured folder; stale cleanup is limited to verified manifest
 * records that remain unchanged since Codepot last wrote them.
 */
export async function applyManagedWrite(
  request: ManagedWriteRequest,
  dependencies: Pick<GenerationDependencies, 'files' | 'writer' | 'data' | 'hashes'>,
): Promise<ManagedWriteResult> {
  const selectedManifestPath = manifestPath(request.projectRoot, request.task, request.configuredManifest);
  const previous = await loadGenerationManifest(selectedManifestPath, dependencies);
  const manifest = await buildGenerationManifest(
    request.task,
    request.projectRoot,
    request.outputRoot,
    artifactReference(request.plan),
    request.rendered,
    dependencies,
  );
  const stale = staleManagedFiles(previous, manifest)
    .filter((record) => cleanScopeAllows(request.plan, request.outputRoot, record.path));
  const transaction = request.transactional && !request.dryRun
    ? new GenerationFileTransaction(dependencies.files)
    : undefined;
  if (transaction) {
    await transaction.captureRendered(request.outputRoot, request.rendered);
    await transaction.captureManaged(request.outputRoot, stale);
    await transaction.captureText(selectedManifestPath);
  }

  try {
    const diagnostics: Diagnostic[] = [];
    const outcomes: FileWriteOutcome[] = [];
    const cleaned: PortablePath[] = [];
    const files = request.rendered.files.map((file) => ({
      ...file,
      path: joinPath(request.outputRoot, file.path),
    }));
    outcomes.push(...await dependencies.writer.writeBatch({
      files,
      root: request.outputRoot,
      atomic: true,
      dryRun: request.dryRun,
    }));

    for (const record of stale) {
      const path = joinPath(request.outputRoot, record.path);
      const digest = await currentFileDigest(request.outputRoot, record, dependencies);
      if (digest === null) continue;
      if (digest !== record.contentDigest) {
        outcomes.push({
          path,
          status: 'refused',
          lifecycle: record.lifecycle,
          reason: 'stale-file-modified-by-user',
        });
        diagnostics.push({
          code: 'GENERATION_STALE_FILE_MODIFIED',
          severity: 'warning',
          layer: 'generation',
          message: `Stale managed file was preserved because its content changed: ${path}`,
          details: { path, previousDigest: record.contentDigest, currentDigest: digest },
        });
        continue;
      }
      if (request.dryRun) {
        outcomes.push({
          path,
          status: 'skipped',
          lifecycle: record.lifecycle,
          reason: 'dry-run:delete-stale-managed',
        });
        cleaned.push(path);
        continue;
      }
      await dependencies.files.remove(path, { force: true });
      outcomes.push({ path, status: 'deleted', lifecycle: record.lifecycle, reason: 'stale-managed' });
      cleaned.push(path);
    }

    if (!request.dryRun) await writeGenerationManifest(selectedManifestPath, manifest, dependencies);
    return {
      manifest,
      manifestPath: selectedManifestPath,
      files: outcomes,
      cleaned,
      diagnostics,
      ...(transaction ? { transaction } : {}),
    };
  } catch (caught) {
    const rollback = transaction ? await transaction.rollback() : [];
    throw new ManagedWriteError('Generation write transaction failed.', { cause: caught, rollback });
  }
}

function cleanScopeAllows(plan: GenerationPlan, outputRoot: string, relativePath: string): boolean {
  const allowed = plan.clean.filter((item) => item.allowed);
  if (!allowed.length) return true;
  const full = normalizePath(joinPath(outputRoot, relativePath));
  return allowed.some((item) => containsPath(full, normalizePath(item.path)));
}

function containsPath(path: string, root: string): boolean {
  return path === root || path.startsWith(`${root}/`);
}

function normalizePath(path: string): string {
  return path.replaceAll('\\', '/').replace(/\/+/g, '/').replace(/\/$/, '');
}
