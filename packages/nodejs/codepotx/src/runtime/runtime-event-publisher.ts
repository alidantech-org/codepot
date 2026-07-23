import type {
  CodepotEventOf,
  Diagnostic,
  PortablePath,
  RuntimeOperationKind,
} from '@/contract/index';
import type { RuntimeDependencies } from './runtime-dependencies.types';

export class RuntimeEventPublisher {
  readonly #dependencies: Pick<RuntimeDependencies, 'events' | 'clock' | 'ids'>;
  readonly #runId: string;
  #sequence = 0;

  constructor(
    dependencies: Pick<RuntimeDependencies, 'events' | 'clock' | 'ids'>,
    runId: string,
  ) {
    this.#dependencies = dependencies;
    this.#runId = runId;
  }

  async started(
    requestKind: RuntimeOperationKind,
    projectRoot: PortablePath | undefined,
  ): Promise<void> {
    const event: CodepotEventOf<'runtime.started'> = {
      ...this.#envelope(),
      source: 'runtime',
      type: 'runtime.started',
      payload: {
        requestKind,
        ...(projectRoot ? { projectRoot } : {}),
      },
    };
    await this.#publish(event);
  }

  async completed(
    requestKind: RuntimeOperationKind,
    success: boolean,
    durationMs: number,
  ): Promise<void> {
    const event: CodepotEventOf<'runtime.completed'> = {
      ...this.#envelope(),
      source: 'runtime',
      type: 'runtime.completed',
      payload: { requestKind, success, durationMs },
    };
    await this.#publish(event);
  }

  async failed(
    requestKind: RuntimeOperationKind,
    durationMs: number,
    diagnostics: readonly Diagnostic[],
  ): Promise<void> {
    const event: CodepotEventOf<'runtime.failed'> = {
      ...this.#envelope(),
      source: 'runtime',
      type: 'runtime.failed',
      payload: { requestKind, durationMs, diagnostics },
    };
    await this.#publish(event);
  }

  #envelope(): {
    readonly version: 1;
    readonly id: string;
    readonly runId: string;
    readonly sequence: number;
    readonly timestamp: string;
  } {
    this.#sequence += 1;
    return {
      version: 1,
      id: this.#dependencies.ids.create('event'),
      runId: this.#runId,
      sequence: this.#sequence,
      timestamp: this.#dependencies.clock.now(),
    };
  }

  async #publish(event: CodepotEventOf<'runtime.started' | 'runtime.completed' | 'runtime.failed'>): Promise<void> {
    try {
      await this.#dependencies.events.publish(event);
    } catch {
      // Runtime listeners are observational and cannot alter required control flow.
    }
  }
}
