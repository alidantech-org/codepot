import Link from "next/link";

export function CTABanner() {
  return (
    <section className="landing-card-section relative mx-auto mb-24 max-w-7xl overflow-hidden rounded-[2.5rem_1.5rem_4.5rem_1.5rem] border border-primary/20 bg-[linear-gradient(135deg,color-mix(in_srgb,var(--card)_94%,var(--primary)_6%)_0%,color-mix(in_srgb,var(--card-muted)_88%,var(--accent)_12%)_52%,color-mix(in_srgb,var(--background)_92%,var(--primary)_8%)_100%)] px-6 py-14 text-center shadow-xl shadow-primary/8 sm:px-12 sm:py-16 dark:border-primary/20 dark:bg-[linear-gradient(135deg,#21130c_0%,#3b2114_52%,#24140c_100%)] dark:shadow-2xl dark:shadow-primary/10">
      <div aria-hidden="true" className="absolute -left-24 -top-28 h-64 w-64 rounded-full bg-primary/12 blur-3xl dark:bg-primary/20" />
      <div aria-hidden="true" className="absolute -bottom-32 -right-20 h-72 w-72 rounded-full bg-accent/10 blur-3xl dark:bg-accent/15" />
      <div aria-hidden="true" className="hero-orbit absolute -right-14 top-6 h-44 w-44 rounded-full border border-dashed border-accent/20 dark:border-accent/25" />

      <div className="relative z-10">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.22em] text-primary dark:text-accent-light">Craft the next layer</p>
        <h2 className="landing-display mx-auto mb-4 max-w-3xl text-4xl font-semibold leading-tight text-foreground sm:text-5xl dark:text-[#fff7ed]">
          Choose the Codepot workflow that fits{" "}
          <span className="text-primary dark:text-[#e4b775]">today</span>
        </h2>
        <p className="mx-auto mb-8 max-w-2xl text-[15px] leading-7 text-muted-foreground dark:text-[#d8c4b0]">
          Build with the supported codepot-openapi and codepotg workflow, evaluate the official codepotx runtime, or follow Codepot Lang as the Rust compiler, codepot CLI, LSP, extension, web, and MCP platform come together.
        </p>
        <div className="mb-7 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/docs/choose-workflow"
            className="warm-shine flex h-12 items-center justify-center rounded-full bg-primary px-7 text-sm font-semibold text-primary-foreground shadow-md shadow-primary/20 transition duration-300 hover:-translate-y-0.5 hover:brightness-105 motion-reduce:transform-none motion-reduce:transition-none dark:bg-[#d89a58] dark:text-[#21130c] dark:shadow-lg dark:shadow-black/20 dark:hover:bg-[#e5ad70]"
          >
            Choose a workflow
          </Link>
          <Link
            href="/docs/codepot-lang"
            className="flex h-12 items-center justify-center rounded-full border border-border bg-background/75 px-7 text-sm font-medium text-foreground backdrop-blur-sm transition duration-300 hover:-translate-y-0.5 hover:border-primary/35 hover:bg-card-muted motion-reduce:transform-none motion-reduce:transition-none dark:border-[#f0c58e]/25 dark:bg-white/5 dark:text-[#fff7ed] dark:hover:bg-white/10"
          >
            Explore Codepot Lang
          </Link>
        </div>
        <div className="flex flex-col items-center gap-2 text-[13px] text-muted-foreground sm:flex-row sm:justify-center sm:gap-5 dark:text-[#bca894]">
          <p>Open source · MIT licensed</p>
          <p>Framework and target-language neutral</p>
          <p>Built for developers, tools, and AI agents</p>
        </div>
      </div>
    </section>
  );
}
