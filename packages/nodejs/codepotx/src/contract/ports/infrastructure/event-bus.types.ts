import type {
  Awaitable,
  Disposable,
} from '../../protocol/common.types';
import type {
  CodepotEvent,
  CodepotEventListener,
  CodepotEventType,
} from '../../events/index';

/** Observational event channel. Domain control flow must not depend on listeners. */
export interface EventBusPort {
  publish(event: CodepotEvent): Awaitable<void>;
  subscribe(listener: CodepotEventListener): Disposable;
  subscribe<TType extends CodepotEventType>(
    type: TType,
    listener: CodepotEventListener<Extract<CodepotEvent, { readonly type: TType }>>,
  ): Disposable;
}
