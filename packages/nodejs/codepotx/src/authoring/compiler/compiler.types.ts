import type { CompiledAuthoringArtifact, Diagnostic, HashPort, ResolvedSource } from '@/contract/index';
import type { CodepotConfig } from '../config/config.types';
export interface AuthoringCompilerDependencies { readonly hash: HashPort; }
export interface AuthoringCompileInput { readonly config: CodepotConfig; readonly source: ResolvedSource; readonly includeDebugMetadata?: boolean; }
export interface AuthoringCompileOutput { readonly artifact: CompiledAuthoringArtifact; readonly diagnostics: readonly Diagnostic[]; }
export interface AuthoringCompiler { compile(input: AuthoringCompileInput): Promise<AuthoringCompileOutput>; }
