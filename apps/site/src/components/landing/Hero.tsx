import Image from "next/image";
import Link from "next/link";

import { HeroDecoration } from "@/components/decorative/HeroDecoration";

export function Hero() {
  return (
    <section className="landing-hero-panel mb-20 px-5 py-16 sm:px-10 sm:py-20 lg:px-16 lg:py-24">
      <div className="relative z-10 flex min-h-[520px] max-w-3xl flex-col items-center justify-center text-center sm:items-start sm:text-left lg:max-w-[58%]">
        <Image
          src="/logo.svg"
          alt="Codepot African clay pot logo"
          width={118}
          height={118}
          priority
          className="mb-4 h-24 w-24 drop-shadow-xl lg:hidden"
        />

        <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1 font-mono text-[11px] tracking-wider text-primary backdrop-blur-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-primary motion-safe:animate-pulse" />
          supported prototypes · official runtime · Rust language platform
        </span>

        <h1 className="landing-display max-w-4xl text-5xl font-semibold leading-[1.02] text-foreground sm:text-6xl lg:text-7xl xl:text-[5.25rem]">
          Make software intent{" "}
          <span className="bg-linear-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            explicit
          </span>
          <br />
          before code is generated.
        </h1>

        <p className="mt-7 max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg">
          Codepot connects typed contracts, reusable template packs, safe generation, and language tooling. Use the mature OpenAPI and Jinja workflow today, follow the official codepotx runtime, and explore the final Codepot Lang platform.
        </p>

        <div className="mt-8 w-full max-w-2xl overflow-x-auto rounded-2xl border border-border bg-background/70 px-4 py-3 font-mono text-xs text-foreground shadow-sm backdrop-blur-md sm:w-auto sm:text-sm">
          <span className="text-primary">codepot-openapi</span>
          <span className="mx-2 text-muted-foreground">→</span>
          <span className="text-primary">codepotg</span>
          <span className="mx-2 text-muted-foreground">→</span>
          <span className="text-secondary">codepotx</span>
          <span className="mx-2 text-muted-foreground">→</span>
          <span className="text-accent">codepot</span>
        </div>

        <div className="mt-8 flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
          <Link
            href="/docs/getting-started"
            className="warm-shine flex h-12 items-center justify-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-7 text-sm font-medium text-primary-foreground shadow-lg shadow-primary/15 transition duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/20 motion-reduce:transform-none motion-reduce:transition-none"
          >
            Get started
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
          <Link
            href="/docs/ecosystem"
            className="flex h-12 items-center justify-center gap-2 rounded-full border border-border bg-background/60 px-7 text-sm font-medium text-foreground backdrop-blur-sm transition duration-300 hover:-translate-y-0.5 hover:border-primary/40 hover:bg-card motion-reduce:transform-none motion-reduce:transition-none"
          >
            Explore the ecosystem
          </Link>
        </div>
      </div>

      <HeroDecoration />
    </section>
  );
}
