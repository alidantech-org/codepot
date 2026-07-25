import Link from "next/link";

export function CTABanner() {
  return (
    <section className="mb-24 overflow-hidden rounded-2xl border border-border bg-linear-to-br from-primary/95 via-card to-secondary/95 p-12 text-center">
      <h2 className="mb-3 text-3xl font-bold tracking-tight text-foreground">
        Choose the Codepot workflow that fits{" "}
        <span className="bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">today</span>
      </h2>
      <p className="mx-auto mb-8 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Build with the supported codepot-openapi and codepotg workflow, evaluate the official codepotx runtime, or follow Codepot Lang as the Rust compiler, codepot CLI, LSP, extension, web, and MCP platform come together.
      </p>
      <div className="mb-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Link href="/docs/choose-workflow" className="flex h-11 items-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-7 text-sm font-medium text-white transition-opacity hover:opacity-90">Choose a workflow</Link>
        <Link href="/docs/codepot-lang" className="flex h-11 items-center gap-2 rounded-full border border-border px-7 text-sm text-foreground transition-colors hover:bg-card-muted/60">Explore Codepot Lang</Link>
      </div>
      <div className="flex flex-col items-center gap-2 text-[13px] text-muted-foreground">
        <p>Open source · MIT licensed</p>
        <p>Framework and target-language neutral</p>
        <p>Designed for developers, tools, and AI agents</p>
      </div>
    </section>
  );
}
