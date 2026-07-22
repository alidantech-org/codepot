import Link from "next/link";
import { HeroDecoration } from "@/components/decorative/HeroDecoration";

export function Hero() {
  return (
    <section className="relative flex flex-col items-center py-28 text-center sm:items-start sm:text-left">
      {/* Badge */}
      <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1 font-mono text-[11px] tracking-wider text-primary">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
        v0.1.0 · semantic metadata compiler
      </span>

      {/* Headline */}
      <h1 className="max-w-3xl text-5xl font-bold leading-[1.05] tracking-tight text-foreground md:text-6xl lg:text-7xl">
        Define{" "}
        <span className="bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">
          facts.
        </span>
        <br />
        Infer everything{" "}
        <span className="italic text-muted-foreground">else.</span>
      </h1>

      {/* Sub */}
      <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
        Codepurify is a semantic metadata inference engine and template
        compiler. Describe your domain once — it infers query capabilities,
        mutation semantics, relation graphs, workflows, and validation rules,
        then renders any architecture you need.
      </p>

      {/* Install */}
      <div className="mt-8 w-full max-w-sm rounded-lg border-border bg-card px-4 py-2.5 font-mono text-sm text-foreground sm:w-auto">
        <span className="mr-2 text-muted-foreground">$</span>
        npm install <span className="text-primary">codepurify</span>
      </div>

      {/* CTAs */}
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <a
          href="https://github.com/alidantech-org/codepurify"
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-11 items-center justify-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-6 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          Get Started
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 8l4 4m0 0l-4 4m4-4H3"
            />
          </svg>
        </a>
        <Link
          href="/docs"
          className="flex h-11 items-center justify-center gap-2 rounded-full border-border px-6 text-sm text-muted-foreground transition-colors hover:border-border hover:bg-card-muted/60 hover:text-foreground"
        >
          Documentation
        </Link>
      </div>

      <div className="opacity-20 md:opacity-50 lg:opacity-100">
        <HeroDecoration />
      </div>
    </section>
  );
}
