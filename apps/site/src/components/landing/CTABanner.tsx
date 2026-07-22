import Link from "next/link";

export function CTABanner() {
  return (
    <section className="mb-24 overflow-hidden rounded-2xl border border-border bg-linear-to-br from-primary/95 via-card to-secondary/95 p-12 text-center">
      <h2 className="mb-3 text-3xl font-bold tracking-tight text-foreground">
        Make software intent{" "}
        <span className="bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">reusable</span>
      </h2>
      <p className="mx-auto mb-8 max-w-lg text-[15px] leading-7 text-muted-foreground">
        Start with the TypeScript package today. The larger Codepot vision continues with Codepot Lang, an in-progress typed language designed to express software systems clearly for people, tools, and AI.
      </p>
      <div className="mb-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Link href="/docs/getting-started" className="flex h-11 items-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-7 text-sm font-medium text-white transition-opacity hover:opacity-90">Get started</Link>
        <a href="https://github.com/alidantech-org/codepot_lang" target="_blank" rel="noopener noreferrer" className="flex h-11 items-center gap-2 rounded-full border border-border px-7 text-sm text-foreground transition-colors hover:bg-card-muted/60">Explore Codepot Lang</a>
      </div>
      <div className="flex flex-col items-center gap-2 text-[13px] text-muted-foreground">
        <p>Open source · MIT licensed</p>
        <p>Framework and target-language neutral</p>
        <p>Built for developer-owned and AI-assisted workflows</p>
      </div>
    </section>
  );
}
