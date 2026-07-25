import type { PipelineStep } from "./types";

export const PIPELINE_STEPS: PipelineStep[] = [
  {
    step: "01",
    description: "Prove contract ideas in codepot-openapi",
    details:
      "The supported TypeScript prototype validates authoring patterns against real APIs and emits standards-based OpenAPI plus generator-focused metadata.",
    icon: "FileText",
  },
  {
    step: "02",
    description: "Prove generation ideas in codepotg",
    details:
      "The supported Python runtime consumes OpenAPI, builds a normalized model, and exercises Jinja template packs, write policies, diagnostics, and project tasks in real applications.",
    icon: "LayoutTemplate",
  },
  {
    step: "03",
    description: "Stabilize validated behavior in codepotx",
    details:
      "The official JavaScript rewrite separates contracts, authoring, templating, generation, platform adapters, and runtime operations behind stable typed artifacts.",
    icon: "Layers",
  },
  {
    step: "04",
    description: "Expose one runtime through many frontends",
    details:
      "codepotx-cli is only the terminal frontend. Web tools, editor extensions, MCP servers, desktop applications, and embedded Node.js clients can drive the same runtime operations.",
    icon: "Link",
  },
  {
    step: "05",
    description: "Move semantic meaning into Codepot Lang",
    details:
      "The Rust language, standard library, compiler, IR, analysis host, formatter, CLI, LSP, and extension make software intent a first-class typed platform rather than a TypeScript-only configuration model.",
    icon: "Zap",
  },
  {
    step: "06",
    description: "Give developers and AI the same truth",
    details:
      "Contracts, semantic artifacts, diagnostics, plans, and templates become shared material for human review, deterministic tools, and future AI integrations through Codepot MCP.",
    icon: "Rocket",
  },
];
