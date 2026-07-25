"use client";

import { javascript } from "@codemirror/lang-javascript";
import { yaml } from "@codemirror/lang-yaml";
import { oneDark } from "@codemirror/theme-one-dark";
import CodeMirror from "@uiw/react-codemirror";
import Link from "next/link";
import { useTheme } from "next-themes";
import { RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";

import type { WorkflowCodeExample, WorkflowExampleKey } from "@/data/types";

interface ExamplesProps {
  examples: WorkflowCodeExample[];
}

function languageExtension(language: string) {
  if (language === "yaml" || language === "yml") return yaml();

  return javascript({
    typescript:
      language === "typescript" ||
      language === "tsx" ||
      language === "jinja",
    jsx: language === "jsx" || language === "tsx",
  });
}

function createDrafts(
  examples: WorkflowCodeExample[],
): Record<WorkflowExampleKey, string> {
  return Object.fromEntries(
    examples.map((example) => [example.key, example.code]),
  ) as Record<WorkflowExampleKey, string>;
}

export function Examples({ examples }: ExamplesProps) {
  const { resolvedTheme } = useTheme();
  const examplesByKey = useMemo(
    () =>
      Object.fromEntries(
        examples.map((example) => [example.key, example]),
      ) as Record<WorkflowExampleKey, WorkflowCodeExample>,
    [examples],
  );
  const [activeKey, setActiveKey] = useState<WorkflowExampleKey>(
    examples[0]?.key ?? "contract",
  );
  const [drafts, setDrafts] = useState<Record<WorkflowExampleKey, string>>(
    () => createDrafts(examples),
  );

  const activeExample = examplesByKey[activeKey] ?? examples[0];
  const extensions = useMemo(
    () => (activeExample ? [languageExtension(activeExample.language)] : []),
    [activeExample],
  );

  if (!activeExample) return null;

  return (
    <section id="examples" className="border-y border-border bg-card/35">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">
          Workflows
        </p>
        <h2 className="max-w-4xl text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Real files from contract to generated code
        </h2>
        <p className="mt-4 max-w-3xl text-[15px] leading-7 text-muted-foreground">
          Each tab is loaded from a real source file in the website project. Edit
          the contract, CodepotG task, paths configuration, or Jinja template in
          the shared syntax-highlighted editor.
        </p>

        <div className="mt-8 grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(18rem,24rem)] xl:items-stretch">
          <div className="order-2 min-w-0 overflow-hidden rounded-2xl border border-border bg-[#17100b] shadow-xl shadow-black/10 xl:order-1">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex shrink-0 items-center gap-1.5" aria-hidden="true">
                  <span className="h-2.5 w-2.5 rounded-full bg-primary" />
                  <span className="h-2.5 w-2.5 rounded-full bg-secondary" />
                  <span className="h-2.5 w-2.5 rounded-full bg-accent" />
                </div>
                <span className="truncate font-mono text-xs text-[#d8c4b0]">
                  {activeExample.filename}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-[10px] uppercase tracking-widest text-[#a9907c]">
                  Editable preview
                </span>
                <button
                  type="button"
                  onClick={() =>
                    setDrafts((current) => ({
                      ...current,
                      [activeKey]: activeExample.code,
                    }))
                  }
                  className="inline-flex items-center gap-1.5 rounded-md border border-white/10 px-2.5 py-1.5 text-xs text-[#d8c4b0] transition-colors hover:bg-white/5 hover:text-white"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Reset
                </button>
              </div>
            </div>

            <CodeMirror
              value={drafts[activeKey] ?? activeExample.code}
              onChange={(value) =>
                setDrafts((current) => ({
                  ...current,
                  [activeKey]: value,
                }))
              }
              extensions={extensions}
              theme={resolvedTheme === "dark" ? oneDark : "light"}
              height="clamp(30rem, 58vw, 44rem)"
              width="100%"
              basicSetup={{
                lineNumbers: true,
                foldGutter: true,
                highlightActiveLine: true,
                highlightActiveLineGutter: true,
                bracketMatching: true,
                closeBrackets: true,
                autocompletion: true,
                indentOnInput: true,
                syntaxHighlighting: true,
              }}
              aria-label={`Editable ${activeExample.filename} example`}
              className="w-full min-w-0 overflow-hidden text-[13px] [&_.cm-content]:min-w-max [&_.cm-content]:py-4 [&_.cm-editor]:w-full [&_.cm-editor]:bg-transparent [&_.cm-gutters]:border-r [&_.cm-gutters]:border-border/50 [&_.cm-scroller]:overflow-auto [&_.cm-scroller]:font-mono [&_.cm-scroller]:leading-6"
            />
          </div>

          <div className="order-1 grid gap-2 sm:grid-cols-2 xl:order-2 xl:grid-cols-1 xl:content-start">
            {examples.map((example) => {
              const isActive = activeKey === example.key;
              return (
                <button
                  key={example.key}
                  type="button"
                  onClick={() => setActiveKey(example.key)}
                  aria-pressed={isActive}
                  className={`group min-w-0 border-l-2 px-4 py-4 text-left transition-colors sm:border-l-0 sm:border-t-2 xl:border-l-2 xl:border-t-0 ${
                    isActive
                      ? "border-primary bg-primary/8"
                      : "border-border hover:border-primary/45 hover:bg-card-muted/45"
                  }`}
                >
                  <span className="font-mono text-[10px] uppercase tracking-widest text-primary">
                    {example.eyebrow}
                  </span>
                  <span className="mt-2 block text-sm font-semibold text-foreground">
                    {example.title}
                  </span>
                  <span className="mt-2 block text-sm leading-6 text-muted-foreground">
                    {example.description}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-6 text-sm text-muted-foreground">
          <Link href="/docs/prototype-workflow" className="font-medium text-primary hover:underline">
            Read the complete prototype workflow
          </Link>
          <span className="mx-2">·</span>
          <Link href="/docs/template-packs" className="font-medium text-foreground hover:underline">
            Learn about template packs
          </Link>
        </div>
      </div>
    </section>
  );
}
