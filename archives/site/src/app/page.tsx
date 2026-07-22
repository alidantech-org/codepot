import type { NextPage } from "next";
import type { Metadata } from "next";
import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { Pipeline } from "@/components/landing/Pipeline";
import { Examples } from "@/components/landing/Examples";
import { UseCases } from "@/components/landing/UseCases";
import { CTABanner } from "@/components/landing/CTABanner";

import { FEATURES } from "@/data/features";
import { PIPELINE_STEPS } from "@/data/pipeline";
import { USE_CASES } from "@/data/use-cases";
import { ENTITY_CODE, TEMPLATE_CODE, OUTPUT_CODE } from "@/data/code-examples";
import { generateMetadata } from "@/lib/metadata";

export const metadata: Metadata = generateMetadata();

// ─── Page ─────────────────────────────────────────────────────────────────────

const Home: NextPage = () => {
  return (
    <div className="mx-auto w-full max-w-7xl px-3 md:px-6">
      <Hero />
      <Features features={FEATURES} />
      <Pipeline steps={PIPELINE_STEPS} />
      <Examples
        entityCode={ENTITY_CODE}
        templateCode={TEMPLATE_CODE}
        outputCode={OUTPUT_CODE}
      />
      <UseCases useCases={USE_CASES} />
      <CTABanner />
    </div>
  );
};

export default Home;
