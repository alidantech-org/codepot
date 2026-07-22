import type { ComponentRef, ParameterRef, PropertyRef } from '../../refs/ref.types.js';
import type { EngineRef } from '../../refs/ref.types.js';
import type { RefUsage } from '../../refs/ref-usage.types.js';
import type { ParameterLocation } from './parameter-location.js';
import type { CodegenMetadata } from '../../codegen/codegen-extension.types.js';

export type ParameterSchemaRef = PropertyRef | ComponentRef | RefUsage<EngineRef>;

export interface ParameterComponentDefinition {
  readonly key: string;
  readonly name: string;
  readonly in: ParameterLocation;
  readonly schema: ParameterSchemaRef;
  readonly required?: boolean;
  readonly description?: string;
  readonly meta?: CodegenMetadata;
}

export interface ParameterComponentRegistry<TRefs extends Record<string, ParameterRef> = Record<string, ParameterRef>> {
  readonly name: string;
  readonly definitions: ParameterComponentDefinition[];
  readonly ref: TRefs;
}
