import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  ArtifactReference,
  DataCodecPort,
  FileSystemPort,
  GenerationManifest,
  HashPort,
  ManagedFileRecord,
  RenderedGeneration,
  VirtualFile,
} from '@/contract/index';

import { joinPath } from './planning';

export interface ManifestDependencies {
  readonly files: FileSystemPort;
  readonly data: DataCodecPort;
  readonly hashes: HashPort;
}

export function manifestPath(projectRoot: string, task: string, configured?: string): string {
  if (configured) return joinPath(projectRoot, configured);
  const safeTask = task.replace(/[^A-Za-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || 'default';
  return joinPath(projectRoot, `.codepot/manifests/${safeTask}.json`);
}

export async function loadGenerationManifest(
  path: string,
  dependencies: ManifestDependencies,
): Promise<GenerationManifest | null> {
  if (!await dependencies.files.exists(path)) return null;
  const value = dependencies.data.parseJson<GenerationManifest>(await dependencies.files.readText(path));
  if (value.header?.kind !== 'codepot.generation-manifest') {
    throw new Error(`Invalid Codepot generation manifest: ${path}`);
  }
  return value;
}

export async function buildGenerationManifest(
  task: string,
  projectRoot: string,
  outputRoot: string,
  plan: ArtifactReference,
  rendered: RenderedGeneration,
  dependencies: Pick<ManifestDependencies, 'data' | 'hashes'>,
): Promise<GenerationManifest> {
  const files: ManagedFileRecord[] = [];
  for (const file of rendered.files) {
    files.push({
      path: normalizePath(file.path),
      contentDigest: await normalizedContentDigest(file, dependencies.hashes),
      encoding: file.content.encoding,
      lifecycle: file.lifecycle,
      compareMode: file.compareMode,
      templateId: String(file.metadata?.['templateId'] ?? file.id),
    });
  }
  files.sort((left, right) => left.path.localeCompare(right.path));
  const body = { task, projectRoot, outputRoot, plan, files } as const;
  const contentDigest = await dependencies.hashes.text(dependencies.data.stringifyJson(body));
  return {
    header: {
      kind: 'codepot.generation-manifest',
      protocolVersion: CODEPOT_PROTOCOL_VERSION,
      artifactVersion: CODEPOT_ARTIFACT_VERSION,
      producer: { name: 'codepotx', version: '0.0.0' },
      contentDigest,
      sourceDigest: rendered.header.contentDigest,
    },
    ...body,
  };
}

export async function writeGenerationManifest(
  path: string,
  manifest: GenerationManifest,
  dependencies: Pick<ManifestDependencies, 'files' | 'data'>,
): Promise<void> {
  await dependencies.files.writeText(path, `${dependencies.data.stringifyJson(manifest, { pretty: true })}\n`);
}

/** Files previously managed but absent from the new manifest. */
export function staleManagedFiles(
  previous: GenerationManifest | null,
  next: GenerationManifest,
): readonly ManagedFileRecord[] {
  if (!previous) return [];
  const current = new Set(next.files.map((file) => normalizePath(file.path)));
  return previous.files
    .filter((file) => file.lifecycle === 'managed' && !current.has(normalizePath(file.path)))
    .sort((left, right) => left.path.localeCompare(right.path));
}

export async function currentFileDigest(
  outputRoot: string,
  record: ManagedFileRecord,
  dependencies: Pick<ManifestDependencies, 'files' | 'hashes'>,
): Promise<string | null> {
  const path = joinPath(outputRoot, record.path);
  if (!await dependencies.files.exists(path)) return null;
  return record.encoding === 'base64'
    ? dependencies.hashes.base64(await dependencies.files.readBase64(path))
    : dependencies.hashes.text(await dependencies.files.readText(path));
}

async function normalizedContentDigest(file: VirtualFile, hashes: HashPort): Promise<string> {
  if (file.content.encoding === 'base64') return hashes.base64(file.content.data);
  const text = file.compareMode === 'raw' ? file.content.text : normalizeText(file.content.text);
  return hashes.text(text);
}

function normalizeText(value: string): string {
  const normalized = value.replaceAll('\r\n', '\n').replaceAll('\r', '\n');
  return normalized ? `${normalized.replace(/\n+$/u, '')}\n` : '';
}

function normalizePath(path: string): string {
  return path.replaceAll('\\', '/').replace(/^\.\//, '').replace(/\/+/g, '/');
}
