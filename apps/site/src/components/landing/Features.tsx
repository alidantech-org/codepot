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
    <section id="features" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">Features</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">A better foundation for AI coding</h2>
      <p className="mb-12 max-w-xl text-[15px] leading-7 text-muted-foreground">
        Codepot makes the important parts of a software system explicit, reusable, and reviewable before generated code reaches your repository.
      </p>

      <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {features.map(({ label, color }) => (
          <li key={label} className="flex items-start gap-3 rounded-xl border border-border bg-card/50 px-4 py-3 text-[14px] text-foreground transition-colors hover:bg-card">
            <Dot color={color} />
            {label}
          </li>
        ))}
      </ul>
    </section>
  );
}
