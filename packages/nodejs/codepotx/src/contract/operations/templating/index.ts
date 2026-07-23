import type { CompiledAuthoringArtifact } from '../../artifacts/authoring/index';
import type { VirtualFile } from '../../artifacts/generation/index';
import type {
  CompiledTemplatePack,
  TemplateContextValidation,
  TemplateVariableCatalog,
} from '../../artifacts/templating/index';
import type { OperationResult, ValidationResult } from '../../diagnostics/index';
import type { JsonObject, PortablePath } from '../../protocol/common.types';
import type { SourceDescriptor } from '../../sources/source.types';
import type { CacheMode } from '../cache-mode.types';

export interface TemplatingLoadRequest {
  readonly source: SourceDescriptor;
  readonly projectRoot?: PortablePath;
  readonly pathsFile?: PortablePath;
  readonly cache?: CacheMode;
}

export interface TemplatingValidateRequest extends TemplatingLoadRequest {}
export interface TemplatingCompileRequest extends TemplatingLoadRequest {}

export interface TemplateContextRequest {
  readonly authoring: CompiledAuthoringArtifact;
  readonly templates: CompiledTemplatePack;
  readonly project?: JsonObject;
  readonly selectedFrontend?: string;
  readonly variables?: JsonObject;
  readonly language?: JsonObject;
  readonly emit?: JsonObject;
  readonly file?: JsonObject;
}

export interface TemplateVariablesRequest extends TemplateContextRequest {
  readonly format?: 'object' | 'json' | 'markdown';
  readonly pretty?: boolean;
}

export interface TemplateContextValidateRequest extends TemplateContextRequest {
  readonly strict?: boolean;
}

export interface TemplateRenderRequest {
  readonly templates: CompiledTemplatePack;
  readonly files: readonly {
    readonly templateId: string;
    readonly outputPath: PortablePath;
    readonly context: JsonObject;
  }[];
}

export type TemplatingLoadResult = OperationResult<CompiledTemplatePack>;
export type TemplatingValidateResult = OperationResult<ValidationResult>;
export type TemplatingCompileResult = OperationResult<CompiledTemplatePack>;
export type TemplateContextResult = OperationResult<JsonObject>;
export type TemplateVariablesResult = OperationResult<TemplateVariableCatalog | string>;
export type TemplateContextValidateResult = OperationResult<TemplateContextValidation>;
export type TemplateRenderResult = OperationResult<readonly VirtualFile[]>;
