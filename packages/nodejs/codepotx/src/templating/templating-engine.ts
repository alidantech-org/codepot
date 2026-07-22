import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CompiledTemplateDescriptor,
  CompiledTemplateFolder,
  CompiledTemplatePack,
  Diagnostic,
  JsonObject,
  TemplateContextRequest,
  TemplateContextResult,
  TemplateContextValidateRequest,
  TemplateContextValidateResult,
  TemplateRenderRequest,
  TemplateRenderResult,
  TemplateVariableRequirement,
  TemplateVariablesRequest,
  TemplateVariablesResult,
  TemplatingCompileRequest,
  TemplatingCompileResult,
  TemplatingLoadRequest,
  TemplatingLoadResult,
  TemplatingValidateRequest,
  TemplatingValidateResult,
  VirtualFile,
} from '@/contract/index';

import { BUILTIN_TEMPLATE_HELPERS, createTemplateRenderer } from './helpers';
import { compilePathParts, compilePathTokens } from './path-tokens';
import { buildTemplateContext } from './template-context';
import { collectTemplateReferences } from './template-references';
import {
  buildTemplateVariableCatalog,
  formatTemplateVariableCatalog,
  validateTemplateContext,
} from './template-variables';
import type {
  PathsFileInput,
  TemplateVariableRequirementInput,
  TemplatingDependencies,
  TemplatingEngine,
} from './templating.types';

/** Default autonomous implementation of the public templating contracts. */
export class DefaultTemplatingEngine implements TemplatingEngine {
  readonly #dependencies: TemplatingDependencies;

  constructor(dependencies: TemplatingDependencies) {
    this.#dependencies = dependencies;
  }

  async load(request: TemplatingLoadRequest): Promise<TemplatingLoadResult> {
    return this.compile(request);
  }

  async validate(request: TemplatingValidateRequest): Promise<TemplatingValidateResult> {
    const result = await this.compile({ ...request, cache: 'bypass' });
    if (!result.success) return result;
    return success({
      valid: result.diagnostics.every((item) => item.severity !== 'error'),
      diagnostics: result.diagnostics,
    }, result.diagnostics);
  }

  async compile(request: TemplatingCompileRequest): Promise<TemplatingCompileResult> {
    try {
      const source = await this.#dependencies.sources.resolve(request.source, {
        ...(request.projectRoot ? { projectRoot: request.projectRoot } : {}),
        cache: request.cache ?? 'auto',
      });
      const pathsPath = request.pathsFile
        ? join(source.root, request.pathsFile)
        : join(source.root, 'paths.yaml');
      const config = this.#dependencies.data.parseYaml<PathsFileInput>(
        await this.#dependencies.files.readText(pathsPath),
      );
      const diagnostics = validatePaths(config);
      const extension = config.templateExtension ?? config.template_extension ?? '.hbs';
      const stripExtension = config.stripTemplateExtension ?? config.strip_template_extension ?? true;
      const includeHidden = config.includeHidden ?? config.include_hidden ?? true;
      const ignore = ['paths.yaml', ...(config.ignore ?? [])];
      const paths = await this.#dependencies.files.glob(
        includeHidden ? ['**/*', '**/.*', '**/.*/**/*'] : ['**/*'],
        { cwd: source.root, absolute: true, ignore },
      );
      const requestedHelpers = config.helpers ?? [];
      // Validate helper names once during compilation rather than failing late in render.
      createTemplateRenderer(requestedHelpers);
      const knownHelpers = new Set([
        ...BUILTIN_TEMPLATE_HELPERS.map((helper) => helper.name),
        ...requestedHelpers,
        'each', 'if', 'unless', 'with', 'lookup', 'log',
      ]);
      const templates: CompiledTemplateDescriptor[] = [];

      for (const path of [...new Set(paths)].sort()) {
        const stat = await this.#dependencies.files.stat(path);
        if (stat.kind !== 'file') continue;
        const relative = relativePath(source.root, path);
        if (ignore.some((pattern) => matchesGlob(relative, pattern))) continue;
        const isTemplate = relative.endsWith(extension);
        if (!isTemplate && !(config.allowRawFiles ?? config.allow_raw_files ?? true)) continue;
        const isPartial = isTemplate && isPartialPath(relative, config.partials ?? []);
        const stripped = isTemplate && stripExtension
          ? relative.slice(0, -extension.length)
          : relative;
        const segments = stripped.split('/');
        const marker = segments[0] ?? '';
        const markerMatch = /^\{([^}]+)\}$/.exec(marker);
        const group = isPartial ? 'partials' : markerMatch?.[1] ?? 'root';
        const folder = config.folders?.[group];
        const templatePath = markerMatch ? segments.slice(1).join('/') : stripped;
        const outputTokens = isPartial
          ? []
          : [...compilePathParts(folder?.parts ?? []), ...compilePathTokens(templatePath)];
        const lifecycle = folderLifecycle(config, group);

        if (isTemplate) {
          const text = await this.#dependencies.files.readText(path);
          const id = `template:${relative}`;
          try {
            templates.push({
              id,
              path: relative,
              kind: isPartial ? 'partial' : 'handlebars',
              group,
              outputTokens,
              ...(isPartial ? { partialName: partialNameFor(relative, extension) } : {}),
              ...(lifecycle ? { lifecycle } : {}),
              compareMode: 'exact',
              references: collectTemplateReferences(id, text, knownHelpers),
              text,
              digest: await this.#dependencies.hashes.text(text),
            });
          } catch (caught) {
            diagnostics.push(diagnostic('TEMPLATING_TEMPLATE_PARSE_FAILED', caught, { path: relative }));
          }
        } else {
          const dataBase64 = await this.#dependencies.files.readBase64(path);
          templates.push({
            id: `template:${relative}`,
            path: relative,
            kind: 'raw',
            group,
            outputTokens,
            ...(lifecycle ? { lifecycle } : {}),
            compareMode: 'raw',
            references: [],
            dataBase64,
            digest: await this.#dependencies.hashes.base64(dataBase64),
          });
        }
      }

      diagnostics.push(...validateCompiledTemplates(config, templates));
      const folders: CompiledTemplateFolder[] = Object.entries(config.folders ?? {})
        .map(([name, folder]) => ({
          name,
          parts: folder.parts ?? [],
          mode: folder.mode ?? 'once',
          ...(folder.select ? { select: folder.select } : {}),
          ...(folder.alias ?? folder.as ? { alias: folder.alias ?? folder.as } : {}),
          ...(folder.lifecycle ? { lifecycle: folder.lifecycle } : {}),
          ...(folder.description ? { description: folder.description } : {}),
          ...(folder.metadata ? { metadata: folder.metadata } : {}),
        }))
        .sort((left, right) => left.name.localeCompare(right.name));
      const variableRequirements = normalizeVariableRequirements(config.variables);
      const body = {
        source,
        manifest: {
          name: config.name ?? source.id,
          version: config.version ?? '1.0.0',
          ...(config.description ? { description: config.description } : {}),
          templateExtension: extension,
          stripTemplateExtension: stripExtension,
          allowRawFiles: config.allowRawFiles ?? config.allow_raw_files ?? true,
          includeHidden,
          ignore: [...ignore].sort(),
          helpers: [...new Set(requestedHelpers)].sort(),
          partials: templates
            .filter((template) => template.kind === 'partial' && template.partialName)
            .map((template) => template.partialName!)
            .sort(),
          variableRequirements,
          ...(config.metadata ? { metadata: config.metadata } : {}),
        },
        folders,
        writePolicy: {
          defaultMode: config.write?.defaultMode ?? config.write?.default_mode ?? 'managed',
          managedRoots: config.write?.managedRoots ?? config.write?.managed_roots ?? [],
          immutableRoots: config.write?.immutableRoots ?? config.write?.immutable_roots ?? [],
          protectedRoots: config.write?.protectedRoots ?? config.write?.protected_roots ?? [],
          cleanRoots: config.write?.cleanRoots ?? config.write?.clean_roots ?? [],
        },
        templates: templates.sort((left, right) => left.path.localeCompare(right.path)),
        files: source.files,
        diagnostics,
      } as const;
      const contentDigest = await this.#dependencies.hashes.text(
        this.#dependencies.data.stringifyJson(body),
      );
      const artifact: CompiledTemplatePack = {
        header: {
          kind: 'codepot.templates',
          protocolVersion: CODEPOT_PROTOCOL_VERSION,
          artifactVersion: CODEPOT_ARTIFACT_VERSION,
          producer: { name: 'codepotx', version: '0.0.0' },
          contentDigest,
          sourceDigest: source.digest,
        },
        ...body,
      };
      return diagnostics.some((item) => item.severity === 'error')
        ? failure(diagnostics)
        : success(artifact, diagnostics);
    } catch (caught) {
      return failure([diagnostic('TEMPLATING_COMPILE_FAILED', caught)]);
    }
  }

  async createContext(request: TemplateContextRequest): Promise<TemplateContextResult> {
    return success(buildTemplateContext(request));
  }

  async variables(request: TemplateVariablesRequest): Promise<TemplateVariablesResult> {
    try {
      const context = buildTemplateContext(request);
      const catalog = await buildTemplateVariableCatalog(context, request.templates, {
        hashes: this.#dependencies.hashes,
        data: this.#dependencies.data,
      });
      return success(
        formatTemplateVariableCatalog(catalog, request.format ?? 'object', request.pretty ?? true),
        catalog.diagnostics,
      );
    } catch (caught) {
      return failure([diagnostic('TEMPLATING_VARIABLES_FAILED', caught)]);
    }
  }

  async validateContext(request: TemplateContextValidateRequest): Promise<TemplateContextValidateResult> {
    try {
      const context = buildTemplateContext(request);
      const catalog = await buildTemplateVariableCatalog(context, request.templates, {
        hashes: this.#dependencies.hashes,
        data: this.#dependencies.data,
      });
      const validation = validateTemplateContext(catalog, request.templates, request.strict ?? true);
      return validation.valid
        ? success(validation, validation.diagnostics)
        : failure(validation.diagnostics);
    } catch (caught) {
      return failure([diagnostic('TEMPLATING_CONTEXT_VALIDATION_FAILED', caught)]);
    }
  }

  async render(request: TemplateRenderRequest): Promise<TemplateRenderResult> {
    try {
      const byId = new Map(request.templates.templates.map((template) => [template.id, template]));
      const renderer = createTemplateRenderer(request.templates.manifest.helpers);
      for (const partial of request.templates.templates.filter((template) => template.kind === 'partial')) {
        if (partial.partialName) renderer.registerPartial(partial.partialName, partial.text ?? '');
      }
      const files: VirtualFile[] = [];
      for (const item of request.files) {
        const template = byId.get(item.templateId);
        if (!template) throw new Error(`Unknown template: ${item.templateId}`);
        if (template.kind === 'partial') throw new Error(`Partial cannot be emitted directly: ${template.id}`);
        const content = template.kind === 'raw'
          ? { encoding: 'base64' as const, data: template.dataBase64 ?? '' }
          : {
              encoding: 'utf8' as const,
              text: renderer.compile(template.text ?? '', { strict: true, noEscape: true })(item.context, {
                allowCallsToHelperMissing: false,
                allowProtoMethodsByDefault: false,
                allowProtoPropertiesByDefault: false,
              }),
            };
        const serialized = content.encoding === 'utf8' ? content.text : content.data;
        files.push({
          id: `virtual:${item.outputPath}`,
          path: item.outputPath,
          lifecycle: template.lifecycle ?? request.templates.writePolicy.defaultMode,
          compareMode: template.compareMode,
          content,
          contentDigest: content.encoding === 'utf8'
            ? await this.#dependencies.hashes.text(serialized)
            : await this.#dependencies.hashes.base64(serialized),
          metadata: { templateId: template.id },
        });
      }
      return success(files);
    } catch (caught) {
      return failure([diagnostic('TEMPLATING_RENDER_FAILED', caught)]);
    }
  }
}

export function createTemplatingEngine(dependencies: TemplatingDependencies): TemplatingEngine {
  return new DefaultTemplatingEngine(dependencies);
}

function validatePaths(config: PathsFileInput): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  const roots = [
    ...(config.write?.protectedRoots ?? config.write?.protected_roots ?? []),
    ...(config.write?.cleanRoots ?? config.write?.clean_roots ?? []),
  ];
  for (const root of roots) {
    if (unsafePath(root)) diagnostics.push({
      code: 'TEMPLATING_UNSAFE_ROOT',
      severity: 'error',
      layer: 'templating',
      message: `Unsafe template write root: ${root}`,
    });
  }
  for (const [name, folder] of Object.entries(config.folders ?? {})) {
    if ((folder.mode === 'each' || folder.mode === 'group') && !folder.select) diagnostics.push({
      code: 'TEMPLATING_SELECTION_REQUIRED',
      severity: 'error',
      layer: 'templating',
      message: `Template folder "${name}" uses mode ${folder.mode} and requires select.`,
    });
  }
  return diagnostics;
}

function validateCompiledTemplates(
  config: PathsFileInput,
  templates: readonly CompiledTemplateDescriptor[],
): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  const partials = new Map<string, string>();
  for (const template of templates) {
    if (template.kind !== 'partial' || !template.partialName) continue;
    const existing = partials.get(template.partialName);
    if (existing) diagnostics.push({
      code: 'TEMPLATING_DUPLICATE_PARTIAL',
      severity: 'error',
      layer: 'templating',
      message: `Partial "${template.partialName}" is defined by both ${existing} and ${template.path}.`,
    });
    else partials.set(template.partialName, template.path);
  }
  for (const name of Object.keys(config.folders ?? {})) {
    if (!templates.some((template) => template.group === name)) diagnostics.push({
      code: 'TEMPLATING_FOLDER_WITHOUT_FILES',
      severity: 'warning',
      layer: 'templating',
      message: `Configured template folder "${name}" has no matching {${name}} files.`,
    });
  }
  if (!templates.some((template) => template.kind !== 'partial')) diagnostics.push({
    code: 'TEMPLATING_NO_EMITTABLE_FILES',
    severity: 'warning',
    layer: 'templating',
    message: 'Template pack contains no emittable templates or raw files.',
  });
  return diagnostics;
}

function normalizeVariableRequirements(
  input: PathsFileInput['variables'],
): readonly TemplateVariableRequirement[] {
  if (!input) return [];
  if (Array.isArray(input)) {
    return input.map((item) => normalizeRequirement(item, item.required ?? true))
      .sort((left, right) => left.path.localeCompare(right.path));
  }
  const grouped = input as {
    readonly required?: readonly (string | TemplateVariableRequirementInput)[];
    readonly optional?: readonly (string | TemplateVariableRequirementInput)[];
  };
  return [
    ...(grouped.required ?? []).map((item) => normalizeRequirement(item, true)),
    ...(grouped.optional ?? []).map((item) => normalizeRequirement(item, false)),
  ].sort((left, right) => left.path.localeCompare(right.path));
}

function normalizeRequirement(
  input: string | TemplateVariableRequirementInput,
  required: boolean,
): TemplateVariableRequirement {
  if (typeof input === 'string') return { path: input, required };
  return {
    path: input.path,
    required: input.required ?? required,
    ...(input.kind ? { kind: input.kind } : {}),
    ...(input.description ? { description: input.description } : {}),
  };
}

function isPartialPath(path: string, configured: readonly string[]): boolean {
  const normalized = path.replaceAll('\\', '/');
  return normalized.startsWith('_partials/')
    || normalized.includes('/_partials/')
    || normalized.startsWith('partials/')
    || normalized.includes('/partials/')
    || configured.some((pattern) => matchesGlob(normalized, pattern));
}

function partialNameFor(path: string, extension: string): string {
  const withoutExtension = path.endsWith(extension) ? path.slice(0, -extension.length) : path;
  const segments = withoutExtension.split('/');
  const marker = Math.max(segments.lastIndexOf('_partials'), segments.lastIndexOf('partials'));
  return (marker >= 0 ? segments.slice(marker + 1) : segments)
    .join('/')
    .replace(/^\{[^}]+\}\//, '');
}

function matchesGlob(path: string, pattern: string): boolean {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replaceAll('**', '::DOUBLE_STAR::')
    .replaceAll('*', '[^/]*')
    .replaceAll('::DOUBLE_STAR::', '.*')
    .replaceAll('?', '.');
  return new RegExp(`^${escaped}$`).test(path);
}

function unsafePath(path: string): boolean {
  const normalized = path.replaceAll('\\', '/');
  return normalized.startsWith('/') || normalized === '..' || normalized.startsWith('../') || normalized.includes('/../');
}

function folderLifecycle(config: PathsFileInput, group: string): 'managed' | 'immutable' | undefined {
  return config.folders?.[group]?.lifecycle;
}

function join(root: string, path: string): string {
  return `${root.replace(/[\\/]$/, '')}/${path.replace(/^[\\/]/, '')}`;
}

function relativePath(root: string, path: string): string {
  return path.replaceAll('\\', '/').replace(`${root.replaceAll('\\', '/').replace(/\/$/, '')}/`, '');
}

function diagnostic(code: string, caught: unknown, details?: JsonObject): Diagnostic {
  return {
    code,
    severity: 'error',
    layer: 'templating',
    message: caught instanceof Error ? caught.message : String(caught),
    ...(details ? { details } : {}),
  };
}

function success<T>(
  value: T,
  diagnostics: readonly Diagnostic[] = [],
): { readonly success: true; readonly value: T; readonly diagnostics: readonly Diagnostic[] } {
  return { success: true, value, diagnostics };
}

function failure(
  diagnostics: readonly Diagnostic[],
): { readonly success: false; readonly diagnostics: readonly Diagnostic[] } {
  return { success: false, diagnostics };
}
