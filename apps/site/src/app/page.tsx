import type { Metadata, NextPage } from "next";

import { CTABanner } from "@/components/landing/CTABanner";
import { Ecosystem } from "@/components/landing/Ecosystem";
import { Examples } from "@/components/landing/Examples";
import { Features } from "@/components/landing/Features";
import { Hero } from "@/components/landing/Hero";
import { Pipeline } from "@/components/landing/Pipeline";
import { UseCases } from "@/components/landing/UseCases";
import { CONTRACT_CODE, RUNTIME_CODE, TASK_CODE } from "@/data/code-examples";
import { FEATURES } from "@/data/features";
import { PIPELINE_STEPS } from "@/data/pipeline";
import { USE_CASES } from "@/data/use-cases";

export const metadata: Metadata = {
  title: "Codepot — typed software intent and reusable code generation",
  description:
    "Explore Codepot's supported OpenAPI and Jinja packages, official JavaScript runtime, and final Rust language platform for developers, tools, and AI agents.",
  alternates: {
    canonical: "/",
  },
};

const Home: NextPage = () => {
  return (
    <div className="landing-shell mx-auto w-full max-w-7xl px-3 md:px-6">
      <div aria-hidden="true" className="landing-free-curves">
        <span />
        <span />
        <span />
      </div>
      <Hero />
      <Ecosystem />
      <Features features={FEATURES} />
      <Pipeline steps={PIPELINE_STEPS} />
      <Examples contractCode={CONTRACT_CODE} taskCode={TASK_CODE} runtimeCode={RUNTIME_CODE} />
      <UseCases useCases={USE_CASES} />
      <CTABanner />
    </div>
  );
};

export default Home;
