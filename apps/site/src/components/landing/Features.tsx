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
  return <span className={`mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full ${map[color]}`} />;
}

export function Features({ features }: { features: Feature[] }) {
  return (
    <section id="features" className="landing-card-section mb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">Why Codepot</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">One project, clear responsibilities</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        Each package has a deliberate role. Contracts describe intent, template systems preserve real project conventions, runtimes coordinate safe work, and language tooling makes the same meaning available to editors and AI.
      </p>

      <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {features.map(({ label, color }) => (
          <li key={label} className="flex items-start gap-3 rounded-xl border border-border bg-background/55 px-4 py-3 text-[14px] text-foreground transition-colors hover:bg-background/80">
            <Dot color={color} />
            {label}
          </li>
        ))}
      </ul>
    </section>
  );
}
