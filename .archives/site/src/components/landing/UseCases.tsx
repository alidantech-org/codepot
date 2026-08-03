interface UseCase {
  title: string;
  items: string[];
}

interface UseCasesProps {
  useCases: UseCase[];
}

export function UseCases({ useCases }: UseCasesProps) {
  return (
    <section className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">
        Use Cases
      </p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">
        Generate anything
      </h2>
      <p className="mb-12 max-w-xl text-[15px] leading-7 text-muted-foreground">
        One semantic source of truth. Unlimited template-driven outputs.
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {useCases.map(({ title, items }) => (
          <div key={title} className="rounded-2xl border-border bg-card p-5 dark:bg-card/50">
            <p className="mb-4 text-sm font-semibold text-foreground">
              {title}
            </p>
            <ul className="space-y-2">
              {items.map((item) => (
                <li
                  key={item}
                  className="flex items-center gap-2 text-[13px] text-foreground"
                >
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
