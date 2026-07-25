import type { Metadata, NextPage } from "next";

import { CTABanner } from "@/components/landing/CTABanner";
import { Ecosystem } from "@/components/landing/Ecosystem";
import { Examples } from "@/components/landing/Examples";
import { Features } from "@/components/landing/Features";
import { Hero } from "@/components/landing/Hero";
import { Pipeline } from "@/components/landing/Pipeline";
import { UseCases } from "@/components/landing/UseCases";
import { FEATURES } from "@/data/features";
import { PIPELINE_STEPS } from "@/data/pipeline";
import { USE_CASES } from "@/data/use-cases";
import { getLandingWorkflowExamples } from "@/lib/landing-workflow-examples";

import styles from "./landing.module.css";

export const metadata: Metadata = {
  title: "Codepot — typed software intent and reusable code generation",
  description:
    "Explore Codepot's supported OpenAPI and Jinja packages, official JavaScript runtime, and final Rust language platform for developers, tools, and AI agents.",
  alternates: {
    canonical: "/",
  },
};

const Home: NextPage = () => {
  const workflowExamples = getLandingWorkflowExamples();

  return (
    <div className={`landing-page relative w-full ${styles.page}`}>
      <div aria-hidden="true" className="landing-free-curves">
        <span />
        <span />
        <span />
      </div>
      <Hero />
      <Ecosystem />
      <Features features={FEATURES} />
      <Pipeline steps={PIPELINE_STEPS} />
      <Examples examples={workflowExamples} />
      <UseCases useCases={USE_CASES} />
      <CTABanner />
    </div>
  );
};

export default Home;
