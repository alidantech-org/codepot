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
  templateCode: CodeExample;
  taskCode: CodeExample;
}

export function Examples({ contractCode, templateCode, taskCode }: ExamplesProps) {
  return (
    <section id="examples" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">Examples</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">The three layers stay simple</h2>
      <p className="mb-12 max-w-xl text-[15px] leading-7 text-muted-foreground">
        Your contract describes software intent, templates describe the code style, and each consuming project decides how generation runs.
      </p>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">1. Typed contract</h3>
          <p className="mb-4 text-sm text-muted-foreground">A shared TypeScript description of the software.</p>
          <CodeBlock example={contractCode} />
        </div>
        <div className="rounded-xl border border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">2. Template pack</h3>
          <p className="mb-4 text-sm text-muted-foreground">Reusable Handlebars files encode team patterns.</p>
          <CodeBlock example={templateCode} />
        </div>
        <div className="rounded-xl border border-border bg-card p-6 px-3">
          <h3 className="mb-3 font-semibold text-foreground">3. Consumer task</h3>
          <p className="mb-4 text-sm text-muted-foreground">The project owns output, cleanup, and commands.</p>
          <CodeBlock example={taskCode} />
        </div>
      </div>
    </section>
  );
}
