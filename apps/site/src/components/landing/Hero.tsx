import Link from "next/link";

import { HeroDecoration } from "@/components/decorative/HeroDecoration";

export function Hero() {
  return (
    <section className="relative flex flex-col items-center py-28 text-center sm:items-start sm:text-left">
      <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1 font-mono text-[11px] tracking-wider text-primary">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
        codepotx · Codepot Lang in progress
      </span>

      <h1 className="max-w-3xl text-5xl font-bold leading-[1.05] tracking-tight text-foreground md:text-6xl lg:text-7xl">
        Give AI a{" "}
        <span className="bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">
          reliable source
        </span>
        <br />
        of truth for{" "}
        <span className="italic text-muted-foreground">software.</span>
      </h1>

      <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
        Codepot connects typed contracts, reusable template packs, and project-owned generation tasks. Developers and AI agents work from the same intent instead of repeatedly guessing your architecture, naming, and patterns.
      </p>

      <div className="mt-8 w-full max-w-sm rounded-lg border border-border bg-card px-4 py-2.5 font-mono text-sm text-foreground sm:w-auto">
        <span className="mr-2 text-muted-foreground">$</span>
        npm install <span className="text-primary">codepotx</span>
      </div>

      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link href="/docs/getting-started" className="flex h-11 items-center justify-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-6 text-sm font-medium text-white transition-opacity hover:opacity-90">
          Get Started
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </Link>
        <Link href="/docs" className="flex h-11 items-center justify-center gap-2 rounded-full border border-border px-6 text-sm text-muted-foreground transition-colors hover:bg-card-muted/60 hover:text-foreground">
          Documentation
        </Link>
      </div>

      <div className="opacity-20 md:opacity-50 lg:opacity-100">
        <HeroDecoration />
      </div>
    </section>
  );
}
