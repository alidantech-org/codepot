import type { CodeExample } from "@/data/types";
import { CodeHighlight } from "@/components/code-highlight";

interface CodeBlockProps {
  example: CodeExample;
}

function CodeBlock({ example }: CodeBlockProps) {
  return (
    <div className="overflow-hidden rounded-xl border-border bg-background">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-border bg-card-muted/60 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-green-500/60" />
        <span className="ml-3 font-mono text-[11px] text-muted-foreground">
          {example.filename}
        </span>
      </div>
      {/* Code */}
      <div className="p-0">
        <CodeHighlight code={example.code} language={example.language} />
      </div>
    </div>
  );
}

interface ExamplesProps {
  entityCode: CodeExample;
  templateCode: CodeExample;
  outputCode: CodeExample;
}

export function Examples({
  entityCode,
  templateCode,
  outputCode,
}: ExamplesProps) {
  return (
    <section id="examples" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">
        Examples
      </p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">
        Define Once, Generate Everywhere
      </h2>
      <p className="mb-12 max-w-xl text-[15px] leading-7 text-muted-foreground">
        Single source of truth for your domain. Generate consistent architecture
        across any language or framework without repetitive AI prompts.
      </p>

      {/* Simple examples grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-xl border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">Domain Config</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Define your entities once with language-neutral facts
          </p>
          <CodeBlock example={entityCode} />
        </div>

        <div className="rounded-xl border-border bg-card  p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">Template Logic</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Simple Codepurify templates render your deterministic context
          </p>
          <CodeBlock example={templateCode} />
        </div>

        <div className="rounded-xl border-border bg-card  p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">Generated Code</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Consistent output across any language or framework
          </p>
          <CodeBlock example={outputCode} />
        </div>
      </div>
    </section>
  );
}
