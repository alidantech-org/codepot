import {
  ContentType,
  definePackageConfig,
  defineVersionContract,
} from "codepot-openapi";
import { z } from "zod";

const v1 = defineVersionContract({
  info: {
    title: "Acme Projects API",
    version: "1.0.0",
    description: "Project and task management contracts for Acme teams.",
  },
  defaults: {
    requestContentType: ContentType.json,
    responseContentType: ContentType.json,
  },
});

const common = v1.defineProperties("Common", {
  id: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
}).ref;

const projects = v1.defineResource({
  name: "projects",
  route: "/projects",
  tags: ["Projects"],
});

const schemas = projects.defineSchemas({
  Project: {
    id: common.id,
    name: z.string().min(2).max(120),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    description: z.string().max(2_000).nullable(),
    status: z.enum(["draft", "active", "archived"]),
    createdAt: common.createdAt,
    updatedAt: common.updatedAt,
  },
  CreateProjectInput: {
    name: z.string().min(2).max(120),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    description: z.string().max(2_000).nullable().optional(),
  },
  UpdateProjectInput: {
    name: z.string().min(2).max(120).optional(),
    description: z.string().max(2_000).nullable().optional(),
    status: z.enum(["draft", "active", "archived"]).optional(),
  },
}).ref;

projects.defineRoutes()
  .params({
    projectId: common.id,
  })
  .routes((route) => ({
    listProjects: route
      .get("/")
      .summary("List projects")
      .response(schemas.Project.array()),

    getProject: route
      .get("/:projectId")
      .summary("Get one project")
      .response(schemas.Project),

    createProject: route
      .post("/")
      .summary("Create a project")
      .body(schemas.CreateProjectInput)
      .response(schemas.Project),

    updateProject: route
      .patch("/:projectId")
      .summary("Update a project")
      .body(schemas.UpdateProjectInput)
      .response(schemas.Project),
  }));

export default definePackageConfig({
  contracts: [v1],
  output: {
    folder: "./openapi",
    filePrefix: "acme-projects",
    formats: ["json", "yaml"],
  },
});
