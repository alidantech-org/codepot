import Link from "next/link";
import { FileQuestion, ArrowLeft, Search } from "lucide-react";

export default function DocsNotFound() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-6 py-16">
      <div className="mx-auto max-w-xl text-center">
        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl border border-border bg-card text-primary shadow-sm">
          <FileQuestion className="h-7 w-7" />
        </div>

        <p className="mb-3 font-mono text-xs uppercase tracking-widest text-primary">
          Documentation page not found
        </p>

        <h1 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          This doc does not exist yet
        </h1>

        <p className="mx-auto mb-8 max-w-md text-sm leading-7 text-muted-foreground sm:text-base">
          The documentation page you're looking for may have been moved,
          renamed, or not created yet.
        </p>

        <div className="flex flex-col justify-center gap-3 sm:flex-row">
          <Link
            href="/docs"
            className="inline-flex h-11 items-center justify-center gap-2 rounded-full bg-primary px-6 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Docs
          </Link>

          <Link
            href="/docs/quickstart"
            className="inline-flex h-11 items-center justify-center gap-2 rounded-full border border-border bg-card px-6 text-sm font-medium text-foreground transition-colors hover:bg-card-muted"
          >
            <Search className="h-4 w-4" />
            View Quickstart
          </Link>
        </div>
      </div>
    </div>
  );
}
