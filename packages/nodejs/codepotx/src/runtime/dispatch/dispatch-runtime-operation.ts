import type {
  RunContext,
  RuntimeOperationKind,
  RuntimeOperationMap,
} from '@/contract/index';
import type { RuntimeOperationHandlerRegistry } from './runtime-handler.types';

export function dispatchRuntimeOperation<TKind extends RuntimeOperationKind>(
  handlers: RuntimeOperationHandlerRegistry,
  kind: TKind,
  input: RuntimeOperationMap[TKind]['request'],
  context: RunContext,
): Promise<RuntimeOperationMap[TKind]['result']> {
  return handlers[kind](input, context);
}
