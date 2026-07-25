import Link from "next/link";
import { ArrowLeft, PackageSearch, Search } from "lucide-react";

export default function DocsNotFound() {
  return (
    <div className="mx-auto flex min-h-[60dvh] w-full max-w-3xl items-center px-5 py-16 sm:px-8">
      <section className="w-full border-y border-border py-10">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-primary">
          Documentation
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          This documentation path does not exist
        </h1>
        <p className="mt-4 max-w-xl text-sm leading-7 text-muted-foreground sm:text-base">
          The page may have moved into a package documentation tree, or the URL may contain an invalid nested path.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            href="/docs"
            className="inline-flex h-10 items-center gap-2 bg-primary px-4 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <ArrowLeft className="h-4 w-4" />
            Documentation home
          </Link>
          <Link
            href="/docs/packages"
            className="inline-flex h-10 items-center gap-2 border border-border px-4 text-sm font-medium text-foreground transition-colors hover:bg-card-muted"
          >
            <PackageSearch className="h-4 w-4" />
            Browse packages
          </Link>
          <span className="inline-flex h-10 items-center gap-2 px-2 text-sm text-muted-foreground">
            <Search className="h-4 w-4" />
            Use Ctrl K to search
          </span>
        </div>
      </section>
    </div>
  );
}
