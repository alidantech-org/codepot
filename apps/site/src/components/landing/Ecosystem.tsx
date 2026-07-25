import Link from "next/link";
import { ArrowRight, Boxes, Braces, Languages } from "lucide-react";

import { ecosystem, getProductsForStage } from "@/lib/ecosystem";

const stageIcons = {
  prototypes: Boxes,
  javascript: Braces,
  platform: Languages,
} as const;

export function Ecosystem() {
  return (
    <section id="ecosystem" className="border-y border-border bg-card/35">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">One ecosystem</p>
        <h2 className="max-w-3xl text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Proven packages, an official runtime, and a complete language platform
        </h2>
        <p className="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
          Codepot evolves features through three complementary stages. The mature prototype packages remain supported while validated ideas move into codepotx and then into the final Rust platform.
        </p>

        <div className="relative mt-8 grid gap-8 border-y border-border py-7 lg:grid-cols-3 lg:gap-0">
          <div aria-hidden="true" className="absolute left-0 right-0 top-0 h-px bg-linear-to-r from-transparent via-primary/45 to-transparent" />
          {ecosystem.stages.map((stage, stageIndex) => {
            const Icon = stageIcons[stage.id as keyof typeof stageIcons] ?? Boxes;
            const products = getProductsForStage(stage.id);
            return (
              <article
                key={stage.id}
                className="relative lg:border-l lg:border-border lg:px-7 first:lg:border-l-0 first:lg:pl-0 last:lg:pr-0"
              >
                <div className="mb-4 flex items-center justify-between gap-4">
                  <Icon className="h-6 w-6 text-primary" />
                  <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    Stage {stageIndex + 1}
                  </span>
                </div>
                <h3 className="text-lg font-semibold tracking-tight text-foreground">{stage.title}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground lg:min-h-20">{stage.summary}</p>
                <div className="mt-4 border-t border-border">
                  {products.map((product) => (
                    <Link
                      key={product.id}
                      href={`/docs/${product.docsSlug}`}
                      className="group flex items-center justify-between gap-3 border-b border-border py-3 transition-colors hover:text-primary"
                    >
                      <span className="min-w-0">
                        <span className="block truncate text-sm font-medium text-foreground transition-colors group-hover:text-primary">{product.name}</span>
                        <span className="block truncate text-[11px] text-muted-foreground">{product.availability}</span>
                      </span>
                      <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
                    </Link>
                  ))}
                </div>
              </article>
            );
          })}
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3 text-sm">
          <Link href="/docs/ecosystem" className="inline-flex items-center gap-2 font-medium text-primary hover:underline">
            Explore the ecosystem <ArrowRight className="h-4 w-4" />
          </Link>
          <span className="text-muted-foreground">or</span>
          <Link href="/docs/choose-workflow" className="font-medium text-foreground hover:underline">
            choose the right workflow
          </Link>
        </div>
      </div>
    </section>
  );
}
