import "server-only";

import { readFileSync } from "node:fs";
import { join } from "node:path";

import type { CodeExample } from "@/data/types";

export type WorkflowExampleKey =
  | "contract"
  | "task"
  | "paths"
  | "template";

export interface WorkflowCodeExample extends CodeExample {
  key: WorkflowExampleKey;
  eyebrow: string;
  title: string;
  description: string;
}

const EXAMPLE_ROOT = join(process.cwd(), "src", "examples", "workflow");

function readExample(relativePath: string): string {
  return readFileSync(join(EXAMPLE_ROOT, relativePath), "utf8").trimEnd();
}

export function getLandingWorkflowExamples(): WorkflowCodeExample[] {
  return [
    {
      key: "contract",
      eyebrow: "01 · Contract",
      title: "Author a real API contract",
      description:
        "Define reusable fields, schemas, resources, route parameters, request bodies, and responses with codepot-openapi.",
      filename: "codepot-openapi.config.ts",
      language: "typescript",
      code: readExample("codepot-openapi.config.ts"),
    },
    {
      key: "task",
      eyebrow: "02 · Task",
      title: "Configure CodepotG",
      description:
        "Connect the OpenAPI document to a template pack, output directory, lifecycle policy, and project commands.",
      filename: "Codepotg.yaml",
      language: "yaml",
      code: readExample("Codepotg.yaml"),
    },
    {
      key: "paths",
      eyebrow: "03 · Pack",
      title: "Plan files with paths.yaml",
      description:
        "Select normalized models and operations, map them to templates, build output paths, and publish barrel exports.",
      filename: "templates/project-sdk/paths.yaml",
      language: "yaml",
      code: readExample("paths.yaml"),
    },
    {
      key: "template",
      eyebrow: "04 · Template",
      title: "Render a Jinja template",
      description:
        "Generate a typed TypeScript model from the normalized model context while preserving optional fields and documentation.",
      filename: "templates/project-sdk/models/model.ts.j2",
      language: "jinja",
      code: readExample(join("models", "model.ts.j2")),
    },
  ];
}
