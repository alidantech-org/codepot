import type { CodeExample } from "./types";

export const CONTRACT_CODE: CodeExample = {
  filename: "codepot-openapi.config.ts",
  language: "typescript",
  code: `import {
  definePackageConfig,
  defineVersionContract,
} from "codepot-openapi";

const v1 = defineVersionContract({
  info: { title: "Example API", version: "v1" },
});

export default definePackageConfig({
  contracts: [v1],
  output: { formats: ["json", "yaml"] },
});`,
};

export const TASK_CODE: CodeExample = {
  filename: "Codepotg.yaml",
  language: "yaml",
  code: `allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
    # templateDir is optional;
    # bundled packs are available.`,
};

export const RUNTIME_CODE: CodeExample = {
  filename: "run-codepotx.ts",
  language: "typescript",
  code: `import {
  createDefaultCodepotRuntime,
} from "codepotx/runtime";

const runtime = createDefaultCodepotRuntime({
  projectRoot: process.cwd(),
});

await runtime.execute({
  kind: "generation.plan",
  input: { task: "sdk" },
});`,
};
