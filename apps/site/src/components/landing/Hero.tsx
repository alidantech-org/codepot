import Link from "next/link";

import { HeroDecoration1, HeroDecoration2 } from "@/components/decorative/HeroDecoration";

export function Hero() {
  return (
    <section className="relative mx-auto flex min-h-[500px] max-w-7xl flex-col items-center justify-center overflow-hidden px-5 py-14 text-center sm:min-h-[560px] sm:items-start sm:px-6 sm:py-18 sm:text-left lg:min-h-[620px] lg:px-8 lg:py-24 lg:pr-72 xl:pr-80">
      <span className="mb-4 inline-flex max-w-full items-center justify-center gap-2 border-y border-border/70 py-1 text-center font-mono text-[9px] leading-5 tracking-wider text-primary sm:mb-5 sm:justify-start sm:text-[11px]">
        <span className="hidden h-1.5 w-1.5 animate-pulse rounded-full bg-primary md:block" />
        supported prototypes · official runtime · Rust language platform
      </span>

      <h1 className="landing-display max-w-4xl text-[2.6rem] font-semibold leading-[1.03] tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl">
        Make software intent{" "}
        <span className="bg-linear-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
          explicit
        </span>
        <br />
        before code is generated.
      </h1>

      <p className="mt-5 max-w-3xl text-[15px] leading-7 text-muted-foreground sm:text-lg sm:leading-8">
        Codepot connects typed contracts, reusable template packs, safe generation, and language tooling. Use the mature OpenAPI and Jinja workflow today, follow the official codepotx runtime, and explore the final Codepot Lang platform.
      </p>

      <div className="mt-6 flex max-w-full flex-wrap items-center justify-center gap-x-2 gap-y-2 border-y border-border/70 py-3 font-mono text-[11px] text-foreground sm:justify-start sm:text-sm">
        <span className="text-primary">codepot-openapi</span>
        <span className="text-muted-foreground">→</span>
        <span className="text-primary">codepotg</span>
        <span className="text-muted-foreground">→</span>
        <span className="text-secondary">codepotx</span>
        <span className="text-muted-foreground">→</span>
        <span className="text-accent">codepot</span>
      </div>

      <div className="mt-6 flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
        <Link
          href="/docs/getting-started"
          className="warm-shine flex h-11 items-center justify-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-6 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
        >
          Get started
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </Link>
        <Link
          href="/docs/ecosystem"
          className="flex h-11 items-center justify-center gap-2 rounded-full border border-border px-6 text-sm text-muted-foreground transition-colors hover:border-primary/35 hover:text-foreground"
        >
          Explore the ecosystem
        </Link>
      </div>

      <div className="pointer-events-none opacity-10 sm:opacity-30 md:opacity-60 lg:opacity-100">
        <HeroDecoration1 />
        <HeroDecoration2 />
      </div>
    </section>
  );
}
