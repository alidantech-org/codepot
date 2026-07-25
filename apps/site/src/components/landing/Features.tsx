interface Feature {
  label: string;
  color: "blue" | "purple" | "teal";
}

function Dot({ color }: { color: Feature["color"] }) {
  const map: Record<Feature["color"], string> = {
    blue: "bg-primary",
    purple: "bg-secondary",
    teal: "bg-accent",
  };
  return <span className={`mt-2 h-2 w-2 shrink-0 rounded-full ${map[color]}`} />;
}

export function Features({ features }: { features: Feature[] }) {
  return (
    <section
      id="features"
      className="relative mx-4 my-14 max-w-7xl overflow-hidden rounded-[1.5rem_1rem_2.5rem_1rem] border border-border bg-card 
      px-5 py-8 shadow-lg shadow-primary/5 sm:mx-6 sm:my-16 sm:rounded-[2.25rem_1.5rem_3.5rem_1.5rem] sm:px-8 sm:py-10 lg:mx-auto lg:my-20 lg:px-8 lg:py-14"
    >
      <div aria-hidden="true" className="absolute -right-20 -top-24 h-52 w-52 rounded-full bg-primary/8 blur-3xl" />

      <div className="relative z-10 py-10">
        <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-primary sm:text-[11px]">Why Codepot</p>
        <h2 className="max-w-3xl text-2xl font-semibold leading-tight tracking-tight text-foreground sm:text-4xl">
          One project, clear responsibilities
        </h2>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-[15px] sm:leading-7">
          Each package has a deliberate role. Contracts describe intent, template systems preserve real project conventions, runtimes coordinate safe work, and language tooling makes the same meaning available to editors and AI.
        </p>

        <ul className="mt-6 grid grid-cols-1 gap-2 sm:mt-8 md:grid-cols-2 md:gap-x-6">
          {features.map(({ label, color }) => (
            <li
              key={label}
              className="flex items-start gap-3 border-b border-border/70 px-3.5 
              py-3 text-[13px] leading-5 text-foreground sm:px-4 sm:py-3.5 sm:text-[14px] sm:leading-6"
            >
              <Dot color={color} />
              <span className="min-w-0">{label}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
