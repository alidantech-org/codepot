import type {
  RunContext,
  RuntimeOperationKind,
  RuntimeOperationMap,
} from '@/contract/index';

export type RuntimeOperationHandler<TKind extends RuntimeOperationKind> = (
  input: RuntimeOperationMap[TKind]['request'],
  context: RunContext,
) => Promise<RuntimeOperationMap[TKind]['result']>;

export type RuntimeOperationHandlerRegistry = {
  readonly [TKind in RuntimeOperationKind]: RuntimeOperationHandler<TKind>;
};
