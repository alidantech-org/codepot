import type {
  CodepotEvent,
  CodepotEventListener,
  CodepotEventOf,
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
    listener: CodepotEventListener<CodepotEventOf<TType>>,
  ): Disposable;
  subscribe<TType extends CodepotEventType>(
    typeOrListener: TType | CodepotEventListener,
    maybeListener?: CodepotEventListener<CodepotEventOf<TType>>,
  ): Disposable {
    if (typeof typeOrListener === 'function') {
      this.#allListeners.add(typeOrListener);
      return new EventSubscription(() => this.#allListeners.delete(typeOrListener));
    }
    if (!maybeListener) throw new TypeError('A typed event subscription requires a listener.');
    const listeners = this.#typedListeners.get(typeOrListener) ?? new Set<CodepotEventListener>();
    const listener: CodepotEventListener = (event) =>
      isCodepotEventOf(event, typeOrListener) ? maybeListener(event) : undefined;
    listeners.add(listener);
    this.#typedListeners.set(typeOrListener, listeners);
    return new EventSubscription(() => {
      listeners.delete(listener);
      if (listeners.size === 0) this.#typedListeners.delete(typeOrListener);
    });
  }
}

function isCodepotEventOf<TType extends CodepotEventType>(
  event: CodepotEvent,
  type: TType,
): event is CodepotEventOf<TType> {
  return event.type === type;
}
