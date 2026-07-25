interface UseCase {
  title: string;
  items: string[];
}

export function UseCases({ useCases }: { useCases: UseCase[] }) {
  return (
    <section className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">Who it serves</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">A shared foundation for teams, tools, and AI</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Codepot keeps domain meaning and implementation patterns explicit, whether you are maintaining today&apos;s OpenAPI workflow or building the next generation of developer tooling.
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {useCases.map(({ title, items }) => (
          <div key={title} className="rounded-2xl border border-border bg-card p-5 dark:bg-card/50">
            <p className="mb-4 text-sm font-semibold text-foreground">{title}</p>
            <ul className="space-y-2">
              {items.map((item) => (
                <li key={item} className="flex items-center gap-2 text-[13px] text-foreground">
                  <span className="h-px w-3 bg-muted-foreground" />
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
