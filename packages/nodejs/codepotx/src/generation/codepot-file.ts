import type {
  CodepotCommandConfig,
  CodepotTaskConfig,
  CompiledCodepotFile,
  JsonObject,
  SourceDescriptor,
} from '@/contract/index';
import type {
  CodepotCommandInput,
  CodepotFileInput,
  CodepotTaskInput,
  SourceInput,
} from './generation.types';

export function compileCodepotFile(input: CodepotFileInput, path: string, root: string): CompiledCodepotFile {
  const sources = input.sources ?? {};
  const entries = Array.isArray(input.tasks)
    ? input.tasks.map((task, index) => [task.name ?? `task-${index + 1}`, task] as const)
    : Object.entries(input.tasks ?? {});
  const tasks = entries.map(([name, task]) => normalizeTask(name, task, sources, input.defaults ?? {}));
  if (tasks.length === 0) throw new Error('CodepotFile.yml must define at least one task.');
  return { path, root, allow: input.allow === true, defaults: input.defaults ?? {}, tasks };
}

export function findTask(file: CompiledCodepotFile, name: string | undefined): CodepotTaskConfig {
  if (!name) {
    if (file.tasks.length === 1) return file.tasks[0]!;
    throw new Error('A task name is required when CodepotFile.yml defines multiple tasks.');
  }
  const task = file.tasks.find((item) => item.name === name);
  if (!task) throw new Error(`Unknown generation task: ${name}`);
  return task;
}

function normalizeTask(
  name: string,
  task: CodepotTaskInput,
  sources: Readonly<Record<string, SourceInput>>,
  defaults: JsonObject,
): CodepotTaskConfig {
  const authoringInput: SourceInput = task.authoring ?? task.input ?? './codepotx.config.ts';
  const templateInput: SourceInput = task.templates ?? task.template_dir ?? './templates';
  const transactional = defaults['transactional'];
  const output = defaults['output'];
  const defaultTransactional = typeof transactional === 'boolean' ? transactional : true;
  return {
    name,
    ...(task.description ? { description: task.description } : {}),
    authoring: normalizeSource(authoringInput, sources, 'codepotx.config.ts'),
    templates: normalizeSource(templateInput, sources, 'paths.yaml'),
    output: task.output ?? String(output ?? './generated'),
    clean: [...(task.clean ?? [])],
    before: (task.before ?? []).map(normalizeCommand),
    after: (task.after ?? []).map(normalizeCommand),
    environment: { ...(task.env ?? {}), ...(task.environment ?? {}) },
    ...(task.variables ? { variables: task.variables } : {}),
    ...(task.frontend ? { frontend: task.frontend } : {}),
    transactional: task.transactional ?? defaultTransactional,
    ...(task.manifest ? { manifest: task.manifest } : {}),
  };
}

function normalizeCommand(command: CodepotCommandInput): CodepotCommandConfig {
  return {
    ...(command.name ? { name: command.name } : {}),
    run: command.run,
    ...(command.cwd ? { cwd: command.cwd } : {}),
    optional: command.optional ?? false,
    environment: { ...(command.env ?? {}), ...(command.environment ?? {}) },
  };
}

function normalizeSource(
  input: SourceInput,
  sources: Readonly<Record<string, SourceInput>>,
  defaultEntry: string,
): SourceDescriptor {
  if (typeof input === 'string') {
    const named = sources[input];
    if (named !== undefined) return normalizeSource(named, sources, defaultEntry);
    return input.endsWith('.ts') || input.endsWith('.json') || input.endsWith('.yaml') || input.endsWith('.yml')
      ? { kind: 'local', path: input }
      : { kind: 'local', path: input, entry: defaultEntry };
  }
  if ('kind' in input && input.kind) return input as SourceDescriptor;
  const kind = input.type ?? 'local';
  if (kind === 'local') return { kind, path: input.path ?? '.', ...(input.entry ? { entry: input.entry } : { entry: defaultEntry }) };
  if (kind === 'package') return { kind, package: input.package ?? '', ...(input.version ? { version: input.version } : {}), ...(input.path ? { path: input.path } : {}), ...(input.entry ? { entry: input.entry } : {}) };
  if (kind === 'git') return { kind, repository: input.repository ?? '', ...(input.ref ? { ref: input.ref } : {}), ...(input.path ? { path: input.path } : {}), ...(input.entry ? { entry: input.entry } : {}) };
  if (kind === 'artifact') return { kind, path: input.path ?? '' };
  return { kind: 'memory', id: input.id ?? '', ...(input.entry ? { entry: input.entry } : {}) };
}
