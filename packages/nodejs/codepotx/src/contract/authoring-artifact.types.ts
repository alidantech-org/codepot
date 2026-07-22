import type { ArtifactHeader, CompiledDocumentation, CompiledNamedItem } from './artifact.types';
import type { CodepotId, JsonObject, JsonValue } from './common.types';
import type { Diagnostic } from './diagnostics.types';
import type { ResolvedSource } from './sources.types';

export type CompiledPrimitiveKind =
  | 'string'
  | 'number'
  | 'integer'
  | 'boolean'
  | 'bigint'
  | 'date'
  | 'binary'
  | 'null'
  | 'unknown';

export interface CompiledSchemaConstraint {
  readonly kind: string;
  readonly value?: JsonValue;
  readonly message?: string;
  readonly metadata?: JsonObject;
}

export interface CompiledSchemaUsageBase {
  readonly required: boolean;
  readonly nullable: boolean;
  readonly readonly?: boolean;
  readonly metadata?: JsonObject;
}

export interface CompiledSchemaReferenceUse extends CompiledSchemaUsageBase {
  readonly kind: 'ref';
  readonly ref: CodepotId;
}

export interface CompiledInlineSchemaUse extends CompiledSchemaUsageBase {
  readonly kind: 'inline';
  readonly schema: CompiledInlineSchema;
}

export type CompiledSchemaUse =
  | CompiledSchemaReferenceUse
  | CompiledInlineSchemaUse;

export interface CompiledPrimitiveSchema {
  readonly kind: 'primitive';
  readonly primitive: CompiledPrimitiveKind;
  readonly format?: string;
  readonly constraints: readonly CompiledSchemaConstraint[];
  readonly defaultValue?: JsonValue;
  readonly metadata?: JsonObject;
}

export interface CompiledLiteralSchema {
  readonly kind: 'literal';
  readonly value: JsonValue;
  readonly metadata?: JsonObject;
}

export interface CompiledEnumOption {
  readonly key: string;
  readonly value: string | number;
  readonly docs?: CompiledDocumentation;
  readonly metadata?: JsonObject;
}

export interface CompiledEnumSchema {
  readonly kind: 'enum';
  readonly valueType: 'string' | 'number';
  readonly options: readonly CompiledEnumOption[];
  readonly metadata?: JsonObject;
}

export interface CompiledFieldLifecycle {
  readonly selectable: boolean;
  readonly editable: boolean;
  readonly immutable: boolean;
  readonly managed: boolean;
}

export interface CompiledFieldQuery {
  readonly enabled: boolean;
  readonly filterable: boolean;
  readonly searchable: boolean;
  readonly sortable: boolean;
  readonly operators: readonly string[];
}

export interface CompiledField extends CompiledNamedItem {
  readonly wireName: string;
  readonly schema: CompiledSchemaUse;
  readonly lifecycle: CompiledFieldLifecycle;
  readonly query: CompiledFieldQuery;
  readonly defaultValue?: JsonValue;
}

export interface CompiledObjectSchema {
  readonly kind: 'object';
  readonly fields: readonly CompiledField[];
  readonly extends: readonly CodepotId[];
  readonly additionalProperties: boolean | CompiledSchemaUse;
  readonly metadata?: JsonObject;
}

export interface CompiledArraySchema {
  readonly kind: 'array';
  readonly items: CompiledSchemaUse;
  readonly constraints: readonly CompiledSchemaConstraint[];
  readonly metadata?: JsonObject;
}

export interface CompiledTupleSchema {
  readonly kind: 'tuple';
  readonly items: readonly CompiledSchemaUse[];
  readonly rest?: CompiledSchemaUse;
  readonly metadata?: JsonObject;
}

export interface CompiledUnionSchema {
  readonly kind: 'union';
  readonly mode: 'oneOf' | 'anyOf' | 'union';
  readonly variants: readonly CompiledSchemaUse[];
  readonly discriminator?: string;
  readonly metadata?: JsonObject;
}

export interface CompiledRecordSchema {
  readonly kind: 'record';
  readonly keys?: CompiledSchemaUse;
  readonly values: CompiledSchemaUse;
  readonly metadata?: JsonObject;
}

export interface CompiledFileSchema {
  readonly kind: 'file';
  readonly mediaTypes: readonly string[];
  readonly metadata?: JsonObject;
}

export interface CompiledNoContentSchema {
  readonly kind: 'noContent';
  readonly metadata?: JsonObject;
}

export type CompiledInlineSchema =
  | CompiledPrimitiveSchema
  | CompiledLiteralSchema
  | CompiledEnumSchema
  | CompiledObjectSchema
  | CompiledArraySchema
  | CompiledTupleSchema
  | CompiledUnionSchema
  | CompiledRecordSchema
  | CompiledFileSchema
  | CompiledNoContentSchema;

export interface CompiledSchema extends CompiledNamedItem {
  readonly group: string;
  readonly schema: CompiledInlineSchema;
  readonly role?: string;
  readonly entityRef?: CodepotId;
}

export interface CompiledPropertyGroup extends CompiledNamedItem {
  readonly properties: readonly CompiledField[];
}

export interface CompiledEntityConstraint {
  readonly id: CodepotId;
  readonly kind: string;
  readonly fields: readonly CodepotId[];
  readonly rules: readonly JsonObject[];
  readonly metadata?: JsonObject;
}

export interface CompiledEntity extends CompiledNamedItem {
  readonly entityKind: 'base' | 'concrete';
  readonly fields: readonly CompiledField[];
  readonly extends?: CodepotId;
  readonly constraints: readonly CompiledEntityConstraint[];
  readonly relationIds: readonly CodepotId[];
  readonly generatedStrategy?: string;
  readonly owner?: string;
}

export interface CompiledRelation extends CompiledNamedItem {
  readonly sourceEntity: CodepotId;
  readonly targetEntity: CodepotId;
  readonly sourceField?: CodepotId;
  readonly targetField?: CodepotId;
  readonly cardinality: 'oneToOne' | 'oneToMany' | 'manyToOne' | 'manyToMany';
  readonly required: boolean;
  readonly deleteBehavior?: string;
}

export interface CompiledAccessDefinition extends CompiledNamedItem {
  readonly owner?: string;
  readonly roleSources: readonly JsonObject[];
  readonly allow: JsonObject;
}

export interface CompiledHook extends CompiledNamedItem {
  readonly owner?: string;
  readonly phase: string;
  readonly transport?: string;
  readonly inbound?: JsonObject;
  readonly outbound?: JsonObject;
}

export interface CompiledFrontend extends CompiledNamedItem {
  readonly components: readonly JsonObject[];
  readonly screens: readonly JsonObject[];
}

export type CompiledHttpMethod =
  | 'GET'
  | 'POST'
  | 'PUT'
  | 'PATCH'
  | 'DELETE'
  | 'OPTIONS'
  | 'HEAD';

export type CompiledParameterLocation = 'path' | 'query' | 'header' | 'cookie';

export interface CompiledParameter extends CompiledNamedItem {
  readonly location: CompiledParameterLocation;
  readonly schema: CompiledSchemaUse;
  readonly required: boolean;
}

export interface CompiledMediaTypeSchema {
  readonly mediaType: string;
  readonly schema?: CompiledSchemaUse;
  readonly examples?: readonly JsonValue[];
}

export interface CompiledRequestBody extends CompiledNamedItem {
  readonly required: boolean;
  readonly content: readonly CompiledMediaTypeSchema[];
}

export interface CompiledResponse extends CompiledNamedItem {
  readonly status: number | 'default';
  readonly content: readonly CompiledMediaTypeSchema[];
  readonly headers: readonly CompiledParameter[];
}

export interface CompiledOperationEffect {
  readonly kind: string;
  readonly value?: JsonValue;
  readonly metadata?: JsonObject;
}

export interface CompiledOperation extends CompiledNamedItem {
  readonly operationId: string;
  readonly resourceId: CodepotId;
  readonly method: CompiledHttpMethod;
  readonly path: string;
  readonly tags: readonly string[];
  readonly parameters: readonly CompiledParameter[];
  readonly requestBody?: CompiledRequestBody;
  readonly responses: readonly CompiledResponse[];
  readonly accessRef?: CodepotId;
  readonly hookRefs: readonly CodepotId[];
  readonly effects: readonly CompiledOperationEffect[];
  readonly cacheInvalidates: readonly string[];
}

export interface CompiledResource extends CompiledNamedItem {
  readonly route: string;
  readonly folders: readonly string[];
  readonly tags: readonly string[];
  readonly operationIds: readonly CodepotId[];
  readonly accessRef?: CodepotId;
  readonly hookRefs: readonly CodepotId[];
  readonly frontend?: JsonObject;
}

export interface CompiledProject {
  readonly name: string;
  readonly version: string;
  readonly description?: string;
  readonly license?: JsonObject;
  readonly tags: readonly string[];
  readonly defaults: JsonObject;
  readonly metadata?: JsonObject;
}

/** Canonical serializable output of the authoring engine. */
export interface CompiledAuthoringArtifact {
  readonly header: ArtifactHeader<'codepot.authoring'>;
  readonly source: ResolvedSource;
  readonly project: CompiledProject;
  readonly properties: readonly CompiledPropertyGroup[];
  readonly schemas: readonly CompiledSchema[];
  readonly entities: readonly CompiledEntity[];
  readonly relations: readonly CompiledRelation[];
  readonly resources: readonly CompiledResource[];
  readonly operations: readonly CompiledOperation[];
  readonly access: readonly CompiledAccessDefinition[];
  readonly hooks: readonly CompiledHook[];
  readonly frontends: readonly CompiledFrontend[];
  readonly metadata: JsonObject;
  readonly diagnostics: readonly Diagnostic[];
}
