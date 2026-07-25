import Link from "next/link";

import { CodeHighlight } from "@/components/code-highlight";
import type { CodeExample } from "@/data/types";

function CodeBlock({ example }: { example: CodeExample }) {
  return (
    <div className="border-y border-border bg-card/20">
      <div className="flex items-center gap-2 border-b border-border px-1 py-3">
        <span className="h-2 w-2 rounded-full bg-primary/60" />
        <span className="h-2 w-2 rounded-full bg-secondary/60" />
        <span className="h-2 w-2 rounded-full bg-accent/70" />
        <span className="ml-2 font-mono text-[11px] text-muted-foreground">{example.filename}</span>
      </div>
      <CodeHighlight code={example.code} language={example.language} />
    </div>
  );
}

interface ExamplesProps {
  contractCode: CodeExample;
  taskCode: CodeExample;
  runtimeCode: CodeExample;
}

const examples = [
  {
    title: "1. Author contracts",
    description: "Use codepot-openapi to produce portable OpenAPI and x-codegen metadata.",
    key: "contract" as const,
  },
  {
    title: "2. Generate with Jinja",
    description: "Use codepotg tasks and bundled or project-owned template packs.",
    key: "task" as const,
  },
  {
    title: "3. Embed the runtime",
    description: "Drive codepotx through the CLI or any future frontend.",
    key: "runtime" as const,
  },
];

export function Examples({ contractCode, taskCode, runtimeCode }: ExamplesProps) {
  const code = { contract: contractCode, task: taskCode, runtime: runtimeCode };

  return (
    <section id="examples" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">Workflows</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">Use today&apos;s packages and follow the stable runtime path</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        The prototype workflow already supports real projects. codepotx is the official runtime rewrite, designed so the CLI, editor tools, web clients, and MCP integrations can share the same behavior.
      </p>

      <div className="grid grid-cols-1 gap-10 border-y border-border py-8 md:grid-cols-3 md:gap-0">
        {examples.map((example) => (
          <div key={example.key} className="md:border-l md:border-border md:px-6 first:md:border-l-0 first:md:pl-0 last:md:pr-0">
            <h3 className="mb-3 font-semibold text-foreground">{example.title}</h3>
            <p className="mb-5 min-h-12 text-sm leading-6 text-muted-foreground">{example.description}</p>
            <CodeBlock example={code[example.key]} />
          </div>
        ))}
      </div>

      <div className="mt-6 text-sm text-muted-foreground">
        <Link href="/docs/choose-workflow" className="font-medium text-primary hover:underline">Compare workflows</Link>
        <span className="mx-2">·</span>
        <Link href="/docs/codepot-platform" className="font-medium text-foreground hover:underline">Explore the final platform</Link>
      </div>
    </section>
  );
}
