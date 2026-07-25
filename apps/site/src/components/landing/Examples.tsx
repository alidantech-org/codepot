import Link from "next/link";

import { CodeHighlight } from "@/components/code-highlight";
import type { CodeExample } from "@/data/types";

function CodeBlock({ example }: { example: CodeExample }) {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-background">
      <div className="flex items-center gap-2 border-b border-border bg-card-muted/60 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-green-500/60" />
        <span className="ml-3 font-mono text-[11px] text-muted-foreground">{example.filename}</span>
      </div>
      <div className="p-0">
        <CodeHighlight code={example.code} language={example.language} />
      </div>
    </div>
  );
}

interface ExamplesProps {
  contractCode: CodeExample;
  taskCode: CodeExample;
  runtimeCode: CodeExample;
}

export function Examples({ contractCode, taskCode, runtimeCode }: ExamplesProps) {
  return (
    <section id="examples" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">Workflows</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">Use today&apos;s packages and follow the stable runtime path</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        The prototype workflow already supports real projects. codepotx is the official runtime rewrite, designed so the CLI, editor tools, web clients, and MCP integrations can share the same behavior.
      </p>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">1. Author contracts</h3>
          <p className="mb-4 text-sm leading-6 text-muted-foreground">Use codepot-openapi to produce portable OpenAPI and x-codegen metadata.</p>
          <CodeBlock example={contractCode} />
        </div>
        <div className="rounded-xl border border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">2. Generate with Jinja</h3>
          <p className="mb-4 text-sm leading-6 text-muted-foreground">Use codepotg tasks and bundled or project-owned template packs.</p>
          <CodeBlock example={taskCode} />
        </div>
        <div className="rounded-xl border border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">3. Embed the runtime</h3>
          <p className="mb-4 text-sm leading-6 text-muted-foreground">Drive codepotx through the CLI or any future frontend.</p>
          <CodeBlock example={runtimeCode} />
        </div>
      </div>

      <div className="mt-6 text-sm text-muted-foreground">
        <Link href="/docs/choose-workflow" className="font-medium text-primary hover:underline">Compare workflows</Link>
        <span className="mx-2">·</span>
        <Link href="/docs/codepot-platform" className="font-medium text-foreground hover:underline">Explore the final platform</Link>
      </div>
    </section>
  );
}
