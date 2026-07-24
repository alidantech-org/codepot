import type { ComponentFieldMap } from '../component.types.js';
import type { ComponentRef, ModelRef, RequestBodyRef } from '../../refs/ref.types.js';
import type { EngineRef } from '../../refs/ref.types.js';
import type { RefUsage } from '../../refs/ref-usage.types.js';
import type { CodegenMetadata } from '../../codegen/codegen-extension.types.js';

export type RequestBodySchemaRef = ComponentRef | ModelRef | ComponentFieldMap | RefUsage<EngineRef>;

export interface RequestBodyComponentDefinition {
  readonly name: string;
  readonly schema: RequestBodySchemaRef;
  readonly required?: boolean;
  readonly description?: string;
  readonly meta?: CodegenMetadata;
}

export interface RequestBodyComponentRegistry<TRefs extends Record<string, RequestBodyRef> = Record<string, RequestBodyRef>> {
  readonly name: string;
  readonly definitions: RequestBodyComponentDefinition[];
  readonly ref: TRefs;
}
