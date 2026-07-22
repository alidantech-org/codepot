import type {
  CodepotRuntimePort,
  RuntimeResponse,
  SourceDescriptor,
} from "codepotx/contract";

import type { CliOptions } from "./cli.types";

export async function executeCliCommand(
  runtime: CodepotRuntimePort,
  options: CliOptions,
): Promise<RuntimeResponse | string> {
  switch (options.command) {
    case "generate":
      return runtime.execute({
        kind: "generation.execute",
        input: {
          codepotFile: codepotFileRequest(options),
          ...(options.task ? { task: options.task } : {}),
          allTasks: options.allTasks,
          dryRun: options.dryRun,
          refresh: options.refresh,
          skipBefore: options.skipBefore,
          skipAfter: options.skipAfter,
          verbose: options.verbose,
        },
      });
    case "plan": {
      const loaded = await runtime.execute({
        kind: "generation.file.load",
        input: codepotFileRequest(options),
      });
      if (!loaded.result.success) return loaded;
      return runtime.execute({
        kind: "generation.plan",
        input: {
          codepotFile: loaded.result.value,
          task: options.task ?? loaded.result.value.tasks[0]?.name ?? "",
          refresh: options.refresh,
          dryRun: true,
          skipBefore: options.skipBefore,
          skipAfter: options.skipAfter,
        },
      });
    }
    case "validate":
      return runtime.execute({
        kind: "authoring.validate",
        input: {
          source: authoringSource(options),
          projectRoot: options.projectRoot,
        },
      });
    case "inspect":
      return runtime.execute({
        kind: "authoring.inspect",
        input: {
          source: authoringSource(options),
          projectRoot: options.projectRoot,
          format: options.json ? "json" : "object",
          pretty: options.pretty,
        },
      });
    case "variables":
      return listVariables(runtime, options);
    case "features":
      return runtime.execute({ kind: "runtime.features", input: {} });
    case "version":
      return "codepotx-cli 0.0.0";
    case "help":
      return helpText();
  }
}

/**
 * The CLI performs only typed runtime orchestration: project parsing, authoring
 * compilation, template compilation, and catalog creation remain in engines.
 */
async function listVariables(
  runtime: CodepotRuntimePort,
  options: CliOptions,
): Promise<RuntimeResponse> {
  const loaded = await runtime.execute({
    kind: "generation.file.load",
    input: codepotFileRequest(options),
  });
  if (!loaded.result.success) return loaded;
  const task = options.task
    ? loaded.result.value.tasks.find((item) => item.name === options.task)
    : loaded.result.value.tasks[0];
  if (!task) return loaded;

  const authoring = await runtime.execute({
    kind: "authoring.compile",
    input: {
      source: task.authoring,
      projectRoot: loaded.result.value.root,
      cache: options.refresh ? "refresh" : "auto",
    },
  });
  if (!authoring.result.success) return authoring;

  const templates = await runtime.execute({
    kind: "templating.compile",
    input: {
      source: task.templates,
      projectRoot: loaded.result.value.root,
      cache: options.refresh ? "refresh" : "auto",
    },
  });
  if (!templates.result.success) return templates;

  return runtime.execute({
    kind: "templating.variables",
    input: {
      authoring: authoring.result.value,
      templates: templates.result.value,
      variables: task.variables ?? {},
      ...(task.frontend ? { selectedFrontend: task.frontend } : {}),
      format: options.json ? "json" : "markdown",
      pretty: options.pretty,
    },
  });
}

function codepotFileRequest(options: CliOptions): {
  readonly projectRoot: string;
  readonly file?: string;
} {
  return {
    projectRoot: options.projectRoot,
    ...(options.file ? { file: options.file } : {}),
  };
}

function authoringSource(options: CliOptions): SourceDescriptor {
  return { kind: "local", path: options.config ?? "./codepotx.config.ts" };
}

function helpText(): string {
  return [
    "Usage: codepotx <command> [options]",
    "",
    "Commands:",
    "  generate [task]   Generate files from CodepotFile.yml",
    "  plan [task]       Create and print a generation plan",
    "  validate          Validate codepotx.config.ts",
    "  inspect           Print the stable authoring artifact",
    "  variables [task]  List valid Handlebars variables, helpers, and partials",
    "  features          List runtime capabilities",
    "",
    "Options:",
    "  -r, --root <path>       Project root",
    "  -f, --file <path>       CodepotFile.yml path",
    "  -c, --config <path>     codepotx.config.ts path",
    "  -t, --task <name>       Task name",
    "      --all               Run all tasks",
    "      --dry-run           Plan/render without writes or commands",
    "      --refresh           Refresh source and authoring caches",
    "      --skip-before       Skip before commands",
    "      --skip-after        Skip after commands",
    "      --json              Emit machine-readable JSON",
    "      --pretty            Pretty-print JSON output",
    "  -v, --verbose           Print runtime events",
  ].join("\n");
}
