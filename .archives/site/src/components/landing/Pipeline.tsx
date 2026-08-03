"use client";

import React, { useState } from "react";
import {
  ChevronRight,
  FileText,
  Link,
  Layers,
  LayoutTemplate,
  Zap,
  Rocket,
} from "lucide-react";
import type { PipelineStep } from "@/data/types";

// Icon mapping
const iconMap = {
  FileText,
  Link,
  Layers,
  LayoutTemplate,
  Zap,
  Rocket,
} as const;

interface PipelineProps {
  steps: PipelineStep[];
}

export function Pipeline({ steps }: PipelineProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  const toggleStep = (step: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(step)) {
      newExpanded.delete(step);
    } else {
      newExpanded.add(step);
    }
    setExpandedSteps(newExpanded);
  };

  return (
    <section id="pipeline" className="pb-24">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-secondary">
        Pipeline
      </p>
      <h2 className="mb-3 text-3xl font-semibold tracking-tight text-foreground">
        How It Works
      </h2>
      <p className="mb-12 max-w-xl text-[15px] leading-7 text-muted-foreground">
        Define your domain once, generate consistent architecture everywhere. No
        more repetitive AI prompts or architectural drift.
      </p>

      <div className="overflow-hidden rounded-2xl border-border bg-card/50">
        {steps.map(({ step, description, details, icon }, i) => {
          const isExpanded = expandedSteps.has(step);

          return (
            <div
              key={step}
              className={`${
                i !== steps.length - 1 ? "border-b border-border" : ""
              }`}
            >
              <button
                onClick={() => toggleStep(step)}
                className="w-full flex items-center gap-5 px-6 py-4 text-left transition-colors hover:bg-card-muted/50 group"
              >
                <span className="w-8 shrink-0 font-mono text-xs text-muted-foreground group-hover:text-primary">
                  {step}
                </span>

                <div className="flex items-center gap-2 flex-1">
                  {icon && iconMap[icon as keyof typeof iconMap] && (
                    <span className="text-primary">
                      {React.createElement(
                        iconMap[icon as keyof typeof iconMap],
                        { className: "h-5 w-5" },
                      )}
                    </span>
                  )}
                  <div className="h-px flex-1 border-t border-dashed border-border" />
                </div>

                <span className="text-sm font-medium text-foreground group-hover:text-foreground">
                  {description}
                </span>

                <div className="flex items-center gap-2">
                  <ChevronRight
                    className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
                      isExpanded ? "rotate-90" : ""
                    } group-hover:text-secondary`}
                  />
                </div>
              </button>

              {/* Expanded Content */}
              <div
                className={`overflow-hidden transition-all duration-300 ease-in-out ${
                  isExpanded ? "max-h-32 opacity-100" : "max-h-0 opacity-0"
                }`}
              >
                <div className="px-6 pb-4 pt-0">
                  <div className="pl-13 text-sm text-muted-foreground leading-relaxed">
                    {details}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
