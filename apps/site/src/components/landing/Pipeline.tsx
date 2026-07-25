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
    <section id="pipeline" className="mx-auto max-w-7xl px-5 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
      <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-secondary sm:text-[11px]">Feature maturity path</p>
      <h2 className="max-w-4xl text-2xl font-semibold leading-tight tracking-tight text-foreground sm:text-4xl">
        How Codepot evolves without abandoning working tools
      </h2>
      <p className="mt-4 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-[15px] sm:leading-7">
        New ideas can be proven in mature packages, stabilized behind the frontend-neutral codepotx runtime, and finally expressed through the Rust language and toolchain.
      </p>

      <div className="mt-7 overflow-hidden md:border-t md:border-b border-border bg-card/35 sm:mt-8">
        {steps.map(({ step, description, details, icon }, index) => {
          const isExpanded = expandedSteps.has(step);
          const Icon = icon ? iconMap[icon as keyof typeof iconMap] : undefined;
          return (
            <div key={step} className={index !== steps.length - 1 ? "border-b border-border" : ""}>
              <button
                type="button"
                onClick={() => toggleStep(step)}
                className="group grid w-full grid-cols-[auto_auto_minmax(0,1fr)_auto] items-center gap-2.5 px-4 py-4 text-left transition-colors hover:bg-card-muted/35 sm:gap-5 sm:px-5 sm:py-5"
              >
                <span className="w-7 shrink-0 font-mono text-[11px] text-muted-foreground group-hover:text-primary sm:text-xs">{step}</span>
                {Icon && <Icon className="h-4.5 w-4.5 shrink-0 text-primary sm:h-5 sm:w-5" />}
                <span className="min-w-0 text-[13px] font-medium leading-5 text-foreground sm:text-sm">{description}</span>
                <ChevronRight className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 ${isExpanded ? "rotate-90" : ""} group-hover:text-secondary`} />
              </button>
              <div className={`grid transition-[grid-template-rows,opacity] duration-300 ease-out ${isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}>
                <div className="overflow-hidden">
                  <p className="px-4 pb-4 pl-[4.7rem] text-[13px] leading-5 text-muted-foreground sm:px-5 sm:pb-5 sm:pl-[5.9rem] sm:text-sm sm:leading-6">{details}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
