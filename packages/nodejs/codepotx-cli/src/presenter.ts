import type { CodepotEvent, Diagnostic, RuntimeResponse } from 'codepotx/contract';

import type { CliIo, CliOptions } from './cli.types';

export class CliPresenter {
  readonly #options: CliOptions;
  readonly #io: CliIo;

  constructor(options: CliOptions, io: CliIo) {
    this.#options = options;
    this.#io = io;
  }

  event(event: CodepotEvent): void {
    if (this.#options.json || !this.#options.verbose) return;
    this.#io.stderr.write(`[${event.sequence}] ${event.type}\n`);
  }

  result(response: RuntimeResponse): number {
    const result = response.result;
    if (this.#options.json) {
      this.#io.stdout.write(`${JSON.stringify(response, null, this.#options.pretty ? 2 : 0)}\n`);
    } else if (result.success) {
      this.#io.stdout.write(`${formatValue(result.value)}\n`);
      this.#diagnostics(result.diagnostics);
    } else {
      this.#diagnostics(result.diagnostics);
    }
    return result.success ? 0 : 1;
  }

  text(value: string): void {
    this.#io.stdout.write(`${value}\n`);
  }

  error(caught: unknown): number {
    const message = caught instanceof Error ? caught.message : String(caught);
    this.#io.stderr.write(`Error: ${message}\n`);
    return 1;
  }

  #diagnostics(diagnostics: readonly Diagnostic[]): void {
    for (const item of diagnostics) {
      const stream = item.severity === 'error' ? this.#io.stderr : this.#io.stdout;
      stream.write(`${item.severity.toUpperCase()} ${item.code}: ${item.message}\n`);
    }
  }
}

function formatValue(value: unknown): string {
  if (Array.isArray(value)) return `Completed ${value.length} item${value.length === 1 ? '' : 's'}.`;
  if (value && typeof value === 'object') {
    if ('header' in value && value.header && typeof value.header === 'object' && 'kind' in value.header) {
      return `Created ${(value.header as { kind: string }).kind}.`;
    }
    return JSON.stringify(value, null, 2);
  }
  return String(value ?? 'Completed.');
}
