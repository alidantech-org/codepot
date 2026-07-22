import type { CodeExample } from "./types";

export const CONTRACT_CODE: CodeExample = {
  filename: "codepotx.config.ts",
  language: "typescript",
  code: `import { defineCodepotConfig, schema } from "codepotx";

const Email = schema.primitive(
  schema.string().email(),
);

export default defineCodepotConfig({
  project: { name: "rescue-platform" },
  contracts: [v1],
});`,
};

export const TEMPLATE_CODE: CodeExample = {
  filename: "{model}/[model.name.kebab].ts.hbs",
  language: "handlebars",
  code: `export interface {{model.name.pascal}} {
{{#each model.fields}}
  {{name.camel}}: {{lang.type}};
{{/each}}
}

// Exact imports and output facts are available
// through file, emit, imports, and dependencies.`,
};

export const TASK_CODE: CodeExample = {
  filename: "CodepotFile.yml",
  language: "yaml",
  code: `allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates/typescript
    output: ./src/generated
    clean: [models]
    transactional: true`,
};
