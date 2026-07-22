import type { CompileOptions } from "../compiler/compile-options.types.js";
import type { PackageConfig } from "./package-config.types.js";

export function resolveCompileOptions(config: PackageConfig): CompileOptions {
  return {
    ...config.compile,
    servers: config.server
      ? [
          {
            url: config.server.url,
            description: config.server.description,
          },
        ]
      : config.compile?.servers,
  };
}
