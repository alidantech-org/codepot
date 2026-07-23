import { AsyncLocalStorage } from 'node:async_hooks';

import type { Awaitable, RunContext } from '@/contract/index';

export class RunContextStore {
  readonly #storage = new AsyncLocalStorage<RunContext>();

  current(): RunContext | undefined {
    return this.#storage.getStore();
  }

  async run<T>(context: RunContext, operation: () => Awaitable<T>): Promise<T> {
    return this.#storage.run(context, async () => operation());
  }
}
