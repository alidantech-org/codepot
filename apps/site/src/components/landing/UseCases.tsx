interface UseCase {
  title: string;
  items: string[];
}

export function UseCases({ useCases }: { useCases: UseCase[] }) {
  return (
    <section className="pb-24 max-w-7xl mx-auto px-3 md:px-6">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">Who it serves</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">A shared foundation for teams, tools, and AI</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Codepot keeps domain meaning and implementation patterns explicit, whether you are maintaining today&apos;s OpenAPI workflow or building the next generation of developer tooling.
      </p>

      <div className="grid grid-cols-1 gap-10 border-y border-border py-8 sm:grid-cols-3 sm:gap-0">
        {useCases.map(({ title, items }) => (
          <div key={title} className="sm:border-l sm:border-border sm:px-7 first:sm:border-l-0 first:sm:pl-0 last:sm:pr-0">
            <p className="mb-5 text-sm font-semibold text-foreground">{title}</p>
            <ul className="space-y-3">
              {items.map((item) => (
                <li key={item} className="flex items-start gap-3 text-[13px] leading-5 text-foreground">
                  <span className="mt-2 h-px w-4 shrink-0 bg-primary/70" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
