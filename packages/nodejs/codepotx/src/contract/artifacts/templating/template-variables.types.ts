import type { ArtifactHeader } from '../../protocol/artifact.types';
import type { JsonObject, JsonValue } from '../../protocol/common.types';
import type { Diagnostic } from '../../diagnostics/diagnostic.types';

/** JSON-level value kinds that a template author may reference. */
export type TemplateVariableKind =
  | 'object'
  | 'array'
  | 'string'
  | 'number'
  | 'boolean'
  | 'null'
  | 'unknown';

/** Logical context area that owns a template variable. */
export type TemplateVariableScope =
  | 'root'
  | 'project'
  | 'authoring'
  | 'resource'
  | 'schema'
  | 'field'
  | 'entity'
  | 'operation'
  | 'parameter'
  | 'requestBody'
  | 'response'
  | 'frontend'
  | 'variables'
  | 'language'
  | 'emit'
  | 'file'
  | 'runtime';

export type TemplateVariableOriginLayer =
  | 'authoring'
  | 'templating'
  | 'generation'
  | 'project'
  | 'task'
  | 'derived'
  | 'runtime';

/** Explains where a variable came from without exposing implementation objects. */
export interface TemplateVariableOrigin {
  readonly layer: TemplateVariableOriginLayer;
  readonly path?: string;
  readonly ref?: string;
  readonly description?: string;
}

/** One flattened deterministic entry in the public template context contract. */
export interface TemplateVariableEntry {
  readonly path: string;
  readonly name: string;
  readonly kind: TemplateVariableKind;
  readonly scope: TemplateVariableScope;
  readonly required: boolean;
  readonly nullable: boolean;
  readonly itemKind?: TemplateVariableKind;
  readonly description?: string;
  readonly examples?: readonly JsonValue[];
  readonly origins: readonly TemplateVariableOrigin[];
  readonly metadata?: JsonObject;
}

export interface TemplateHelperArgument {
  readonly name: string;
  readonly required: boolean;
  readonly description?: string;
}

/** Safe helper exposed by the Codepot Handlebars runtime. */
export interface TemplateHelperDescriptor {
  readonly name: string;
  readonly description: string;
  readonly arguments: readonly TemplateHelperArgument[];
  readonly returns: TemplateVariableKind;
  readonly block: boolean;
}

/** Registered partial that can be referenced by `{{> name}}`. */
export interface TemplatePartialDescriptor {
  readonly name: string;
  readonly templateId: string;
  readonly path: string;
}

export type TemplateReferenceKind =
  | 'variable'
  | 'helper'
  | 'partial'
  | 'data'
  | 'blockParameter';

export interface TemplateReferenceLocation {
  readonly line: number;
  readonly column: number;
  readonly endLine?: number;
  readonly endColumn?: number;
}

/** Static reference collected from Handlebars source without executing it. */
export interface TemplateReference {
  readonly templateId: string;
  readonly kind: TemplateReferenceKind;
  readonly name: string;
  readonly raw: string;
  readonly resolvedPath?: string;
  readonly location?: TemplateReferenceLocation;
}

/** A template-pack declaration that narrows the shared context contract. */
export interface TemplateVariableRequirement {
  readonly path: string;
  readonly required: boolean;
  readonly kind?: TemplateVariableKind;
  readonly description?: string;
}

export interface TemplateReferenceValidation {
  readonly reference: TemplateReference;
  readonly valid: boolean;
  readonly resolvedPath?: string;
  readonly reason?: string;
}

/** Versioned variable catalog consumed by CLI, IDEs, generators, and docs. */
export interface TemplateVariableCatalog {
  readonly header: ArtifactHeader<'codepot.template-variables'>;
  readonly roots: readonly string[];
  readonly entries: readonly TemplateVariableEntry[];
  readonly helpers: readonly TemplateHelperDescriptor[];
  readonly partials: readonly TemplatePartialDescriptor[];
  readonly dataVariables: readonly TemplateVariableEntry[];
  readonly requirements: readonly TemplateVariableRequirement[];
  readonly diagnostics: readonly Diagnostic[];
}

/** Complete pre-render validation result for one template context. */
export interface TemplateContextValidation {
  readonly valid: boolean;
  readonly catalog: TemplateVariableCatalog;
  readonly references: readonly TemplateReferenceValidation[];
  readonly diagnostics: readonly Diagnostic[];
}
