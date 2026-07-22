import Link from "next/link";
import { getAllDocs } from "@/lib/docs";
import { ArrowRight, FileText } from "lucide-react";

export default async function DocsPage() {
  const docs = await getAllDocs();

  return (
    <div className="mx-auto w-full max-w-4xl px-4 md:px-6">
      <section className="border-b border-border pb-10">
        <p className="mb-3 font-mono text-xs uppercase tracking-widest text-primary">
          Documentation
        </p>

        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Codepurify Docs
        </h1>

        <p className="mt-4 max-w-2xl text-lg leading-8 text-muted-foreground">
          Learn how to define typed domain configs, infer metadata, and generate
          architecture artifacts with Codepurify.
        </p>
      </section>

      <section className="grid gap-4 py-10 sm:grid-cols-2">
        {docs.map((doc) => (
          <Link
            key={doc.slug}
            href={`/docs/${doc.slug}`}
            className="group rounded-2xl border border-border bg-card p-5 transition-colors hover:bg-card-muted"
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-background text-primary">
              <FileText className="h-5 w-5" />
            </div>

            <h2 className="text-lg font-semibold tracking-tight text-foreground">
              {doc.title}
            </h2>

            {doc.description && (
              <p className="mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground">
                {doc.description}
              </p>
            )}

            <div className="mt-4 flex items-center gap-2 text-sm font-medium text-primary">
              Read doc
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </div>
          </Link>
        ))}
      </section>
    </div>
  );
}
