interface Feature {
  label: string;
  color: "blue" | "purple" | "teal";
}

interface DotProps {
  color: "blue" | "purple" | "teal";
}

function Dot({ color }: DotProps) {
  const map: Record<DotProps["color"], string> = {
    blue: "bg-primary",
    purple: "bg-secondary",
    teal: "bg-accent",
  };
  return (
    <span
      className={`mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full ${map[color]}`}
    />
  );
}

interface FeaturesProps {
  features: Feature[];
}

export function Features({ features }: FeaturesProps) {
  return (
    <section id="features" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-primary">
        Features
      </p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">
        Core Features
      </h2>
      <p className="mb-12 max-w-xl text-[15px] leading-7 text-muted-foreground">
        Stop wasting tokens on repetitive AI prompts. Generate consistent
        architecture across any language with deterministic, template-driven
        code generation.
      </p>

      <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {features.map(({ label, color }) => (
          <li
            key={label}
            className="flex items-start gap-3 rounded-xl border-border bg-card/50 px-4 py-3 text-[14px] text-foreground transition-colors hover:border-border hover:bg-card"
          >
            <Dot color={color} />
            {label}
          </li>
        ))}
      </ul>
    </section>
  );
}
