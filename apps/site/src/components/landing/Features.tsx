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
  return <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${map[color]}`} />;
}

export function Features({ features }: { features: Feature[] }) {
  return (
    <section id="features" className="landing-card-section mx-4 my-14 max-w-7xl sm:mx-6 sm:my-16 lg:mx-auto lg:my-20">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">Why Codepot</p>
      <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">One project, clear responsibilities</h2>
      <p className="mt-4 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Each package has a deliberate role. Contracts describe intent, template systems preserve real project conventions, runtimes coordinate safe work, and language tooling makes the same meaning available to editors and AI.
      </p>

      <ul className="mt-8 grid grid-cols-1 gap-x-6 md:grid-cols-2">
        {features.map(({ label, color }) => (
          <li key={label} className="flex items-start gap-3 border-b border-border/60 px-1 py-3.5 text-[14px] leading-6 text-foreground transition-colors hover:bg-background/45 sm:px-3">
            <Dot color={color} />
            {label}
          </li>
        ))}
      </ul>
    </section>
  );
}
