import type { PipelineStep } from "./types";

export const PIPELINE_STEPS: PipelineStep[] = [
  {
    step: "01",
    description: "Define Your Domain",
    details:
      "Create typed entity configs with fields, relationships, and business rules. Use TypeScript to define your domain model once.",
    icon: "FileText",
  },
  {
    step: "02",
    description: "Infer Relationships",
    details:
      "Automatically detect entity relationships, foreign keys, and connection patterns. No manual relationship mapping required.",
    icon: "Link",
  },
  {
    step: "03",
    description: "Build Context",
    details:
      "Generate rich context objects with field metadata, validation rules, query capabilities, and mutation semantics.",
    icon: "Layers",
  },
  {
    step: "04",
    description: "Apply Templates",
    details:
      "Use Codepurify templates to render context into any language or framework. Create reusable templates for consistent architecture.",
    icon: "LayoutTemplate",
  },
  {
    step: "05",
    description: "Generate Code",
    details:
      "Produce production-ready code with proper typing, validation, and patterns. Generate DTOs, entities, APIs, and more.",
    icon: "Zap",
  },
  {
    step: "06",
    description: "Deploy Anywhere",
    details:
      "Deploy generated code to any platform. Works with Node.js, Python, Java, Go, and any framework you can template.",
    icon: "Rocket",
  },
];
