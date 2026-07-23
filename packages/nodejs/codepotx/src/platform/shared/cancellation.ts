import type { CancellationSignal, Disposable } from '@/contract/index';
import { OperationCancelledError } from './errors';

class CancellationSubscription implements Disposable {
  readonly #dispose: () => void;

  constructor(dispose: () => void) {
    this.#dispose = dispose;
  }

  dispose(): void {
    this.#dispose();
  }
}

export class CodepotCancellationSignal implements CancellationSignal {
  #aborted = false;
  #reason = 'Operation cancelled.';
  readonly #listeners = new Set<() => void>();

  get aborted(): boolean {
    return this.#aborted;
  }

  get reason(): string {
    return this.#reason;
  }

  throwIfAborted(): void {
    if (this.#aborted) throw new OperationCancelledError(this.#reason);
  }

  subscribe(listener: () => void): Disposable {
    if (this.#aborted) {
      listener();
      return new CancellationSubscription(() => undefined);
    }
    this.#listeners.add(listener);
    return new CancellationSubscription(() => this.#listeners.delete(listener));
  }

  abort(reason = 'Operation cancelled.'): void {
    if (this.#aborted) return;
    this.#aborted = true;
    this.#reason = reason;
    for (const listener of [...this.#listeners]) listener();
    this.#listeners.clear();
  }
}

export class CodepotCancellationController {
  readonly signal: CodepotCancellationSignal = new CodepotCancellationSignal();

  abort(reason?: string): void {
    this.signal.abort(reason);
  }
}
