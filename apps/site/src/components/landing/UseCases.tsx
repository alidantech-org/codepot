interface UseCase {
  title: string;
  items: string[];
}

export function UseCases({ useCases }: { useCases: UseCase[] }) {
  return (
    <section className="mx-auto max-w-7xl px-5 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
      <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-primary sm:text-[11px]">Who it serves</p>
      <h2 className="max-w-4xl text-2xl font-semibold leading-tight tracking-tight text-foreground sm:text-4xl">
        A shared foundation for teams, tools, and AI
      </h2>
      <p className="mt-4 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-[15px] sm:leading-7">
        Codepot keeps domain meaning and implementation patterns explicit, whether you are maintaining today&apos;s OpenAPI workflow or building the next generation of developer tooling.
      </p>

      <div className="mt-7 md:border-t md:border-b border-border grid grid-cols-1 gap-4 sm:mt-8 sm:grid-cols-3 sm:gap-0 sm:overflow-hidden">
        {useCases.map(({ title, items }) => (
          <article
            key={title}
            className="rounded-2xl border border-border bg-card/40 px-4 py-5 sm:rounded-none sm:border-0 sm:border-l sm:border-border sm:bg-transparent sm:px-6 sm:py-7 first:sm:border-l-0"
          >
            <p className="mb-4 text-sm font-semibold text-foreground">{title}</p>
            <ul className="space-y-2.5">
              {items.map((item) => (
                <li key={item} className="flex items-start gap-3 text-[13px] leading-5 text-foreground">
                  <span className="mt-2 h-px w-4 shrink-0 bg-primary/70" />
                  <span className="min-w-0">{item}</span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
