import type { UseCase } from "./types";

export const USE_CASES: UseCase[] = [
  {
    title: "API and platform teams",
    items: [
      "Author typed OpenAPI contracts",
      "Share schemas and route intent",
      "Preserve x-codegen metadata",
      "Generate SDKs and application layers",
      "Keep API decisions reviewable",
    ],
  },
  {
    title: "Template and product teams",
    items: [
      "Reuse Jinja or Handlebars packs",
      "Preserve real project conventions",
      "Plan and preview generated files",
      "Protect edited and immutable files",
      "Control generation in each project",
    ],
  },
  {
    title: "Tooling and AI builders",
    items: [
      "Embed a frontend-neutral runtime",
      "Build CLI, web, editor, or MCP clients",
      "Use compiler-grade diagnostics",
      "Read target-neutral semantic artifacts",
      "Reduce repeated repository discovery",
    ],
  },
];
