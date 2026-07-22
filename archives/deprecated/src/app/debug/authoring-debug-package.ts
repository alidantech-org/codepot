// src/app/debug/authoring-debug-package.ts

import type { CodepotConfig } from '@/contract/types/authoring/1.codepot-config.types';

import { toDebugAuthoringJson } from '@/contract/debug/to-debug-authoring-json';

import { createFileSystemManager, type FileSystemManager } from '@/utils/filesystem';

import { serializeJson, serializeYaml } from '@/utils/serializers';

// ============================================================================
// TYPES
// ============================================================================

export interface AuthoringDebugPackage {
  readonly contracts: readonly unknown[];
}

export interface WriteAuthoringDebugPackageOptions {
  readonly file_system?: FileSystemManager;
}

export interface WriteAuthoringDebugPackageResult {
  readonly files: readonly string[];
}

// ============================================================================
// EMIT
// ============================================================================

/**
 * Converts authoring contracts into debug-friendly JSON.
 *
 * This does not compile to IR. It only shows the authoring/debug shape.
 */
export function emitAuthoringDebugPackage(config: CodepotConfig): AuthoringDebugPackage {
  return {
    contracts: config.contracts.map((contract) => toDebugAuthoringJson(contract.snapshot())),
  };
}

// ============================================================================
// SERIALIZE
// ============================================================================

/**
 * Serializes the authoring debug package as JSON.
 */
export function serializeAuthoringDebugPackageJson(config: CodepotConfig): string {
  return serializeJson(emitAuthoringDebugPackage(config));
}

/**
 * Serializes the authoring debug package as YAML.
 */
export function serializeAuthoringDebugPackageYaml(config: CodepotConfig): string {
  return serializeYaml(emitAuthoringDebugPackage(config));
}

// ============================================================================
// WRITE
// ============================================================================

/**
 * Writes authoring debug JSON/YAML output files.
 */
export async function writeAuthoringDebugPackage(
  config: CodepotConfig,
  options: WriteAuthoringDebugPackageOptions = {},
): Promise<WriteAuthoringDebugPackageResult> {
  const fileSystem = options.file_system ?? createFileSystemManager();

  const folder = config.output?.folder ?? 'debug';
  const baseName = config.output?.baseName ?? 'codepot';

  await fileSystem.ensureDirectory(folder);

  const jsonPath = fileSystem.joinPath(folder, `${baseName}.authoring.json`);
  const yamlPath = fileSystem.joinPath(folder, `${baseName}.authoring.yaml`);

  await fileSystem.writeTextFile({
    path: jsonPath,
    content: serializeAuthoringDebugPackageJson(config),
  });

  await fileSystem.writeTextFile({
    path: yamlPath,
    content: serializeAuthoringDebugPackageYaml(config),
  });

  return {
    files: [fileSystem.toPosixPath(jsonPath), fileSystem.toPosixPath(yamlPath)],
  };
}
