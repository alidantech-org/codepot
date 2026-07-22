import type { PackageOutputFormat } from "../config/package-config.types.js";

export function createOpenApiFileName(
  prefix: string,
  version: string,
  format: PackageOutputFormat,
): string {
  return `${prefix}.${normalizeVersion(version)}.${format}`;
}

export function createDebugFileName(prefix: string, version: string): string {
  return `${prefix}.${normalizeVersion(version)}.json`;
}

function normalizeVersion(version: string): string {
  return version
    .trim()
    .toLowerCase()
    .replace(/^v/, "v")
    .replace(/[^a-z0-9._-]+/g, "-");
}
