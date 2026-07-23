import type {
  CodepotEvent,
  CodepotEventListener,
  CodepotEventType,
  Disposable,
  EventBusPort,
} from '@/contract/index';

export type EventListenerErrorHandler = (
  error: unknown,
  event: CodepotEvent,
) => void | Promise<void>;

class EventSubscription implements Disposable {
  readonly #dispose: () => void;

  constructor(dispose: () => void) {
    this.#dispose = dispose;
  }

  dispose(): void {
    this.#dispose();
  }
}

export class SequentialEventBus implements EventBusPort {
  readonly #allListeners = new Set<CodepotEventListener>();
  readonly #typedListeners = new Map<CodepotEventType, Set<CodepotEventListener>>();
  readonly #onListenerError: EventListenerErrorHandler;
  #queue: Promise<void> = Promise.resolve();

  constructor(onListenerError: EventListenerErrorHandler = () => undefined) {
    this.#onListenerError = onListenerError;
  }

  publish(event: CodepotEvent): Promise<void> {
    const dispatch = async (): Promise<void> => {
      const typed = this.#typedListeners.get(event.type) ?? new Set<CodepotEventListener>();
      for (const listener of [...this.#allListeners, ...typed]) {
        try {
          await listener(event);
        } catch (caught) {
          try {
            await this.#onListenerError(caught, event);
          } catch {
            // Observer failures never alter required control flow.
          }
        }
      }
    };
    const scheduled = this.#queue.then(dispatch, dispatch);
    this.#queue = scheduled.catch(() => undefined);
    return scheduled;
  }

  subscribe(listener: CodepotEventListener): Disposable;
  subscribe<TType extends CodepotEventType>(
    type: TType,
    listener: CodepotEventListener<Extract<CodepotEvent, { readonly type: TType }>>,
  ): Disposable;
  subscribe<TType extends CodepotEventType>(
    typeOrListener: TType | CodepotEventListener,
    maybeListener?: CodepotEventListener<Extract<CodepotEvent, { readonly type: TType }>>,
  ): Disposable {
    if (typeof typeOrListener === 'function') {
      this.#allListeners.add(typeOrListener);
      return new EventSubscription(() => this.#allListeners.delete(typeOrListener));
    }
    if (!maybeListener) throw new TypeError('A typed event subscription requires a listener.');
    const listeners = this.#typedListeners.get(typeOrListener) ?? new Set<CodepotEventListener>();
    const listener: CodepotEventListener = maybeListener;
    listeners.add(listener);
    this.#typedListeners.set(typeOrListener, listeners);
    return new EventSubscription(() => {
      listeners.delete(listener);
      if (listeners.size === 0) this.#typedListeners.delete(typeOrListener);
    });
  }
}
