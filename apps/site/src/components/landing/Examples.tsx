"use client";

import Link from "next/link";
import { RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";

import type { CodeExample } from "@/data/types";

interface ExamplesProps {
  contractCode: CodeExample;
  taskCode: CodeExample;
  runtimeCode: CodeExample;
}

type ExampleKey = "contract" | "task" | "runtime";

const examples: Array<{
  key: ExampleKey;
  eyebrow: string;
  title: string;
  description: string;
}> = [
  {
    key: "contract",
    eyebrow: "01 · Contract",
    title: "Author typed contracts",
    description: "Use codepot-openapi to produce portable OpenAPI and x-codegen metadata.",
  },
  {
    key: "task",
    eyebrow: "02 · Generation",
    title: "Generate with Jinja",
    description: "Use codepotg tasks and bundled or project-owned template packs.",
  },
  {
    key: "runtime",
    eyebrow: "03 · Runtime",
    title: "Embed the runtime",
    description: "Drive codepotx through the CLI, editor tools, web clients, or another frontend.",
  },
];

export function Examples({ contractCode, taskCode, runtimeCode }: ExamplesProps) {
  const initialCode = useMemo(
    () => ({ contract: contractCode, task: taskCode, runtime: runtimeCode }),
    [contractCode, taskCode, runtimeCode],
  );
  const [activeKey, setActiveKey] = useState<ExampleKey>("contract");
  const [drafts, setDrafts] = useState<Record<ExampleKey, string>>({
    contract: contractCode.code,
    task: taskCode.code,
    runtime: runtimeCode.code,
  });

  const activeExample = initialCode[activeKey];

  return (
    <section id="examples" className="border-y border-border bg-card/35">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">Workflows</p>
        <h2 className="max-w-4xl text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          One editable workspace for the full Codepot flow
        </h2>
        <p className="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
          Select a workflow step to load its code into the shared editor. Your edits remain available while you move between steps.
        </p>

        <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1.45fr)_minmax(280px,0.55fr)] lg:items-stretch">
          <div className="order-2 min-w-0 overflow-hidden rounded-2xl border border-border bg-[#17100b] shadow-xl shadow-black/10 lg:order-1">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex shrink-0 items-center gap-1.5" aria-hidden="true">
                  <span className="h-2.5 w-2.5 rounded-full bg-primary" />
                  <span className="h-2.5 w-2.5 rounded-full bg-secondary" />
                  <span className="h-2.5 w-2.5 rounded-full bg-accent" />
                </div>
                <span className="truncate font-mono text-xs text-[#d8c4b0]">{activeExample.filename}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-[10px] uppercase tracking-widest text-[#a9907c]">Editable</span>
                <button
                  type="button"
                  onClick={() =>
                    setDrafts((current) => ({ ...current, [activeKey]: activeExample.code }))
                  }
                  className="inline-flex items-center gap-1.5 rounded-md border border-white/10 px-2.5 py-1.5 text-xs text-[#d8c4b0] transition-colors hover:bg-white/5 hover:text-white"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Reset
                </button>
              </div>
            </div>

            <textarea
              value={drafts[activeKey]}
              onChange={(event) =>
                setDrafts((current) => ({ ...current, [activeKey]: event.target.value }))
              }
              aria-label={`Editable ${activeExample.filename} example`}
              spellCheck={false}
              className="block min-h-[24rem] w-full resize-y bg-transparent px-4 py-5 font-mono text-[13px] leading-6 text-[#f8eadb] outline-none selection:bg-primary/35 sm:min-h-[28rem] sm:px-5 lg:min-h-[32rem]"
            />
          </div>

          <div className="order-1 grid gap-2 sm:grid-cols-3 lg:order-2 lg:grid-cols-1 lg:content-start">
            {examples.map((example) => {
              const isActive = activeKey === example.key;
              return (
                <button
                  key={example.key}
                  type="button"
                  onClick={() => setActiveKey(example.key)}
                  aria-pressed={isActive}
                  className={`group min-w-0 border-l-2 px-4 py-4 text-left transition-colors sm:border-l-0 sm:border-t-2 lg:border-l-2 lg:border-t-0 ${
                    isActive
                      ? "border-primary bg-primary/8"
                      : "border-border hover:border-primary/45 hover:bg-card-muted/45"
                  }`}
                >
                  <span className="font-mono text-[10px] uppercase tracking-widest text-primary">{example.eyebrow}</span>
                  <span className="mt-2 block text-sm font-semibold text-foreground">{example.title}</span>
                  <span className="mt-2 block text-sm leading-6 text-muted-foreground">{example.description}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-6 text-sm text-muted-foreground">
          <Link href="/docs/choose-workflow" className="font-medium text-primary hover:underline">Compare workflows</Link>
          <span className="mx-2">·</span>
          <Link href="/docs/codepot-platform" className="font-medium text-foreground hover:underline">Explore the final platform</Link>
        </div>
      </div>
    </section>
  );
}
