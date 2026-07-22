import type { Metadata, NextPage } from "next";

import { CTABanner } from "@/components/landing/CTABanner";
import { Examples } from "@/components/landing/Examples";
import { Features } from "@/components/landing/Features";
import { Hero } from "@/components/landing/Hero";
import { Pipeline } from "@/components/landing/Pipeline";
import { UseCases } from "@/components/landing/UseCases";
import { CONTRACT_CODE, TASK_CODE, TEMPLATE_CODE } from "@/data/code-examples";
import { FEATURES } from "@/data/features";
import { PIPELINE_STEPS } from "@/data/pipeline";
import { USE_CASES } from "@/data/use-cases";

export const metadata: Metadata = {
  title: "Codepot — reliable context for developers and AI",
  description:
    "Use typed contracts, reusable template packs, and project-owned generation tasks to keep developer and AI-generated code consistent.",
};

const Home: NextPage = () => {
  return (
    <div className="mx-auto w-full max-w-7xl px-3 md:px-6">
      <Hero />
      <Features features={FEATURES} />
      <Pipeline steps={PIPELINE_STEPS} />
      <Examples contractCode={CONTRACT_CODE} templateCode={TEMPLATE_CODE} taskCode={TASK_CODE} />
      <UseCases useCases={USE_CASES} />
      <CTABanner />
    </div>
  );
};

export default Home;
