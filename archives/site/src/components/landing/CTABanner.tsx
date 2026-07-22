export function CTABanner() {
  return (
    <section className="mb-24 overflow-hidden rounded-2xl border-border bg-linear-to-br from-primary/95 via-card to-secondary/95 p-12 text-center">
      <h2 className="mb-3 text-3xl font-bold tracking-tight text-foreground">
        Start generating from{" "}
        <span className="bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">
          semantic facts
        </span>
      </h2>
      <p className="mx-auto mb-8 max-w-md text-[15px] leading-7 text-muted-foreground">
        MIT licensed. Framework agnostic. One config, infinite architecture
        outputs. Open source and ready for your contributions.
      </p>
      <div className="mb-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <a
          href="https://github.com/alidantech-org/codepurify"
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-11 items-center gap-2 rounded-full bg-linear-to-r from-primary to-secondary px-7 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          Get Started on GitHub
        </a>
        <a
          href="https://github.com/alidantech-org/codepurify#readme"
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-11 items-center gap-2 rounded-full border-border px-7 text-sm text-foreground transition-colors hover:bg-card-muted/60"
        >
          Read the Docs
        </a>
      </div>
      <div className="flex flex-col items-center gap-2 text-[13px] text-muted-foreground">
        <p className="flex items-center gap-2">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          Open source MIT license
        </p>
        <p className="flex items-center gap-2">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
          </svg>
          Community driven development
        </p>
        <p className="flex items-center gap-2">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
          Contributions welcome
        </p>
      </div>
    </section>
  );
}
