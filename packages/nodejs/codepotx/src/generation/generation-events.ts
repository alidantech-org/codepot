import type {
  CodepotEvent,
  CommandExecutionOutcome,
  Diagnostic,
  FileWriteOutcome,
} from '@/contract/index';

import type { GenerationDependencies } from './generation.types';

type Draft = CodepotEvent extends infer TEvent
  ? TEvent extends CodepotEvent
    ? Omit<TEvent, 'version' | 'id' | 'runId' | 'sequence' | 'timestamp'>
    : never
  : never;

/**
 * Generation events are observation only. Publishing failures are isolated so
 * frontends and telemetry can never change task control flow.
 */
export class GenerationEventPublisher {
  readonly #dependencies: Pick<GenerationDependencies, 'events' | 'clock' | 'ids'>;
  readonly #runId: string;
  #sequence = 0;

  constructor(
    dependencies: Pick<GenerationDependencies, 'events' | 'clock' | 'ids'>,
    runId?: string,
  ) {
    this.#dependencies = dependencies;
    this.#runId = runId ?? dependencies.ids.create('generation');
  }

  async stage(
    type: 'stage.started' | 'stage.completed',
    stage: string,
    payload: { readonly itemCount?: number; readonly durationMs?: number } = {},
  ): Promise<void> {
    await this.#publish({ source: 'generation', type, payload: { stage, ...payload } });
  }

  async diagnostic(diagnostic: Diagnostic): Promise<void> {
    await this.#publish({ source: 'generation', type: 'diagnostic.emitted', payload: { diagnostic } });
  }

  async file(file: FileWriteOutcome, contentDigest?: string): Promise<void> {
    await this.#publish({
      source: 'generation',
      type: 'file.classified',
      payload: {
        path: file.path,
        status: file.status,
        lifecycle: file.lifecycle,
        ...(contentDigest ? { contentDigest } : {}),
        ...(file.reason ? { reason: file.reason } : {}),
      },
    });
  }

  async command(command: CommandExecutionOutcome): Promise<void> {
    await this.#publish({
      source: 'generation',
      type: 'command.completed',
      payload: {
        command: command.command,
        cwd: command.cwd,
        exitCode: command.exitCode,
        skipped: command.skipped,
        optional: command.optional,
      },
    });
  }

  async #publish(event: Draft): Promise<void> {
    this.#sequence += 1;
    try {
      await this.#dependencies.events.publish({
        ...event,
        version: 1,
        id: this.#dependencies.ids.create('event'),
        runId: this.#runId,
        sequence: this.#sequence,
        timestamp: this.#dependencies.clock.now(),
      } as CodepotEvent);
    } catch {
      // Observation must never become hidden control flow.
    }
  }
}
