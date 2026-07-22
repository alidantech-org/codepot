import Handlebars from 'handlebars';
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
  TemplateRenderRequest,
  TemplateRenderResult,
  TemplatingCompileRequest,
  TemplatingCompileResult,
  TemplatingLoadRequest,
  TemplatingLoadResult,
  TemplatingValidateRequest,
  TemplatingValidateResult,
  VirtualFile,
} from '@/contract/index';
import { compilePathParts, compilePathTokens } from './path-tokens';
import type { PathsFileInput, TemplatingDependencies, TemplatingEngine } from './templating.types';

export class DefaultTemplatingEngine implements TemplatingEngine {
  readonly #dependencies: TemplatingDependencies;
  constructor(dependencies: TemplatingDependencies) { this.#dependencies = dependencies; }

  async load(request: TemplatingLoadRequest): Promise<TemplatingLoadResult> { return this.compile(request); }

  async validate(request: TemplatingValidateRequest): Promise<TemplatingValidateResult> {
    const result = await this.compile({ ...request, cache: 'bypass' });
    if (!result.success) return result;
    return success({ valid: result.diagnostics.every((item) => item.severity !== 'error'), diagnostics: result.diagnostics }, result.diagnostics);
  }

  async compile(request: TemplatingCompileRequest): Promise<TemplatingCompileResult> {
    try {
      const source = await this.#dependencies.sources.resolve(request.source, {
        ...(request.projectRoot ? { projectRoot: request.projectRoot } : {}),
        cache: request.cache ?? 'auto',
      });
      const pathsPath = request.pathsFile ? join(source.root, request.pathsFile) : join(source.root, 'paths.yaml');
      const config = this.#dependencies.data.parseYaml<PathsFileInput>(await this.#dependencies.files.readText(pathsPath));
      const diagnostics = validatePaths(config);
      const extension = config.templateExtension ?? config.template_extension ?? '.hbs';
      const allFiles = await this.#dependencies.files.glob(['**/*'], { cwd: source.root, absolute: true, ignore: ['paths.yaml'] });
      const templates: CompiledTemplateDescriptor[] = [];
      for (const path of allFiles.sort()) {
        const stat = await this.#dependencies.files.stat(path);
        if (stat.kind !== 'file') continue;
        const relative = relativePath(source.root, path);
        const isTemplate = relative.endsWith(extension);
        const allowRawFiles = config.allowRawFiles ?? config.allow_raw_files ?? true;
        if (!isTemplate && !allowRawFiles) continue;
        const stripTemplateExtension = config.stripTemplateExtension ?? config.strip_template_extension ?? true;
        const outputPath = isTemplate && stripTemplateExtension ? relative.slice(0, -extension.length) : relative;
        const segments = outputPath.split('/');
        const marker = segments[0] ?? '';
        const folderMatch = /^\{([^}]+)\}$/.exec(marker);
        const group = folderMatch?.[1] ?? 'root';
        const folder = config.folders?.[group];
        const templateRelative = folderMatch ? segments.slice(1).join('/') : outputPath;
        const outputTokens = [...compilePathParts(folder?.parts ?? []), ...compilePathTokens(templateRelative)];
        if (isTemplate) {
          const text = await this.#dependencies.files.readText(path);
          templates.push({
            id: `template:${relative}`,
            path: relative,
            kind: 'handlebars',
            group,
            outputTokens,
            lifecycle: folderLifecycle(config, group),
            compareMode: 'exact',
            text,
            digest: await this.#dependencies.hashes.text(text),
          });
        } else {
          const dataBase64 = await this.#dependencies.files.readBase64(path);
          templates.push({
            id: `template:${relative}`,
            path: relative,
            kind: 'raw',
            group,
            outputTokens,
            lifecycle: folderLifecycle(config, group),
            compareMode: 'raw',
            dataBase64,
            digest: await this.#dependencies.hashes.base64(dataBase64),
          });
        }
      }
      const folders: CompiledTemplateFolder[] = Object.entries(config.folders ?? {}).map(([name, folder]) => ({
        name,
        parts: folder.parts ?? [],
        mode: folder.mode ?? 'once',
        ...(folder.select ? { select: folder.select } : {}),
        ...(folder.alias ?? folder.as ? { alias: folder.alias ?? folder.as } : {}),
        ...(folder.lifecycle ? { lifecycle: folder.lifecycle } : {}),
        ...(folder.description ? { description: folder.description } : {}),
        ...(folder.metadata ? { metadata: folder.metadata } : {}),
      }));
      const body = {
        source,
        manifest: {
          name: config.name ?? source.id,
          version: config.version ?? '1.0.0',
          ...(config.description ? { description: config.description } : {}),
          templateExtension: extension,
          stripTemplateExtension: config.stripTemplateExtension ?? config.strip_template_extension ?? true,
          allowRawFiles: config.allowRawFiles ?? config.allow_raw_files ?? true,
          helpers: config.helpers ?? [],
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
        templates,
        files: source.files,
        diagnostics,
      } as const;
      const contentDigest = await this.#dependencies.hashes.text(this.#dependencies.data.stringifyJson(body));
      const artifact: CompiledTemplatePack = {
        header: {
          kind: 'codepot.templates', protocolVersion: CODEPOT_PROTOCOL_VERSION, artifactVersion: CODEPOT_ARTIFACT_VERSION,
          producer: { name: 'codepotx', version: '0.0.0' }, contentDigest, sourceDigest: source.digest,
        },
        ...body,
      };
      return diagnostics.some((item) => item.severity === 'error') ? failure(diagnostics) : success(artifact, diagnostics);
    } catch (caught) { return failure([diagnostic('TEMPLATING_COMPILE_FAILED', caught)]); }
  }

  async createContext(request: TemplateContextRequest): Promise<TemplateContextResult> {
    const frontend = request.selectedFrontend ? request.authoring.frontends.find((item) => item.name === request.selectedFrontend) : undefined;
    return success({
      authoring: request.authoring as unknown as JsonObject,
      project: request.project ?? {},
      variables: request.variables ?? {},
      ...(frontend ? { frontend: frontend as unknown as JsonObject } : {}),
    });
  }

  async render(request: TemplateRenderRequest): Promise<TemplateRenderResult> {
    try {
      const byId = new Map(request.templates.templates.map((template) => [template.id, template]));
      const renderer = createRenderer(request.templates.manifest.helpers);
      const files: VirtualFile[] = [];
      for (const item of request.files) {
        const template = byId.get(item.templateId);
        if (!template) throw new Error(`Unknown template: ${item.templateId}`);
        const content = template.kind === 'raw'
          ? { encoding: 'base64' as const, data: template.dataBase64 ?? '' }
          : { encoding: 'utf8' as const, text: renderer.compile(template.text ?? '', { strict: true, noEscape: true })(item.context) };
        const serialized = content.encoding === 'utf8' ? content.text : content.data;
        files.push({
          id: `virtual:${item.outputPath}`,
          path: item.outputPath,
          lifecycle: template.lifecycle ?? request.templates.writePolicy.defaultMode,
          compareMode: template.compareMode,
          content,
          contentDigest: content.encoding === 'utf8' ? await this.#dependencies.hashes.text(serialized) : await this.#dependencies.hashes.base64(serialized),
          metadata: { templateId: template.id },
        });
      }
      return success(files);
    } catch (caught) { return failure([diagnostic('TEMPLATING_RENDER_FAILED', caught)]); }
  }
}

export function createTemplatingEngine(dependencies: TemplatingDependencies): TemplatingEngine { return new DefaultTemplatingEngine(dependencies); }


function createRenderer(requestedHelpers: readonly string[]): typeof Handlebars {
  const renderer = Handlebars.create();
  const helpers: Readonly<Record<string, (...args: unknown[]) => unknown>> = {
    json: (value: unknown) => JSON.stringify(value, null, 2),
    lower: (value: unknown) => String(value).toLowerCase(),
    upper: (value: unknown) => String(value).toUpperCase(),
    camel: (value: unknown) => words(value).map((word, index) => index === 0 ? word.toLowerCase() : capitalize(word)).join(''),
    pascal: (value: unknown) => words(value).map(capitalize).join(''),
    snake: (value: unknown) => words(value).map((word) => word.toLowerCase()).join('_'),
    kebab: (value: unknown) => words(value).map((word) => word.toLowerCase()).join('-'),
    eq: (left: unknown, right: unknown) => left === right,
    and: (...values: unknown[]) => values.slice(0, -1).every(Boolean),
    or: (...values: unknown[]) => values.slice(0, -1).some(Boolean),
  };
  for (const name of requestedHelpers) {
    const helper = helpers[name];
    if (!helper) throw new Error(`Unknown Handlebars helper requested by template pack: ${name}`);
    renderer.registerHelper(name, helper);
  }
  return renderer;
}
function words(value: unknown): string[] {
  return String(value).replace(/([a-z0-9])([A-Z])/g, '$1 $2').split(/[^A-Za-z0-9]+/).filter(Boolean);
}
function capitalize(value: string): string { return value.length ? value[0]!.toUpperCase() + value.slice(1).toLowerCase() : value; }

function validatePaths(config: PathsFileInput): Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  for (const root of [...(config.write?.protectedRoots ?? config.write?.protected_roots ?? []), ...(config.write?.cleanRoots ?? config.write?.clean_roots ?? [])]) {
    if (root.startsWith('/') || root.includes('..')) diagnostics.push({ code: 'TEMPLATING_UNSAFE_ROOT', severity: 'error', layer: 'templating', message: `Unsafe template write root: ${root}` });
  }
  return diagnostics;
}
function folderLifecycle(config: PathsFileInput, group: string): 'managed' | 'immutable' | undefined { return config.folders?.[group]?.lifecycle; }
function join(root: string, path: string): string { return `${root.replace(/[\\/]$/, '')}/${path.replace(/^[\\/]/, '')}`; }
function relativePath(root: string, path: string): string { return path.replaceAll('\\', '/').replace(`${root.replaceAll('\\', '/').replace(/\/$/, '')}/`, ''); }
function diagnostic(code: string, caught: unknown): Diagnostic { return { code, severity: 'error', layer: 'templating', message: caught instanceof Error ? caught.message : String(caught) }; }
function success<T>(value: T, diagnostics: readonly Diagnostic[] = []): { readonly success: true; readonly value: T; readonly diagnostics: readonly Diagnostic[] } { return { success: true, value, diagnostics }; }
function failure(diagnostics: readonly Diagnostic[]): { readonly success: false; readonly diagnostics: readonly Diagnostic[] } { return { success: false, diagnostics }; }
