import type {
  RuntimeFeatureQuery,
  RuntimeFeatureResult,
  RuntimeOperationKind,
  RuntimeRequest,
  RuntimeResponse,
} from '../../operations/runtime/index';
import type { EventBusPort } from '../infrastructure/event-bus.types';

/** Shared runtime facade consumed by CLI, IDE, UI, and programmatic frontends. */
export interface CodepotRuntimePort {
  readonly events: EventBusPort;

  execute<TKind extends RuntimeOperationKind>(
    request: RuntimeRequest<TKind>,
  ): Promise<RuntimeResponse<TKind>>;

  features(query?: RuntimeFeatureQuery): Promise<RuntimeFeatureResult>;
}
