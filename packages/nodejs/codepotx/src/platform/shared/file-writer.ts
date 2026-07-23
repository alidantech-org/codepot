import { dirname, resolve } from 'node:path';
import type {
  CompareFileRequest,
  CompareFileResult,
  FileWriteOutcome,
  FileWriterPort,
  HashPort,
  IdPort,
  VirtualFileContent,
  WriteBatchRequest,
  WriteFileRequest,
} from '@/contract/index';
import type { AtomicFileSystemPort } from './file-writer.types';
import { assertPathWithin } from './path-utils';

function normalizeText(value: string): string {
  const normalized = value.replaceAll('\r\n', '\n').replaceAll('\r', '\n');
  return normalized ? `${normalized.replace(/\n+$/u, '')}\n` : '';
}

function layoutKey(value: string): string {
  const result: string[] = [];
  let quote: string | undefined;
  let escaped = false;
  for (const char of value) {
    if (quote) {
      result.push(char);
      if (escaped) escaped = false;
      else if (char === '\\') escaped = true;
      else if (char === quote) quote = undefined;
      continue;
    }
    if (char === '"' || char === "'") {
      quote = char;
      result.push(char);
      continue;
    }
    if (!/\s/u.test(char)) result.push(char);
  }
  return result.join('');
}

function comparisonValue(
  content: VirtualFileContent,
  mode: CompareFileRequest['compareMode'],
): string {
  if (content.encoding === 'base64') return content.data;
  if (mode === 'raw') return content.text;
  const text = normalizeText(content.text);
  return mode === 'layoutInsensitive' ? layoutKey(text) : text;
}

export class ChangedAwareFileWriter implements FileWriterPort {
  readonly #files: AtomicFileSystemPort;
  readonly #hash: HashPort;
  readonly #ids: IdPort;

  constructor(files: AtomicFileSystemPort, hash: HashPort, ids: IdPort) {
    this.#files = files;
    this.#hash = hash;
    this.#ids = ids;
  }

  async compare(request: CompareFileRequest): Promise<CompareFileResult> {
    const nextValue = comparisonValue(request.content, request.compareMode);
    const nextDigest = request.content.encoding === 'base64'
      ? await this.#hash.base64(nextValue)
      : await this.#hash.text(nextValue);
    if (!await this.#files.exists(request.path)) return { exists: false, changed: true, nextDigest };
    const previousContent = request.content.encoding === 'base64'
      ? { encoding: 'base64' as const, data: await this.#files.readBase64(request.path) }
      : { encoding: 'utf8' as const, text: await this.#files.readText(request.path) };
    const previousValue = comparisonValue(previousContent, request.compareMode);
    const previousDigest = previousContent.encoding === 'base64'
      ? await this.#hash.base64(previousValue)
      : await this.#hash.text(previousValue);
    return {
      exists: true,
      changed: previousDigest !== nextDigest,
      previousDigest,
      nextDigest,
    };
  }

  async write(request: WriteFileRequest): Promise<FileWriteOutcome> {
    const comparison = await this.compare(request);
    if (request.lifecycle === 'immutable' && comparison.exists) {
      return { path: request.path, status: 'skipped', lifecycle: request.lifecycle, reason: 'immutable-existing' };
    }
    if (!comparison.changed) return { path: request.path, status: 'unchanged', lifecycle: request.lifecycle };
    const nextStatus = comparison.exists ? 'updated' : 'created';
    if (request.dryRun) {
      return { path: request.path, status: 'skipped', lifecycle: request.lifecycle, reason: `dry-run:${nextStatus}` };
    }
    const content = request.content.encoding === 'utf8' && request.compareMode !== 'raw'
      ? { encoding: 'utf8' as const, text: normalizeText(request.content.text) }
      : request.content;
    if (request.atomic) {
      const temporary = resolve(dirname(request.path), `.${this.#ids.create('codepot')}.tmp`);
      await this.#writeContent(temporary, content);
      await this.#files.move(temporary, request.path, { overwrite: true });
    } else {
      await this.#writeContent(request.path, content);
    }
    return { path: request.path, status: nextStatus, lifecycle: request.lifecycle };
  }

  async writeBatch(request: WriteBatchRequest): Promise<readonly FileWriteOutcome[]> {
    const outcomes: FileWriteOutcome[] = [];
    for (const file of request.files) {
      assertPathWithin(file.path, request.root);
      outcomes.push(await this.write({
        path: file.path,
        content: file.content,
        compareMode: file.compareMode,
        lifecycle: file.lifecycle,
        ...(request.atomic === undefined ? {} : { atomic: request.atomic }),
        ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }),
      }));
    }
    return outcomes;
  }

  async #writeContent(path: string, content: VirtualFileContent): Promise<void> {
    if (content.encoding === 'utf8') await this.#files.writeText(path, content.text);
    else await this.#files.writeBase64(path, content.data);
  }
}
