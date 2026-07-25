"use client";

import React, { useState } from "react";
import { ChevronRight, FileText, Layers, LayoutTemplate, Link, Rocket, Zap } from "lucide-react";

import type { PipelineStep } from "@/data/types";

const iconMap = { FileText, Link, Layers, LayoutTemplate, Zap, Rocket } as const;

export function Pipeline({ steps }: { steps: PipelineStep[] }) {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  function toggleStep(step: string) {
    const next = new Set(expandedSteps);
    if (next.has(step)) next.delete(step);
    else next.add(step);
    setExpandedSteps(next);
  }

  return (
    <section id="pipeline" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-secondary">Feature maturity path</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">How Codepot evolves without abandoning working tools</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        New ideas can be proven in mature packages, stabilized behind the frontend-neutral codepotx runtime, and finally expressed through the Rust language and toolchain.
      </p>

      <div className="overflow-hidden rounded-2xl border border-border bg-card/50">
        {steps.map(({ step, description, details, icon }, index) => {
          const isExpanded = expandedSteps.has(step);
          const Icon = icon ? iconMap[icon as keyof typeof iconMap] : undefined;
          return (
            <div key={step} className={index !== steps.length - 1 ? "border-b border-border" : ""}>
              <button type="button" onClick={() => toggleStep(step)} className="group flex w-full items-center gap-5 px-6 py-4 text-left transition-colors hover:bg-card-muted/50">
                <span className="w-8 shrink-0 font-mono text-xs text-muted-foreground group-hover:text-primary">{step}</span>
                <div className="flex flex-1 items-center gap-2">
                  {Icon && <span className="text-primary"><Icon className="h-5 w-5" /></span>}
                  <div className="h-px flex-1 border-t border-dashed border-border" />
                </div>
                <span className="text-sm font-medium text-foreground">{description}</span>
                <ChevronRight className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${isExpanded ? "rotate-90" : ""} group-hover:text-secondary`} />
              </button>
              <div className={`overflow-hidden transition-all duration-300 ease-in-out ${isExpanded ? "max-h-40 opacity-100" : "max-h-0 opacity-0"}`}>
                <div className="px-6 pb-4 pt-0">
                  <div className="pl-13 text-sm leading-relaxed text-muted-foreground">{details}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
