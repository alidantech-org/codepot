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
    <section id="ecosystem" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">One ecosystem</p>
      <h2 className="mb-3 max-w-3xl text-3xl font-semibold tracking-tight text-foreground">
        Proven packages, an official runtime, and a complete language platform
      </h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Codepot evolves features through three complementary stages. The mature prototype packages remain supported while validated ideas move into codepotx and then into the final Rust platform.
      </p>

      <div className="grid gap-4 lg:grid-cols-3">
        {ecosystem.stages.map((stage, stageIndex) => {
          const Icon = stageIcons[stage.id as keyof typeof stageIcons] ?? Boxes;
          const products = getProductsForStage(stage.id);
          return (
            <article key={stage.id} className="relative overflow-hidden rounded-2xl border border-border bg-card/70 p-6">
              <div className="mb-5 flex items-center justify-between">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-background text-primary">
                  <Icon className="h-5 w-5" />
                </span>
                <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  Stage {stageIndex + 1}
                </span>
              </div>
              <h3 className="text-lg font-semibold tracking-tight text-foreground">{stage.title}</h3>
              <p className="mt-2 min-h-20 text-sm leading-6 text-muted-foreground">{stage.summary}</p>
              <div className="mt-5 space-y-2 border-t border-border pt-5">
                {products.map((product) => (
                  <Link
                    key={product.id}
                    href={`/docs/${product.docsSlug}`}
                    className="group flex items-center justify-between gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-card-muted"
                  >
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium text-foreground">{product.name}</span>
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

      <div className="mt-6 flex flex-wrap items-center gap-3 text-sm">
        <Link href="/docs/ecosystem" className="inline-flex items-center gap-2 font-medium text-primary hover:underline">
          Explore the ecosystem <ArrowRight className="h-4 w-4" />
        </Link>
        <span className="text-muted-foreground">or</span>
        <Link href="/docs/choose-workflow" className="font-medium text-foreground hover:underline">
          choose the right workflow
        </Link>
      </div>
    </section>
  );
}
