import type {
  FileSystemPort,
  FileWriteOutcome,
  ManagedFileRecord,
  RenderedGeneration,
  VirtualFileContent,
} from '@/contract/index';

import { joinPath } from './planning';

interface ExistingFileSnapshot {
  readonly path: string;
  readonly existed: boolean;
  readonly content?: VirtualFileContent;
}

/**
 * Captures every path before mutation. Rollback restores bytes exactly and
 * removes files created by the failed task. It deliberately owns no planning.
 */
export class GenerationFileTransaction {
  readonly #files: FileSystemPort;
  readonly #snapshots = new Map<string, ExistingFileSnapshot>();
  #completed = false;

  constructor(files: FileSystemPort) {
    this.#files = files;
  }

  async captureRendered(outputRoot: string, rendered: RenderedGeneration): Promise<void> {
    for (const file of rendered.files) {
      await this.capture(joinPath(outputRoot, file.path), file.content.encoding);
    }
  }

  async captureManaged(outputRoot: string, records: readonly ManagedFileRecord[]): Promise<void> {
    for (const record of records) {
      await this.capture(joinPath(outputRoot, record.path), record.encoding);
    }
  }

  async captureText(path: string): Promise<void> {
    await this.capture(path, 'utf8');
  }

  complete(): void {
    this.#completed = true;
    this.#snapshots.clear();
  }

  async rollback(): Promise<readonly FileWriteOutcome[]> {
    if (this.#completed) return [];
    const outcomes: FileWriteOutcome[] = [];
    const snapshots = [...this.#snapshots.values()].reverse();
    for (const snapshot of snapshots) {
      if (!snapshot.existed) {
        await this.#files.remove(snapshot.path, { force: true });
      } else if (snapshot.content?.encoding === 'base64') {
        await this.#files.writeBase64(snapshot.path, snapshot.content.data);
      } else if (snapshot.content?.encoding === 'utf8') {
        await this.#files.writeText(snapshot.path, snapshot.content.text);
      }
      outcomes.push({
        path: snapshot.path,
        status: 'rolledBack',
        lifecycle: 'managed',
        reason: snapshot.existed ? 'restored-previous-content' : 'removed-created-file',
      });
    }
    this.#completed = true;
    this.#snapshots.clear();
    return outcomes;
  }

  async capture(path: string, encoding: 'utf8' | 'base64'): Promise<void> {
    if (this.#snapshots.has(path)) return;
    const existed = await this.#files.exists(path);
    if (!existed) {
      this.#snapshots.set(path, { path, existed: false });
      return;
    }
    const stat = await this.#files.stat(path);
    if (stat.kind !== 'file') {
      throw new Error(`Generation transaction can only snapshot files: ${path}`);
    }
    const content = encoding === 'base64'
      ? { encoding: 'base64' as const, data: await this.#files.readBase64(path) }
      : { encoding: 'utf8' as const, text: await this.#files.readText(path) };
    this.#snapshots.set(path, { path, existed: true, content });
  }
}
