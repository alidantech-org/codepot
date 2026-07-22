import type { UseCase } from "./types";

export const USE_CASES: UseCase[] = [
  {
    title: "Backend",
    items: [
      "ORM entities",
      "Repositories",
      "DTOs",
      "Validation layers",
      "Query builders",
    ],
  },
  {
    title: "API & Schema",
    items: [
      "GraphQL schemas",
      "OpenAPI specs",
      "Zod schemas",
      "Pydantic models",
    ],
  },
  {
    title: "Frontend",
    items: ["React forms", "Admin panels", "SDKs", "Metadata registries"],
  },
];
