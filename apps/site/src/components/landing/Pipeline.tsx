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
    <section id="pipeline" className="landing-section max-w-7xl mx-auto py-4 px-3 md:px-6">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-secondary">Feature maturity path</p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">How Codepot evolves without abandoning working tools</h2>
      <p className="mb-12 max-w-2xl text-[15px] leading-7 text-muted-foreground">
        New ideas can be proven in mature packages, stabilized behind the frontend-neutral codepotx runtime, and finally expressed through the Rust language and toolchain.
      </p>

      <div className="border-y border-border">
        {steps.map(({ step, description, details, icon }, index) => {
          const isExpanded = expandedSteps.has(step);
          const Icon = icon ? iconMap[icon as keyof typeof iconMap] : undefined;
          return (
            <div key={step} className={index !== steps.length - 1 ? "border-b border-border" : ""}>
              <button
                type="button"
                onClick={() => toggleStep(step)}
                className="group flex w-full items-center gap-4 py-5 text-left transition-colors hover:text-primary sm:gap-6"
              >
                <span className="w-8 shrink-0 font-mono text-xs text-muted-foreground group-hover:text-primary">{step}</span>
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  {Icon && <Icon className="h-5 w-5 shrink-0 text-primary" />}
                  <div className="hidden h-px flex-1 border-t border-dashed border-border sm:block" />
                </div>
                <span className="max-w-[55%] text-sm font-medium text-foreground sm:max-w-none">{description}</span>
                <ChevronRight className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 ${isExpanded ? "rotate-90" : ""} group-hover:text-secondary`} />
              </button>
              <div className={`grid transition-[grid-template-rows,opacity] duration-300 ease-out ${isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}>
                <div className="overflow-hidden">
                  <p className="pb-5 pl-12 text-sm leading-relaxed text-muted-foreground sm:pl-14">{details}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
