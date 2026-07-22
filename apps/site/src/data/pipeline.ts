import type { PipelineStep } from "./types";

export const PIPELINE_STEPS: PipelineStep[] = [
  {
    step: "01",
    description: "Define typed contracts",
    details:
      "Describe resources, schemas, fields, routes, access rules, and frontend intent in TypeScript. This becomes the shared vocabulary used by developers, tools, and AI agents.",
    icon: "FileText",
  },
  {
    step: "02",
    description: "Choose a template pack",
    details:
      "Use local, packaged, or Git-backed Handlebars templates that encode how your team writes models, services, SDKs, screens, documentation, or any other output.",
    icon: "LayoutTemplate",
  },
  {
    step: "03",
    description: "Create a consumer task",
    details:
      "A project-owned CodepotFile.yml connects the contract and templates, selects output folders, adds project variables, and defines optional formatting or validation commands.",
    icon: "Link",
  },
  {
    step: "04",
    description: "Inspect and validate",
    details:
      "List every template variable, validate paths and references before rendering, and review the deterministic plan before Codepot changes files.",
    icon: "Layers",
  },
  {
    step: "05",
    description: "Generate safely",
    details:
      "Codepot renders everything in memory, writes changed files atomically, preserves immutable or user-edited files, and records managed outputs for safe future cleanup.",
    icon: "Zap",
  },
  {
    step: "06",
    description: "Let AI build with context",
    details:
      "AI can work from the same contracts and templates instead of guessing your architecture. The broader Codepot plan includes Codepot Lang, a typed language for expressing software intent more directly.",
    icon: "Rocket",
  },
];
