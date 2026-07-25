import Link from "next/link";
import { ArrowRight, BookOpen, Boxes, Braces, Languages } from "lucide-react";

import { getAllDocs } from "@/lib/docs";
import { ecosystem } from "@/lib/ecosystem";

const groupIcons = {
  Start: BookOpen,
  Packages: Boxes,
  "Codepot Platform": Languages,
  Concepts: Braces,
} as const;

export default function DocsPage() {
  const docs = getAllDocs();
  const grouped = docs.reduce<Record<string, typeof docs>>((output, doc) => {
    const group = doc.group ?? "Documentation";
    output[group] ??= [];
    output[group].push(doc);
    return output;
  }, {});

  return (
    <div className="mx-auto w-full max-w-5xl px-4 md:px-6">
      <section className="border-b border-border pb-10">
        <p className="mb-3 font-mono text-xs uppercase tracking-widest text-primary">Documentation</p>
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Understand the whole Codepot ecosystem
        </h1>
        <p className="mt-4 max-w-3xl text-lg leading-8 text-muted-foreground">
          Learn the supported prototype workflow, the official JavaScript runtime, and the Rust language platform from one documentation source maintained in the repository&apos;s root docs directory.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link href="/docs/getting-started" className="inline-flex h-10 items-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-5 text-sm font-medium text-white">
            Start here <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/docs/choose-workflow" className="inline-flex h-10 items-center rounded-full border border-border px-5 text-sm text-foreground transition-colors hover:bg-card-muted">
            Choose a workflow
          </Link>
        </div>
      </section>

      <section className="grid gap-4 border-b border-border py-10 lg:grid-cols-3">
        {ecosystem.stages.map((stage) => (
          <div key={stage.id} className="rounded-2xl border border-border bg-card p-5">
            <p className="font-mono text-[10px] uppercase tracking-widest text-primary">{stage.title}</p>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">{stage.summary}</p>
          </div>
        ))}
      </section>

      <div className="space-y-12 py-10">
        {Object.entries(grouped).map(([group, groupDocs]) => {
          const Icon = groupIcons[group as keyof typeof groupIcons] ?? BookOpen;
          return (
            <section key={group}>
              <div className="mb-2 flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center text-primary">
                  <Icon className="h-5 w-5" />
                </span>
                <div>
                  <h2 className="text-xl font-semibold tracking-tight text-foreground">{group}</h2>
                  {/* <p className="text-sm text-muted-foreground">{groupDocs.length} documentation pages</p> */}
                </div>
              </div>
              <div className="grid sm:grid-cols-2">
                {groupDocs.map((doc) => (
                  <Link key={doc.slug} href={`/docs/${doc.slug}`} className="group  border-t border-border p-5 transition-colors hover:bg-card-muted">
                    <h3 className="text-base font-semibold tracking-tight text-foreground">{doc.title}</h3>
                    {doc.description && <p className="mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground">{doc.description}</p>}
                    <div className="mt-4 flex items-center gap-2 text-xs font-medium text-primary">
                      Read page <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
