import Link from "next/link";

export function CTABanner() {
  return (
    <section className="landing-card-section max-w-7xl mx-auto px-3 md:px-6 relative mb-24 overflow-hidden rounded-[2.5rem_1.5rem_4.5rem_1.5rem] border border-primary/25 bg-[linear-gradient(135deg,#21130c_0%,#3b2114_52%,#24140c_100%)] px-6 py-14 text-center shadow-2xl shadow-primary/10 sm:px-12 sm:py-16 dark:border-primary/20">
      <div aria-hidden="true" className="absolute -left-24 -top-28 h-64 w-64 rounded-full bg-primary/20 blur-3xl" />
      <div aria-hidden="true" className="absolute -bottom-32 -right-20 h-72 w-72 rounded-full bg-accent/15 blur-3xl" />
      <div aria-hidden="true" className="hero-orbit absolute -right-14 top-6 h-44 w-44 rounded-full border border-dashed border-accent/25" />

      <div className="relative z-10">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.22em] text-accent-light">Craft the next layer</p>
        <h2 className="landing-display mx-auto mb-4 max-w-3xl text-4xl font-semibold leading-tight text-[#fff7ed] sm:text-5xl">
          Choose the Codepot workflow that fits{" "}
          <span className="text-[#e4b775]">today</span>
        </h2>
        <p className="mx-auto mb-8 max-w-2xl text-[15px] leading-7 text-[#d8c4b0]">
          Build with the supported codepot-openapi and codepotg workflow, evaluate the official codepotx runtime, or follow Codepot Lang as the Rust compiler, codepot CLI, LSP, extension, web, and MCP platform come together.
        </p>
        <div className="mb-7 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/docs/choose-workflow"
            className="warm-shine flex h-12 items-center justify-center rounded-full bg-[#d89a58] px-7 text-sm font-semibold text-[#21130c] shadow-lg shadow-black/20 transition duration-300 hover:-translate-y-0.5 hover:bg-[#e5ad70] motion-reduce:transform-none motion-reduce:transition-none"
          >
            Choose a workflow
          </Link>
          <Link
            href="/docs/codepot-lang"
            className="flex h-12 items-center justify-center rounded-full border border-[#f0c58e]/25 bg-white/5 px-7 text-sm font-medium text-[#fff7ed] backdrop-blur-sm transition duration-300 hover:-translate-y-0.5 hover:bg-white/10 motion-reduce:transform-none motion-reduce:transition-none"
          >
            Explore Codepot Lang
          </Link>
        </div>
        <div className="flex flex-col items-center gap-2 text-[13px] text-[#bca894] sm:flex-row sm:justify-center sm:gap-5">
          <p>Open source · MIT licensed</p>
          <p>Framework and target-language neutral</p>
          <p>Built for developers, tools, and AI agents</p>
        </div>
      </div>
    </section>
  );
}
